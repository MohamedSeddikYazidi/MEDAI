"""
MedAI - Analytics API Endpoints
Serves dashboard data and KPIs for the frontend.
"""

from fastapi import APIRouter, Depends
from backend.api.auth import get_current_user
from backend.database.models import User
from agents.bi_agent import BIAgent

router = APIRouter(prefix="/api/analytics", tags=["Analytics & BI"])

bi_agent = BIAgent()


@router.get("/kpis")
async def get_kpis(user: User = Depends(get_current_user)):
    """Get executive KPIs."""
    result = await bi_agent.process({"query_type": "kpis"})
    return result.data


@router.get("/dashboard/{dashboard_type}")
async def get_dashboard(dashboard_type: str, user: User = Depends(get_current_user)):
    """
    Get dashboard data.
    Types: executive_dashboard, predictive_dashboard, clinical_dashboard, operational_dashboard
    """
    result = await bi_agent.process({"query_type": dashboard_type})
    return result.data


@router.get("/model-metrics")
async def get_model_metrics(user: User = Depends(get_current_user)):
    """Get ML model performance metrics."""
    try:
        from models.predictor import prediction_service
        return prediction_service.get_all_metrics()
    except Exception as e:
        return {"error": str(e), "message": "Train models first with: python -m models.training"}
