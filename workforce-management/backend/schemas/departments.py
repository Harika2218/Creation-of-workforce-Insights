"""
Department Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class DepartmentCreate(BaseModel):
    department_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    code: str = Field(..., min_length=2)
    description: Optional[str] = None
    head_employee_id: Optional[str] = None
    budget: float = Field(default=0.0, ge=0.0)

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    head_employee_id: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0.0)

class DepartmentResponse(BaseModel):
    department_id: str
    name: str
    code: str
    description: Optional[str] = None
    head_employee_id: Optional[str] = None
    budget: float
    employee_count: Optional[int] = 0
