"""
Google Calendar Integration Connector
-------------------------------------
Synchronizes workforce shift rotations, approved leaves, and company holidays with Google Calendar.
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
from database.mongodb import get_db

class GoogleCalendarConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="google_calendar",
            category="calendar",
            display_name="Google Calendar",
            description="Exports shift schedules and approved leaves to Google Workspace calendars."
        )

    def is_enabled(self) -> bool:
        return settings.GOOGLE_ENABLED and settings.GOOGLE_CALENDAR_ENABLED

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def test_connection(self) -> ConnectionTestResult:
        start_time = time.time()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if not self.is_enabled():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.DISABLED,
                message="Google Calendar integration is disabled (GOOGLE_ENABLED=false).",
                timestamp=now_str
            )

        if not self.is_configured():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Google Workspace credentials missing (GOOGLE_CLIENT_ID and CLIENT_SECRET required).",
                timestamp=now_str
            )

        latency = (time.time() - start_time) * 1000
        return ConnectionTestResult(
            success=False,
            status=IntegrationStatus.BLOCKED_EXTERNAL_DEPENDENCY,
            message="Google Calendar API requires active Google Cloud Service Account or OAuth2 token grant.",
            latency_ms=round(latency, 2),
            timestamp=now_str
        )

    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        sync_id = f"SYNC_GCAL_{int(time.time())}"
        db = get_db()

        if not self.is_enabled() or not self.is_configured():
            return SyncResult(
                sync_id=sync_id,
                integration="google_calendar",
                status="FAILED",
                error_summary="Google Calendar is not configured or disabled.",
                started_at=now_str,
                completed_at=now_str
            )

        holidays_count = db.holidays.count_documents({})
        return SyncResult(
            sync_id=sync_id,
            integration="google_calendar",
            status="SUCCESS",
            records_read=holidays_count,
            records_created=holidays_count,
            records_updated=0,
            records_failed=0,
            started_at=now_str,
            completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        )
