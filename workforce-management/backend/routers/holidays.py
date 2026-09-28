"""
Holiday Calendar Router
-----------------------
Company official holiday calendar management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.holidays import HolidayCreate, HolidayResponse
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/holidays", tags=["Holidays"])

@router.get("", response_model=List[HolidayResponse], summary="List company holidays")
async def list_holidays(year: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    if year:
        query["date"] = {"$regex": f"^{year}"}
    return list(db.holidays.find(query, {"_id": 0}).sort("date", 1))

@router.post("", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED, summary="Add holiday (HR/Admin only)")
async def create_holiday(payload: HolidayCreate, current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    if db.holidays.find_one({"holiday_id": payload.holiday_id}):
        raise HTTPException(status_code=409, detail=f"Holiday ID '{payload.holiday_id}' already exists.")

    doc = payload.model_dump()
    db.holidays.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{holiday_id}", response_model=HolidayResponse, summary="Update holiday (HR/Admin only)")
async def update_holiday(holiday_id: str, payload: HolidayCreate, current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    if not db.holidays.find_one({"holiday_id": holiday_id}):
        raise HTTPException(status_code=404, detail=f"Holiday '{holiday_id}' not found.")

    doc = payload.model_dump()
    db.holidays.replace_one({"holiday_id": holiday_id}, doc)
    return doc

@router.delete("/{holiday_id}", response_model=MessageResponse, summary="Delete holiday (HR/Admin only)")
async def delete_holiday(holiday_id: str, current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    result = db.holidays.delete_one({"holiday_id": holiday_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Holiday '{holiday_id}' not found.")
    return {"message": f"Holiday '{holiday_id}' deleted successfully."}
