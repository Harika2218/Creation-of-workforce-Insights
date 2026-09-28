"""
Pydantic Schemas for AI/ML Workforce Intelligence API
-----------------------------------------------------
Defines request and response data models for all AI services.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float
    current_value: Optional[Any] = None

class AbsenteeismResponse(BaseModel):
    employee_id: str
    prediction: int = Field(..., description="0 for low risk, 1 for flagged absence risk")
    probability: float = Field(..., description="Model-estimated probability of absence (0.0 to 1.0)")
    risk_level: str = Field(..., description="'LOW', 'MEDIUM', or 'HIGH'")
    important_features: List[FeatureImportanceItem]
    prediction_date: str
    model_version: str
    disclaimer: str

class AttritionResponse(BaseModel):
    prediction_id: Optional[str] = None
    employee_id: str
    department_id: Optional[str] = None
    attrition_probability: Optional[float] = None
    risk_score: float = 0.20
    risk_band: Optional[str] = None
    risk_category: Optional[str] = "LOW"
    top_contributing_features: Optional[List[str]] = None
    contributing_factors: Optional[List[str]] = None
    prediction_date: Optional[str] = None
    last_evaluated: Optional[str] = None
    model_version: Optional[str] = "attrition_v1.0.0"
    disclaimer: Optional[str] = "Predictive workforce planning signal only. Not proof of employee intent to leave."

class AttendanceAnomalyItem(BaseModel):
    anomaly_id: str
    attendance_id: str
    employee_id: str
    date: str
    anomaly_score: float = 0.85
    is_anomaly: bool = True
    anomaly_type: Optional[str] = None
    reason: str = "Unusual attendance pattern"
    severity: str = "MEDIUM"
    status: str = "Investigating"
    detected_at: Optional[str] = None
    model_version: Optional[str] = "anomaly_iforest_v1.0.0"

class ProductivityScoreComponents(BaseModel):
    kpi_achievement: float
    goal_completion: float
    billable_efficiency: float
    attendance_reliability: float

class ProductivityResponse(BaseModel):
    employee_id: str
    productivity_score: float
    score_components: ProductivityScoreComponents
    period: str
    model_version: str
    explanation: str

class WorkforceForecastItem(BaseModel):
    forecast_id: str
    department_id: str
    department_name: Optional[str] = None
    forecast_period: str
    current_headcount: int
    projected_headcount_need: int
    predicted_demand: Optional[int] = None
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None
    recommended_hires: int
    estimated_gap: Optional[int] = None
    budget_impact: float
    status: str
    model_version: Optional[str] = "forecaster_v1.0.0"

class StaffingRecommendationItem(BaseModel):
    recommendation_id: str
    department_id: str
    department_name: Optional[str] = None
    target_role: str
    current_staff: Optional[int] = None
    forecast_demand: Optional[int] = None
    estimated_gap: Optional[int] = None
    recommended_count: int = 1
    priority: str = "MEDIUM"
    recommendation: Optional[str] = None
    rationale: str
    model_version: Optional[str] = "forecaster_v1.0.0"

class SkillGapItem(BaseModel):
    department_id: str
    department_name: str
    role: str
    required_skill: str
    target_proficiency: str
    available_skill_count: int
    target_headcount: Optional[int] = None
    skill_gap: int
    priority: str
    model_version: Optional[str] = "skill_gap_v1.0.0"

class TrainingRecommendationItem(BaseModel):
    employee_id: str
    skill: str
    current_proficiency: str
    target_proficiency: str
    recommended_training: str
    program_id: Optional[str] = None
    duration_hours: Optional[int] = None
    reason: str
    model_version: Optional[str] = "training_rec_v1.0.0"

class ShiftRecommendationItem(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    department_id: Optional[str] = None
    recommended_shift: str
    shift_name: str
    reason: str
    expected_overtime: str
    skill_match: str
    status: Optional[str] = "Proposed"
    model_version: Optional[str] = "shift_rec_v1.0.0"

class ResourceRecommendationItem(BaseModel):
    allocation_id: str
    project_id: str
    project_name: Optional[str] = "Enterprise Project"
    recommended_employee: Optional[str] = None
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    skill_match_pct: Optional[float] = 90.0
    availability_hours: Optional[float] = 40.0
    current_workload_hours: Optional[float] = 0.0
    recommendation_reason: Optional[str] = "Strategic resource allocation"
    status: Optional[str] = "Active"
    model_version: Optional[str] = "resource_opt_v1.0.0"

class AIModelMetricsResponse(BaseModel):
    system: str
    version: str
    evaluated_at: str
    fairness_safeguards: Dict[str, Any]
    models: Dict[str, Any]

class WorkforceSimulationRequest(BaseModel):
    scenario_type: str = Field(
        ...,
        description="DEMAND_INCREASE, WORKFORCE_REDUCTION, ATTRITION_SPIKE, NEW_PROJECT_SKILLS, SHIFT_CAPACITY_CHANGE"
    )
    percentage_change: float = Field(default=15.0, description="Magnitude of change in percentage")
    department_id: Optional[str] = Field(default=None, description="Department ID to isolate, or None for organization-wide")
    target_skills: Optional[List[str]] = Field(default_factory=list, description="Target skills needed (for project scenarios)")
    simulation_horizon_months: int = Field(default=6, ge=1, le=24, description="Planning window in months")

class WorkforceSimulationResponse(BaseModel):
    simulation_id: str
    scenario_type: str
    label: str = Field(default="Scenario Simulation — For Strategic Decision Support Only (Not an Actual Forecast)")
    base_headcount: int
    projected_headcount_needed: int
    staffing_gap: int = Field(..., description="Positive indicates deficit, negative indicates surplus")
    projected_monthly_cost_delta: float
    affected_departments: List[str]
    required_hiring_count: int
    available_internal_reallocations: int
    critical_skill_gaps: List[str]
    recommended_actions: List[str]
    created_at: str

