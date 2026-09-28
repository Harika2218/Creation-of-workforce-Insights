"""
Payroll Schemas
"""

from typing import Optional
from pydantic import BaseModel

class PayrollResponse(BaseModel):
    payroll_id: str
    employee_id: str
    month: str
    base_salary: float
    overtime_pay: float
    leave_deduction: float
    incentives: float
    bonuses: float
    gross_salary: float
    deductions: float
    net_salary: float
    payment_status: str
    payment_date: Optional[str] = None

class PayrollSummaryResponse(BaseModel):
    month: str
    total_employees_paid: int
    total_base_payroll: float
    total_overtime_paid: float
    total_bonuses_incentives: float
    total_gross_disbursement: float
    total_deductions: float
    total_net_disbursement: float
