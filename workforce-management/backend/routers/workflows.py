"""
Workflows & Preferences Direct Endpoints Router
------------------------------------------------
Provides administrative inspection of workflow rules, triggered events,
scheduler operational status, and direct /notification-preferences routes.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from database.mongodb import get_db
from backend.auth.dependencies import get_current_user, require_role
from backend.workflows.engine import get_workflow_engine
from backend.workflows.scheduler import get_workflow_scheduler
from backend.schemas.notification import (
    WorkflowStatusResponse,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate
)
from backend.notifications.preferences import NotificationPreferencesService

router = APIRouter(tags=["Workflows & Automation"])

_pref_service = NotificationPreferencesService()

# -------------------------------------------------------------------
# 1. Direct /notification-preferences route (Section 24 specification)
# -------------------------------------------------------------------
@router.get("/notification-preferences", response_model=NotificationPreferencesResponse, summary="Get user notification preferences")
async def get_preferences_direct(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    return _pref_service.get_preferences(emp_id)

@router.put("/notification-preferences", response_model=NotificationPreferencesResponse, summary="Update user notification preferences")
async def update_preferences_direct(
    payload: NotificationPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employee_id") or current_user.get("user_id")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    return _pref_service.update_preferences(emp_id, updates)

# -------------------------------------------------------------------
# 2. Workflow Rules & Status (HR/Admin Scoped)
# -------------------------------------------------------------------
@router.get("/workflows", summary="List active workflow rules (HR/Admin only)")
async def list_workflows(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    engine = get_workflow_engine()
    return engine.get_all_rules()

@router.get("/workflows/events", summary="List recent workflow events (HR/Admin only)")
async def list_workflow_events(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    events = list(db.workflow_events.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    return events

@router.get("/workflows/status", response_model=WorkflowStatusResponse, summary="Get workflow scheduler & engine status")
async def get_workflow_status(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    scheduler = get_workflow_scheduler()
    return scheduler.get_status()

@router.post("/workflows/run-scheduled", summary="Manually trigger all scheduled HR checks (HR/Admin only)")
async def trigger_scheduled_checks(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    scheduler = get_workflow_scheduler()
    results = scheduler.run_all_checks()
    return {
        "status": "success",
        "message": "Scheduled HR workflow checks executed successfully.",
        "results": results
    }
