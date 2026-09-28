"""
End-to-End Model Training Pipeline
----------------------------------
Extracts live enterprise data, engineers features, trains all machine learning models,
computes validation metrics, and serializes trained artifacts with versioning into models/.

Usage:
    python -m ai.training.train_all
"""

import os
import sys
import json
import pandas as pd

from ai.data.extractor import DataExtractor
from ai.features.feature_builder import FeatureBuilder
from ai.models.absenteeism import AbsenteeismModel
from ai.models.attrition import AttritionModel
from ai.models.anomaly_detector import AttendanceAnomalyDetector
from ai.models.forecaster import WorkforceForecaster
from ai.evaluation.evaluator import ModelEvaluator

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")

def run_training_pipeline():
    print("=" * 70)
    print("HRVANTAGE AI/ML WORKFORCE INTELLIGENCE — MODEL TRAINING PIPELINE")
    print("=" * 70)

    extractor = DataExtractor()
    feature_builder = FeatureBuilder(extractor)
    evaluator = ModelEvaluator(MODELS_DIR)

    metrics_map = {}

    # -------------------------------------------------------------
    # 1. Model 1: Predictive Absenteeism
    # -------------------------------------------------------------
    print("\n[1/4] Training Predictive Absenteeism Model (Random Forest)...")
    absenteeism_df = feature_builder.build_absenteeism_features()
    if not absenteeism_df.empty:
        abs_model = AbsenteeismModel()
        abs_metrics = abs_model.train(absenteeism_df)
        save_path = os.path.join(MODELS_DIR, "absenteeism", "model.joblib")
        abs_model.save(save_path)
        metrics_map["absenteeism"] = abs_metrics
        print(f"      Trained on {abs_metrics['samples_trained']} samples (Tested: {abs_metrics['samples_tested']})")
        print(f"      Accuracy: {abs_metrics['accuracy']:.4f}, F1-Score: {abs_metrics['f1_score']:.4f}, ROC-AUC: {abs_metrics['roc_auc']:.4f}")
        print(f"      Model artifact saved to: {save_path}")
    else:
        print("      [WARN] Insufficient attendance data for absenteeism feature generation.")

    # -------------------------------------------------------------
    # 2. Model 2: Attrition Prediction
    # -------------------------------------------------------------
    print("\n[2/4] Training Employee Attrition Model (Gradient Boosting)...")
    attrition_df = feature_builder.build_attrition_features()
    if not attrition_df.empty:
        att_model = AttritionModel()
        att_metrics = att_model.train(attrition_df)
        save_path = os.path.join(MODELS_DIR, "attrition", "model.joblib")
        att_model.save(save_path)
        metrics_map["attrition"] = att_metrics
        print(f"      Trained on {att_metrics['samples_trained']} samples (Tested: {att_metrics['samples_tested']})")
        print(f"      Accuracy: {att_metrics['accuracy']:.4f}, F1-Score: {att_metrics['f1_score']:.4f}, ROC-AUC: {att_metrics['roc_auc']:.4f}")
        print(f"      Model artifact saved to: {save_path}")
    else:
        print("      [WARN] Insufficient data for attrition feature generation.")

    # -------------------------------------------------------------
    # 3. Model 3: Attendance Anomaly Detection (Isolation Forest)
    # -------------------------------------------------------------
    print("\n[3/4] Fitting Attendance Anomaly Detector (Isolation Forest)...")
    anomaly_df = feature_builder.build_anomaly_features(limit=5000)
    if not anomaly_df.empty:
        anom_model = AttendanceAnomalyDetector(contamination=0.03)
        anom_metrics = anom_model.fit(anomaly_df)
        save_path = os.path.join(MODELS_DIR, "attendance_anomaly", "model.joblib")
        anom_model.save(save_path)
        metrics_map["attendance_anomaly"] = anom_metrics
        print(f"      Evaluated {anom_metrics['total_records_analyzed']} attendance records.")
        print(f"      Anomalies Detected: {anom_metrics['anomalies_detected']} (Rate: {anom_metrics['anomaly_rate']*100:.2f}%)")
        print(f"      Model artifact saved to: {save_path}")
    else:
        print("      [WARN] Insufficient data for anomaly detection.")

    # -------------------------------------------------------------
    # 4. Model 4: Workforce Forecasting & Staffing Capacity
    # -------------------------------------------------------------
    print("\n[4/4] Generating Workforce Demand Forecast Models...")
    emp_df = extractor.get_employees()
    dept_df = extractor.get_departments()
    project_df = extractor.get_projects()
    timesheet_df = extractor.get_timesheets()

    forecaster = WorkforceForecaster()
    forecasts = forecaster.forecast_demand(emp_df, dept_df, project_df, timesheet_df, forecast_period="Q3-2026")
    meta_path = os.path.join(MODELS_DIR, "workforce_forecasting", "forecast_metadata.json")
    forecaster.save_metadata(meta_path)
    metrics_map["workforce_forecasting"] = {
        "model_version": forecaster.VERSION,
        "departments_forecasted": len(forecasts),
        "target_period": "Q3-2026",
        "methodology": "Exponential Smoothing & Project Pipeline Scaling",
    }
    print(f"      Forecasted demand across {len(forecasts)} departments for Q3-2026.")
    print(f"      Metadata saved to: {meta_path}")

    # -------------------------------------------------------------
    # 5. Compile Model Registry & Metadata
    # -------------------------------------------------------------
    registry = evaluator.compile_model_registry(metrics_map)
    print("\n" + "=" * 70)
    print("ALL MODELS TRAINED AND METADATA SERIALIZED SUCCESSFULLY!")
    print(f"Model Registry Written to: {os.path.join(MODELS_DIR, 'model_metadata.json')}")
    print("=" * 70)

if __name__ == "__main__":
    run_training_pipeline()
