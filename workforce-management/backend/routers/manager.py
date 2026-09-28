"""
Manager Portal Router
---------------------
Provides scoped endpoints for managers to oversee direct reports' attendance, leaves, and shifts.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.performance import TeamMemberResponse, TeamSummaryResponse
from backend.schemas.attendance import AttendanceResponse
from backend.schemas.leave import LeaveResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/manager", tags=["Manager"])

def get_manager_team_ids(current_user: dict, db) -> List[str]:
    """Helper to get list of employee IDs reporting to current manager."""
    mgr_id = current_user.get("employee_id")
    # HR / Admin can specify or see default demo manager
    if current_user.get("role") in ["ADMIN", "HR"]:
        team = db.employees.distinct("employee_id", {"manager_id": mgr_id})
        if not team:
            # Fallback to team for EMP002 (VP/Lead)
            team = db.employees.distinct("employee_id", {"manager_id": "EMP002"})
        return team
    return db.employees.distinct("employee_id", {"manager_id": mgr_id})

@router.get("/team", response_model=List[TeamMemberResponse], summary="Get direct reports for current manager")
async def get_my_team(current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    team_ids = get_manager_team_ids(current_user, db)
    return list(db.employees.find({"employee_id": {"$in": team_ids}}, {"_id": 0}))

@router.get("/team/summary", response_model=TeamSummaryResponse, summary="Get high-level summary of manager's team")
async def get_team_summary(current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    mgr_id = current_user.get("employee_id") or "EMP002"
    team_ids = get_manager_team_ids(current_user, db)
    team_size = len(team_ids)

    # Attendance today
    today_str = date.today().strftime("%Y-%m-%d")
    present_count = db.attendance.count_documents({
        "employee_id": {"$in": team_ids},
        "date": today_str,
        "attendance_status": {"$in": ["Present", "Late", "Work From Home"]}
    })
    leave_count = db.attendance.count_documents({
        "employee_id": {"$in": team_ids},
        "date": today_str,
        "attendance_status": "Leave"
    })

    # Pending approvals
    pending_leaves = db.leave_requests.count_documents({
        "employee_id": {"$in": team_ids},
        "status": "Pending"
    })
    pending_timesheets = db.timesheets.count_documents({
        "employee_id": {"$in": team_ids},
        "status": "Submitted"
    })

    return {
        "manager_id": mgr_id,
        "team_size": team_size,
        "present_today": present_count,
        "on_leave_today": leave_count,
        "pending_leave_approvals": pending_leaves,
        "pending_timesheet_approvals": pending_timesheets
    }

@router.get("/team/attendance", response_model=List[AttendanceResponse], summary="Get team attendance records")
async def get_team_attendance(
    date_val: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    team_ids = get_manager_team_ids(current_user, db)
    query = {"employee_id": {"$in": team_ids}}
    if date_val:
        query["date"] = date_val
    else:
        # Default to latest active date
        query["date"] = "2026-03-20"
    return list(db.attendance.find(query, {"_id": 0}))

@router.get("/team/leave", response_model=List[LeaveResponse], summary="Get team leave applications")
async def get_team_leaves(
    status_val: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    team_ids = get_manager_team_ids(current_user, db)
    query = {"employee_id": {"$in": team_ids}}
    if status_val:
        query["status"] = status_val
    return list(db.leave_requests.find(query, {"_id": 0}).sort("created_at", -1))

@router.get("/team/shifts", summary="Get team shift assignments")
async def get_team_shifts(current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    team_ids = get_manager_team_ids(current_user, db)
    return list(db.employee_shifts.find({"employee_id": {"$in": team_ids}}, {"_id": 0}))
