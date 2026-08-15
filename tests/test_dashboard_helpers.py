import pytest
import pandas as pd
from unittest.mock import patch, Mock
from dashboard.api_client import get_analytics, predict_incident, get_similar_incidents
from dashboard.charts import plot_volume_over_time, plot_distribution, plot_sla_pie

@patch('dashboard.api_client.requests.get')
def test_get_analytics(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"total_incidents": 100}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    data = get_analytics()
    assert data["total_incidents"] == 100
    mock_get.assert_called_once_with("http://localhost:8000/analytics")

@patch('dashboard.api_client.requests.post')
def test_predict_incident(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"risk_level": "HIGH"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    data = predict_incident({"opened_hour": 10})
    assert data["risk_level"] == "HIGH"
    mock_post.assert_called_once_with("http://localhost:8000/predict", json={"opened_hour": 10})

def test_plot_volume_over_time_empty():
    fig = plot_volume_over_time([])
    assert fig is not None

def test_plot_volume_over_time():
    data = [{"month": "2026-01", "count": 10}, {"month": "2026-02", "count": 20}]
    fig = plot_volume_over_time(data)
    assert fig is not None
    # Figure layout title text check
    assert "Incident Volume" in fig.layout.title.text

def test_plot_distribution():
    data = [{"category": "Software", "count": 15}, {"category": "Hardware", "count": 5}]
    fig = plot_distribution(data, "category", "Cat Dist")
    assert fig is not None
    assert "Cat Dist" in fig.layout.title.text

def test_plot_sla_pie():
    data = [{"made_sla": True, "count": 80}, {"made_sla": False, "count": 20}]
    fig = plot_sla_pie(data)
    assert fig is not None
    assert "SLA Breakdown" in fig.layout.title.text
