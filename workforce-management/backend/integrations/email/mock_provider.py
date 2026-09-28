"""
Mock / Local Email Provider Implementation
------------------------------------------
Simulates email delivery safely in development and automated testing environments.
Persists delivered messages to MongoDB `email_delivery_logs` collection.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from database.mongodb import get_db
from backend.integrations.email.provider import BaseEmailProvider

class MockEmailProvider(BaseEmailProvider):
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        db = get_db()
        db.email_delivery_logs.insert_one({
            "log_id": f"EML_{uuid.uuid4().hex[:8].upper()}",
            "recipient_email": recipient_email,
            "from_email": from_email or "notifications@innovatecorp.demo",
            "subject": subject,
            "text_body": text_body,
            "status": "MOCK_DELIVERED",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })
        return True

    def test_connection(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "provider": "mock",
            "mode": "in_memory_simulation",
            "message": "Local test email provider operational."
        }
