"""
Skills & Competencies Router
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.performance import SkillResponse, EmployeeSkillCreate, EmployeeSkillResponse
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[SkillResponse], summary="List enterprise skills catalog")
async def list_skills(current_user: dict = Depends(get_current_user)):
    db = get_db()
    return list(db.skills.find({}, {"_id": 0}).sort("skill_name", 1))

@router.get("/employee/{employee_id}", response_model=List[EmployeeSkillResponse], summary="Get employee skills")
async def get_employee_skills(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    emp_skills = list(db.employee_skills.find({"employee_id": employee_id}, {"_id": 0}))

    # Enrich with skill name and category
    skills_map = {s["skill_id"]: s for s in db.skills.find({}, {"_id": 0})}
    for es in emp_skills:
        skill_info = skills_map.get(es["skill_id"], {})
        es["skill_name"] = skill_info.get("skill_name", "Unknown")
        es["category"] = skill_info.get("category", "General")

    return emp_skills

@router.post("/employee/{employee_id}", response_model=EmployeeSkillResponse, summary="Map skill to employee profile")
async def add_employee_skill(
    employee_id: str,
    payload: EmployeeSkillCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own skills.")

    skill = db.skills.find_one({"skill_id": payload.skill_id})
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{payload.skill_id}' not found.")

    doc = {
        "employee_id": employee_id,
        "skill_id": payload.skill_id,
        "proficiency_level": payload.proficiency_level,
        "years_experience": payload.years_experience
    }
    db.employee_skills.replace_one({"employee_id": employee_id, "skill_id": payload.skill_id}, doc, upsert=True)

    doc["skill_name"] = skill["skill_name"]
    doc["category"] = skill["category"]
    return doc

PROFICIENCY_NUM = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4
}

DEPARTMENT_REQUIRED_SKILLS = {
    "DEP01": [("Python", "Technical", 3), ("SQL", "Technical", 3), ("AWS", "Technical", 3), ("Docker", "Technical", 2)],
    "DEP02": [("Product Management", "Management", 3), ("Agile", "Management", 3), ("User Research", "Design", 3)],
    "DEP03": [("Talent Acquisition", "HR", 3), ("HR Compliance", "HR", 4), ("Employee Relations", "HR", 3)],
    "DEP04": [("Financial Modeling", "Finance", 4), ("Accounting", "Finance", 4), ("Risk Management", "Finance", 3)],
    "DEP05": [("Sales Negotiation", "Sales", 4), ("CRM Management", "Sales", 3), ("Client Relations", "Sales", 3)],
}

DEFAULT_REQUIRED_SKILLS = [("Python", "Technical", 3), ("SQL", "Technical", 3), ("Communication", "Soft Skills", 3)]

@router.get("/gap-analysis/{employee_id}", summary="Perform explainable skill gap analysis for an employee")
async def analyze_skill_gaps(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    emp = db.employees.find_one({"employee_id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    # RBAC check
    role = current_user.get("role")
    curr_id = current_user.get("employee_id")
    if role == "EMPLOYEE" and curr_id != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only view your own skill gap analysis.")
    if role == "MANAGER" and curr_id != employee_id and emp.get("manager_id") != curr_id:
        raise HTTPException(status_code=403, detail="Forbidden: Employee is not in your direct reporting team.")

    # Current employee skills
    emp_skills_raw = list(db.employee_skills.find({"employee_id": employee_id}))
    skills_map = {s["skill_id"]: s for s in db.skills.find({})}

    current_skill_levels = {}
    for es in emp_skills_raw:
        s_info = skills_map.get(es["skill_id"], {})
        s_name = s_info.get("skill_name", "Unknown")
        raw_prof = str(es.get("proficiency_level", "Beginner")).lower()
        num_prof = PROFICIENCY_NUM.get(raw_prof, 1)
        current_skill_levels[s_name.lower()] = (s_info.get("skill_id", es["skill_id"]), s_name, s_info.get("category", "General"), num_prof)

    dept_id = emp.get("department_id", "DEP01")
    req_skills = DEPARTMENT_REQUIRED_SKILLS.get(dept_id, DEFAULT_REQUIRED_SKILLS)

    gaps = []
    matched_count = 0

    for req_name, req_cat, req_level in req_skills:
        found = current_skill_levels.get(req_name.lower())
        if found:
            s_id, s_disp_name, s_category, cur_level = found
            if cur_level >= req_level:
                matched_count += 1
            else:
                gap_mag = req_level - cur_level
                priority = "CRITICAL" if gap_mag >= 3 else ("HIGH" if gap_mag == 2 else "MEDIUM")
                gaps.append({
                    "skill_id": s_id,
                    "skill_name": s_disp_name,
                    "category": s_category,
                    "current_proficiency": cur_level,
                    "required_proficiency": req_level,
                    "gap_magnitude": gap_mag,
                    "priority": priority
                })
        else:
            # Entirely missing skill
            gap_mag = req_level
            priority = "CRITICAL" if gap_mag >= 3 else "HIGH"
            gaps.append({
                "skill_id": f"REQ_{req_name.replace(' ', '_').upper()}",
                "skill_name": req_name,
                "category": req_cat,
                "current_proficiency": 0,
                "required_proficiency": req_level,
                "gap_magnitude": gap_mag,
                "priority": priority
            })

    total_req = max(1, len(req_skills))
    readiness_pct = round((matched_count / total_req) * 100, 1)

    return {
        "employee_id": employee_id,
        "employee_name": f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip(),
        "department_id": dept_id,
        "current_role": emp.get("job_title", "Specialist"),
        "target_role": f"Senior {emp.get('job_title', 'Specialist')}",
        "overall_readiness_pct": readiness_pct,
        "matched_skills_count": matched_count,
        "gap_skills_count": len(gaps),
        "skill_gaps": gaps
    }

