from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.engine import Engine
import pandas as pd
from datetime import datetime
from src.db.connection import get_engine
from api.schemas import PredictRequest, PredictResponse, SimilarIncidentResponse

# This will be injected dynamically on startup
models_registry = {}

router = APIRouter()

def get_db_engine():
    return get_engine()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/incidents")
def get_incidents(limit: int = 50, offset: int = 0, engine: Engine = Depends(get_db_engine)):
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM incidents LIMIT {limit} OFFSET {offset}", con=conn)
        return df.to_dict(orient="records")

@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, engine: Engine = Depends(get_db_engine)):
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM incidents WHERE incident_id = '{incident_id}'", con=conn)
        if df.empty:
            raise HTTPException(status_code=404, detail="Incident not found")
        return df.to_dict(orient="records")[0]

@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, engine: Engine = Depends(get_db_engine)):
    if "sla_model" not in models_registry or "res_model" not in models_registry:
        raise HTTPException(status_code=500, detail="Models not loaded")
        
    # Format input for models
    input_df = pd.DataFrame([request.dict()])
    
    # Optional defaults if some pipeline columns were missed (e.g., opened_by, caller_id)
    input_df['opened_by'] = "Missing"
    input_df['caller_id'] = "Missing"
    input_df['assigned_to'] = "Missing"
    input_df['priority'] = "Missing"
    
    # Predict SLA Breach
    # The minority class is 'False' (Breached). Assuming models_registry['sla_model'] is trained to predict boolean (True=Met, False=Breached)
    # The probability of breach is the probability of class False (index 0 usually, but let's be careful).
    sla_classes = models_registry["sla_model"].classes_
    breach_idx = list(sla_classes).index(False)
    
    sla_probs = models_registry["sla_model"].predict_proba(input_df)[0]
    breach_prob = float(sla_probs[breach_idx])
    
    # Predict Resolution Time
    res_time = float(models_registry["res_model"].predict(input_df)[0])
    
    # Determine Risk Level
    # Risk thresholds: < 0.3 LOW, 0.3 - 0.6 MEDIUM, > 0.6 HIGH
    if breach_prob < 0.3:
        risk_level = "LOW"
    elif breach_prob <= 0.6:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    # Log prediction to MySQL
    prediction_df = pd.DataFrame({
        'incident_id': [None], # Since it's ad-hoc
        'model_name': ["sla_rf_and_res_rf"],
        'model_version': ["1.0"],
        'sla_breach_probability': [breach_prob],
        'sla_risk_level': [risk_level],
        'estimated_resolution_hours': [res_time],
        'prediction_timestamp': [datetime.now()]
    })
    
    try:
        prediction_df.to_sql('incident_predictions', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"Failed to log prediction: {e}")
        
    return PredictResponse(
        sla_breach_probability=breach_prob,
        risk_level=risk_level,
        estimated_resolution_hours=res_time
    )

@router.post("/similar-incidents", response_model=List[SimilarIncidentResponse])
def get_similar_incidents(request: PredictRequest):
    if "similarity_engine" not in models_registry:
        raise HTTPException(status_code=500, detail="Similarity engine not loaded")
        
    sim_results = models_registry["similarity_engine"].find_similar_incidents(request.dict(), top_n=5)
    
    return [{"incident_id": res[0], "similarity_score": res[1]} for res in sim_results]

@router.get("/analytics")
def get_analytics(engine: Engine = Depends(get_db_engine)):
    with engine.connect() as conn:
        df = pd.read_sql("SELECT made_sla, resolution_time_hours, category, subcategory, impact, urgency, location, assignment_group, opened_at FROM incidents", con=conn)
        
        total = len(df)
        avg_res = df['resolution_time_hours'].mean() if total > 0 else None
        
        sla_counts = df['made_sla'].value_counts().reset_index()
        sla_counts.columns = ['made_sla', 'count']
        
        category_dist = df['category'].value_counts().reset_index()
        category_dist.columns = ['category', 'count']
        
        subcategory_dist = df['subcategory'].value_counts().reset_index()
        subcategory_dist.columns = ['subcategory', 'count']
        
        impact_dist = df['impact'].value_counts().reset_index()
        impact_dist.columns = ['impact', 'count']
        
        urgency_dist = df['urgency'].value_counts().reset_index()
        urgency_dist.columns = ['urgency', 'count']
        
        location_dist = df['location'].value_counts().reset_index()
        location_dist.columns = ['location', 'count']
        
        assignment_dist = df['assignment_group'].value_counts().reset_index()
        assignment_dist.columns = ['assignment_group', 'count']
        
        # Volume over time
        df['month'] = pd.to_datetime(df['opened_at']).dt.strftime('%Y-%m')
        volume_over_time = df['month'].value_counts().sort_index().reset_index()
        volume_over_time.columns = ['month', 'count']
        
        return {
            "total_incidents": int(total),
            "average_resolution_hours": float(avg_res) if pd.notnull(avg_res) else None,
            "sla_counts": sla_counts.to_dict(orient='records'),
            "category_dist": category_dist.to_dict(orient='records'),
            "subcategory_dist": subcategory_dist.to_dict(orient='records'),
            "impact_dist": impact_dist.to_dict(orient='records'),
            "urgency_dist": urgency_dist.to_dict(orient='records'),
            "location_dist": location_dist.to_dict(orient='records'),
            "assignment_dist": assignment_dist.to_dict(orient='records'),
            "volume_over_time": volume_over_time.to_dict(orient='records')
        }
