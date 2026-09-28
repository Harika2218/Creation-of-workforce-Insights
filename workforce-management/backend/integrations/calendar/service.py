"""
Calendar Synchronization Service
--------------------------------
Coordinates calendar event export across Outlook and Google Calendar.
"""

from typing import Dict, Any, Optional
from database.mongodb import get_db

class CalendarSyncService:
    def sync_leave_event(self, leave_request: Dict[str, Any]) -> Dict[str, Any]:
        """Maps an approved leave request to external calendar formats with deduplication key."""
        return {
            "title": f"Leave: {leave_request.get('leave_type')} ({leave_request.get('employee_id')})",
            "start_date": leave_request.get("start_date"),
            "end_date": leave_request.get("end_date"),
            "external_event_id": f"CAL_LV_{leave_request.get('leave_id')}",
            "status": "CONFIRMED"
        }

    def sync_shift_event(self, shift_assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Maps an assigned shift to external calendar formats."""
        return {
            "title": f"Shift: {shift_assignment.get('shift_id')}",
            "employee_id": shift_assignment.get("employee_id"),
            "external_event_id": f"CAL_SH_{shift_assignment.get('schedule_id')}",
            "status": "CONFIRMED"
        }
