"""
Performance, Skills, Training, Notifications, Manager, and HR Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field

# Performance
class PerformanceCreate(BaseModel):
    employee_id: str
    kpi_score: float = Field(..., ge=0, le=100)
    goal_completion: float = Field(..., ge=0, le=100)
    productivity_score: float = Field(..., ge=0, le=100)
    manager_feedback: str
    performance_rating: str
    review_date: str

class PerformanceResponse(BaseModel):
    review_id: str
    employee_id: str
    kpi_score: float
    goal_completion: float
    productivity_score: float
    manager_feedback: str
    performance_rating: str
    review_date: str
    reviewer_id: Optional[str] = None

# Skills
class SkillResponse(BaseModel):
    skill_id: str
    skill_name: str
    category: str

class EmployeeSkillCreate(BaseModel):
    skill_id: str
    proficiency_level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced|Expert)$")
    years_experience: float = Field(default=1.0, ge=0)

class EmployeeSkillResponse(BaseModel):
    employee_id: str
    skill_id: str
    skill_name: Optional[str] = None
    category: Optional[str] = None
    proficiency_level: str
    years_experience: float

# Training
class TrainingResponse(BaseModel):
    training_id: str
    employee_id: str
    training_name: str
    skill: str
    completion_status: str
    type: Optional[str] = "COMPLETED"
    reason: Optional[str] = None
    score: Optional[float] = None
    completion_date: Optional[str] = None

# Notifications
class NotificationCreate(BaseModel):
    employee_id: str
    category: str
    title: str
    message: str

class NotificationResponse(BaseModel):
    notification_id: str
    employee_id: str
    category: str
    title: str
    message: str
    is_read: int
    created_at: str

# Manager Team
class TeamMemberResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    designation: str
    department_id: str
    email: str
    employment_status: str
    location_id: str

class TeamSummaryResponse(BaseModel):
    manager_id: str
    team_size: int
    present_today: int
    on_leave_today: int
    pending_leave_approvals: int
    pending_timesheet_approvals: int

# HR Dashboard
class HRDashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    notice_period_employees: int
    departments_count: int
    locations_count: int
    daily_attendance_rate: float
    pending_leave_requests: int
    total_monthly_payroll: float
    attrition_risk_high: int
    attrition_risk_medium: int
    attrition_risk_low: int
