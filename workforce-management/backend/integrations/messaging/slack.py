"""
Slack Integration Connector
---------------------------
Delivers notifications to Slack channels using Block Kit via Incoming Webhooks or Slack Bot API.
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

class SlackConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="slack",
            category="messaging",
            display_name="Slack Workspace",
            description="Broadcasts operational HR announcements, shift changes, and workflow approvals to Slack."
        )

    def is_enabled(self) -> bool:
        return settings.SLACK_ENABLED

    def is_configured(self) -> bool:
        has_webhook = bool(settings.SLACK_WEBHOOK_URL and settings.SLACK_WEBHOOK_URL.startswith("https://"))
        has_token = bool(settings.SLACK_BOT_TOKEN and settings.SLACK_BOT_TOKEN.startswith("xoxb-"))
        return has_webhook or has_token

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
            raise IntegrationNotConfiguredError("Slack credentials not configured.", provider="slack")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📢 {title}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Category:* {category.upper()}"},
                    {"type": "mrkdwn", "text": f"*Priority:* {priority.upper()}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            }
        ]

        if action_url:
            blocks.append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open HR Portal"},
                    "url": action_url,
                    "style": "primary"
                }]
            })

        payload: Dict[str, Any] = {"blocks": blocks, "text": f"{title}: {message}"}

        # Send via Webhook
        if settings.SLACK_WEBHOOK_URL:
            target_url = settings.SLACK_WEBHOOK_URL
            headers = {"Content-Type": "application/json"}
        else:
            target_url = "https://slack.com/api/chat.postMessage"
            payload["channel"] = settings.SLACK_DEFAULT_CHANNEL
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"
            }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(target_url, data=data, headers=headers, method="POST")

        def _do_send():
            with urllib.request.urlopen(req, timeout=settings.INTEGRATION_TIMEOUT_SECONDS) as resp:
                return resp.status in (200, 201, 202)

        try:
            res = self.circuit_breaker.call(_do_send)
            self.record_success()
            return res
        except urllib.error.URLError as e:
            self.record_failure(str(e))
            raise IntegrationConnectionError(f"Slack delivery failed: {e.reason}", provider="slack")
        except TimeoutError:
            self.record_failure("Slack request timed out.")
            raise IntegrationTimeoutError("Slack request timed out.", provider="slack")
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
                message="Slack integration is disabled (SLACK_ENABLED=false).",
                timestamp=now_str
            )

        if not self.is_configured():
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Slack webhook or bot token not configured.",
                timestamp=now_str
            )

        try:
            # If bot token is set, test auth directly via auth.test
            if settings.SLACK_BOT_TOKEN:
                req = urllib.request.Request(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=settings.INTEGRATION_TIMEOUT_SECONDS) as resp:
                    data = json.loads(resp.read().decode())
                    if not data.get("ok"):
                        raise IntegrationConnectionError(f"Slack auth error: {data.get('error')}", provider="slack")
            else:
                # Webhook ping test
                self.send_notification("Connectivity Verification", "Slack integration connection test verified.", "system", "low")

            latency = (time.time() - start_time) * 1000
            return ConnectionTestResult(
                success=True,
                status=IntegrationStatus.CONNECTED,
                message="Successfully verified Slack workspace connectivity.",
                latency_ms=round(latency, 2),
                timestamp=now_str
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.ERROR,
                message=f"Slack test failed: {e}",
                latency_ms=round(latency, 2),
                timestamp=now_str
            )

    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return SyncResult(
            sync_id=f"SYNC_SLACK_{int(time.time())}",
            integration="slack",
            status="SUCCESS",
            records_read=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            started_at=now_str,
            completed_at=now_str
        )
