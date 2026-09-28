"""
Attendance Anomaly Detection Model
----------------------------------
Unsupervised anomaly detection using scikit-learn's IsolationForest.
Detects unusual check-in times, extreme work hours, and erratic patterns,
with explainable root-cause attribution.
"""

from typing import Dict, Any, List, Optional
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AttendanceAnomalyDetector:
    VERSION = "anomaly_iforest_v1.0.0"

    FEATURE_COLS = [
        "in_mins",
        "out_mins",
        "work_duration",
        "late_minutes",
        "overtime_hours",
    ]

    def __init__(self, contamination: float = 0.03):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.detector = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        self.is_fitted = False
        self.metrics: Dict[str, Any] = {}

    def fit(self, data: pd.DataFrame) -> Dict[str, Any]:
        if data.empty:
            raise ValueError("Training data for anomaly detector cannot be empty.")

        X = data[self.FEATURE_COLS].copy().fillna(0)
        X_scaled = self.scaler.fit_transform(X)

        self.detector.fit(X_scaled)
        self.is_fitted = True

        scores = self.detector.score_samples(X_scaled)
        preds = self.detector.predict(X_scaled) # -1 for anomaly, 1 for normal
        anomaly_count = int((preds == -1).sum())

        self.metrics = {
            "model_version": self.VERSION,
            "total_records_analyzed": len(data),
            "anomalies_detected": anomaly_count,
            "anomaly_rate": round(anomaly_count / len(data), 4),
            "contamination_threshold": self.contamination,
            "mean_anomaly_score": round(float(scores.mean()), 4),
        }
        return self.metrics

    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Runs batch anomaly scoring and generates human-readable explanations.
        """
        if not self.is_fitted:
            raise RuntimeError("Anomaly detector model has not been fitted or loaded.")

        X = data[self.FEATURE_COLS].copy().fillna(0)
        X_scaled = self.scaler.transform(X)

        raw_scores = self.detector.score_samples(X_scaled)
        preds = self.detector.predict(X_scaled)

        anomalies = []
        for idx, (is_anom, score) in enumerate(zip(preds, raw_scores)):
            if is_anom == -1: # Anomaly flagged
                row = data.iloc[idx]
                reasons = []

                # Explainable heuristics
                late = float(row.get("late_minutes", 0))
                ot = float(row.get("overtime_hours", 0))
                dur = float(row.get("work_duration", 0))
                in_m = float(row.get("in_mins", 540))

                if late > 60:
                    reasons.append(f"Excessive late arrival ({late:.0f} mins past shift)")
                if ot > 3.0:
                    reasons.append(f"Unusual high overtime ({ot:.1f} hrs in single shift)")
                if dur > 12.0:
                    reasons.append(f"Prolonged shift duration ({dur:.1f} hrs)")
                elif dur < 3.0:
                    reasons.append(f"Abnormally brief shift duration ({dur:.1f} hrs)")
                if in_m < 360: # before 6 AM
                    reasons.append(f"Irregular early check-in ({in_m/60:.1f} hrs from midnight)")

                if not reasons:
                    reasons.append("Unusual multidimensional check-in / check-out cluster deviation")

                anomalies.append({
                    "anomaly_id": f"ANO_{row.get('attendance_id', idx)}",
                    "attendance_id": row.get("attendance_id", f"ATT_{idx}"),
                    "employee_id": row.get("employee_id", "EMP_UNKNOWN"),
                    "date": str(row.get("date", pd.Timestamp.now().strftime("%Y-%m-%d"))),
                    "anomaly_score": round(float(abs(score)), 4),
                    "is_anomaly": True,
                    "reason": " & ".join(reasons),
                    "severity": "HIGH" if (ot > 4 or late > 120 or dur > 14) else "MEDIUM",
                    "status": "Investigating",
                    "detected_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model_version": self.VERSION,
                })

        return anomalies

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "detector": self.detector,
            "contamination": self.contamination,
            "is_fitted": self.is_fitted,
            "metrics": self.metrics,
            "version": self.VERSION,
        }, filepath)

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Anomaly model not found at: {filepath}")
        bundle = joblib.load(filepath)
        self.scaler = bundle["scaler"]
        self.detector = bundle["detector"]
        self.contamination = bundle.get("contamination", 0.03)
        self.is_fitted = bundle["is_fitted"]
        self.metrics = bundle.get("metrics", {})
