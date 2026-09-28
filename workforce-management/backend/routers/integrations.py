"""
External Integrations Management Router
---------------------------------------
Admin-only endpoints for monitoring integration health, executing connection tests,
managing synchronization runs, and processing inbound secure webhooks.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Body, Query
from backend.auth.dependencies import require_role
from backend.integrations.registry import registry
from backend.integrations.base.models import (
    IntegrationHealth,
    ConnectionTestResult,
    SyncResult
)
from backend.integrations.sync import SyncManager
from backend.integrations.webhooks import WebhookDispatcher

router = APIRouter(prefix="/integrations", tags=["External Integrations"])

@router.get("", response_model=List[IntegrationHealth], summary="List all external integrations and health status")
async def list_integrations(current_user: dict = Depends(require_role(["ADMIN"]))):
    """
    Returns the real-time operational status, configuration state, and circuit-breaker
    health for all registered enterprise integrations. (Admin only)
    """
    return registry.get_all_health()

@router.get("/{name}", response_model=IntegrationHealth, summary="Get single integration health")
async def get_integration(name: str, current_user: dict = Depends(require_role(["ADMIN"]))):
    """
    Returns detailed health and operational metrics for a specific integration.
    """
    connector = registry.get_connector(name)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{name}' not found."
        )
    return connector.get_health()

@router.post("/{name}/test", response_model=ConnectionTestResult, summary="Test integration connection safely")
async def test_integration_connection(name: str, current_user: dict = Depends(require_role(["ADMIN"]))):
    """
    Executes a non-destructive connectivity and authentication verification.
    Returns latency, operational status, and diagnostics.
    """
    connector = registry.get_connector(name)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{name}' not found in registry."
        )
    return connector.test_connection()

@router.get("/{name}/sync-history", summary="Get recent synchronization history for an integration")
async def get_sync_history(
    name: str,
    limit: int = Query(25, ge=1, le=100),
    current_user: dict = Depends(require_role(["ADMIN"]))
):
    """
    Retrieves audit logs of past background or manual synchronization runs.
    """
    connector = registry.get_connector(name)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{name}' not found."
        )
    return SyncManager.get_sync_history(integration=name, limit=limit)

@router.post("/{name}/sync", response_model=SyncResult, summary="Trigger manual data synchronization")
async def trigger_manual_sync(
    name: str,
    payload: Optional[Dict[str, Any]] = Body(None),
    current_user: dict = Depends(require_role(["ADMIN"]))
):
    """
    Initiates an on-demand data synchronization job for the specified integration.
    """
    connector = registry.get_connector(name)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{name}' not found."
        )
    return SyncManager.execute_sync(connector, payload)

# -------------------------------------------------------------------
# Inbound Webhook Receiver
# -------------------------------------------------------------------
@router.post("/webhooks/{provider}", summary="Process incoming external webhook")
async def handle_incoming_webhook(
    provider: str,
    request: Request,
    x_signature_256: Optional[str] = Header(None, alias="X-Signature-256"),
    x_webhook_timestamp: Optional[str] = Header(None, alias="X-Webhook-Timestamp"),
    event_type: str = Query("generic", alias="event")
):
    """
    Receives, cryptographically verifies, and dispatches external webhooks.
    Applies HMAC-SHA256 signature verification, replay protection, and deduplication.
    """
    body_bytes = await request.body()
    try:
        payload = await request.json() if body_bytes else {}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON webhook body."
        )

    success, msg, details = WebhookDispatcher.process_incoming_webhook(
        provider=provider,
        event_type=event_type,
        payload=payload,
        signature=x_signature_256,
        timestamp_header=x_webhook_timestamp,
        raw_body=body_bytes
    )

    if not success:
        if "INVALID_SIGNATURE" in msg:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        elif "TIMESTAMP_EXPIRED" in msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    return {
        "status": "ACCEPTED",
        "provider": provider,
        "message": msg,
        "details": details
    }
