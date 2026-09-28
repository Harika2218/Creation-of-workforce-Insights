"""
FastAPI Router: AI/ML Workforce Intelligence
--------------------------------------------
Exposes 11+ RESTful endpoints for absenteeism, attrition, anomalies,
productivity, workforce forecasting, staffing, skill gaps, and shift recommendations.
Enforces strict Role-Based Access Control (RBAC).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth.dependencies import get_current_user, require_role
from backend.services.ai_service import AIService
from backend.schemas.ai import (
    AbsenteeismResponse,
    AttritionResponse,
    AttendanceAnomalyItem,
    ProductivityResponse,
    WorkforceForecastItem,
    StaffingRecommendationItem,
    SkillGapItem,
    TrainingRecommendationItem,
    ShiftRecommendationItem,
    ResourceRecommendationItem,
    AIModelMetricsResponse,
    WorkforceSimulationRequest,
    WorkforceSimulationResponse,
)
from database.mongodb import get_db

router = APIRouter(prefix="/ai", tags=["AI & Workforce Intelligence"])

def verify_employee_access(target_emp_id: str, current_user: dict):
    """
    Enforces RBAC: EMPLOYEE can only view their own records.
    MANAGER can only view their direct reports or themselves.
    HR/ADMIN have unrestricted access.
    """
    role = current_user.get("role", "EMPLOYEE")
    curr_emp_id = current_user.get("employee_id")

    if role == "EMPLOYEE" and curr_emp_id != target_emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: You are only authorized to view your own AI insights (Your ID: {curr_emp_id})."
        )
    if role == "MANAGER" and curr_emp_id != target_emp_id:
        # Check if target is in manager's direct reports
        db = get_db()
        emp = db.employees.find_one({"employee_id": target_emp_id})
        if not emp or emp.get("manager_id") != curr_emp_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Employee {target_emp_id} is not in your reporting team."
            )

# -------------------------------------------------------------------
# 1. Predictive Absenteeism
# -------------------------------------------------------------------
@router.get("/absenteeism", response_model=List[AbsenteeismResponse], summary="Query absenteeism predictions")
async def get_absenteeism(
    department_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    emp_id = current_user.get("employee_id") if role == "EMPLOYEE" else None
    return AIService.get_absenteeism(employee_id=emp_id, department_id=department_id)

@router.get("/absenteeism/{employee_id}", response_model=AbsenteeismResponse, summary="Get absenteeism prediction for an employee")
async def get_employee_absenteeism(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)
    results = AIService.get_absenteeism(employee_id=employee_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No absenteeism prediction found for employee {employee_id}. Insufficient data or unmodeled."
        )
    return results[0]

# -------------------------------------------------------------------
# 2. Attrition Risk
# -------------------------------------------------------------------
@router.get("/attrition", response_model=List[AttritionResponse], summary="Query workforce attrition risks")
async def get_attrition(
    department_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    # Managers filtered by team if applicable
    role = current_user.get("role")
    curr_emp_id = current_user.get("employee_id")
    if role == "MANAGER":
        db = get_db()
        team_emp_ids = [e["employee_id"] for e in db.employees.find({"manager_id": curr_emp_id}, {"employee_id": 1})]
        all_attr = AIService.get_attrition(department_id=department_id)
        return [a for a in all_attr if a["employee_id"] in team_emp_ids]
    return AIService.get_attrition(department_id=department_id)

@router.get("/attrition/{employee_id}", response_model=AttritionResponse, summary="Get attrition risk for an employee")
async def get_employee_attrition(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)
    results = AIService.get_attrition(employee_id=employee_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attrition prediction record found for employee {employee_id}."
        )
    return results[0]

# -------------------------------------------------------------------
# 3. Attendance Anomalies (Isolation Forest)
# -------------------------------------------------------------------
@router.get("/attendance-anomalies", response_model=List[AttendanceAnomalyItem], summary="Get attendance anomalies detected by Isolation Forest")
async def get_attendance_anomalies(
    limit: int = Query(default=100, ge=1, le=500),
    severity: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    return AIService.get_attendance_anomalies(limit=limit, severity=severity)

# -------------------------------------------------------------------
# 4. Transparent Productivity Scoring
# -------------------------------------------------------------------
@router.get("/productivity", response_model=List[ProductivityResponse], summary="Query workforce productivity scores")
async def get_productivity(
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    emp_id = current_user.get("employee_id") if role == "EMPLOYEE" else None
    return AIService.get_productivity(employee_id=emp_id)

@router.get("/productivity/{employee_id}", response_model=ProductivityResponse, summary="Get productivity scorecard for employee")
async def get_employee_productivity(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)
    results = AIService.get_productivity(employee_id=employee_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No productivity evaluation scorecard found for employee {employee_id}."
        )
    return results[0]

# -------------------------------------------------------------------
# 5. Workforce Demand Forecasting
# -------------------------------------------------------------------
@router.get("/workforce-forecast", response_model=List[WorkforceForecastItem], summary="Get department workforce demand forecasts")
async def get_workforce_forecast(
    period: Optional[str] = Query(default="Q3-2026"),
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    return AIService.get_workforce_forecasts(period=period)

# -------------------------------------------------------------------
# 6. Staffing Gap Recommendations
# -------------------------------------------------------------------
@router.get("/staffing-recommendations", response_model=List[StaffingRecommendationItem], summary="Get strategic staffing recommendations")
async def get_staffing_recommendations(
    department_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    return AIService.get_staffing_recommendations(department_id=department_id)

# -------------------------------------------------------------------
# 7. Enterprise Skill Gaps Matrix
# -------------------------------------------------------------------
@router.get("/skill-gaps", response_model=List[SkillGapItem], summary="Get enterprise skill matrix gaps")
async def get_skill_gaps(
    department_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    return AIService.get_skill_gaps(department_id=department_id)

# -------------------------------------------------------------------
# 8. Training Curriculum Recommendations
# -------------------------------------------------------------------
@router.get("/training-recommendations/{employee_id}", response_model=List[TrainingRecommendationItem], summary="Get recommended training courses for employee")
async def get_training_recommendations(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)
    return AIService.get_training_recommendations(employee_id=employee_id)

# -------------------------------------------------------------------
# 9. Intelligent Shift Recommendations
# -------------------------------------------------------------------
@router.get("/shift-recommendations", response_model=List[ShiftRecommendationItem], summary="Get optimized shift allocation advice")
async def get_shift_recommendations(
    department_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    return AIService.get_shift_recommendations(department_id=department_id)

# -------------------------------------------------------------------
# 10. Project Resource Optimization
# -------------------------------------------------------------------
@router.get("/resource-recommendations", response_model=List[ResourceRecommendationItem], summary="Get project resource matching recommendations")
async def get_resource_recommendations(
    project_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    return AIService.get_resource_recommendations(project_id=project_id)

# -------------------------------------------------------------------
# 11. AI Model Governance & Evaluation Metrics
# -------------------------------------------------------------------
@router.get("/model-metrics", response_model=AIModelMetricsResponse, summary="Get model validation metrics and fairness metadata")
async def get_model_metrics(
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    return AIService.get_model_metrics()

# -------------------------------------------------------------------
# 12. Strategic Workforce Scenario Simulation (Deterministic Engine)
# -------------------------------------------------------------------
@router.post("/simulation", response_model=WorkforceSimulationResponse, summary="Execute strategic workforce scenario simulation (HR/Admin only)")
async def run_workforce_simulation(
    payload: WorkforceSimulationRequest,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    """
    Simulates strategic HR scenarios:
    - DEMAND_INCREASE: Simulates headcount and cost scaling.
    - WORKFORCE_REDUCTION: Simulates reduction in workforce and cost savings.
    - ATTRITION_SPIKE: Simulates key personnel turnover and replacement cost overhead.
    - NEW_PROJECT_SKILLS: Evaluates skill deficits for prospective contracts.
    - SHIFT_CAPACITY_CHANGE: Evaluates 24/7 rotational shift redistribution costs.
    Outputs are clearly labeled as Scenario Simulation decision-support models.
    """
    import uuid
    from datetime import datetime, timezone
    db = get_db()

    query = {}
    if payload.department_id:
        query["department_id"] = payload.department_id

    base_count = db.employees.count_documents(query)
    if base_count == 0:
        base_count = db.employees.count_documents({}) or 200

    # Determine average monthly compensation
    avg_salary = 4800.0
    depts = [payload.department_id] if payload.department_id else db.departments.distinct("department_id")

    pct = max(1.0, min(100.0, payload.percentage_change))
    scenario = payload.scenario_type.upper()

    if scenario == "DEMAND_INCREASE":
        needed = int(round(base_count * (1 + pct / 100.0)))
        gap = needed - base_count
        cost_delta = round(gap * avg_salary, 2)
        hiring = int(round(gap * 0.7))
        realloc = gap - hiring
        skill_gaps = ["System Architecture", "Cloud Engineering", "Data Analytics"]
        actions = [
            f"Open {hiring} external requisitions across key technical departments.",
            f"Initiate internal talent mobility for {realloc} lateral reassignments.",
            "Establish accelerated onboarding cohort to meet project deadlines."
        ]
    elif scenario == "WORKFORCE_REDUCTION":
        needed = int(round(base_count * (1 - pct / 100.0)))
        gap = needed - base_count  # negative
        cost_delta = round(gap * avg_salary, 2)  # negative (cost savings)
        hiring = 0
        realloc = 0
        skill_gaps = []
        actions = [
            "Enact temporary hiring freeze on non-critical backfills.",
            "Review contractor/vendor engagements prior to regular personnel adjustments.",
            "Identify consolidation opportunities across overlapping project functions."
        ]
    elif scenario == "ATTRITION_SPIKE":
        turnover_count = int(round(base_count * (pct / 100.0)))
        needed = base_count
        gap = turnover_count
        cost_delta = round(turnover_count * avg_salary * 0.35, 2)  # Recruitment & ramp overhead
        hiring = turnover_count
        realloc = int(round(turnover_count * 0.25))
        skill_gaps = ["Senior Leadership", "Core Domain Knowledge", "Client Account Management"]
        actions = [
            "Conduct structured stay-interviews with critical talent in high-risk bands.",
            "Calibrate compensation against market benchmarks for essential roles.",
            "Strengthen succession planning and cross-training redundancy."
        ]
    elif scenario == "NEW_PROJECT_SKILLS":
        target_skills = payload.target_skills or ["Python", "AWS", "Machine Learning"]
        needed = base_count + int(max(2, base_count * 0.05))
        gap = needed - base_count
        cost_delta = round(gap * avg_salary, 2)
        hiring = int(round(gap * 0.6))
        realloc = gap - hiring
        skill_gaps = target_skills
        actions = [
            f"Launch specialized training bootcamps for skills: {', '.join(target_skills)}.",
            f"Engage temporary specialized contractors for immediate kickoff deliverables.",
            "Partner with department leads to review internal staff certifications."
        ]
    else:  # SHIFT_CAPACITY_CHANGE or default
        needed = base_count
        gap = int(round(base_count * 0.05))
        cost_delta = round(base_count * 0.20 * 450.0, 2)  # Shift allowance
        hiring = 0
        realloc = gap
        skill_gaps = ["Night Shift Safety Protocols"]
        actions = [
            "Rebalance rotational shift preferences across morning and evening rosters.",
            "Verify compliance with mandatory 12-hour rest intervals between shifts.",
            "Review transport and security arrangements for extended night operations."
        ]

    sim_id = f"SIM_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:6].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    sim_doc = {
        "simulation_id": sim_id,
        "scenario_type": scenario,
        "label": "Scenario Simulation — For Strategic Decision Support Only (Not an Actual Forecast)",
        "base_headcount": base_count,
        "projected_headcount_needed": needed,
        "staffing_gap": gap,
        "projected_monthly_cost_delta": cost_delta,
        "affected_departments": depts,
        "required_hiring_count": hiring,
        "available_internal_reallocations": realloc,
        "critical_skill_gaps": skill_gaps,
        "recommended_actions": actions,
        "created_at": now_iso
    }

    # Record to simulation history
    try:
        db.workforce_simulations.insert_one(sim_doc.copy())
    except Exception:
        pass

    # Audit log
    db.audit_logs.insert_one({
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": now_iso,
        "actor_user_id": current_user.get("user_id"),
        "actor_role": current_user.get("role"),
        "action": "RUN_WORKFORCE_SIMULATION",
        "resource_type": "simulation",
        "resource_id": sim_id,
        "status": "SUCCESS",
        "details": {"scenario_type": scenario, "percentage": pct}
    })

    return sim_doc

