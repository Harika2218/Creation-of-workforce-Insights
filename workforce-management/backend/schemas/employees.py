"""
Employee Management Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class EmployeeCreate(BaseModel):
    employee_id: Optional[str] = None # Auto-assigned if omitted
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    gender: str = Field(..., pattern="^(Male|Female|Non-Binary)$")
    date_of_birth: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    email: EmailStr
    phone: str
    address: str
    joining_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    employment_type: str = Field(default="Full-Time")
    designation: str
    department_id: str
    manager_id: Optional[str] = None
    location_id: str
    salary: float = Field(..., ge=0.0)
    experience: float = Field(..., ge=0.0)
    employment_status: str = Field(default="Active")
    role: str = Field(default="EMPLOYEE")

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[str] = None
    manager_id: Optional[str] = None
    location_id: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0.0)
    employment_status: Optional[str] = None
    role: Optional[str] = None

class EmployeeResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    email: str
    phone: str
    address: str
    joining_date: str
    employment_type: str
    designation: str
    department_id: str
    manager_id: Optional[str] = None
    location_id: str
    salary: float
    experience: float
    employment_status: str
    role: str

class EmployeeProfileResponse(EmployeeResponse):
    department_name: Optional[str] = None
    location_name: Optional[str] = None
    manager_name: Optional[str] = None
    skills: Optional[List[dict]] = None
    leave_balances: Optional[List[dict]] = None
