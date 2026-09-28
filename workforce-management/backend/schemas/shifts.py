"""
Shift Management Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class ShiftCreate(BaseModel):
    shift_id: str
    shift_name: str
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    grace_period_mins: int = 15
    is_rotational: int = 0

class ShiftResponse(BaseModel):
    shift_id: str
    shift_name: str
    start_time: str
    end_time: str
    grace_period_mins: int
    is_rotational: int

class ShiftAssignRequest(BaseModel):
    employee_id: str
    shift_id: str
    effective_from: str
    effective_to: Optional[str] = None

class ShiftSwapRequestCreate(BaseModel):
    requester_id: str
    target_employee_id: str
    shift_id: str
    target_shift_id: str
    requested_date: str
    reason: str

class ShiftSwapResponse(BaseModel):
    swap_id: str
    requester_id: str
    target_employee_id: str
    shift_id: str
    target_shift_id: str
    requested_date: str
    status: str
    reason: str
    approved_by: Optional[str] = None
