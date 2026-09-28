"""
Notification & Workflow Pydantic Schemas
----------------------------------------
Data transfer objects for notification querying, preferences, unread counts, and workflow inspection.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class NotificationCreate(BaseModel):
    employee_id: str
    category: str
    title: str
    message: str
    priority: Optional[str] = "normal"
    type: Optional[str] = "INFO"
    action_url: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

class NotificationResponse(BaseModel):
    notification_id: str
    employee_id: str
    recipient_employee_id: Optional[str] = None
    recipient_user_id: Optional[str] = None
    category: str
    title: str
    message: str
    priority: Optional[str] = "normal"
    type: Optional[str] = "INFO"
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action_url: Optional[str] = None
    is_read: int = 0
    created_at: str
    read_at: Optional[str] = None
    channels: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="ignore")

class NotificationUnreadCountResponse(BaseModel):
    unread_count: int

class NotificationPreferencesResponse(BaseModel):
    employee_id: str
    attendance_alerts: bool = True
    leave_notifications: bool = True
    shift_notifications: bool = True
    timesheet_notifications: bool = True
    payroll_notifications: bool = True
    performance_notifications: bool = True
    training_notifications: bool = True
    birthday_notifications: bool = True
    anniversary_notifications: bool = True
    ai_alerts: bool = True
    compliance_notifications: bool = True
    email_enabled: bool = True
    in_app_enabled: bool = True

class NotificationPreferencesUpdate(BaseModel):
    attendance_alerts: Optional[bool] = None
    leave_notifications: Optional[bool] = None
    shift_notifications: Optional[bool] = None
    timesheet_notifications: Optional[bool] = None
    payroll_notifications: Optional[bool] = None
    performance_notifications: Optional[bool] = None
    training_notifications: Optional[bool] = None
    birthday_notifications: Optional[bool] = None
    anniversary_notifications: Optional[bool] = None
    ai_alerts: Optional[bool] = None
    compliance_notifications: Optional[bool] = None
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None

class WorkflowStatusResponse(BaseModel):
    is_running: bool
    interval_seconds: int
    last_run_timestamp: Optional[str] = None
    stats: Dict[str, Any] = Field(default_factory=dict)
