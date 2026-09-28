"""
Notification Preferences Service
--------------------------------
User preference management with safeguards preventing deactivation of mandatory compliance alerts.
"""

from typing import Dict, Any, Optional
from database.mongodb import get_db

DEFAULT_PREFERENCES: Dict[str, Any] = {
    "attendance_alerts": True,
    "leave_notifications": True,
    "shift_notifications": True,
    "timesheet_notifications": True,
    "payroll_notifications": True,
    "performance_notifications": True,
    "training_notifications": True,
    "birthday_notifications": True,
    "anniversary_notifications": True,
    "ai_alerts": True,
    "email_enabled": True,
    "in_app_enabled": True,
    "compliance_notifications": True # MANDATORY - cannot be turned off
}

# Category to preference key mapping
CATEGORY_PREFERENCE_MAP = {
    "attendance": "attendance_alerts",
    "leave": "leave_notifications",
    "shifts": "shift_notifications",
    "timesheets": "timesheet_notifications",
    "payroll": "payroll_notifications",
    "performance": "performance_notifications",
    "training": "training_notifications",
    "celebration": "birthday_notifications",
    "ai_alerts": "ai_alerts",
    "compliance": "compliance_notifications"
}

class NotificationPreferencesService:
    def __init__(self):
        pass

    def get_preferences(self, employee_id: str) -> Dict[str, Any]:
        """
        Retrieves user notification preferences, falling back to defaults.
        """
        db = get_db()
        doc = db.notification_preferences.find_one({"employee_id": employee_id}, {"_id": 0})
        prefs = dict(DEFAULT_PREFERENCES)
        if doc:
            # Map any legacy fields
            if "email_notifications" in doc:
                prefs["email_enabled"] = bool(doc["email_notifications"])
            if "shift_reminders" in doc:
                prefs["shift_notifications"] = bool(doc["shift_reminders"])
            if "leave_status_alerts" in doc:
                prefs["leave_notifications"] = bool(doc["leave_status_alerts"])
            if "payroll_alerts" in doc:
                prefs["payroll_notifications"] = bool(doc["payroll_alerts"])
            if "anniversary_alerts" in doc:
                prefs["anniversary_notifications"] = bool(doc["anniversary_alerts"])
            # Update with all explicitly saved modern fields
            for k in DEFAULT_PREFERENCES.keys():
                if k in doc:
                    prefs[k] = bool(doc[k])

        # Enforce compliance cannot be disabled
        prefs["compliance_notifications"] = True
        prefs["employee_id"] = employee_id
        return prefs

    def update_preferences(self, employee_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates preference toggles, explicitly disallowing disabling of mandatory compliance notices.
        """
        db = get_db()
        cleaned_updates = {}
        for k, v in updates.items():
            if k == "compliance_notifications" and not v:
                # Reject disabling mandatory compliance alerts
                cleaned_updates[k] = True
            elif k in DEFAULT_PREFERENCES:
                cleaned_updates[k] = bool(v)

        # Always enforce compliance
        cleaned_updates["compliance_notifications"] = True
        cleaned_updates["employee_id"] = employee_id

        # Also update legacy fields for backward compatibility
        cleaned_updates["email_notifications"] = cleaned_updates.get("email_enabled", True)
        cleaned_updates["shift_reminders"] = cleaned_updates.get("shift_notifications", True)
        cleaned_updates["leave_status_alerts"] = cleaned_updates.get("leave_notifications", True)
        cleaned_updates["payroll_alerts"] = cleaned_updates.get("payroll_notifications", True)
        cleaned_updates["anniversary_alerts"] = cleaned_updates.get("anniversary_notifications", True)

        db.notification_preferences.update_one(
            {"employee_id": employee_id},
            {"$set": cleaned_updates},
            upsert=True
        )

        return self.get_preferences(employee_id)

    def is_notification_allowed(self, employee_id: str, category: str, channel: str = "in_app") -> bool:
        """
        Checks whether an employee allows notifications for this category and channel.
        Mandatory compliance alerts ALWAYS return True.
        """
        if category == "compliance":
            return True

        prefs = self.get_preferences(employee_id)

        # Check channel toggle
        if channel == "in_app" and not prefs.get("in_app_enabled", True):
            return False
        if channel == "email" and not prefs.get("email_enabled", True):
            return False

        pref_key = CATEGORY_PREFERENCE_MAP.get(category)
        if pref_key and not prefs.get(pref_key, True):
            return False

        return True
