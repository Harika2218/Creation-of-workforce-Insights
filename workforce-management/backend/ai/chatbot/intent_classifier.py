"""
Intent Classification & Context Resolution Engine
--------------------------------------------------
Identifies the primary user intent, determines target retrieval mechanisms
(MongoDB vs. RAG Document vs. AI/ML vs. Multi-Source), and rewrites follow-up queries.
"""

from typing import Dict, Any, List, Optional
import re

class IntentClassifier:
    """
    Classifies user natural language inputs into structured HR intents.
    """

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        # Leave Intents
        "leave_balance": ["leave balance", "remaining leave", "how many leaves", "days of leave", "leave days left", "vacation days left", "sick leave balance", "casual leave balance"],
        "leave_policy": ["leave policy", "maternity leave", "paternity leave", "bereavement leave", "sick leave policy", "annual leave policy", "casual leave policy", "comp off policy", "encash leave", "carry forward"],
        "leave_request": ["apply for leave", "how to apply leave", "request leave", "submit leave", "take time off"],
        "leave_status": ["leave status", "leave approved", "leave rejected", "pending leave", "status of my leave"],

        # Attendance & Punctuality
        "attendance_history": ["my attendance", "attendance record", "attendance history", "clock in record", "punch in history", "check in time"],
        "attendance_summary": ["attendance summary", "attendance rate", "hours worked this month", "punctuality", "grace period", "late arrival policy"],

        # Shifts
        "shift_information": ["my shift", "next shift", "shift timing", "scheduled shift", "night shift", "shift roster", "what shift"],
        "shift_swap": ["shift swap", "swap shift", "exchange shift", "trade shift"],

        # Timesheets
        "timesheet": ["timesheet", "billable hours", "hours logged", "project hours", "submit timesheet"],

        # Payroll & Compensation
        "payroll": ["salary", "payroll", "compensation", "pay check", "how much do i earn", "ctc", "basic pay", "hra", "allowance"],
        "payslip": ["payslip", "pay slip", "download payslip", "salary slip", "march payslip"],

        # Performance
        "performance": ["performance review", "kpi", "performance rating", "appraisal", "goal completion", "pip", "performance improvement plan"],

        # Skills & Training
        "training": ["training program", "courses", "upskilling", "certification reimbursement", "l&d budget", "learning development"],
        "skills": ["my skills", "skill profile", "competencies", "endorsed skills"],

        # Profile
        "employee_profile": ["my profile", "designation", "manager", "department", "employee id", "who is my manager"],

        # Manager Team Scoped
        "team_attendance": ["team attendance", "who is absent", "employees absent", "absent today", "my team absent", "team clock in"],
        "team_leave": ["team leave", "pending leave requests", "leaves pending approval", "who is on leave"],
        "team_productivity": ["team productivity", "team utilization", "workforce utilization", "team billable"],

        # Phase 5 AI/ML Workforce Intelligence
        "workforce_forecast": ["workforce forecast", "headcount forecast", "projected demand", "hiring forecast", "demand forecast", "headcount need"],
        "attrition": ["attrition", "attrition risk", "retention risk", "turnover risk", "who might leave"],
        "skill_gap": ["skill gap", "competency gap", "skills missing", "department skill gap", "skill matrix"],

        # General Policy & FAQs
        "hr_policy": ["remote work policy", "wfh policy", "hybrid policy", "code of conduct", "posh", "sexual harassment", "ethics policy", "notice period", "resignation policy", "insurance policy", "mediclaim"],
        "general_hr_question": ["how to", "who to contact", "hr contact", "office address", "holiday", "calendar", "faq"]
    }

    # Resource Routing Map
    INTENT_RESOURCE_TYPE = {
        "leave_balance": "mongodb",
        "leave_status": "mongodb",
        "attendance_history": "mongodb",
        "attendance_summary": "mongodb",
        "shift_information": "mongodb",
        "timesheet": "mongodb",
        "payroll": "mongodb",
        "payslip": "mongodb",
        "performance": "mongodb",
        "skills": "mongodb",
        "employee_profile": "mongodb",
        "team_attendance": "mongodb",
        "team_leave": "mongodb",
        "team_productivity": "mongodb",

        "leave_policy": "rag_document",
        "leave_request": "rag_document",
        "shift_swap": "rag_document",
        "training": "multi_source",
        "hr_policy": "rag_document",
        "general_hr_question": "rag_document",

        "workforce_forecast": "ai_ml",
        "attrition": "ai_ml",
        "skill_gap": "ai_ml",
    }

    @classmethod
    def classify_intent(cls, query: str) -> Dict[str, Any]:
        """
        Analyzes query text and returns intent classification and target resource origin.
        """
        q_lower = query.lower()

        # Score matching intents
        best_intent = "unknown"
        highest_score = 0

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in q_lower:
                    # Multi-word match receives higher weight
                    score += len(kw.split()) * 2
            if score > highest_score:
                highest_score = score
                best_intent = intent

        # Fallback heuristic if unknown
        if best_intent == "unknown":
            if any(w in q_lower for w in ["policy", "rules", "guideline", "allowed", "handbook", "posh", "conduct", "notice"]):
                best_intent = "hr_policy"
            elif any(w in q_lower for w in ["leave", "vacation", "off"]):
                best_intent = "leave_policy"
            elif any(w in q_lower for w in ["predict", "forecast", "future", "risk"]):
                best_intent = "workforce_forecast"
            elif any(w in q_lower for w in ["who", "what", "where", "how", "when", "why"]):
                best_intent = "general_hr_question"

        resource_type = cls.INTENT_RESOURCE_TYPE.get(best_intent, "rag_document")

        return {
            "intent": best_intent,
            "confidence": 0.95 if highest_score > 0 else 0.60,
            "resource_type": resource_type
        }

    @classmethod
    def resolve_follow_up_context(cls, current_query: str, last_message_content: Optional[str], last_intent: Optional[str]) -> str:
        """
        Resolves pronouns or elliptical follow-ups using conversation history.
        E.g. If previous topic was 'leave_balance' and user asks 'Can I use it next month?',
        rewrites context to 'Can I use my remaining leave balance next month under the leave policy?'.
        """
        if not last_intent or not last_message_content:
            return current_query

        q_lower = current_query.lower()
        pronouns = ["it", "them", "those", "that", "this", "my team"]

        has_pronoun = any(re.search(rf"\b{p}\b", q_lower) for p in pronouns)
        is_short = len(current_query.split()) <= 6

        if has_pronoun or is_short:
            if last_intent in ["leave_balance", "leave_policy"]:
                return f"{current_query} (Context: Regarding annual leave balance and leave carry-over / application policy)"
            elif last_intent in ["attendance_history", "team_attendance"]:
                return f"{current_query} (Context: Regarding attendance records and attendance policy)"
            elif last_intent in ["payroll", "payslip"]:
                return f"{current_query} (Context: Regarding salary components and payslip policy)"
            elif last_intent in ["shift_information"]:
                return f"{current_query} (Context: Regarding work shifts and shift swap rules)"
            elif last_intent in ["workforce_forecast", "skill_gap"]:
                return f"{current_query} (Context: Regarding workforce planning and department skill gaps)"

        return current_query
