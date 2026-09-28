"""
Employee Attrition Risk Prediction Model
----------------------------------------
Estimates retention/attrition risk using Gradient Boosting.
Provides top contributing factors and risk banding (Low, Medium, High).
Decision-support signal only; does not declare certainty.
"""

from typing import Dict, Any, List, Optional
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

class AttritionModel:
    VERSION = "attrition_v1.0.0"

    FEATURE_COLS = [
        "tenure_years",
        "attendance_rate",
        "total_overtime_hours",
        "avg_late_minutes",
        "kpi_score",
        "goal_completion",
        "productivity_score",
        "salary_log",
        "experience_years",
        "leave_days_taken",
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=4,
            random_state=42
        )
        self.is_fitted = False
        self.feature_importances: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {}

    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        if data.empty or "target_attrition" not in data.columns:
            raise ValueError("Training data must contain 'target_attrition' column and features.")

        X = data[self.FEATURE_COLS].copy()
        y = data["target_attrition"].copy()

        # Handle class balance
        strat = y if (y.nunique() > 1 and y.value_counts().min() >= 2) else None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=strat
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.classifier.fit(X_train_scaled, y_train)
        self.is_fitted = True

        y_pred = self.classifier.predict(X_test_scaled)
        y_proba = self.classifier.predict_proba(X_test_scaled)[:, 1] if self.classifier.classes_.shape[0] > 1 else y_pred

        for col, imp in zip(self.FEATURE_COLS, self.classifier.feature_importances_):
            self.feature_importances[col] = round(float(imp), 4)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        try:
            auc = float(roc_auc_score(y_test, y_proba))
        except Exception:
            auc = 0.50

        self.metrics = {
            "model_version": self.VERSION,
            "samples_trained": len(X_train),
            "samples_tested": len(X_test),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "feature_importances": self.feature_importances,
        }
        return self.metrics

    def predict_one(self, feature_row: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_fitted:
            raise RuntimeError("Model has not been trained or loaded yet.")

        x_df = pd.DataFrame([{col: float(feature_row.get(col, 0.0)) for col in self.FEATURE_COLS}])
        x_scaled = self.scaler.transform(x_df)

        proba = float(self.classifier.predict_proba(x_scaled)[0, 1]) if self.classifier.classes_.shape[0] > 1 else 0.15
        proba = round(proba, 4)

        if proba >= 0.60:
            risk_band = "HIGH"
        elif proba >= 0.30:
            risk_band = "MEDIUM"
        else:
            risk_band = "LOW"

        # Explainable factors for this employee
        factors = []
        ot = float(feature_row.get("total_overtime_hours", 0))
        if ot > 25.0:
            factors.append(f"Elevated cumulative overtime ({ot:.1f} hrs)")
        kpi = float(feature_row.get("kpi_score", 70))
        if kpi < 65.0:
            factors.append(f"Sub-target KPI score ({kpi:.1f})")
        att = float(feature_row.get("attendance_rate", 0.95))
        if att < 0.88:
            factors.append(f"Declining attendance reliability ({att*100:.1f}%)")
        tenure = float(feature_row.get("tenure_years", 2.0))
        if tenure > 4.0:
            factors.append(f"Extended tenure in role ({tenure:.1f} yrs)")

        if not factors:
            factors = ["Workload Benchmark", "Normal Career Trajectory"]

        return {
            "prediction_id": f"ATT_PRED_{feature_row.get('employee_id', 'EMP')}",
            "employee_id": feature_row.get("employee_id", "UNKNOWN"),
            "department_id": feature_row.get("department_id", "DEP01"),
            "attrition_probability": proba,
            "risk_score": proba,
            "risk_band": risk_band,
            "risk_category": risk_band,
            "top_contributing_features": factors[:3],
            "contributing_factors": factors[:3],
            "prediction_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "last_evaluated": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "model_version": self.VERSION,
            "disclaimer": "Predictive workforce planning signal only. Not proof of employee intent to leave."
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "classifier": self.classifier,
            "is_fitted": self.is_fitted,
            "feature_importances": self.feature_importances,
            "metrics": self.metrics,
            "version": self.VERSION,
        }, filepath)

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at: {filepath}")
        bundle = joblib.load(filepath)
        self.scaler = bundle["scaler"]
        self.classifier = bundle["classifier"]
        self.is_fitted = bundle["is_fitted"]
        self.feature_importances = bundle["feature_importances"]
        self.metrics = bundle.get("metrics", {})
