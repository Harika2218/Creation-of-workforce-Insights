"""
SendGrid Email Provider Implementation
--------------------------------------
Delivers transactional emails via SendGrid v3 REST Mail Send API.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from backend.config import settings
from backend.integrations.email.provider import BaseEmailProvider
from backend.integrations.base.exceptions import (
    IntegrationAuthenticationError,
    IntegrationConnectionError,
    IntegrationTimeoutError
)

class SendGridProvider(BaseEmailProvider):
    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None, timeout: int = 8):
        self.api_key = api_key or settings.SENDGRID_API_KEY
        self.from_email = from_email or settings.EMAIL_FROM
        self.timeout = timeout
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        if not self.api_key:
            raise IntegrationAuthenticationError("SendGrid API key not configured.", provider="sendgrid")

        content = [{"type": "text/plain", "value": text_body}]
        if html_body:
            content.append({"type": "text/html", "value": html_body})

        payload = {
            "personalizations": [{"to": [{"email": recipient_email}]}],
            "from": {"email": from_email or self.from_email},
            "subject": subject,
            "content": content
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status in (200, 202)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise IntegrationAuthenticationError(f"SendGrid API key unauthorized: {e.reason}", provider="sendgrid")
            raise IntegrationConnectionError(f"SendGrid API HTTP {e.code}: {e.reason}", provider="sendgrid")
        except urllib.error.URLError as e:
            raise IntegrationConnectionError(f"SendGrid network unreachable: {e.reason}", provider="sendgrid")
        except TimeoutError:
            raise IntegrationTimeoutError("SendGrid request timed out.", provider="sendgrid")

    def test_connection(self) -> Dict[str, Any]:
        """Tests SendGrid API key validity."""
        if not self.api_key:
            raise IntegrationAuthenticationError("SendGrid API key is missing.", provider="sendgrid")

        # Query user profile or scopes
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/scopes",
            headers={"Authorization": f"Bearer {self.api_key}"},
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
                return {"ok": True, "provider": "sendgrid", "scopes_count": len(data.get("scopes", []))}
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise IntegrationAuthenticationError("Invalid SendGrid API Key.", provider="sendgrid")
            raise IntegrationConnectionError(f"SendGrid verification failed: {e.reason}", provider="sendgrid")
        except Exception as e:
            raise IntegrationConnectionError(f"SendGrid connectivity error: {e}", provider="sendgrid")
