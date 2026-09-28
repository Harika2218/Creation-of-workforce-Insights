"""
Pydantic Schemas for Skills Intelligence & Explainable Training Recommendations
------------------------------------------------------------------------------
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class SkillGapDetail(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    current_proficiency: int = Field(..., ge=0, le=5, description="Current level (0=None to 5=Master)")
    required_proficiency: int = Field(..., ge=1, le=5, description="Required role level")
    gap_magnitude: int = Field(..., description="Required minus Current")
    priority: str = Field(default="MEDIUM", description="CRITICAL, HIGH, MEDIUM, LOW")

class SkillGapAnalysisResponse(BaseModel):
    employee_id: str
    employee_name: str
    department_id: str
    current_role: str
    target_role: str
    overall_readiness_pct: float
    matched_skills_count: int
    gap_skills_count: int
    skill_gaps: List[SkillGapDetail]

class ExplainableTrainingRecommendation(BaseModel):
    program_id: str
    title: str
    provider: str
    duration_hours: int
    skill_id: str
    skill_name: str
    priority: str
    reason: str = Field(..., description="Explainable rationale connecting employee gap to course")
    expected_improvement: str
    disclaimer: str = Field(
        default="AI training recommendation is a decision-support guide and does not guarantee automated performance rating change."
    )
