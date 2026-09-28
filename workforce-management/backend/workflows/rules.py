"""
Workflow Rules Definition
-------------------------
Standardized business rules matching HR events against operational conditions and actions.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WorkflowRule(BaseModel):
    rule_id: str
    name: str
    description: str
    event_type: str
    is_active: bool = True
    actions: List[str]
    conditions: Dict[str, Any] = Field(default_factory=dict)

def evaluate_condition(conditions: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Evaluates condition expressions (e.g. {'late_minutes': {'$gte': 15}}) against event payload.
    """
    if not conditions:
        return True

    for field, expr in conditions.items():
        val = payload.get(field)
        if isinstance(expr, dict):
            for op, target in expr.items():
                if op == "$gte" and (val is None or val < target):
                    return False
                elif op == "$gt" and (val is None or val <= target):
                    return False
                elif op == "$lte" and (val is None or val > target):
                    return False
                elif op == "$lt" and (val is None or val >= target):
                    return False
                elif op == "$eq" and val != target:
                    return False
                elif op == "$ne" and val == target:
                    return False
                elif op == "$in" and val not in target:
                    return False
        else:
            if val != expr:
                return False

    return True

DEFAULT_WORKFLOW_RULES: List[WorkflowRule] = [
    # 1. Attendance Rules
    WorkflowRule(
        rule_id="RULE_LATE_ARRIVAL",
        name="Late Arrival Alerts",
        description="Notifies employee on any late arrival, and escalates to manager if late by 15+ minutes.",
        event_type="LATE_ARRIVAL",
        actions=["notify_employee", "notify_manager"],
        conditions={"late_minutes": {"$gte": 1}}
    ),
    WorkflowRule(
        rule_id="RULE_MISSING_CHECKOUT",
        name="Missing Check-Out Reminder",
        description="Reminds employees who have not clocked out after shift completion.",
        event_type="MISSING_CHECK_OUT",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_ATTENDANCE_ANOMALY",
        name="Attendance Anomaly Notification",
        description="Alerts employee and manager when an attendance anomaly or geofence violation occurs.",
        event_type="ATTENDANCE_ANOMALY",
        actions=["notify_employee", "notify_manager"],
        conditions={}
    ),
    # 2. Leave Rules
    WorkflowRule(
        rule_id="RULE_LEAVE_REQUEST_CREATED",
        name="Leave Request Manager Escalation",
        description="Alerts direct manager when an employee submits a new leave request.",
        event_type="LEAVE_REQUEST_CREATED",
        actions=["notify_manager"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_LEAVE_STATUS_CHANGED",
        name="Leave Status Notification",
        description="Notifies employee when leave is approved, rejected, or updated.",
        event_type="LEAVE_APPROVED",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_LEAVE_REJECTED",
        name="Leave Rejection Notification",
        description="Notifies employee when leave is rejected with the operational reason.",
        event_type="LEAVE_REJECTED",
        actions=["notify_employee"],
        conditions={}
    ),
    # 3. Shift Rules
    WorkflowRule(
        rule_id="RULE_SHIFT_ASSIGNMENT",
        name="Shift Schedule Notification",
        description="Notifies employee of a new or updated shift schedule.",
        event_type="SHIFT_ASSIGNED",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_SHIFT_REMINDER",
        name="Upcoming Shift Reminder",
        description="Sends shift reminder 60 minutes prior to scheduled shift start.",
        event_type="SHIFT_REMINDER",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_SHIFT_SWAP_REQUEST",
        name="Shift Swap Collaboration Alert",
        description="Alerts target employee and manager when a shift swap is proposed.",
        event_type="SHIFT_SWAP_REQUESTED",
        actions=["notify_employee", "notify_manager"],
        conditions={}
    ),
    # 4. Overtime Rule
    WorkflowRule(
        rule_id="RULE_OVERTIME_ALERT",
        name="Overtime Threshold Escalation",
        description="Alerts employee and manager when daily overtime meets or exceeds threshold hours.",
        event_type="OVERTIME_DETECTED",
        actions=["notify_employee", "notify_manager"],
        conditions={"overtime_hours": {"$gte": 2.0}}
    ),
    # 5. Timesheet Rules
    WorkflowRule(
        rule_id="RULE_TIMESHEET_SUBMITTED",
        name="Timesheet Review Notice",
        description="Alerts manager when an employee submits timesheet hours for review.",
        event_type="TIMESHEET_SUBMITTED",
        actions=["notify_manager"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_TIMESHEET_APPROVED",
        name="Timesheet Approval Notice",
        description="Notifies employee when project timesheet hours are approved.",
        event_type="TIMESHEET_APPROVED",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_TIMESHEET_REMINDER",
        name="Incomplete Timesheet Reminder",
        description="Reminds employees with unlogged timesheets prior to period close.",
        event_type="TIMESHEET_REMINDER",
        actions=["notify_employee"],
        conditions={}
    ),
    # 6. Payroll Rules
    WorkflowRule(
        rule_id="RULE_PAYSLIP_AVAILABLE",
        name="Monthly Payslip Notification",
        description="Alerts employee immediately upon payslip disbursement.",
        event_type="PAYSLIP_AVAILABLE",
        actions=["notify_employee"],
        conditions={}
    ),
    # 7. Performance & Training Rules
    WorkflowRule(
        rule_id="RULE_PERFORMANCE_REVIEW",
        name="Performance Appraisal Deadline",
        description="Notifies employee when self-assessment or goal deadline is approaching.",
        event_type="PERFORMANCE_REVIEW_DUE",
        actions=["notify_employee"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_TRAINING_DEADLINE",
        name="Training Module Deadline Alert",
        description="Alerts employee when assigned training program deadline is nearing.",
        event_type="TRAINING_DEADLINE",
        actions=["notify_employee"],
        conditions={}
    ),
    # 8. Celebrations
    WorkflowRule(
        rule_id="RULE_BIRTHDAY",
        name="Birthday Greeting",
        description="Sends birthday greeting to employee and informs manager.",
        event_type="BIRTHDAY_REMINDER",
        actions=["notify_employee", "notify_manager"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_WORK_ANNIVERSARY",
        name="Work Anniversary Milestone",
        description="Celebrates milestone work anniversary with employee and management.",
        event_type="WORK_ANNIVERSARY",
        actions=["notify_employee", "notify_manager"],
        conditions={}
    ),
    # 9. AI Workforce Alerts
    WorkflowRule(
        rule_id="RULE_AI_ABSENTEEISM",
        name="AI High Absenteeism Risk Escalation",
        description="Escalates high absenteeism probability indicators to HR and manager.",
        event_type="AI_ABSENTEEISM_ALERT",
        actions=["notify_hr", "notify_manager"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_AI_ATTRITION",
        name="AI Attrition Vulnerability Alert",
        description="Notifies HR leaders of critical retention vulnerability signals.",
        event_type="AI_ATTRITION_ALERT",
        actions=["notify_hr"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_AI_WORKFORCE_FORECAST",
        name="AI Capacity Shortage Advisory",
        description="Alerts HR leadership when department staffing forecast reveals significant deficit.",
        event_type="AI_WORKFORCE_FORECAST_ALERT",
        actions=["notify_hr"],
        conditions={}
    ),
    WorkflowRule(
        rule_id="RULE_AI_ATTENDANCE_ANOMALY",
        name="AI Attendance Anomaly Alert",
        description="Alerts HR and manager when unsupervised Isolation Forest detects outlier pattern.",
        event_type="AI_ATTENDANCE_ANOMALY",
        actions=["notify_hr", "notify_manager"],
        conditions={}
    ),
    # 10. Compliance Rule
    WorkflowRule(
        rule_id="RULE_COMPLIANCE",
        name="Mandatory Statutory Compliance Notice",
        description="Dispatches mandatory compliance alerts that cannot be disabled.",
        event_type="COMPLIANCE_ALERT",
        actions=["notify_hr", "notify_employee"],
        conditions={}
    )
]
