import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_analytics():
    response = requests.get(f"{API_URL}/analytics")
    response.raise_for_status()
    return response.json()

def predict_incident(data: dict):
    response = requests.post(f"{API_URL}/predict", json=data)
    response.raise_for_status()
    return response.json()

def get_similar_incidents(data: dict):
    response = requests.post(f"{API_URL}/similar-incidents", json=data)
    response.raise_for_status()
    return response.json()
