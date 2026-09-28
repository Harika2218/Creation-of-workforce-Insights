"""
Notifications Package
---------------------
Notification delivery service, delivery channels, templates, and preference management.
"""

from backend.notifications.service import NotificationService
from backend.notifications.channels import ws_manager, InAppChannel, EmailChannel
from backend.notifications.preferences import NotificationPreferencesService
from backend.notifications.templates import render_notification

__all__ = [
    "NotificationService",
    "ws_manager",
    "InAppChannel",
    "EmailChannel",
    "NotificationPreferencesService",
    "render_notification"
]
