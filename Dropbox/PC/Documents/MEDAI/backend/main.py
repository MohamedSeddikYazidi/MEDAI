"""
MedAI - FastAPI Main Application
Entry point for the backend API server.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.config import settings
from backend.database.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"[*] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_database()

    # Initialize RAG knowledge base
    try:
        from rag.ingestion import ingest_medical_knowledge
        ingest_medical_knowledge()
    except Exception as e:
        print(f"[!] RAG ingestion skipped: {e}")

    # Load ML models
    try:
        from models.predictor import prediction_service
        prediction_service.load()
    except Exception as e:
        print(f"[!] ML models not loaded: {e}")

    yield

    # Shutdown
    print(f"[*] Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent Medical Decision Support Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Register routers
from backend.api.auth import router as auth_router
from backend.api.agents import router as agents_router
from backend.api.analytics import router as analytics_router
from backend.api.patients import router as patients_router
from backend.api.chat import router as chat_router

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(analytics_router)
app.include_router(patients_router)
app.include_router(chat_router)


# Health check
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


# System info
@app.get("/api/system/info", tags=["System"])
async def system_info():
    """Get system configuration info."""
    try:
        from models.predictor import prediction_service
        models = prediction_service.get_available_models()
    except Exception:
        models = []

    try:
        from rag.vector_store import vector_store
        rag_stats = vector_store.get_stats()
    except Exception:
        rag_stats = {}

    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "ml_models_loaded": models,
        "rag_status": rag_stats,
        "agents": [
            "Patient Intake Agent",
            "Diagnostic Agent",
            "Risk Prediction Agent",
            "Medical Knowledge RAG Agent",
            "Treatment Recommendation Agent",
            "BI & Analytics Agent",
            "Supervisor Agent",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
