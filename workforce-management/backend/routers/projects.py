"""
Projects Router
---------------
Enterprise project tracking and budget management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse], summary="List all enterprise projects")
async def list_projects(status_val: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    if status_val:
        query["status"] = status_val
    return list(db.projects.find(query, {"_id": 0}).sort("project_id", 1))

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project by ID")
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    p = db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not p:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return p

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Create project (HR/Admin/Manager only)")
async def create_project(payload: ProjectCreate, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    if db.projects.find_one({"project_id": payload.project_id}):
        raise HTTPException(status_code=409, detail=f"Project ID '{payload.project_id}' already exists.")

    doc = payload.model_dump()
    db.projects.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update project (HR/Admin/Manager only)")
async def update_project(project_id: str, payload: ProjectUpdate, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    existing = db.projects.find_one({"project_id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        db.projects.update_one({"project_id": project_id}, {"$set": updates})

    return db.projects.find_one({"project_id": project_id}, {"_id": 0})
