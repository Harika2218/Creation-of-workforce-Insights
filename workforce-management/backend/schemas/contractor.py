"""
Pydantic Schemas for Contractor & Vendor Workforce Management
-------------------------------------------------------------
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class ContractorBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    vendor_org: str = Field(..., description="External vendor/agency company name")
    contract_type: str = Field(default="Fixed Term", description="Fixed Term, SOW, Time & Materials")
    start_date: str = Field(..., description="Contract start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Contract end date (YYYY-MM-DD)")
    hourly_billing_rate: float = Field(..., ge=0.0, description="Hourly client billing rate")
    currency: str = Field(default="USD")
    assigned_location_id: str = Field(default="LOC01")
    assigned_project_id: str = Field(default="PRJ01")
    manager_id: str = Field(..., description="Internal supervisor employee ID (e.g. EMP003)")
    status: str = Field(default="Active", description="Active, Completed, Terminated")

class ContractorCreate(ContractorBase):
    contractor_id: Optional[str] = None

class ContractorResponse(ContractorBase):
    contractor_id: str
    total_billed_hours: Optional[float] = 0.0
    active_timesheets_count: Optional[int] = 0

class ContractorTimesheetCreate(BaseModel):
    week_start_date: str = Field(..., description="Monday of work week (YYYY-MM-DD)")
    hours_worked: float = Field(..., ge=0.0, le=80.0, description="Total weekly hours")
    task_description: str = Field(..., description="Summary of deliverables completed")

class ContractorTimesheetResponse(BaseModel):
    timesheet_id: str
    contractor_id: str
    vendor_org: str
    week_start_date: str
    hours_worked: float
    hourly_rate: float
    total_amount: float
    currency: str
    task_description: str
    status: str = Field(default="Submitted", description="Submitted, Approved, Rejected")
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None
