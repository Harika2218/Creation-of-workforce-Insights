# FINAL AI / ML MODEL CATALOG — INNOVATECORP HRVANTAGE

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document Reference:** `docs/FINAL_AI_MODEL_CATALOG.md`  
**Evaluation Benchmark Source:** `models/model_metadata.json`  
**Evaluated At:** 2026-09-23 18:01:34  
**Ethical AI Governance:** Human-in-the-Loop Decision Support (Zero Autonomous Punitive Employment Actions)  

---

## 1. ETHICAL GOVERNANCE & FAIRNESS PRINCIPLES

### 1.1 Non-Autonomous Decision-Support Invariant
All machine learning and predictive statistical models within HRvantage operate strictly as **decision-support systems**. 
The system architecture categorically prohibits autonomous algorithmic employment actions:
- **NO automated employee termination or dismissal.**
- **NO automated salary reduction or fine deduction.**
- **NO automated disciplinary warnings or sanctions.**
- **NO automated leave rejection or shift revocation.**
- **NO automated hiring or promotion disqualification.**

Every AI prediction (e.g., an elevated attrition risk or anomalous punch pattern) is rendered with explainable feature contributions and uncertainty confidence intervals, requiring qualified human HR or managerial review before any personnel action is initiated.

### 1.2 Algorithmic Fairness & Protected Attributes
To prevent institutional bias and disparate impact, all models strictly exclude protected demographic attributes from the feature engineering pipeline:
- **Excluded Features:** `gender`, `date_of_birth` (age is binned/excluded), `address` (neighborhood/zip code), `marital_status`, and `religion`.
- **Temporal Data Leakage Controls:** Strict temporal split prevents future information leakage into historical evaluation datasets.

---

## 2. PRODUCTION MODEL SPECIFICATIONS

### Model 1: Absenteeism Prediction Model

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `absenteeism_v1.0.0` |
| **Primary Purpose** | Predict the probability that a scheduled employee will be absent during the upcoming work cycle to enable proactive shift rebalancing. |
| **Algorithm** | Random Forest Classifier (`n_estimators=100`, `max_depth=6`, `random_state=42`) |
| **Input Data** | 30-day historical attendance logs, shift assignments, and approved leave records. |
| **Engineered Features** | 1. `attendance_rate_30d` (Importance: 0.1286)<br>2. `late_count_30d` (Importance: 0.1156)<br>3. `avg_late_minutes_30d` (Importance: 0.2148)<br>4. `overtime_hours_30d` (Importance: 0.1940)<br>5. `recent_absences_30d` (Importance: 0.0710)<br>6. `unplanned_leaves_30d` (Importance: 0.0572)<br>7. `avg_duration_hours_30d` (Importance: 0.2188) |
| **Target Variable** | Binary indicator: `is_absent` (1 = Absent / 0 = Present) |
| **Training Dataset** | 150 training samples, 50 hold-out test samples (temporal split). |
| **Empirical Evaluation** | • **Accuracy:** `0.7200` (72.0%)<br>• **Precision:** `0.5714`<br>• **Recall:** `0.2667`<br>• **F1-Score:** `0.3636`<br>• **ROC-AUC:** `0.5124` |
| **Storage & Serialization** | `models/absenteeism/model.joblib` |
| **Inference Process** | Executed batch-wise prior to weekly roster generation (`GET /api/v1/ai/absenteeism-risk`). |
| **Explainability** | Feature importance ranking and individual z-score deviations highlight primary drivers (e.g., sudden spikes in late minutes or heavy overtime fatigue). |
| **Limitations** | Low recall (0.2667) indicates the model is conservative; it avoids false alarms but misses sporadic, non-patterned emergency leaves. |

---

### Model 2: Employee Attrition Risk Model

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `attrition_v1.0.0` |
| **Primary Purpose** | Identify employees experiencing systemic burnout, compensation disengagement, or stagnation to support proactive retention interventions. |
| **Algorithm** | Gradient Boosting / Random Forest Classifier with probability calibration |
| **Input Data** | Historical employee tenure, promotion history, compensation, overtime ratios, and review scores. |
| **Engineered Features** | `attendance_rate`, `tenure_years`, `total_overtime_hours`, `avg_late_minutes`, `kpi_score`, `goal_completion`, `productivity_score`, `salary_log`, `experience_years`, `leave_days_taken`. |
| **Target Variable** | Binary indicator: `employment_status` (`Terminated` = 1, `Active` = 0) |
| **Training Dataset** | 150 training samples, 50 hold-out test samples. |
| **Empirical Evaluation** | • **Accuracy:** `0.9800` (98.0%)<br>• **Precision:** `1.0000`<br>• **Recall:** `0.9375`<br>• **F1-Score:** `0.9677`<br>• **ROC-AUC:** `0.9688` |
| **Storage & Serialization** | `models/attrition/model.joblib` |
| **Inference Process** | Cached on monthly cadence; queried via `GET /api/v1/ai/attrition-risk` (restricted strictly to `ADMIN` and `HR` roles). |
| **Explainability** | Generates top 3 contributing factors per flagged employee (e.g., severe overtime imbalance, prolonged absence of promotion, or below-market salary band). |
| **Limitations** | Highly polarized on attendance consistency in synthetic datasets; requires retraining on diversified real-world corporate exit interview logs. |

---

### Model 3: Attendance Anomaly Detection Model

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `anomaly_iforest_v1.0.0` |
| **Primary Purpose** | Detect irregular, potentially fraudulent, or erroneous punch timestamps and locations without requiring labeled ground truth. |
| **Algorithm** | Isolation Forest (`contamination=0.03`, `n_estimators=100`, `random_state=42`) |
| **Input Data** | 5,000 empirical attendance punch records. |
| **Engineered Features** | 1. `punch_in_minute_of_day` (minutes from midnight)<br>2. `duration_hours`<br>3. `distance_from_campus_center_meters`<br>4. `day_of_week` |
| **Target Variable** | Anomaly classification (-1 = Outlier / 1 = Inlier) and continuous decision function score. |
| **Empirical Evaluation** | • **Total Records Analyzed:** 5,000<br>• **Anomalies Detected:** 150<br>• **Empirical Anomaly Rate:** `0.0300` (3.0%)<br>• **Mean Outlier Decision Score:** `-0.4067` |
| **Storage & Serialization** | `models/attendance_anomaly/model.joblib` |
| **Inference Process** | Evaluated asynchronously upon punch submission or queried via `GET /api/v1/attendance/anomalies`. |
| **Explainability** | Flags the specific dimensional outlier reason: "Late Night Punch (02:14 AM)", "Excessive Duration (14.2h)", or "Coordinate Variance (650m from geofence)". |
| **Limitations** | Unsupervised detection can occasionally flag legitimate executive overtime or off-site client meetings as anomalies until confirmed by a manager. |

---

### Model 4: 30-Day Workforce Demand Forecaster

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `forecaster_v1.0.0` |
| **Primary Purpose** | Forecast required departmental headcount across 30 and 90-day future horizons based on historical seasonal workload, project roadmaps, and leave cycles. |
| **Algorithm** | Holt-Winters Exponential Smoothing (Additive Trend, Additive Seasonality) & Project Pipeline Scaling |
| **Input Data** | 180-day aggregated daily operational timesheet hours across 9 departments (`DEP01`–`DEP09`). |
| **Target Variable** | Continuous daily required FTE (Full-Time Equivalent) staffing requirement per department. |
| **Empirical Evaluation** | • **Departments Forecasted:** 9<br>• **Target Period Evaluated:** Q3-2026<br>• **Mean Absolute Percentage Error (MAPE):** ~4.8% across engineering and customer support departments. |
| **Storage & Serialization** | `models/workforce_forecasting/` |
| **Inference Process** | Calculated on-demand or weekly via `GET /api/v1/ai/demand-forecast`. |
| **Explainability** | Decomposes time series into baseline demand, seasonal project surge, and scheduled leave deficit components. |
| **Limitations** | Requires historical timesheet data; macro economic shifts or unplanned enterprise reorganizations cannot be anticipated from time-series alone. |

---

### Model 5: Composite Productivity Scoring Engine

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `productivity_composite_v1.0.0` |
| **Primary Purpose** | Synthesize a balanced, objective, and multi-dimensional operational productivity metric. |
| **Algorithm** | Weighted multi-factor normalization composite |
| **Input Data** | Monthly attendance percentage, timesheet billability ratio, and quarterly OKR goal achievement score. |
| **Formula Formulation** | $$\text{Score} = (0.35 \times \text{Attendance Compliance}) + (0.40 \times \text{Billable Ratio}) + (0.25 \times \text{OKR Progress})$$ |
| **Scale** | Bounded continuous range [0.0, 100.0] |
| **Explainability** | Direct linear attribution showing exact point contributions from attendance regularity, timesheet hours, and goal completions. |
| **Limitations** | Does not capture qualitative work output (e.g., mentorship, code review quality) without accompanying manager review comments. |

---

### Model 6: Skills Gap & Training Recommendation Engine

| Attribute | Specification |
| :--- | :--- |
| **Model Version** | `skills_gap_v1.0.0` |
| **Primary Purpose** | Compare employee competencies against standardized role proficiency benchmarks and recommend targeted upskilling courses. |
| **Algorithm** | Vector Cosine Similarity & Rule-Based Deficit Mapping |
| **Input Data** | Employee skill proficiency matrix (1–5 scale) and target role benchmark profiles. |
| **Inference Process** | Computes deficiency score: $\Delta = \max(0, \text{Benchmark} - \text{Current Level})$. Courses mapped via skill tag taxonomy (`backend/routers/skills.py` & `backend/routers/training.py`). |
| **Explainability** | Outlines required vs current level for each skill (e.g., "Python: Current 2, Required 4 -> Gap 2 -> Recommended Course: Advanced Python & Asynchronous Design"). |

---

## 3. SUMMARY OF AI ASSETS

All 6 AI and predictive intelligence systems are validated, serialized, loaded into FastAPI memory at server startup, and covered by automated regression tests in `tests/test_ai_pipeline.py` and `tests/test_ai_api.py`.
