"""
Controlled MongoDB and Phase 5 AI Data Retriever
------------------------------------------------
Performs scoped, minimal, projection-filtered queries to existing MongoDB collections
and integrates Phase 5 AI workforce intelligence service models.
Excludes passwords, personal phone numbers, and addresses.
"""

from typing import Dict, Any, List, Optional
from database.mongodb import get_db
from backend.services.ai_service import AIService

class ScopedDataRetriever:
    """
    Retrieves authorized enterprise records strictly according to permission scope.
    """

    def __init__(self):
        self.db = get_db()

    def retrieve_mongodb_data(self, intent: str, scoped_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes targeted MongoDB query matching intent and authorized scope.
        """
        emp_id = scoped_params.get("target_employee_id") or scoped_params.get("employee_id")
        team_ids = scoped_params.get("team_employee_ids", [])
        role = scoped_params.get("role", "EMPLOYEE")

        data: Dict[str, Any] = {"context_type": "database_record"}

        # -------------------------------------------------------------
        # 1. Leave Balances & Requests
        # -------------------------------------------------------------
        if intent == "leave_balance":
            balances = list(self.db.leave_balances.find({"employee_id": emp_id}, {"_id": 0}))
            data["leave_balances"] = balances
            data["employee_id"] = emp_id

        elif intent == "leave_status":
            requests = list(self.db.leave_requests.find({"employee_id": emp_id}, {"_id": 0}).sort("applied_on", -1).limit(5))
            data["recent_leave_requests"] = requests
            data["employee_id"] = emp_id

        # -------------------------------------------------------------
        # 2. Attendance & Punctuality
        # -------------------------------------------------------------
        elif intent in ["attendance_history", "attendance_summary"]:
            records = list(self.db.attendance.find({"employee_id": emp_id}, {"_id": 0}).sort("date", -1).limit(7))
            total_days = self.db.attendance.count_documents({"employee_id": emp_id})
            present_days = self.db.attendance.count_documents({"employee_id": emp_id, "status": "Present"})
            late_days = self.db.attendance.count_documents({"employee_id": emp_id, "late_minutes": {"$gt": 15}})

            data["recent_attendance"] = records
            data["summary_stats"] = {
                "total_recorded_days": total_days,
                "present_days": present_days,
                "late_arrivals": late_days,
                "attendance_rate": f"{round((present_days / max(total_days, 1)) * 100, 1)}%"
            }
            data["employee_id"] = emp_id

        # -------------------------------------------------------------
        # 3. Shifts & Schedules
        # -------------------------------------------------------------
        elif intent == "shift_information":
            current_shift = self.db.employee_shifts.find_one({"employee_id": emp_id, "status": "Active"}, {"_id": 0})
            if current_shift:
                shift_details = self.db.shifts.find_one({"shift_id": current_shift.get("shift_id")}, {"_id": 0})
                data["assigned_shift"] = {
                    "shift_id": current_shift.get("shift_id"),
                    "shift_name": shift_details.get("name") if shift_details else "Standard Shift",
                    "start_time": shift_details.get("start_time") if shift_details else "09:00",
                    "end_time": shift_details.get("end_time") if shift_details else "18:00",
                    "effective_from": current_shift.get("effective_from")
                }
            else:
                data["assigned_shift"] = {
                    "shift_name": "General Shift",
                    "start_time": "09:00",
                    "end_time": "18:00",
                    "note": "Standard office roster"
                }

        # -------------------------------------------------------------
        # 4. Timesheets
        # -------------------------------------------------------------
        elif intent == "timesheet":
            ts_list = list(self.db.timesheets.find({"employee_id": emp_id}, {"_id": 0}).sort("date", -1).limit(5))
            data["recent_timesheets"] = ts_list
            data["employee_id"] = emp_id

        # -------------------------------------------------------------
        # 5. Payroll & Payslips
        # -------------------------------------------------------------
        elif intent in ["payroll", "payslip"]:
            pay_records = list(self.db.payroll_records.find({"employee_id": emp_id}, {"_id": 0}).sort("pay_period", -1).limit(3))
            data["payroll_history"] = pay_records
            data["employee_id"] = emp_id

        # -------------------------------------------------------------
        # 6. Performance & Goals
        # -------------------------------------------------------------
        elif intent == "performance":
            reviews = list(self.db.performance_reviews.find({"employee_id": emp_id}, {"_id": 0}).sort("cycle", -1).limit(2))
            goals = list(self.db.employee_goals.find({"employee_id": emp_id}, {"_id": 0}))
            data["performance_reviews"] = reviews
            data["goals"] = goals
            data["employee_id"] = emp_id

        # -------------------------------------------------------------
        # 7. Employee Profile
        # -------------------------------------------------------------
        elif intent == "employee_profile":
            emp = self.db.employees.find_one(
                {"employee_id": emp_id},
                {
                    "_id": 0, "first_name": 1, "last_name": 1, "employee_id": 1,
                    "department_id": 1, "designation": 1, "joining_date": 1,
                    "employment_type": 1, "employment_status": 1, "manager_id": 1
                }
            )
            data["profile"] = emp

        # -------------------------------------------------------------
        # 8. Manager Team Scoped Queries
        # -------------------------------------------------------------
        elif intent == "team_attendance":
            # Count absent/present in managed team
            if team_ids:
                today_cursor = list(self.db.attendance.find({"employee_id": {"$in": team_ids}}, {"_id": 0}).sort("date", -1).limit(len(team_ids)))
                # Count status
                present_count = sum(1 for a in today_cursor if a.get("status") == "Present")
                absent_count = len(team_ids) - present_count
                absent_names = []
                for a in today_cursor:
                    if a.get("status") != "Present":
                        emp_info = self.db.employees.find_one({"employee_id": a["employee_id"]}, {"first_name": 1, "last_name": 1, "_id": 0})
                        if emp_info:
                            absent_names.append(f"{emp_info['first_name']} {emp_info['last_name']} ({a['employee_id']})")

                data["team_attendance"] = {
                    "total_team_members": len(team_ids),
                    "present_count": present_count,
                    "absent_count": max(absent_count, 0),
                    "absent_employees": absent_names
                }
            else:
                data["team_attendance"] = {
                    "total_team_members": 0,
                    "present_count": 0,
                    "absent_count": 0,
                    "absent_employees": []
                }

        elif intent == "team_leave":
            if team_ids:
                pending_leaves = list(self.db.leave_requests.find(
                    {"employee_id": {"$in": team_ids}, "status": "Pending"},
                    {"_id": 0}
                ))
                data["pending_team_leaves"] = pending_leaves
            else:
                data["pending_team_leaves"] = []

        return data

    def retrieve_ai_analytics(self, intent: str, scoped_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetches authorized predictions and decision support from Phase 5 AI models.
        """
        emp_id = scoped_params.get("target_employee_id") or scoped_params.get("employee_id")
        role = scoped_params.get("role", "EMPLOYEE")
        data: Dict[str, Any] = {"context_type": "ai_prediction"}

        if intent == "workforce_forecast":
            forecasts = AIService.get_workforce_forecasts(period="Q3-2026")
            staffing = AIService.get_staffing_recommendations()
            data["workforce_forecasts"] = forecasts[:5]
            data["staffing_recommendations"] = staffing[:5]

        elif intent == "attrition":
            if role in ["HR", "ADMIN"]:
                attr_data = AIService.get_attrition()
                high_risk = [a for a in attr_data if (a.get("risk_band") or a.get("risk_category")) == "HIGH"]
                data["total_evaluated"] = len(attr_data)
                data["high_attrition_count"] = len(high_risk)
                data["sample_high_risk"] = high_risk[:4]
            else:
                # Scoped to self
                single_attr = AIService.get_attrition(employee_id=emp_id)
                data["employee_attrition_risk"] = single_attr[0] if single_attr else {}

        elif intent == "skill_gap":
            gaps = AIService.get_skill_gaps(priority="HIGH")
            data["high_priority_skill_gaps"] = gaps[:6]
            if emp_id:
                recs = AIService.get_training_recommendations(employee_id=emp_id)
                data["personal_training_recommendations"] = recs[:3]

        return data
