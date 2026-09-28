"""
Chatbot Authorization Engine
----------------------------
Enforces strict Role-Based Access Control (RBAC) and data-scoping BEFORE
any database query or data retrieval occurs.
Never relies on the LLM to filter unauthorized records.
"""

from typing import Dict, Any, Tuple, Optional, List
import re
from database.mongodb import get_db

class AuthorizationGate:
    """
    Evaluates whether the authenticated user has permission to view the requested data.
    """

    @classmethod
    def check_authorization(
        cls,
        current_user: Dict[str, Any],
        intent: str,
        query: str
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validates access rights before retrieval.
        Returns:
            (is_authorized, denial_reason, scoped_params)
        """
        role = current_user.get("role", "EMPLOYEE").upper()
        emp_id = current_user.get("employee_id")
        user_id = current_user.get("user_id")
        db = get_db()

        scoped_params: Dict[str, Any] = {
            "role": role,
            "employee_id": emp_id,
            "user_id": user_id,
            "target_employee_id": emp_id,  # Default to self
            "target_department_id": None,
            "team_employee_ids": []
        }

        # Retrieve manager team IDs if applicable
        if role in ["MANAGER", "ADMIN", "HR"] and emp_id:
            team_cursor = db.employees.find({"manager_id": emp_id}, {"employee_id": 1, "_id": 0})
            scoped_params["team_employee_ids"] = [e["employee_id"] for e in team_cursor]

        q_lower = query.lower()

        # Check for explicit other-employee ID mentions (e.g., EMP002, EMP050, EMP001)
        mentioned_emps = re.findall(r"\bEMP\d{3}\b", query, re.IGNORECASE)
        other_emps = [e.upper() for e in mentioned_emps if e.upper() != emp_id]

        # Check for aggregate broad salary or unauthorized data requests
        is_asking_all_salaries = any(
            phrase in q_lower for phrase in [
                "everyone's salary", "everyones salary", "all salaries", "all employee salary",
                "show salaries", "company payroll", "salary list", "reveal salaries", "another employee's salary",
                "other employees salary", "other employee salary"
            ]
        )

        # -------------------------------------------------------------
        # 1. Employee Role Rules
        # -------------------------------------------------------------
        if role == "EMPLOYEE":
            # Rule 1A: Attempting to query everyone's salary or other employee's salary
            if is_asking_all_salaries:
                return False, (
                    "Access Denied: You are not authorized to view organization-wide payroll records. "
                    "Employees may only view their own personal compensation and payslips."
                ), scoped_params

            # Rule 1B: Attempting to query specific other employee
            if other_emps:
                return False, (
                    f"Access Denied: You are not authorized to view records for other employees ({', '.join(other_emps)}). "
                    "You may only inquire about your own employment details."
                ), scoped_params

            # Rule 1C: Attempting to access team-wide or management-exclusive intents
            if intent in ["team_attendance", "team_leave", "team_productivity", "workforce_forecast", "attrition"]:
                return False, (
                    f"Access Denied: The requested operational analytics ('{intent.replace('_', ' ').title()}') "
                    "require Manager, HR, or Administrator role privileges."
                ), scoped_params

            # Permitted: Self queries or general company policy queries
            return True, None, scoped_params

        # -------------------------------------------------------------
        # 2. Manager Role Rules
        # -------------------------------------------------------------
        elif role == "MANAGER":
            # Rule 2A: Organization-wide payroll or non-self/non-team salary
            if is_asking_all_salaries or (intent in ["payroll", "payslip"] and other_emps):
                return False, (
                    "Access Denied: Department Managers cannot view organizational payroll archives "
                    "or compensation records outside their own individual salary."
                ), scoped_params

            # Rule 2B: Querying specific other employee outside their direct team
            if other_emps:
                unmanaged = [e for e in other_emps if e not in scoped_params["team_employee_ids"]]
                if unmanaged:
                    return False, (
                        f"Access Denied: Employee(s) {', '.join(unmanaged)} do not report to your team. "
                        "You can only view records for your direct reports."
                    ), scoped_params
                # Target is in manager's team
                scoped_params["target_employee_id"] = other_emps[0]

            # Rule 2C: Organization-wide attrition prediction matrix
            if intent == "attrition" and not other_emps:
                # Scoped to manager team only
                scoped_params["scope"] = "team_only"

            return True, None, scoped_params

        # -------------------------------------------------------------
        # 3. HR & Admin Role Rules
        # -------------------------------------------------------------
        elif role in ["HR", "ADMIN"]:
            if other_emps:
                scoped_params["target_employee_id"] = other_emps[0]
            # HR and Admin have organization-wide authorized access
            return True, None, scoped_params

        # Default Deny for unknown roles
        return False, "Access Denied: Unrecognized system authorization role.", scoped_params
