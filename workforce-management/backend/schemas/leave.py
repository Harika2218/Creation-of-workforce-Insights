"""
Leave Management Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type: str = Field(..., pattern="^(Annual Leave|Sick Leave|Casual Leave|Emergency Leave|Maternity/Paternity Leave)$")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    days_count: float = Field(..., gt=0)
    reason: str = Field(..., min_length=3)

class LeaveApprovalAction(BaseModel):
    status: str = Field(..., pattern="^(Approved|Rejected)$")
    rejection_reason: Optional[str] = None

class LeaveResponse(BaseModel):
    leave_id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_count: float
    reason: str
    status: str
    approved_by: Optional[str] = None
    created_at: Optional[str] = None

class LeaveBalanceResponse(BaseModel):
    balance_id: str
    employee_id: str
    leave_type: str
    allocated_days: float
    used_days: float
    remaining_days: float
    year: int
