"""
Notification & Email Templates
------------------------------
Standardized message formatters, action URLs, priority assignments,
and AI explainability disclaimers.
"""

from typing import Dict, Any, Tuple

AI_GOVERNANCE_DISCLAIMER = (
    "AI-Generated Advisory: This is a probabilistic decision-support indicator "
    "governed by ethical AI principles. No autonomous or punitive employment action is permitted."
)

def render_notification(event_type: str, payload: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
    """
    Renders (title, message, priority, category, action_url) based on event type and payload.
    Priority options: 'low', 'normal', 'high', 'critical'
    """
    emp_name = payload.get("employee_name", "Employee")
    emp_id = payload.get("employee_id", "")

    # 1. Attendance Events
    if event_type == "LATE_ARRIVAL":
        late_mins = payload.get("late_minutes", 0)
        shift_name = payload.get("shift_name", "Scheduled Shift")
        return (
            "Late Clock-In Recorded",
            f"{emp_name} ({emp_id}) clocked in {late_mins} minutes late for {shift_name}.",
            "high" if late_mins >= 30 else "normal",
            "attendance",
            "/attendance"
        )

    elif event_type == "MISSING_CHECK_OUT":
        date_val = payload.get("date", "today")
        return (
            "Missing Check-Out Alert",
            f"No check-out was registered for {emp_name} on {date_val}. Please regularize your attendance.",
            "high",
            "attendance",
            "/attendance"
        )

    elif event_type == "ATTENDANCE_ANOMALY":
        reason = payload.get("reason", "Irregular attendance pattern")
        return (
            "Attendance Anomaly Detected",
            f"An anomaly was flagged for {emp_name}: {reason}.",
            "high",
            "attendance",
            "/attendance"
        )

    elif event_type == "ATTENDANCE_CHECK_IN":
        return (
            "Clock-In Confirmation",
            f"Clock-in confirmed at {payload.get('time', 'now')} via {payload.get('method', 'Web')}.",
            "low",
            "attendance",
            "/attendance"
        )

    elif event_type == "ATTENDANCE_CHECK_OUT":
        return (
            "Clock-Out Confirmation",
            f"Clock-out confirmed. Total daily duration: {payload.get('hours_worked', 8.0)} hrs.",
            "low",
            "attendance",
            "/attendance"
        )

    # 2. Leave Events
    elif event_type == "LEAVE_REQUEST_CREATED":
        leave_type = payload.get("leave_type", "Leave")
        days = payload.get("days_count", 1)
        start = payload.get("start_date", "")
        return (
            "New Leave Application Submitted",
            f"{emp_name} ({emp_id}) requested {days} day(s) of {leave_type} starting {start}.",
            "normal",
            "leave",
            "/leave"
        )

    elif event_type == "LEAVE_APPROVED":
        leave_type = payload.get("leave_type", "Leave")
        start = payload.get("start_date", "")
        return (
            "Leave Application Approved",
            f"Your {leave_type} application starting {start} has been approved by management.",
            "normal",
            "leave",
            "/leave"
        )

    elif event_type == "LEAVE_REJECTED":
        leave_type = payload.get("leave_type", "Leave")
        reason = payload.get("reason", "Operational exigency")
        return (
            "Leave Application Update",
            f"Your {leave_type} application was not approved. Reason: {reason}",
            "high",
            "leave",
            "/leave"
        )

    elif event_type == "LEAVE_CANCELLED":
        return (
            "Leave Application Cancelled",
            f"Leave application for {emp_name} has been cancelled.",
            "low",
            "leave",
            "/leave"
        )

    # 3. Shift Events
    elif event_type == "SHIFT_ASSIGNED":
        shift_name = payload.get("shift_name", "Shift")
        effective = payload.get("effective_date", "immediately")
        return (
            "New Shift Assignment",
            f"You have been assigned to {shift_name} effective {effective}.",
            "normal",
            "shifts",
            "/shifts"
        )

    elif event_type == "SHIFT_CHANGED":
        shift_name = payload.get("shift_name", "Shift")
        return (
            "Shift Schedule Updated",
            f"Your work shift has been adjusted to {shift_name}.",
            "normal",
            "shifts",
            "/shifts"
        )

    elif event_type == "SHIFT_REMINDER":
        shift_name = payload.get("shift_name", "Upcoming Shift")
        start_time = payload.get("start_time", "09:00 AM")
        return (
            "Upcoming Shift Reminder",
            f"Reminder: Your {shift_name} begins at {start_time}.",
            "normal",
            "shifts",
            "/shifts"
        )

    elif event_type == "SHIFT_SWAP_REQUESTED":
        requester = payload.get("requester_name", "A colleague")
        target_shift = payload.get("shift_name", "Shift")
        return (
            "Shift Swap Request Received",
            f"{requester} has requested to swap shifts with you for {target_shift}.",
            "normal",
            "shifts",
            "/shifts"
        )

    elif event_type == "SHIFT_SWAP_APPROVED":
        return (
            "Shift Swap Approved",
            "Your shift swap request has been approved and updated in the roster.",
            "normal",
            "shifts",
            "/shifts"
        )

    elif event_type == "SHIFT_SWAP_REJECTED":
        return (
            "Shift Swap Rejected",
            "Your shift swap request could not be accommodated at this time.",
            "low",
            "shifts",
            "/shifts"
        )

    # 4. Overtime Events
    elif event_type == "OVERTIME_DETECTED":
        ot_hours = payload.get("overtime_hours", 0.0)
        return (
            "Overtime Threshold Notification",
            f"Overtime recorded: {ot_hours} hours. Please ensure proper rest and compliance with labor norms.",
            "high" if ot_hours >= 3.0 else "normal",
            "attendance",
            "/attendance"
        )

    # 5. Timesheet Events
    elif event_type == "TIMESHEET_SUBMITTED":
        hours = payload.get("total_hours", 0)
        date_val = payload.get("date", "today")
        return (
            "Timesheet Submitted for Review",
            f"{emp_name} submitted a project timesheet for {date_val} ({hours} hours).",
            "normal",
            "timesheets",
            "/timesheets"
        )

    elif event_type == "TIMESHEET_APPROVED":
        date_val = payload.get("date", "recent")
        return (
            "Timesheet Approved",
            f"Your project timesheet for {date_val} has been approved.",
            "low",
            "timesheets",
            "/timesheets"
        )

    elif event_type == "TIMESHEET_REJECTED":
        reason = payload.get("reason", "Timesheet hours requires review")
        return (
            "Timesheet Revision Requested",
            f"Your timesheet submission requires revision: {reason}",
            "high",
            "timesheets",
            "/timesheets"
        )

    elif event_type == "TIMESHEET_REMINDER":
        return (
            "Pending Timesheet Reminder",
            "Please remember to log and submit your project timesheet for the current period.",
            "normal",
            "timesheets",
            "/timesheets"
        )

    # 6. Payroll Events
    elif event_type == "PAYSLIP_AVAILABLE":
        month = payload.get("month", "Recent Month")
        return (
            "Payslip Available",
            f"Your salary payslip for {month} is now generated and ready for viewing.",
            "normal",
            "payroll",
            "/payroll"
        )

    elif event_type == "PAYROLL_PROCESSED":
        month = payload.get("month", "Current Month")
        return (
            "Monthly Payroll Processed",
            f"Company payroll disbursement for {month} has been successfully executed.",
            "normal",
            "payroll",
            "/payroll"
        )

    # 7. Performance Events
    elif event_type == "PERFORMANCE_REVIEW_DUE":
        cycle = payload.get("cycle", "Annual")
        due_date = payload.get("due_date", "soon")
        return (
            "Performance Review Due",
            f"{cycle} appraisal self-assessment is due by {due_date}.",
            "normal",
            "performance",
            "/performance"
        )

    elif event_type == "GOAL_DEADLINE":
        goal_title = payload.get("goal_title", "Quarterly Objective")
        return (
            "Goal Target Deadline Approaching",
            f"Deadline approaching for performance goal: '{goal_title}'.",
            "normal",
            "performance",
            "/performance"
        )

    elif event_type == "PERFORMANCE_REVIEW_COMPLETED":
        score = payload.get("rating", "3.0")
        return (
            "Performance Appraisal Completed",
            f"Your performance appraisal evaluation has been finalized (Rating: {score}).",
            "normal",
            "performance",
            "/performance"
        )

    # 8. Training Events
    elif event_type == "TRAINING_ASSIGNED":
        course = payload.get("course_name", "Required Module")
        return (
            "New Training Program Assigned",
            f"You have been enrolled in '{course}'. Please review the syllabus and start your module.",
            "low",
            "training",
            "/skills-training"
        )

    elif event_type == "TRAINING_DEADLINE":
        course = payload.get("course_name", "Training Module")
        due_in = payload.get("days_left", 3)
        return (
            "Training Module Deadline Reminder",
            f"Reminder: Assigned training '{course}' is due in {due_in} day(s).",
            "normal",
            "training",
            "/skills-training"
        )

    elif event_type == "TRAINING_COMPLETED":
        course = payload.get("course_name", "Training Module")
        return (
            "Training Completed Successfully",
            f"Congratulations on completing '{course}'! Skill competencies updated.",
            "low",
            "training",
            "/skills-training"
        )

    # 9. Celebrations
    elif event_type == "BIRTHDAY_REMINDER":
        return (
            "Happy Birthday!",
            f"Wishing you a very Happy Birthday, {emp_name}! Have a wonderful day ahead!",
            "low",
            "celebration",
            "/dashboard"
        )

    elif event_type == "WORK_ANNIVERSARY":
        years = payload.get("years", 1)
        return (
            "Happy Work Anniversary!",
            f"Congratulations on {years} year(s) with InnovateCorp! Thank you for your continued dedication.",
            "low",
            "celebration",
            "/dashboard"
        )

    # 10. AI Alerts (Strictly Labeled with Disclaimers)
    elif event_type == "AI_ABSENTEEISM_ALERT":
        prob = payload.get("probability", 0.0)
        risk = payload.get("risk_level", "HIGH")
        factor = payload.get("top_factor", "Recent attendance pattern")
        return (
            "AI Workforce Alert: Elevated Absenteeism Risk",
            f"[AI Insight] Employee {emp_name} ({emp_id}) flagged with {risk} absenteeism risk ({prob*100:.1f}%). Primary indicator: {factor}. {AI_GOVERNANCE_DISCLAIMER}",
            "high",
            "ai_alerts",
            "/ai-intelligence"
        )

    elif event_type == "AI_ATTRITION_ALERT":
        prob = payload.get("probability", 0.0)
        risk = payload.get("risk_band", "HIGH")
        factor = payload.get("top_contributing_factor", "Compensation/tenure ratio")
        return (
            "AI Workforce Alert: Attrition Vulnerability",
            f"[AI Insight] Employee {emp_name} ({emp_id}) identified with {risk} retention vulnerability. Driver: {factor}. Proactive 1-on-1 check-in recommended. {AI_GOVERNANCE_DISCLAIMER}",
            "high",
            "ai_alerts",
            "/ai-intelligence"
        )

    elif event_type == "AI_WORKFORCE_FORECAST_ALERT":
        dept = payload.get("department_name", "Department")
        deficit = payload.get("projected_deficit", 0)
        return (
            "AI Workforce Alert: Staffing Capacity Deficit",
            f"[AI Insight] Q3-2026 Forecast indicates projected deficit of +{deficit} positions in {dept}. Review staffing pipeline. {AI_GOVERNANCE_DISCLAIMER}",
            "high",
            "ai_alerts",
            "/ai-intelligence"
        )

    elif event_type == "AI_SKILL_GAP_ALERT":
        dept = payload.get("department_name", "Department")
        skill = payload.get("skill_name", "Skill")
        return (
            "AI Workforce Alert: Department Skill Gap",
            f"[AI Insight] High-priority competency gap identified in {dept} for '{skill}'. Targeted upskilling recommended. {AI_GOVERNANCE_DISCLAIMER}",
            "normal",
            "ai_alerts",
            "/ai-intelligence"
        )

    elif event_type == "AI_ATTENDANCE_ANOMALY":
        score = payload.get("anomaly_score", -0.4)
        reason = payload.get("reason", "Multi-dimensional duration outlier")
        return (
            "AI Workforce Alert: Attendance Anomaly Detected",
            f"[AI Isolation Forest] Statistical deviation flagged for {emp_name} on {payload.get('date', 'today')}: {reason} (Score: {score:.3f}). {AI_GOVERNANCE_DISCLAIMER}",
            "high",
            "ai_alerts",
            "/ai-intelligence"
        )

    # 11. Compliance Alerts
    elif event_type == "COMPLIANCE_ALERT":
        rule = payload.get("rule_name", "Labor Law Compliance")
        desc = payload.get("description", "Mandatory policy compliance notification.")
        return (
            f"Compliance Notice: {rule}",
            f"{desc} This notice is mandatory and cannot be disabled.",
            "critical",
            "compliance",
            "/reports"
        )

    # Fallback
    return (
        "HR System Notification",
        payload.get("message", f"Event {event_type} occurred."),
        "normal",
        "system",
        "/notifications"
    )
