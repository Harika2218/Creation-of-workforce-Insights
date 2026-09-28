"""
Grounded Context Builder for RAG & Chatbot
------------------------------------------
Formats retrieved database records, document policy chunks, and AI predictions
into a clean, structured, cited markdown context block with strict token bounds.
"""

from typing import Dict, Any, List, Tuple
from backend.ai.chatbot.schemas import CitationSource
from backend.ai.chatbot.guardrails import GuardrailEngine

class ContextBuilder:
    """
    Builds structured context strings and tracks exact source citations.
    """

    @classmethod
    def build_context(
        cls,
        mongo_data: Optional[Dict[str, Any]] = None,
        rag_chunks: Optional[List[Dict[str, Any]]] = None,
        ai_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[CitationSource]]:
        """
        Combines disparate retrieval streams into a unified context block and citation list.
        """
        context_parts: List[str] = []
        citations: List[CitationSource] = []

        # 1. MongoDB Database Records
        if mongo_data and any(k for k in mongo_data.keys() if k != "context_type"):
            db_lines = ["### Verified HR System Records (Live Database):"]

            if "leave_balances" in mongo_data and mongo_data["leave_balances"]:
                db_lines.append("**Official Leave Balances**:")
                for b in mongo_data["leave_balances"]:
                    db_lines.append(
                        f"- {b.get('leave_type', 'Leave')}: {b.get('available_days', 0)} days available "
                        f"(Used: {b.get('used_days', 0)}, Total Entitlement: {b.get('entitled_days', 0)} days)"
                    )
                citations.append(CitationSource(
                    title="Employee Leave Balance",
                    source_type="database_record",
                    section="HR System Live Record (leave_balances)",
                    snippet=f"Available leave balance data for Employee {mongo_data.get('employee_id')}"
                ))

            if "recent_leave_requests" in mongo_data and mongo_data["recent_leave_requests"]:
                db_lines.append("\n**Recent Leave Applications**:")
                for req in mongo_data["recent_leave_requests"]:
                    db_lines.append(
                        f"- Request ID {req.get('request_id')}: {req.get('leave_type')} from {req.get('start_date')} to {req.get('end_date')} "
                        f"| Status: {req.get('status')} | Applied On: {req.get('applied_on')}"
                    )
                citations.append(CitationSource(
                    title="Leave Application History",
                    source_type="database_record",
                    section="HR System Live Record (leave_requests)"
                ))

            if "assigned_shift" in mongo_data and mongo_data["assigned_shift"]:
                s = mongo_data["assigned_shift"]
                db_lines.append(f"\n**Assigned Shift**: {s.get('shift_name')} ({s.get('start_time')} - {s.get('end_time')})")
                citations.append(CitationSource(
                    title="Work Schedule Roster",
                    source_type="database_record",
                    section="HR System Live Record (employee_shifts)"
                ))

            if "summary_stats" in mongo_data and mongo_data["summary_stats"]:
                stats = mongo_data["summary_stats"]
                db_lines.append(
                    f"\n**Attendance Summary**: Rate {stats.get('attendance_rate')}, "
                    f"Present: {stats.get('present_days')}/{stats.get('total_recorded_days')} days, "
                    f"Late Arrivals: {stats.get('late_arrivals')}"
                )
                citations.append(CitationSource(
                    title="Attendance Summary Statistics",
                    source_type="database_record",
                    section="HR System Live Record (attendance)"
                ))

            if "team_attendance" in mongo_data and mongo_data["team_attendance"]:
                ta = mongo_data["team_attendance"]
                db_lines.append(
                    f"\n**Team Attendance Status**: Total Team: {ta.get('total_team_members')}, "
                    f"Present: {ta.get('present_count')}, Absent: {ta.get('absent_count')}"
                )
                if ta.get("absent_employees"):
                    db_lines.append(f"Absent Members: {', '.join(ta.get('absent_employees'))}")
                citations.append(CitationSource(
                    title="Manager Team Attendance Roster",
                    source_type="database_record",
                    section="HR System Live Record (team_attendance)"
                ))

            if "payroll_history" in mongo_data and mongo_data["payroll_history"]:
                db_lines.append("\n**Personal Payroll Summary**:")
                for p in mongo_data["payroll_history"]:
                    db_lines.append(
                        f"- Period {p.get('pay_period')}: Gross ₹{p.get('gross_salary', 0):,.2f}, "
                        f"Net ₹{p.get('net_salary', 0):,.2f}, Deductions ₹{p.get('deductions', 0):,.2f}"
                    )
                citations.append(CitationSource(
                    title="Personal Payroll Record",
                    source_type="database_record",
                    section="HR System Live Record (payroll_records)"
                ))

            if "profile" in mongo_data and mongo_data["profile"]:
                p = mongo_data["profile"]
                db_lines.append(
                    f"\n**Employee Profile**: {p.get('first_name')} {p.get('last_name')} ({p.get('employee_id')}), "
                    f"Designation: {p.get('designation')}, Department: {p.get('department_id')}, Status: {p.get('employment_status')}"
                )
                citations.append(CitationSource(
                    title="Employee Master Profile",
                    source_type="database_record",
                    section="HR System Live Record (employees)"
                ))

            context_parts.append("\n".join(db_lines))

        # 2. Phase 5 AI/ML Workforce Intelligence
        if ai_data and any(k for k in ai_data.keys() if k != "context_type"):
            ai_lines = ["### AI Workforce Intelligence Predictions & Analytics:"]

            if "workforce_forecasts" in ai_data and ai_data["workforce_forecasts"]:
                ai_lines.append("**Workforce Demand Projections (Q3-2026)**:")
                for fc in ai_data["workforce_forecasts"]:
                    ai_lines.append(
                        f"- Department {fc.get('department_id')} ({fc.get('department_name', '')}): "
                        f"Current Headcount: {fc.get('current_headcount')}, "
                        f"Projected Need: {fc.get('projected_headcount_need')}, "
                        f"Recommended Hires: +{fc.get('recommended_hires', 0)}"
                    )
                citations.append(CitationSource(
                    title="Workforce Demand Forecast (Q3-2026)",
                    source_type="ai_prediction",
                    section="AI Model Forecaster (v1.0.0)"
                ))

            if "high_priority_skill_gaps" in ai_data and ai_data["high_priority_skill_gaps"]:
                ai_lines.append("\n**Key Organizational Skill Gaps**:")
                for sg in ai_data["high_priority_skill_gaps"][:4]:
                    ai_lines.append(
                        f"- {sg.get('department_name', sg.get('department_id'))}: "
                        f"Deficit in '{sg.get('required_skill')}' (Gap: {sg.get('skill_gap')}, Priority: {sg.get('priority')})"
                    )
                citations.append(CitationSource(
                    title="Enterprise Skill Gap Matrix",
                    source_type="ai_prediction",
                    section="AI Competency Evaluation Engine"
                ))

            if "total_evaluated" in ai_data:
                ai_lines.append(
                    f"\n**Attrition Vulnerability Overview**: {ai_data.get('high_attrition_count', 0)} employees "
                    f"flagged in High Vulnerability band out of {ai_data.get('total_evaluated', 0)} evaluated."
                )
                citations.append(CitationSource(
                    title="Workforce Attrition Risk Distribution",
                    source_type="ai_prediction",
                    section="AI Gradient Boosting Attrition Model"
                ))

            context_parts.append("\n".join(ai_lines))

        # 3. RAG Policy Documents
        if rag_chunks:
            doc_lines = ["### Official Enterprise HR Policy Documents:"]
            for idx, ch in enumerate(rag_chunks, 1):
                doc_lines.append(
                    f"\n[Source {idx}: {ch.get('document_name')} | Section: {ch.get('section')} | Page: {ch.get('page')}]\n"
                    f"{ch.get('text')}"
                )
                citations.append(CitationSource(
                    title=f"{ch.get('title', ch.get('document_name'))}",
                    source_type="policy_document",
                    section=ch.get("section"),
                    page=ch.get("page"),
                    document_name=ch.get("document_name"),
                    snippet=ch.get("text")[:160] + "..." if len(ch.get("text", "")) > 160 else ch.get("text")
                ))
            context_parts.append("\n".join(doc_lines))

        full_context = "\n\n---\n\n".join(context_parts)
        # Apply safety sanitization
        clean_context = GuardrailEngine.sanitize_pii(full_context)
        return clean_context, citations
