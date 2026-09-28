"""
Training & L&D Router
"""

from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.performance import TrainingResponse
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/training", tags=["Training"])

@router.get("", response_model=List[TrainingResponse], summary="List all training enrollments & recommendations")
async def list_trainings(current_user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    if current_user.get("role") == "EMPLOYEE":
        query["employee_id"] = current_user.get("employee_id")
    return list(db.employee_training.find(query, {"_id": 0}))

@router.get("/employee/{employee_id}", response_model=List[TrainingResponse], summary="Get employee training records & AI recommendations")
async def get_employee_trainings(employee_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot view another employee's training records.")

    db = get_db()
    return list(db.employee_training.find({"employee_id": employee_id}, {"_id": 0}))

@router.get("/programs", summary="List enterprise training course catalog")
async def list_training_programs(current_user: dict = Depends(get_current_user)):
    db = get_db()
    return list(db.training_programs.find({}, {"_id": 0}))

@router.get("/recommendations/{employee_id}", summary="Get transparent AI training recommendations with explainable reasoning")
async def get_training_recommendations(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    emp = db.employees.find_one({"employee_id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    # RBAC check
    role = current_user.get("role")
    curr_id = current_user.get("employee_id")
    if role == "EMPLOYEE" and curr_id != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only view your own training recommendations.")
    if role == "MANAGER" and curr_id != employee_id and emp.get("manager_id") != curr_id:
        raise HTTPException(status_code=403, detail="Forbidden: Employee is not in your direct reporting team.")

    # Fetch programs
    all_programs = list(db.training_programs.find({}, {"_id": 0}))
    emp_skills = {es["skill_id"]: es for es in db.employee_skills.find({"employee_id": employee_id})}
    skills_map = {s["skill_id"]: s["skill_name"] for s in db.skills.find({})}

    recommendations = []
    for prog in all_programs:
        prog_skill = prog.get("skill", "")
        # Find if employee has this skill
        matched_es = None
        for sid, es in emp_skills.items():
            if skills_map.get(sid, "").lower() == prog_skill.lower():
                matched_es = es
                break

        if not matched_es:
            recommendations.append({
                "program_id": prog.get("program_id", f"TRP_{prog_skill.upper()}"),
                "title": prog.get("name", f"Professional {prog_skill} Mastery"),
                "provider": prog.get("provider", "InnovateCorp Learning Academy"),
                "duration_hours": prog.get("duration_hours", 30),
                "skill_id": f"SK_{prog_skill.upper()}",
                "skill_name": prog_skill,
                "priority": "HIGH",
                "reason": f"Employee does not currently hold verified proficiency in '{prog_skill}', which is a required baseline competency for {emp.get('job_title', 'their role')}.",
                "expected_improvement": f"Establish baseline competence and certification in {prog_skill}.",
                "disclaimer": "AI training recommendation is a decision-support guide and does not guarantee automated performance rating change."
            })
        elif matched_es.get("proficiency_level") in ["Beginner", "Intermediate"]:
            recommendations.append({
                "program_id": prog.get("program_id", f"TRP_{prog_skill.upper()}"),
                "title": prog.get("name", f"Advanced {prog_skill} Specialization"),
                "provider": prog.get("provider", "InnovateCorp Learning Academy"),
                "duration_hours": prog.get("duration_hours", 40),
                "skill_id": matched_es["skill_id"],
                "skill_name": prog_skill,
                "priority": "MEDIUM",
                "reason": f"Employee currently demonstrates {matched_es.get('proficiency_level')} level in '{prog_skill}'. Completing this curriculum bridges the gap to Advanced proficiency.",
                "expected_improvement": f"Advance from {matched_es.get('proficiency_level')} to Advanced proficiency tier.",
                "disclaimer": "AI training recommendation is a decision-support guide and does not guarantee automated performance rating change."
            })

    return {
        "employee_id": employee_id,
        "employee_name": f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip(),
        "job_title": emp.get("job_title", "Specialist"),
        "total_recommendations": len(recommendations),
        "recommendations": recommendations[:6]
    }

