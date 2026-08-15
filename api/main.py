import joblib
import pandas as pd
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes import router, models_registry
from src.similarity.similarity import IncidentSimilarityEngine
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load SLA Model
    if os.path.exists('models/sla_risk_model.pkl'):
        models_registry['sla_model'] = joblib.load('models/sla_risk_model.pkl')
        
    # Load Resolution Model
    if os.path.exists('models/resolution_time_model.pkl'):
        models_registry['res_model'] = joblib.load('models/resolution_time_model.pkl')
        
    # Initialize and fit Similarity Engine
    if os.path.exists('data/processed/incidents_at_creation.csv'):
        df = pd.read_csv('data/processed/incidents_at_creation.csv')
        engine = IncidentSimilarityEngine()
        engine.fit(df)
        models_registry['similarity_engine'] = engine
        
    yield
    # Cleanup on shutdown if necessary
    models_registry.clear()

app = FastAPI(title="IT Incident Intelligence API", lifespan=lifespan)

app.include_router(router)
