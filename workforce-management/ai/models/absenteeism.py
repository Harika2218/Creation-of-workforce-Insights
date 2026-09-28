"""
Predictive Absenteeism Model
----------------------------
Estimates the probability that an employee may be absent in an upcoming period.
Uses Random Forest with balanced class weights and decision-support risk banding.
"""

from typing import Dict, Any, List, Optional
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

class AbsenteeismModel:
    VERSION = "absenteeism_v1.0.0"

    FEATURE_COLS = [
        "attendance_rate_30d",
        "late_count_30d",
        "avg_late_minutes_30d",
        "overtime_hours_30d",
        "recent_absences_30d",
        "unplanned_leaves_30d",
        "avg_duration_hours_30d",
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            class_weight="balanced",
            random_state=42
        )
        self.is_fitted = False
        self.feature_importances: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {}

    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains the Random Forest model and calculates evaluation metrics.
        """
        if data.empty or "target_absent" not in data.columns:
            raise ValueError("Training data must contain 'target_absent' column and feature columns.")

        X = data[self.FEATURE_COLS].copy()
        y = data["target_absent"].copy()

        # Check class balance
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

        # Feature importances
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
        """
        Generates probabilistic prediction for a single employee feature dict.
        """
        if not self.is_fitted:
            raise RuntimeError("Model has not been trained or loaded yet.")

        # Extract features
        x_df = pd.DataFrame([{col: float(feature_row.get(col, 0.0)) for col in self.FEATURE_COLS}])
        x_scaled = self.scaler.transform(x_df)

        proba = float(self.classifier.predict_proba(x_scaled)[0, 1]) if self.classifier.classes_.shape[0] > 1 else 0.20
        proba = round(proba, 4)

        # Risk banding: Low (< 0.30), Medium (0.30 - 0.65), High (> 0.65)
        if proba >= 0.65:
            risk_level = "HIGH"
        elif proba >= 0.30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Determine top 2 contributing features for this prediction
        contributing = []
        for col, imp in sorted(self.feature_importances.items(), key=lambda item: item[1], reverse=True)[:3]:
            val = feature_row.get(col, 0)
            contributing.append({
                "feature": col,
                "importance": imp,
                "current_value": val
            })

        return {
            "employee_id": feature_row.get("employee_id", "UNKNOWN"),
            "prediction": 1 if proba >= 0.50 else 0,
            "probability": proba,
            "risk_level": risk_level,
            "important_features": contributing,
            "prediction_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "model_version": self.VERSION,
            "disclaimer": "Probabilistic model output for workforce decision support only. Not a guarantee of absence."
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
