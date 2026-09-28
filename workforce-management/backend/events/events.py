"""
HR Event Definitions
--------------------
Standardized event types and structured event payload model.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, ConfigDict

class HREventType(str, Enum):
    # Attendance Events
    ATTENDANCE_CHECK_IN = "ATTENDANCE_CHECK_IN"
    ATTENDANCE_CHECK_OUT = "ATTENDANCE_CHECK_OUT"
    LATE_ARRIVAL = "LATE_ARRIVAL"
    MISSING_CHECK_OUT = "MISSING_CHECK_OUT"
    ATTENDANCE_ANOMALY = "ATTENDANCE_ANOMALY"

    # Leave Events
    LEAVE_REQUEST_CREATED = "LEAVE_REQUEST_CREATED"
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    LEAVE_CANCELLED = "LEAVE_CANCELLED"

    # Shift Events
    SHIFT_ASSIGNED = "SHIFT_ASSIGNED"
    SHIFT_CHANGED = "SHIFT_CHANGED"
    SHIFT_REMINDER = "SHIFT_REMINDER"
    SHIFT_SWAP_REQUESTED = "SHIFT_SWAP_REQUESTED"
    SHIFT_SWAP_APPROVED = "SHIFT_SWAP_APPROVED"
    SHIFT_SWAP_REJECTED = "SHIFT_SWAP_REJECTED"

    # Overtime Events
    OVERTIME_DETECTED = "OVERTIME_DETECTED"

    # Timesheet Events
    TIMESHEET_SUBMITTED = "TIMESHEET_SUBMITTED"
    TIMESHEET_APPROVED = "TIMESHEET_APPROVED"
    TIMESHEET_REJECTED = "TIMESHEET_REJECTED"
    TIMESHEET_REMINDER = "TIMESHEET_REMINDER"

    # Payroll Events
    PAYROLL_READY = "PAYROLL_READY"
    PAYROLL_PROCESSED = "PAYROLL_PROCESSED"
    PAYSLIP_AVAILABLE = "PAYSLIP_AVAILABLE"

    # Performance Events
    PERFORMANCE_REVIEW_DUE = "PERFORMANCE_REVIEW_DUE"
    GOAL_DEADLINE = "GOAL_DEADLINE"
    PERFORMANCE_REVIEW_COMPLETED = "PERFORMANCE_REVIEW_COMPLETED"

    # Training Events
    TRAINING_ASSIGNED = "TRAINING_ASSIGNED"
    TRAINING_DEADLINE = "TRAINING_DEADLINE"
    TRAINING_COMPLETED = "TRAINING_COMPLETED"

    # Celebrations & Reminders
    BIRTHDAY_REMINDER = "BIRTHDAY_REMINDER"
    WORK_ANNIVERSARY = "WORK_ANNIVERSARY"

    # AI-Powered Alerts
    AI_ATTENDANCE_ANOMALY = "AI_ATTENDANCE_ANOMALY"
    AI_ABSENTEEISM_ALERT = "AI_ABSENTEEISM_ALERT"
    AI_ATTRITION_ALERT = "AI_ATTRITION_ALERT"
    AI_WORKFORCE_FORECAST_ALERT = "AI_WORKFORCE_FORECAST_ALERT"
    AI_SKILL_GAP_ALERT = "AI_SKILL_GAP_ALERT"

    # Compliance Events
    COMPLIANCE_ALERT = "COMPLIANCE_ALERT"


class HREvent(BaseModel):
    """
    Standard event model representing any event occurring within the HR ecosystem.
    """
    event_id: str = Field(default_factory=lambda: f"EVT_{uuid.uuid4().hex[:8].upper()}")
    event_type: HREventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    actor_id: Optional[str] = "SYSTEM"
    entity_type: str
    entity_id: Optional[str] = None
    target_employee_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    dedup_key: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)
