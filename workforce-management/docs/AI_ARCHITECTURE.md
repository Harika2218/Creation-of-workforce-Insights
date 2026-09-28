# AI/ML WORKFORCE INTELLIGENCE ARCHITECTURE SPECIFICATION

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** AI & Machine Learning Pipeline Architecture  
**Phase:** 13 — Final Consolidation  
**Version:** 1.0  
**Machine Learning Frameworks:** Scikit-learn 1.8, NumPy 2.3, Pandas 2.3, SciPy 1.17, Joblib 1.5  

---

## 1. Executive Summary & Design Principles

The workforce intelligence layer provides predictive decision support across human capital operations. In strict adherence to engineering honesty, **the system utilizes classical statistical machine learning and ensemble models (Random Forest, Logistic Regression, Time-Series Decompositions)** rather than multi-billion parameter neural networks. This guarantees:
1. **Explainability & Interpretability:** Every attrition probability score is accompanied by quantitative feature contribution weights (e.g. commute distance, overtime hours, tenure).
2. **Deterministic Inference Velocity:** Predictions execute in sub-15ms on standard CPU hardware without GPU acceleration.
3. **Training vs. Inference Separation:** Models are pre-trained, serialized with Joblib into `/models/`, and loaded into memory at startup. Zero retraining occurs during user inference requests.

---

## 2. Predictive Pipeline Inventory

### 2.1 Attrition Risk Predictor
- **Algorithm:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`) with 100 estimators and entropy criterion.
- **Input Features (14 Dimensions):**
  - Tenure (months), Age, Distance from Office (km), Overtime Hours (last 90 days), Performance Rating (1–5), Total Working Years, Monthly Income, Years Since Last Promotion, Leave Days Used, Commute Mode, Job Satisfaction Index, Training Programs Completed.
- **Output:** Continuous probability $P(\text{Attrition}) \in [0.0, 1.0]$, risk tier classification (`LOW`, `MEDIUM`, `HIGH`), and top 3 contributing factors.
- **Artifact Location:** `models/attrition/attrition_model.joblib`.

### 2.2 Absenteeism Risk Predictor
- **Algorithm:** Logistic Regression with L2 regularization (`sklearn.linear_model.LogisticRegression`).
- **Input Features:**
  - Day of week (Monday/Friday weighting), historical unplanned sick leave frequency, consecutive shift count, recent overtime volume, commute distance.
- **Output:** Predicted unplanned absence likelihood for upcoming shift windows.
- **Artifact Location:** `models/absenteeism/absenteeism_model.joblib`.

### 2.3 Workforce Demand Forecaster
- **Algorithm:** Rolling-window statistical decomposition with trend and seasonal departmental smoothing.
- **Input:** 6-month historical attendance and timesheet billing volume by department.
- **Output:** 30-day and 90-day projected headcount demand by department, identifying upcoming staffing deficits or surplus allocations.
- **Artifact Location:** `models/workforce_forecasting/forecast_metadata.joblib`.

### 2.4 Attendance Anomaly Detector
- **Algorithm:** Multi-variate Isolation Forest (`sklearn.ensemble.IsolationForest`) combined with deterministic business rule gates.
- **Input:** Check-in time delta from shift start, check-out time delta, total daily hours, geofence radius distance.
- **Output:** Anomaly flag (`ANOMALY_CONFIRMED`), severity classification, and inclusion in the 307 cataloged anomalies.
- **Artifact Location:** `models/attendance_anomaly/anomaly_detector.joblib`.

### 2.5 Skill Gap Analysis & Training Recommender
- **Algorithm:** Vector cosine similarity and Euclidean norm distance between individual employee skill vectors and departmental benchmark profiles.
- **Output:** Radar gap differential and ranked course recommendations mapped to the enterprise `training_programs` catalog.

---

## 3. Model Storage & Lifespan Architecture

```text
Host File System (/models/)
  ├── attrition/attrition_model.joblib
  ├── absenteeism/absenteeism_model.joblib
  ├── workforce_forecasting/forecast_metadata.joblib
  └── attendance_anomaly/anomaly_detector.joblib
                  │
                  ▼ [Loaded once at FastAPI Lifespan Startup]
           AIService Memory Cache
                  │
                  ▼ [Sub-15ms In-Memory Inference]
        FastAPI /api/v1/ai Routers
```

- **Fairness & Bias Controls:** Demographics such as gender, religion, marital status, and ethnicity are strictly excluded from feature extraction vectors to prevent algorithmic discrimination.
- **Fallback Behavior:** If model artifact files are missing or unreadable, `AIService` falls back gracefully to deterministic rule-based heuristic scoring, and `/api/v1/health/ready` reports status `degraded` without crashing the application.
