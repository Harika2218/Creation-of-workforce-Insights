"""
Data Extraction Module for AI/ML Pipeline
-----------------------------------------
Extracts raw documents from MongoDB collections into clean pandas DataFrames.
Ensures no protected attributes (gender, DOB, address) are exposed to models.
"""

from typing import Dict, Any, List
import pandas as pd
from database.mongodb import get_db

class DataExtractor:
    def __init__(self):
        self.db = get_db()

    def get_employees(self) -> pd.DataFrame:
        """
        Extracts employee base data excluding sensitive/protected characteristics.
        """
        projection = {
            "_id": 0,
            "employee_id": 1,
            "first_name": 1,
            "last_name": 1,
            "department_id": 1,
            "designation": 1,
            "location_id": 1,
            "salary": 1,
            "experience": 1,
            "joining_date": 1,
            "employment_status": 1,
            "role": 1,
            "manager_id": 1,
        }
        docs = list(self.db.employees.find({}, projection))
        df = pd.DataFrame(docs)
        if not df.empty and "joining_date" in df.columns:
            df["joining_date"] = pd.to_datetime(df["joining_date"])
        return df

    def get_attendance(self) -> pd.DataFrame:
        """
        Extracts full historical attendance logs.
        """
        projection = {
            "_id": 0,
            "attendance_id": 1,
            "employee_id": 1,
            "date": 1,
            "check_in": 1,
            "check_out": 1,
            "attendance_status": 1,
            "attendance_method": 1,
            "location_id": 1,
            "late_minutes": 1,
            "overtime_hours": 1,
            "shift_id": 1,
            "anomaly_flag": 1,
        }
        docs = list(self.db.attendance.find({}, projection))
        df = pd.DataFrame(docs)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def get_leaves(self) -> pd.DataFrame:
        """
        Extracts leave requests.
        """
        projection = {
            "_id": 0,
            "leave_id": 1,
            "employee_id": 1,
            "leave_type": 1,
            "start_date": 1,
            "end_date": 1,
            "days_count": 1,
            "status": 1,
            "created_at": 1,
        }
        docs = list(self.db.leave_requests.find({}, projection))
        df = pd.DataFrame(docs)
        if not df.empty:
            df["start_date"] = pd.to_datetime(df["start_date"])
            df["created_at"] = pd.to_datetime(df["created_at"])
        return df

    def get_performance(self) -> pd.DataFrame:
        """
        Extracts performance appraisals.
        """
        projection = {
            "_id": 0,
            "review_id": 1,
            "employee_id": 1,
            "kpi_score": 1,
            "goal_completion": 1,
            "productivity_score": 1,
            "performance_rating": 1,
            "review_date": 1,
        }
        docs = list(self.db.performance_reviews.find({}, projection))
        df = pd.DataFrame(docs)
        if not df.empty and "review_date" in df.columns:
            df["review_date"] = pd.to_datetime(df["review_date"])
        return df

    def get_timesheets(self) -> pd.DataFrame:
        """
        Extracts timesheet entries.
        """
        projection = {
            "_id": 0,
            "timesheet_id": 1,
            "employee_id": 1,
            "project_id": 1,
            "date": 1,
            "hours_worked": 1,
            "billable_hours": 1,
            "non_billable_hours": 1,
            "status": 1,
        }
        docs = list(self.db.timesheets.find({}, projection))
        df = pd.DataFrame(docs)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def get_skills_and_training(self) -> Dict[str, pd.DataFrame]:
        """
        Extracts skills, employee_skills, and training programs.
        """
        emp_skills = pd.DataFrame(list(self.db.employee_skills.find({}, {"_id": 0})))
        skills = pd.DataFrame(list(self.db.skills.find({}, {"_id": 0})))
        training_programs = pd.DataFrame(list(self.db.training_programs.find({}, {"_id": 0})))
        employee_training = pd.DataFrame(list(self.db.employee_training.find({}, {"_id": 0})))
        return {
            "employee_skills": emp_skills,
            "skills": skills,
            "training_programs": training_programs,
            "employee_training": employee_training,
        }

    def get_projects(self) -> pd.DataFrame:
        """
        Extracts enterprise project data.
        """
        docs = list(self.db.projects.find({}, {"_id": 0}))
        return pd.DataFrame(docs)

    def get_departments(self) -> pd.DataFrame:
        """
        Extracts department records.
        """
        docs = list(self.db.departments.find({}, {"_id": 0}))
        return pd.DataFrame(docs)
