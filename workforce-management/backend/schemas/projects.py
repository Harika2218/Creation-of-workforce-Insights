"""
Project Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    project_id: str
    project_name: str
    client_name: str
    department_id: str
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = None
    status: str = Field(default="Active")
    budget: float = Field(default=0.0, ge=0.0)

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0.0)

class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    client_name: str
    department_id: str
    start_date: str
    end_date: Optional[str] = None
    status: str
    budget: float
