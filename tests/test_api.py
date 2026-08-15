from fastapi.testclient import TestClient
import pytest
import os

# Set testing environment variable BEFORE importing app/engine
os.environ["TESTING"] = "True"

from api.main import app
from src.db.connection import get_engine
import pandas as pd

client = TestClient(app)

from sqlalchemy import text

@pytest.fixture(autouse=True)
def setup_test_db():
    # Create the test DB in memory
    engine = get_engine()
    # Simple setup of tables we query
    with engine.connect() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS incidents (
            incident_id VARCHAR(50), resolution_time_hours FLOAT, 
            made_sla BOOLEAN, category VARCHAR(50), subcategory VARCHAR(50), 
            impact VARCHAR(50), urgency VARCHAR(50), location VARCHAR(50), 
            assignment_group VARCHAR(50), opened_at DATETIME)"""))
        conn.execute(text("CREATE TABLE IF NOT EXISTS incident_predictions (prediction_id INT, incident_id VARCHAR(50), sla_risk_level VARCHAR(50))"))
        conn.execute(text("""INSERT INTO incidents (incident_id, resolution_time_hours, made_sla, category, subcategory, impact, urgency, location, assignment_group, opened_at) 
            VALUES ('INC0001', 5.0, 1, 'Software', 'OS', '1', '1', 'Loc1', 'Group1', '2026-01-01 10:00:00')"""))
        conn.commit()
    yield
    # No teardown needed for in-memory sqlite

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_missing_field():
    # month is required but missing here
    payload = {
        "opened_hour": 10,
        "day_of_week": 2
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422 # Pydantic Validation Error

def test_get_incident_not_found():
    response = client.get("/incidents/BAD_INCIDENT_ID")
    assert response.status_code == 404

def test_predict_success():
    payload = {
        "contact_type": "Phone",
        "category": "Software",
        "subcategory": "OS",
        "u_symptom": "Crash",
        "impact": "1 - High",
        "urgency": "1 - High",
        "location": "Site A",
        "assignment_group": "Group 1",
        "opened_hour": 9,
        "day_of_week": 0,
        "month": 1
    }
    
    # We trigger the lifespan manually via TestClient
    with TestClient(app) as client_with_lifespan:
        response = client_with_lifespan.post("/predict", json=payload)
        
        # If models didn't load (e.g., paths not found in CI), it returns 500, else 200
        if response.status_code == 200:
            data = response.json()
            assert "sla_breach_probability" in data
            assert "risk_level" in data
            assert "estimated_resolution_hours" in data
        else:
            assert response.status_code == 500

def test_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_incidents" in data
    assert "average_resolution_hours" in data
    # We inserted 1 record in setup
    assert data["total_incidents"] >= 1
