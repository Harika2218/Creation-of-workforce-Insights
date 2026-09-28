"""
Pydantic Schemas for Enterprise Compliance Alerting & Monitoring
----------------------------------------------------------------
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ComplianceAlertItem(BaseModel):
    alert_id: str
    rule_name: str
    category: str = Field(..., description="WORKING_HOURS, ATTENDANCE, GOVERNANCE, VENDOR_CONTRACTS")
    severity: str = Field(default="MEDIUM", description="CRITICAL, HIGH, MEDIUM, LOW")
    entity_type: str = Field(default="employee", description="employee, contractor, department")
    entity_id: str
    entity_name: str
    description: str
    recommended_action: str
    status: str = Field(default="Open", description="Open, In_Review, Resolved")
    detected_at: str

class ComplianceAlertStatusUpdate(BaseModel):
    status: str = Field(..., description="In_Review, Resolved, Dismissed")
    review_notes: str = Field(..., description="Action taken or justification")

class ComplianceSummaryResponse(BaseModel):
    total_active_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    category_breakdown: dict
    alerts: List[ComplianceAlertItem]
    disclaimer: str = Field(
        default="Operational compliance monitoring guidelines. Does not constitute formal legal counsel across all global jurisdictions."
    )
