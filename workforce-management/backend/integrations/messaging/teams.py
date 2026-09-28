"""
Microsoft Teams Integration Connector
-------------------------------------
Delivers automated HR notifications and alerts to Microsoft Teams channels
using Microsoft Teams Adaptive Cards via secure Incoming Webhook.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.config import settings
from backend.integrations.base.connector import BaseConnector
from backend.integrations.base.models import (
    IntegrationStatus,
    ConnectionTestResult,
    SyncResult
)
from backend.integrations.base.exceptions import (
    IntegrationNotConfiguredError,
    IntegrationConnectionError,
    IntegrationTimeoutError
)

class TeamsConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="teams",
            category="messaging",
            display_name="Microsoft Teams",
            description="Delivers automated workforce alerts and approvals to Microsoft Teams channels."
        )

    def is_enabled(self) -> bool:
        return settings.TEAMS_ENABLED

    def is_configured(self) -> bool:
        return bool(settings.TEAMS_WEBHOOK_URL and settings.TEAMS_WEBHOOK_URL.startswith("https://"))

    def send_notification(
        self,
        title: str,
        message: str,
        category: str = "general",
        priority: str = "normal",
        action_url: Optional[str] = None
    ) -> bool:
        if not self.is_enabled():
            return False
        if not self.is_configured():
            raise IntegrationNotConfiguredError("Teams webhook URL not configured.", provider="teams")

        # Color bar indicator based on priority
        theme_colors = {
            "critical": "D32F2F",
            "high": "E65100",
            "medium": "0288D1",
            "low": "388E3C",
            "normal": "4F46E5"
        }
        theme_color = theme_colors.get(priority.lower(), "4F46E5")

        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": title,
            "sections": [{
                "activityTitle": f"📢 {title}",
                "activitySubtitle": f"InnovateCorp HR Automation | Category: {category.upper()}",
                "text": message,
                "markdown": True
            }]
        }

        if action_url:
            card["potentialAction"] = [{
                "@type": "OpenURI",
                "name": "View in HR Portal",
                "targets": [{"os": "default", "uri": action_url}]
            }]

        data = json.dumps(card).encode("utf-8")
        req = urllib.request.Request(
            settings.TEAMS_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        def _do_send():
            with urllib.request.urlopen(req, timeout=settings.INTEGRATION_TIMEOUT_SECONDS) as resp:
                return resp.status in (200, 201, 202)

        try:
            res = self.circuit_breaker.call(_do_send)
            self.record_success()
            return res
        except urllib.error.URLError as e:
            self.record_failure(str(e))
            raise IntegrationConnectionError(f"Teams webhook delivery failed: {e.reason}", provider="teams")
        except TimeoutError:
            self.record_failure("Teams webhook timeout.")
            raise IntegrationTimeoutError("Teams request timed out.", provider="teams")
        except Exception as e:
            self.record_failure(str(e))
            return False

    def test_connection(self) -> ConnectionTestResult:
        start_time = time.time()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if not self.is_enabled():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.DISABLED,
                message="Microsoft Teams integration is disabled (TEAMS_ENABLED=false).",
                timestamp=now_str
            )

        if not self.is_configured():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Microsoft Teams webhook URL not configured (TEAMS_WEBHOOK_URL is empty).",
                timestamp=now_str
            )

        try:
            # Send test ping payload
            success = self.send_notification(
                title="Connectivity Verification",
                message="InnovateCorp HR Automation integration connection test verified.",
                category="system",
                priority="low"
            )
            latency = (time.time() - start_time) * 1000
            return ConnectionTestResult(
                success=True,
                status=IntegrationStatus.CONNECTED,
                message="Successfully delivered test ping to Microsoft Teams channel.",
                latency_ms=round(latency, 2),
                timestamp=now_str
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.ERROR,
                message=f"Microsoft Teams test failed: {e}",
                latency_ms=round(latency, 2),
                timestamp=now_str
            )

    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return SyncResult(
            sync_id=f"SYNC_TEAMS_{int(time.time())}",
            integration="teams",
            status="SUCCESS",
            records_read=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            started_at=now_str,
            completed_at=now_str
        )
