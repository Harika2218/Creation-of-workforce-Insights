"""
Holiday Calendar Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class HolidayCreate(BaseModel):
    holiday_id: str
    holiday_name: str = Field(..., min_length=2)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    location_id: str = "ALL"
    department_id: Optional[str] = "ALL"

class HolidayResponse(BaseModel):
    holiday_id: str
    holiday_name: str
    date: str
    location_id: str
    department_id: Optional[str] = "ALL"
