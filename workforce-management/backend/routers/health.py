"""
AI-Powered Workforce Management Automation System
Health, Readiness & Metrics Endpoints
--------------------------------------------------
Implements Kubernetes/Docker standard liveness and readiness probes,
dependency-aware status checks, and application metrics reporting.
"""

import os
from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.config import settings
from database.mongodb import check_connection
from backend.monitoring.metrics import metrics
from backend.workflows.scheduler import get_workflow_scheduler

router = APIRouter(tags=["System & Observability"])

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@router.get("/health", summary="Basic System & Database Health Check")
async def health_check():
    """
    Verifies that the FastAPI server is running and actively connected to MongoDB.
    Maintained for backward compatibility.
    """
    mongo_status = check_connection()
    if not mongo_status["ok"]:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": mongo_status.get("error")
        }

    return {
        "status": "healthy",
        "database": "connected",
        "database_name": mongo_status["database"],
        "mongodb_version": mongo_status["version"],
        "api_version": settings.VERSION
    }

@router.get("/health/live", summary="Liveness Probe")
async def liveness_probe():
    """
    Lightweight probe confirming the FastAPI process is alive and responsive.
    Suitable for container orchestrator liveness checks (e.g. Kubernetes livenessProbe).
    """
    return {
        "status": "alive",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/health/ready", summary="Readiness Probe with Dependency Auditing")
async def readiness_probe():
    """
    Evaluates whether the service and its critical dependencies are ready to accept traffic.
    Examines:
    - MongoDB connectivity (CRITICAL: returns 503 if unavailable)
    - AI Workforce Models (NON-CRITICAL: reports degraded if uninitialized)
    - Workflow Engine Scheduler (NON-CRITICAL)
    - External Integrations (Reports healthy, degraded, or not_configured)
    """
    dependencies = {}
    is_ready = True

    # 1. MongoDB Database Check (CRITICAL)
    mongo_status = check_connection()
    if mongo_status["ok"]:
        dependencies["database"] = {
            "status": "healthy",
            "type": "mongodb",
            "database": mongo_status["database"],
            "version": mongo_status["version"]
        }
    else:
        dependencies["database"] = {
            "status": "unavailable",
            "type": "mongodb",
            "error": mongo_status.get("error", "Failed to connect")
        }
        is_ready = False

    # 2. AI Model Pipelines Check (NON-CRITICAL)
    models_dir = os.path.join(ROOT_DIR, "models")
    attrition_exists = os.path.exists(os.path.join(models_dir, "attrition"))
    absenteeism_exists = os.path.exists(os.path.join(models_dir, "absenteeism"))
    forecasting_exists = os.path.exists(os.path.join(models_dir, "workforce_forecasting"))
    
    if attrition_exists and absenteeism_exists and forecasting_exists:
        dependencies["ai_models"] = {
            "status": "healthy",
            "models_loaded": ["attrition", "absenteeism", "workforce_forecasting"]
        }
    else:
        dependencies["ai_models"] = {
            "status": "degraded",
            "note": "Some serialized model artifacts are missing"
        }

    # 3. Workflow Engine & Scheduler
    try:
        scheduler = get_workflow_scheduler()
        dependencies["workflow_scheduler"] = {
            "status": "healthy" if scheduler.is_running else "degraded",
            "is_running": scheduler.is_running,
            "interval_seconds": scheduler.interval_seconds
        }
    except Exception as e:
        dependencies["workflow_scheduler"] = {
            "status": "unavailable",
            "error": str(e)
        }

    # 4. RAG / Policy Vector Search Check
    rag_dir = os.path.join(ROOT_DIR, "data", "policies")
    dependencies["rag_vector_search"] = {
        "status": "healthy" if os.path.exists(rag_dir) else "degraded",
        "provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER
    }

    # 5. External Integrations Status (Reporting without fake claims)
    dependencies["integrations"] = {
        "microsoft_teams": "healthy" if settings.TEAMS_ENABLED else "not_configured",
        "slack": "healthy" if settings.SLACK_ENABLED else "not_configured",
        "microsoft_calendar": "healthy" if settings.MICROSOFT_CALENDAR_ENABLED else "not_configured",
        "google_calendar": "healthy" if settings.GOOGLE_CALENDAR_ENABLED else "not_configured",
        "email_channel": "healthy" if settings.EMAIL_ENABLED else "not_configured",
        "sap_erp": "healthy" if settings.SAP_ENABLED else "not_configured",
        "oracle_hrms": "healthy" if settings.ORACLE_HRMS_ENABLED else "not_configured",
        "biometric_kiosks": "healthy" if settings.BIOMETRIC_ENABLED else "not_configured"
    }

    overall_status = "healthy" if is_ready else "unavailable"
    if is_ready and any(
        dep.get("status") == "degraded"
        for k, dep in dependencies.items()
        if isinstance(dep, dict) and "status" in dep
    ):
        overall_status = "degraded"

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": dependencies
        }
    )

@router.get("/metrics", summary="Application Metrics Exposition")
async def get_metrics(format: str = "prometheus"):
    """
    Exposes application metrics for Prometheus scraping or JSON dashboard consumption.
    Query parameter ?format=json returns structured JSON.
    Default returns standard Prometheus text format.
    """
    if format.lower() == "json":
        return metrics.get_summary()

    return PlainTextResponse(
        content=metrics.to_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
