"""
Workflow Actions
----------------
Reusable action executors triggered when workflow rule conditions match.
"""

from typing import Dict, Any, Optional
from database.mongodb import get_db
from backend.notifications.service import NotificationService

_notification_service = NotificationService()

def action_notify_employee(
    event_type: str,
    target_employee_id: str,
    payload: Dict[str, Any],
    dedup_key: Optional[str] = None,
    priority: Optional[str] = None,
    action_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Notifies the employee directly involved in the event."""
    if not target_employee_id:
        return None
    return _notification_service.create_notification(
        recipient_employee_id=target_employee_id,
        event_type=event_type,
        payload=payload,
        dedup_key=dedup_key,
        priority=priority,
        action_url=action_url,
        channels=["in_app", "email"]
    )

def action_notify_manager(
    event_type: str,
    target_employee_id: str,
    payload: Dict[str, Any],
    dedup_key: Optional[str] = None,
    priority: Optional[str] = None,
    action_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Resolves the direct manager of the employee and sends an alert."""
    if not target_employee_id:
        return None
    db = get_db()
    emp = db.employees.find_one({"employee_id": target_employee_id})
    if not emp:
        return None
    manager_id = emp.get("manager_id")
    if not manager_id:
        # Fallback to HR if no manager assigned
        return action_notify_hr(event_type, payload, dedup_key=dedup_key, priority=priority, action_url=action_url)

    manager_payload = dict(payload)
    manager_payload["employee_name"] = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
    manager_payload["employee_id"] = target_employee_id

    return _notification_service.create_notification(
        recipient_employee_id=manager_id,
        event_type=event_type,
        payload=manager_payload,
        dedup_key=dedup_key,
        priority=priority,
        action_url=action_url,
        channels=["in_app", "email"]
    )

def action_notify_hr(
    event_type: str,
    payload: Dict[str, Any],
    dedup_key: Optional[str] = None,
    priority: Optional[str] = None,
    action_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Notifies HR administrators (e.g. EMP003 / Head of HR) regarding organization-wide alerts."""
    db = get_db()
    # Find HR representatives or default to EMP003
    hr_users = list(db.users.find({"role": "HR"}, {"employee_id": 1}))
    hr_ids = [u["employee_id"] for u in hr_users if u.get("employee_id")]
    if not hr_ids:
        hr_ids = ["EMP003"]

    results = []
    for hr_id in hr_ids[:3]: # Limit to primary HR representatives
        hr_dedup = f"HR_{hr_id}_{dedup_key}" if dedup_key else None
        res = _notification_service.create_notification(
            recipient_employee_id=hr_id,
            event_type=event_type,
            payload=payload,
            dedup_key=hr_dedup,
            priority=priority,
            action_url=action_url,
            channels=["in_app", "email"]
        )
        if res:
            results.append(res)
    return results[0] if results else None
