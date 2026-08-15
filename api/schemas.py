from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    contact_type: str = Field(default="Missing")
    category: str = Field(default="Missing")
    subcategory: str = Field(default="Missing")
    u_symptom: str = Field(default="Missing")
    impact: str = Field(default="Missing")
    urgency: str = Field(default="Missing")
    location: str = Field(default="Missing")
    assignment_group: str = Field(default="Missing")
    opened_hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)

class PredictResponse(BaseModel):
    sla_breach_probability: float
    risk_level: str
    estimated_resolution_hours: float

class SimilarIncidentResponse(BaseModel):
    incident_id: str
    similarity_score: float
