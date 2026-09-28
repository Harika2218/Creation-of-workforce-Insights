"""
Email Integration Connector
---------------------------
Connects the Email subsystem into the central Integration Registry.
Supports SMTP, SendGrid, Amazon SES, and local mock simulation.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import time
from backend.config import settings
from backend.integrations.base.connector import BaseConnector
from backend.integrations.base.models import (
    IntegrationStatus,
    ConnectionTestResult,
    SyncResult
)
from backend.integrations.email.smtp_provider import SMTPProvider
from backend.integrations.email.sendgrid_provider import SendGridProvider
from backend.integrations.email.mock_provider import MockEmailProvider

class EmailConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="email",
            category="email",
            display_name="Enterprise Email Delivery",
            description="Multi-provider transactional email service supporting SMTP, SendGrid, and AWS SES."
        )

    def is_enabled(self) -> bool:
        return settings.EMAIL_ENABLED

    def is_configured(self) -> bool:
        provider = settings.EMAIL_PROVIDER.lower()
        if provider == "smtp":
            return bool(settings.SMTP_HOST and settings.SMTP_HOST not in ["localhost", "127.0.0.1", ""])
        elif provider == "sendgrid":
            return bool(settings.SENDGRID_API_KEY)
        elif provider == "mock":
            return True
        return False

    def get_provider(self):
        prov = settings.EMAIL_PROVIDER.lower()
        if prov == "sendgrid" and settings.SENDGRID_API_KEY:
            return SendGridProvider()
        elif prov == "smtp" and self.is_configured():
            return SMTPProvider()
        return MockEmailProvider()

    def test_connection(self) -> ConnectionTestResult:
        start_time = time.time()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if not self.is_enabled():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.DISABLED,
                message="Email integration is disabled in system configuration (EMAIL_ENABLED=false).",
                timestamp=now_str
            )

        if not self.is_configured():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Email provider credentials not configured.",
                timestamp=now_str
            )

        try:
            provider = self.get_provider()
            details = self.circuit_breaker.call(provider.test_connection)
            latency = (time.time() - start_time) * 1000
            self.record_success()
            return ConnectionTestResult(
                success=True,
                status=IntegrationStatus.CONNECTED,
                message="Email service connection and authentication verified successfully.",
                latency_ms=round(latency, 2),
                timestamp=now_str,
                details=details
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            err_msg = str(e)
            self.record_failure(err_msg)
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.ERROR,
                message=f"Email connection test failed: {err_msg}",
                latency_ms=round(latency, 2),
                timestamp=now_str
            )

    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        # Email has no batch database synchronization
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return SyncResult(
            sync_id=f"SYNC_EMAIL_{int(time.time())}",
            integration="email",
            status="SUCCESS",
            records_read=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            started_at=now_str,
            completed_at=now_str,
            error_summary=None
        )
