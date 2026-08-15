import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import pytest
from src.models.pipeline import create_preprocessing_pipeline
from src.similarity.similarity import IncidentSimilarityEngine
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def get_synthetic_data():
    return pd.DataFrame({
        'number': ['INC01', 'INC02', 'INC03', 'INC04', 'INC05'],
        'category': ['Software', 'Hardware', 'Software', 'Hardware', 'Network'],
        'subcategory': ['OS', 'PC', 'App', 'Printer', 'Router'],
        'u_symptom': ['Crash', 'Slow', 'Crash', 'Paper Jam', 'Down'],
        'impact': ['1 - High', '2 - Medium', '3 - Low', '2 - Medium', '1 - High'],
        'urgency': ['1 - High', '2 - Medium', '3 - Low', '2 - Medium', '1 - High'],
        'location': ['Site A', 'Site B', 'Site A', 'Site C', 'Site D'],
        'assignment_group': ['Group 1', 'Group 2', 'Group 1', 'Group 3', 'Group 4'],
        'opened_hour': [9, 10, 11, 14, 15],
        'day_of_week': [0, 1, 2, 3, 4],
        'month': [1, 1, 2, 2, 3],
        # Only needed to prevent KeyError in pipeline (if these are listed as categoricals)
        'contact_type': ['Phone'] * 5, 'priority': ['1'] * 5,
        'caller_id': ['Caller 1'] * 5, 'opened_by': ['User 1'] * 5,
        'assigned_to': ['Agent 1'] * 5,
        'target_made_sla': [True, False, True, True, False],
        'target_resolution_time_hours': [1.5, 20.0, 0.5, 4.0, 15.0]
    })

def test_preprocessing_pipeline():
    df = get_synthetic_data()
    preprocessor = create_preprocessing_pipeline()
    
    # Fit transform should drop targets and 'number'
    X = df.drop(columns=['target_made_sla', 'target_resolution_time_hours'])
    transformed = preprocessor.fit_transform(X)
    
    # Output should be a sparse matrix or dense array, typically sparse for OneHot
    assert transformed.shape[0] == 5
    assert transformed.shape[1] > 5 # Many encoded features

def test_model_pipeline_predict_proba():
    df = get_synthetic_data()
    X = df.drop(columns=['target_made_sla', 'target_resolution_time_hours'])
    y = df['target_made_sla']
    
    preprocessor = create_preprocessing_pipeline()
    model = LogisticRegression()
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    
    pipeline.fit(X, y)
    probs = pipeline.predict_proba(X)
    
    assert probs.shape == (5, 2)
    assert np.all((probs >= 0) & (probs <= 1))

def test_similarity_engine():
    df = get_synthetic_data()
    engine = IncidentSimilarityEngine()
    engine.fit(df)
    
    sample_incident = df.iloc[0].to_dict()
    similar = engine.find_similar_incidents(sample_incident, top_n=2)
    
    assert len(similar) == 2
    # The first one should be itself (or very similar)
    assert similar[0][0] == 'INC01'
    assert similar[0][1] >= 0.99 # almost 1.0 similarity
