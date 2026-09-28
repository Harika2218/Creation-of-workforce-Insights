"""
Notification Service Implementation
-----------------------------------
Core notification creation, deduplication, RBAC-filtered retrieval,
and delivery orchestration.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import uuid
from database.mongodb import get_db
from backend.notifications.templates import render_notification
from backend.notifications.channels import (
    InAppChannel,
    EmailChannel,
    TeamsNotificationChannel,
    SlackNotificationChannel
)
from backend.notifications.preferences import NotificationPreferencesService
from backend.config import settings

class NotificationService:
    def __init__(self):
        self.in_app_channel = InAppChannel()
        self.email_channel = EmailChannel()
        self.teams_channel = TeamsNotificationChannel()
        self.slack_channel = SlackNotificationChannel()
        self.preferences_service = NotificationPreferencesService()

    def create_notification(
        self,
        recipient_employee_id: str,
        event_type: str,
        title: Optional[str] = None,
        message: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        dedup_key: Optional[str] = None,
        channels: Optional[List[str]] = None,
        recipient_user_id: Optional[str] = None,
        expires_at: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Creates, deduplicates, and delivers an HR notification across configured channels.
        """
        db = get_db()
        payload = payload or {}

        # 1. Idempotency / Duplicate Prevention Check
        if dedup_key:
            existing = db.notifications.find_one({"dedup_key": dedup_key}, {"_id": 0})
            if existing:
                return existing

        # 2. Render from template if title/message missing
        t_title, t_msg, t_prio, t_cat, t_url = render_notification(event_type, payload)
        title = title or t_title
        message = message or t_msg
        priority = (priority or t_prio).lower()
        category = (category or t_cat).lower()
        action_url = action_url or t_url
        channels = channels or ["in_app"]

        # 3. Check User Preferences
        in_app_allowed = self.preferences_service.is_notification_allowed(
            recipient_employee_id, category, "in_app"
        )
        email_allowed = self.preferences_service.is_notification_allowed(
            recipient_employee_id, category, "email"
        )

        if not in_app_allowed and not email_allowed:
            # User opted out of this optional category across all channels
            return None

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        notification_id = f"NOT_{uuid.uuid4().hex[:8].upper()}"

        notif_doc = {
            "notification_id": notification_id,
            "employee_id": recipient_employee_id,
            "recipient_employee_id": recipient_employee_id,
            "recipient_user_id": recipient_user_id or recipient_employee_id,
            "type": event_type,
            "title": title,
            "message": message,
            "priority": priority,
            "category": category,
            "entity_type": entity_type or "system",
            "entity_id": entity_id,
            "action_url": action_url,
            "channels": channels,
            "is_read": 0,
            "created_at": now_str,
            "read_at": None,
            "expires_at": expires_at,
            "dedup_key": dedup_key,
            "metadata": payload
        }

        # 4. In-App Delivery
        if in_app_allowed and "in_app" in channels:
            self.in_app_channel.send(notif_doc)

        # 5. Email Delivery
        if email_allowed and "email" in channels:
            self.email_channel.send(notif_doc)

        # 6. Microsoft Teams Delivery
        if ("teams" in channels or getattr(settings, "TEAMS_ENABLED", False)) and self.teams_channel.connector.is_configured():
            self.teams_channel.send(notif_doc)

        # 7. Slack Delivery
        if ("slack" in channels or getattr(settings, "SLACK_ENABLED", False)) and self.slack_channel.connector.is_configured():
            self.slack_channel.send(notif_doc)

        # 6. Audit Log
        try:
            db.audit_logs.insert_one({
                "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
                "timestamp": now_str,
                "user_id": "SYSTEM_WORKFLOW",
                "action": f"NOTIFICATION_CREATED {event_type} -> {recipient_employee_id}",
                "status_code": 200,
                "notification_id": notification_id,
                "category": category,
                "priority": priority
            })
        except Exception:
            pass

        return notif_doc

    def get_user_notifications(
        self,
        employee_id: str,
        unread_only: bool = False,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieves paginated notifications for the specified employee with filtering.
        """
        db = get_db()
        query: Dict[str, Any] = {
            "$or": [
                {"employee_id": employee_id},
                {"recipient_employee_id": employee_id}
            ]
        }

        if unread_only:
            query["is_read"] = {"$in": [0, False]}

        if category and category.lower() != "all":
            query["category"] = category.lower()

        if priority and priority.lower() != "all":
            query["priority"] = priority.lower()

        if search:
            query["$and"] = [
                {
                    "$or": [
                        {"title": {"$regex": search, "$options": "i"}},
                        {"message": {"$regex": search, "$options": "i"}}
                    ]
                }
            ]

        total = db.notifications.count_documents(query)
        skip = (page - 1) * page_size
        items = list(
            db.notifications.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        # Normalize is_read to bool/int friendly
        for item in items:
            item["is_read"] = 1 if item.get("is_read") in [1, True, "1"] else 0

        return items, total

    def get_unread_count(self, employee_id: str) -> int:
        db = get_db()
        return db.notifications.count_documents({
            "$or": [
                {"employee_id": employee_id},
                {"recipient_employee_id": employee_id}
            ],
            "is_read": {"$in": [0, False]}
        })

    def mark_as_read(self, notification_id: str, employee_id: str) -> bool:
        db = get_db()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        res = db.notifications.update_one(
            {
                "notification_id": notification_id,
                "$or": [
                    {"employee_id": employee_id},
                    {"recipient_employee_id": employee_id}
                ]
            },
            {"$set": {"is_read": 1, "read_at": now_str}}
        )
        return res.matched_count > 0

    def mark_all_as_read(self, employee_id: str) -> int:
        db = get_db()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        res = db.notifications.update_many(
            {
                "$or": [
                    {"employee_id": employee_id},
                    {"recipient_employee_id": employee_id}
                ],
                "is_read": {"$in": [0, False]}
            },
            {"$set": {"is_read": 1, "read_at": now_str}}
        )
        return res.modified_count

    def get_notification_by_id(self, notification_id: str, employee_id: str, user_role: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        query: Dict[str, Any] = {"notification_id": notification_id}
        if user_role not in ["ADMIN", "HR"]:
            query["$or"] = [
                {"employee_id": employee_id},
                {"recipient_employee_id": employee_id}
            ]
        notif = db.notifications.find_one(query, {"_id": 0})
        if notif:
            notif["is_read"] = 1 if notif.get("is_read") in [1, True, "1"] else 0
        return notif
