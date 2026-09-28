"""
Notification Delivery Channels
------------------------------
Abstraction layer for In-App, Email, and Real-Time WebSocket delivery.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from starlette.websockets import WebSocket
from database.mongodb import get_db
from backend.config import settings

class WebSocketManager:
    """
    Tracks and pushes messages to active client WebSockets keyed by employee_id and user_id.
    """
    def __init__(self):
        # Map employee_id / user_id -> set of active WebSockets
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, key: str, websocket: WebSocket):
        await websocket.accept()
        if key not in self._connections:
            self._connections[key] = set()
        self._connections[key].add(websocket)

    def disconnect(self, key: str, websocket: WebSocket):
        if key in self._connections:
            self._connections[key].discard(websocket)
            if not self._connections[key]:
                del self._connections[key]

    async def send_personal_message(self, key: str, message: Dict[str, Any]):
        sockets = list(self._connections.get(key, []))
        dead_sockets = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
        for dead in dead_sockets:
            self.disconnect(key, dead)

    def get_active_count(self) -> int:
        return sum(len(s) for s in self._connections.values())


# Global singleton instance
ws_manager = WebSocketManager()


class BaseNotificationChannel(ABC):
    """Abstract interface for all notification delivery channels."""
    @abstractmethod
    def send(self, notification: Dict[str, Any]) -> bool:
        pass


class InAppChannel(BaseNotificationChannel):
    """
    Delivers notifications directly into MongoDB notifications collection
    and emits real-time event to connected WebSockets.
    """
    def send(self, notification: Dict[str, Any]) -> bool:
        db = get_db()
        recipient_emp_id = notification.get("recipient_employee_id") or notification.get("employee_id")
        recipient_user_id = notification.get("recipient_user_id")

        # Guarantee both fields exist for 100% backward compatibility
        doc = dict(notification)
        if "employee_id" not in doc and recipient_emp_id:
            doc["employee_id"] = recipient_emp_id
        if "recipient_employee_id" not in doc and "employee_id" in doc:
            doc["recipient_employee_id"] = doc["employee_id"]

        try:
            # Upsert using dedup_key if provided, otherwise insert
            dedup = doc.get("dedup_key")
            if dedup:
                existing = db.notifications.find_one({"dedup_key": dedup})
                if existing:
                    # Idempotent skip: Already delivered
                    return True
                db.notifications.insert_one(doc)
            else:
                db.notifications.insert_one(doc)

            doc.pop("_id", None)

            # Push to real-time WebSocket if user is connected
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    if recipient_emp_id:
                        asyncio.create_task(ws_manager.send_personal_message(recipient_emp_id, doc))
                    if recipient_user_id and recipient_user_id != recipient_emp_id:
                        asyncio.create_task(ws_manager.send_personal_message(recipient_user_id, doc))
            except Exception:
                pass

            return True
        except Exception as e:
            print(f"[ERROR] InAppChannel delivery failed: {e}")
            return False


class EmailChannel(BaseNotificationChannel):
    """
    Configurable SMTP Email delivery abstraction.
    Does not crash or interrupt workflows if SMTP credentials are unconfigured or fail.
    """
    def __init__(self):
        self.enabled = getattr(settings, "EMAIL_ENABLED", False)
        self.smtp_host = getattr(settings, "SMTP_HOST", "localhost")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.username = getattr(settings, "SMTP_USERNAME", "")
        self.password = getattr(settings, "SMTP_PASSWORD", "")
        self.from_email = getattr(settings, "EMAIL_FROM", "notifications@innovatecorp.demo")

    def send(self, notification: Dict[str, Any]) -> bool:
        recipient_email = notification.get("recipient_email")
        if not recipient_email:
            # Attempt to resolve from employees collection
            db = get_db()
            emp_id = notification.get("recipient_employee_id") or notification.get("employee_id")
            if emp_id:
                emp = db.employees.find_one({"employee_id": emp_id})
                if emp:
                    recipient_email = emp.get("email")

        if not recipient_email:
            # No valid email target
            return False

        # If email not explicitly enabled or dummy host, log mock delivery and succeed
        if not self.enabled or not self.username or self.smtp_host in ["localhost", "127.0.0.1", ""]:
            # Mock delivery simulation: logged safely
            db = get_db()
            db.email_delivery_logs.insert_one({
                "notification_id": notification.get("notification_id"),
                "recipient_email": recipient_email,
                "title": notification.get("title"),
                "status": "MOCK_DELIVERED",
                "timestamp": notification.get("created_at")
            })
            return True

        # Real SMTP Delivery attempt
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = notification.get("title", "HR Notification")
            msg["From"] = self.from_email
            msg["To"] = recipient_email

            text_content = f"{notification.get('title')}\n\n{notification.get('message')}\n\nInnovateCorp HR Automation"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #4F46E5;">{notification.get('title')}</h2>
                <p style="font-size: 15px; color: #333333; line-height: 1.6;">{notification.get('message')}</p>
                <div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid #eeeeee; font-size: 12px; color: #888888;">
                    This is an automated operational notification sent by InnovateCorp HRvantage.
                </div>
            </div>
            """

            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=5) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, recipient_email, msg.as_string())

            return True
        except Exception as e:
            # Do NOT raise. Catch and record delivery failure.
            print(f"[WARN] EmailChannel delivery failed for {recipient_email}: {e}")
            try:
                db = get_db()
                db.email_delivery_logs.insert_one({
                    "notification_id": notification.get("notification_id"),
                    "recipient_email": recipient_email,
                    "title": notification.get("title"),
                    "status": "FAILED",
                    "error": str(e)
                })
            except Exception:
                pass
            return False


class TeamsNotificationChannel(BaseNotificationChannel):
    """Delivers notification directly to Microsoft Teams if enabled."""
    def __init__(self):
        from backend.integrations.messaging.teams import TeamsConnector
        self.connector = TeamsConnector()

    def send(self, notification: Dict[str, Any]) -> bool:
        if not self.connector.is_enabled() or not self.connector.is_configured():
            return False
        try:
            return self.connector.send_notification(
                title=notification.get("title", "HR Notification"),
                message=notification.get("message", ""),
                category=notification.get("category", "general"),
                priority=notification.get("priority", "normal"),
                action_url=notification.get("action_url")
            )
        except Exception:
            return False


class SlackNotificationChannel(BaseNotificationChannel):
    """Delivers notification directly to Slack if enabled."""
    def __init__(self):
        from backend.integrations.messaging.slack import SlackConnector
        self.connector = SlackConnector()

    def send(self, notification: Dict[str, Any]) -> bool:
        if not self.connector.is_enabled() or not self.connector.is_configured():
            return False
        try:
            return self.connector.send_notification(
                title=notification.get("title", "HR Notification"),
                message=notification.get("message", ""),
                category=notification.get("category", "general"),
                priority=notification.get("priority", "normal"),
                action_url=notification.get("action_url")
            )
        except Exception:
            return False
