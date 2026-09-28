"""
Timesheet Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class TimesheetCreate(BaseModel):
    employee_id: str
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    project_id: str
    hours_worked: float = Field(..., gt=0, le=24.0)
    billable_hours: float = Field(..., ge=0, le=24.0)
    non_billable_hours: float = Field(default=0.0, ge=0, le=24.0)
    overtime_hours: float = Field(default=0.0, ge=0, le=12.0)
    description: Optional[str] = "Daily project task execution"

class TimesheetUpdate(BaseModel):
    hours_worked: Optional[float] = Field(None, gt=0, le=24.0)
    billable_hours: Optional[float] = Field(None, ge=0, le=24.0)
    non_billable_hours: Optional[float] = Field(None, ge=0, le=24.0)
    overtime_hours: Optional[float] = Field(None, ge=0, le=12.0)
    description: Optional[str] = None

class TimesheetApprovalAction(BaseModel):
    status: str = Field(..., pattern="^(Approved|Rejected)$")
    rejection_reason: Optional[str] = None

class TimesheetResponse(BaseModel):
    timesheet_id: str
    employee_id: str
    date: str
    project_id: str
    hours_worked: float
    billable_hours: float
    non_billable_hours: float
    overtime_hours: float
    status: str
    description: Optional[str] = None
