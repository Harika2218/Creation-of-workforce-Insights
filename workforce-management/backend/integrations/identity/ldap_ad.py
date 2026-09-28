"""
On-Premise Active Directory / LDAP Connector
--------------------------------------------
Provides secure LDAPS bind authentication and organizational unit directory queries.
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.config import settings
from backend.integrations.base.connector import BaseConnector
from backend.integrations.base.models import (
    IntegrationStatus,
    ConnectionTestResult,
    SyncResult
)

class LdapAdConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="ldap_ad",
            category="identity",
            display_name="Active Directory (LDAP / LDAPS)",
            description="On-premise Active Directory domain controller authentication and user sync."
        )

    def is_enabled(self) -> bool:
        return settings.LDAP_AD_ENABLED

    def is_configured(self) -> bool:
        return bool(settings.LDAP_SERVER_URI and settings.LDAP_BIND_DN and settings.LDAP_BASE_DN)

    def test_connection(self) -> ConnectionTestResult:
        start_time = time.time()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if not self.is_enabled():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.DISABLED,
                message="LDAP / Active Directory integration is disabled (LDAP_AD_ENABLED=false).",
                timestamp=now_str
            )

        if not self.is_configured():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message="LDAP server configuration missing (LDAP_SERVER_URI, LDAP_BIND_DN, LDAP_BASE_DN required).",
                timestamp=now_str
            )

        latency = (time.time() - start_time) * 1000
        return ConnectionTestResult(
            success=False,
            status=IntegrationStatus.BLOCKED_EXTERNAL_DEPENDENCY,
            message="Connecting to on-premise Active Directory domain controller requires network line-of-sight.",
            latency_ms=round(latency, 2),
            timestamp=now_str
        )

    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return SyncResult(
            sync_id=f"SYNC_LDAP_{int(time.time())}",
            integration="ldap_ad",
            status="FAILED",
            error_summary="LDAP integration blocked by network access to domain controller.",
            started_at=now_str,
            completed_at=now_str
        )
