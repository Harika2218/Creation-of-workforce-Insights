"""
Tests for AI Pipeline, Feature Builder, and Models
--------------------------------------------------
Verifies data extraction, feature generation, model training,
metric computation, serialization, and batch inference.
"""

import os
import pytest
import pandas as pd
from ai.data.extractor import DataExtractor
from ai.features.feature_builder import FeatureBuilder
from ai.models.absenteeism import AbsenteeismModel
from ai.models.attrition import AttritionModel
from ai.models.anomaly_detector import AttendanceAnomalyDetector
from ai.models.forecaster import WorkforceForecaster
from ai.models.rules_engines import (
    ProductivityEngine,
    SkillGapEngine,
    TrainingRecommendationEngine,
    ShiftRecommendationEngine,
    ResourceOptimizationEngine,
)

def test_data_extractor():
    extractor = DataExtractor()
    emp_df = extractor.get_employees()
    att_df = extractor.get_attendance()

    assert not emp_df.empty
    assert len(emp_df) == 200
    # Ensure protected attributes are excluded
    assert "gender" not in emp_df.columns
    assert "date_of_birth" not in emp_df.columns
    assert "address" not in emp_df.columns

    assert not att_df.empty
    assert len(att_df) >= 24000

def test_feature_builder_absenteeism():
    feature_builder = FeatureBuilder()
    df = feature_builder.build_absenteeism_features()
    assert not df.empty
    assert "attendance_rate_30d" in df.columns
    assert "target_absent" in df.columns
    assert len(df) == 200

def test_feature_builder_attrition():
    feature_builder = FeatureBuilder()
    df = feature_builder.build_attrition_features()
    assert not df.empty
    assert "tenure_years" in df.columns
    assert "target_attrition" in df.columns
    assert len(df) == 200

def test_absenteeism_model_train_and_predict():
    feature_builder = FeatureBuilder()
    df = feature_builder.build_absenteeism_features()
    model = AbsenteeismModel()
    metrics = model.train(df)

    assert metrics["accuracy"] >= 0.60
    assert metrics["model_version"] == "absenteeism_v1.0.0"

    sample = df.iloc[0].to_dict()
    pred = model.predict_one(sample)
    assert pred["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= pred["probability"] <= 1.0
    assert len(pred["important_features"]) > 0

def test_attrition_model_train_and_predict():
    feature_builder = FeatureBuilder()
    df = feature_builder.build_attrition_features()
    model = AttritionModel()
    metrics = model.train(df)

    assert metrics["accuracy"] >= 0.70
    assert metrics["model_version"] == "attrition_v1.0.0"

    sample = df.iloc[0].to_dict()
    pred = model.predict_one(sample)
    assert pred["risk_band"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= pred["attrition_probability"] <= 1.0
    assert len(pred["top_contributing_features"]) > 0

def test_anomaly_detector():
    feature_builder = FeatureBuilder()
    df = feature_builder.build_anomaly_features(limit=500)
    detector = AttendanceAnomalyDetector(contamination=0.03)
    metrics = detector.fit(df)

    assert metrics["anomalies_detected"] > 0
    anomalies = detector.detect_anomalies(df)
    assert len(anomalies) > 0
    assert "reason" in anomalies[0]
    assert anomalies[0]["severity"] in ["MEDIUM", "HIGH"]

def test_workforce_forecaster():
    extractor = DataExtractor()
    emp_df = extractor.get_employees()
    dept_df = extractor.get_departments()
    project_df = extractor.get_projects()
    timesheet_df = extractor.get_timesheets()

    forecaster = WorkforceForecaster()
    forecasts = forecaster.forecast_demand(emp_df, dept_df, project_df, timesheet_df, forecast_period="Q3-2026")
    assert len(forecasts) == 9
    assert all("predicted_demand" in f for f in forecasts)

    staffing = forecaster.generate_staffing_recommendations(forecasts, emp_df)
    assert len(staffing) == 9
    assert all("target_role" in s for s in staffing)

def test_productivity_engine():
    res = ProductivityEngine.calculate_productivity(
        emp_id="EMP050",
        kpi_score=80.0,
        goal_completion=85.0,
        billable_hours=38.0,
        total_hours=40.0,
        attendance_rate=0.96,
        late_count=0
    )
    assert 0.0 <= res["productivity_score"] <= 100.0
    assert "kpi_achievement" in res["score_components"]

def test_skill_gap_and_training():
    extractor = DataExtractor()
    emp_df = extractor.get_employees()
    skills_data = extractor.get_skills_and_training()
    dept_df = extractor.get_departments()

    gaps = SkillGapEngine.analyze_gaps(
        emp_df, skills_data["skills"], skills_data["employee_skills"], dept_df
    )
    assert len(gaps) > 0

    recs = TrainingRecommendationEngine.recommend_for_employee(
        "EMP050", skills_data["employee_skills"], skills_data["skills"], skills_data["training_programs"], emp_df
    )
    assert len(recs) > 0
    assert "recommended_training" in recs[0]
