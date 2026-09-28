"""
Attendance Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class GPSLocationInput(BaseModel):
    latitude: float
    longitude: float

class CheckInRequest(BaseModel):
    employee_id: str
    attendance_method: str = Field(default="GPS", pattern="^(GPS|QR|Biometric|Face Recognition|Manual/Demo)$")
    location: Optional[GPSLocationInput] = None
    shift_id: Optional[str] = "SH01"

class CheckOutRequest(BaseModel):
    employee_id: str
    location: Optional[GPSLocationInput] = None

class AttendanceResponse(BaseModel):
    attendance_id: str
    employee_id: str
    date: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    attendance_status: str
    attendance_method: Optional[str] = None
    location_id: Optional[str] = None
    late_minutes: int = 0
    overtime_hours: float = 0.0
    shift_id: str
    anomaly_flag: int = 0
    anomaly_reason: Optional[str] = None

class AttendanceSummaryResponse(BaseModel):
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    half_days: int
    wfh_days: int
    leave_days: int
    total_overtime_hours: float
    attendance_percentage: float
