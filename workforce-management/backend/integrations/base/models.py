"""
Integration Data Models & Schema Definitions
--------------------------------------------
Standardized types for health, connection testing, sync results, and webhooks.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

class IntegrationStatus(str, Enum):
    CONNECTED = "CONNECTED"
    CONFIGURED = "CONFIGURED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    BLOCKED_EXTERNAL_DEPENDENCY = "BLOCKED_EXTERNAL_DEPENDENCY"

class ConnectionTestResult(BaseModel):
    success: bool
    status: IntegrationStatus
    message: str
    latency_ms: float = 0.0
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class IntegrationHealth(BaseModel):
    name: str
    category: str
    display_name: str
    enabled: bool
    configured: bool
    status: IntegrationStatus
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    error_message: Optional[str] = None
    total_calls: int = 0
    failed_calls: int = 0
    circuit_breaker_state: str = "CLOSED"

class SyncResult(BaseModel):
    sync_id: str
    integration: str
    status: str  # "SUCCESS", "PARTIAL", "FAILED", "RUNNING"
    records_read: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    started_at: str
    completed_at: Optional[str] = None
    error_summary: Optional[str] = None

class WebhookEvent(BaseModel):
    provider: str
    event_type: str
    payload: Dict[str, Any]
    event_id: Optional[str] = None
    timestamp: Optional[str] = None
    signature_verified: bool = False
