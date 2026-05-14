"""
MedAI - Agent API Endpoints
Exposes all AI agents via REST API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from backend.api.auth import get_current_user
from backend.database.models import User
from agents.supervisor_agent import supervisor

router = APIRouter(prefix="/api/agents", tags=["AI Agents"])


class AgentRequest(BaseModel):
    query: str
    query_type: str = "auto"
    patient_info: dict = {}
    features: dict = {}
    filters: dict = {}
    dashboard_type: str = "executive_dashboard"


class AgentQueryRequest(BaseModel):
    query: str
    n_results: int = 5


class RiskRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    features: dict = {}
    model_name: Optional[str] = None
    # Patient fields for convenience
    age_numeric: float = 55
    time_in_hospital: int = 4
    num_lab_procedures: int = 40
    num_procedures: int = 1
    num_medications: int = 12
    number_outpatient: int = 0
    number_emergency: int = 0
    number_inpatient: int = 0
    number_diagnoses: int = 7


@router.post("/analyze")
async def full_analysis(request: AgentRequest, user: User = Depends(get_current_user)):
    """Run the full multi-agent analysis pipeline."""
    result = await supervisor.process({
        "query": request.query,
        "query_type": request.query_type,
        "patient_info": request.patient_info,
        "features": request.features,
        "filters": request.filters,
        "dashboard_type": request.dashboard_type,
    })
    return result.model_dump()


@router.post("/intake")
async def patient_intake(request: AgentRequest, user: User = Depends(get_current_user)):
    """Process patient intake."""
    result = await supervisor.agents["intake"].process({
        "symptoms": request.query,
        "patient_info": request.patient_info,
    })
    return result.model_dump()


@router.post("/diagnose")
async def diagnose(request: AgentRequest, user: User = Depends(get_current_user)):
    """Get diagnostic hypotheses."""
    result = await supervisor._diagnosis_only({
        "query": request.query,
        "patient_info": request.patient_info,
    })
    return result.model_dump()


@router.post("/predict-risk")
async def predict_risk(request: RiskRequest, user: User = Depends(get_current_user)):
    """Predict patient risk."""
    features = request.features or {
        "age_numeric": request.age_numeric,
        "time_in_hospital": request.time_in_hospital,
        "num_lab_procedures": request.num_lab_procedures,
        "num_procedures": request.num_procedures,
        "num_medications": request.num_medications,
        "number_outpatient": request.number_outpatient,
        "number_emergency": request.number_emergency,
        "number_inpatient": request.number_inpatient,
        "number_diagnoses": request.number_diagnoses,
    }
    result = await supervisor.agents["risk"].process({"features": features, "model_name": request.model_name})
    return result.model_dump()


@router.post("/search-knowledge")
async def search_knowledge(request: AgentQueryRequest, user: User = Depends(get_current_user)):
    """Search medical knowledge base."""
    result = await supervisor.agents["rag"].process({
        "query": request.query,
        "n_results": request.n_results,
    })
    return result.model_dump()


@router.post("/recommend-treatment")
async def recommend_treatment(request: AgentRequest, user: User = Depends(get_current_user)):
    """Get treatment recommendations."""
    result = await supervisor.agents["treatment"].process({
        "diagnoses": request.patient_info.get("diagnoses", []),
        "risk_level": request.patient_info.get("risk_level", "MEDIUM"),
        "symptoms": request.patient_info.get("symptoms", []),
        "medications": request.patient_info.get("medications", []),
        "patient_info": request.patient_info,
    })
    return result.model_dump()
