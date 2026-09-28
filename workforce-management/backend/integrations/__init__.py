"""
AI Workforce Management Automation System - Integration Subsystem
-----------------------------------------------------------------
Provides modular, decoupled enterprise connectors, health monitoring,
synchronization tracking, and secure inbound webhooks.
"""

from backend.integrations.base import (
    IntegrationStatus,
    ConnectionTestResult,
    IntegrationHealth,
    SyncResult,
    WebhookEvent,
    BaseConnector,
    CircuitBreaker,
    with_retry
)
from backend.integrations.registry import registry, IntegrationRegistry
from backend.integrations.sync import SyncManager
from backend.integrations.webhooks import WebhookSecurity, WebhookDispatcher

__all__ = [
    "IntegrationStatus",
    "ConnectionTestResult",
    "IntegrationHealth",
    "SyncResult",
    "WebhookEvent",
    "BaseConnector",
    "CircuitBreaker",
    "with_retry",
    "registry",
    "IntegrationRegistry",
    "SyncManager",
    "WebhookSecurity",
    "WebhookDispatcher",
]
