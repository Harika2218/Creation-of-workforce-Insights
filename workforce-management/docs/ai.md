# AI/ML Workforce Intelligence Documentation
## AI-Powered Workforce Management Automation System (Phase 5)

This document provides comprehensive technical documentation for the AI/ML Workforce Intelligence subsystem (`ai/`), offline training pipelines, batch inference orchestrators, REST APIs (`/api/v1/ai/*`), and React analytics interfaces.

---

## 1. System Overview & Ethical Governance

The AI/ML Workforce Intelligence subsystem acts as an **augmented decision-support layer** designed to empower HR leaders, operations managers, and employees with proactive workforce insights.

### Ethical AI Principles
1. **Decision Support, Not Automated Decisions**:
   - Machine learning predictions provide probabilistic risk indicators and recommendations.
   - **No punitive or adverse employment actions** (e.g., termination, disciplinary action, pay cuts) are automated.
   - Clear disclaimers and human-in-the-loop review mechanisms are present on every dashboard.
2. **Strict Attribute Exclusion & Bias Prevention**:
   - Protected characteristics are **hard-excluded** at the data extraction level:
     - `gender`, `date_of_birth` (age proxy), `address` (geographic/socioeconomic proxy), `marital_status`, and `religion`.
   - Feature generation strictly leverages objective operational metrics: project timesheets, KPI completions, attendance durations, leave frequency, and skill competencies.
3. **Temporal Separation (Zero Data Leakage)**:
   - Attendance and performance metrics are engineered using temporal windows strictly preceding the prediction evaluation horizon.
   - Historical features reflect past behavior; targets evaluate future events.

---

## 2. Machine Learning & Decision-Support Engines

| Model / Engine | Algorithm / Methodology | Primary Inputs | Output / Metrics | Artifact Path |
|---|---|---|---|---|
| **Absenteeism Risk Model** | Random Forest Classifier (`n_estimators=100`, `max_depth=6`) | 30d/60d attendance duration, punctuality rates, leave balances, overtime | Probability `[0.0, 1.0]`, Risk Band (`LOW`, `MEDIUM`, `HIGH`), Top 3 feature attributions | `models/absenteeism/model.joblib` |
| **Attrition Vulnerability Model** | Gradient Boosting Classifier (`n_estimators=100`, `learning_rate=0.08`) | Tenure, compensation relative to peers, overtime burden, attendance trend, performance rating | Probability `[0.0, 1.0]`, Risk Category, Primary contributing retention factors | `models/attrition/model.joblib` |
| **Attendance Anomaly Detection** | Isolation Forest (`contamination=0.03`, `random_state=42`) | Check-in offset, check-out offset, duration delta, overtime hours | Anomaly Score, Binary Flag (`is_anomaly`), Root-cause reason heuristic | `models/attendance_anomaly/model.joblib` |
| **Transparent Productivity Engine** | Deterministic Multi-Factor Scoring Formula | KPI Achievement (30%), Goal Completion (25%), Billable Timesheet Efficiency (25%), Attendance Reliability (20%) | Score `[0 - 100]`, Detailed component breakdown, Plain-language explanation | `ai/models/rules_engines.py` |
| **Workforce Demand Forecaster** | Exponential Smoothing & Project Pipeline Scaling | Department headcount, active client projects, billable overtime trends | Q3-2026 Headcount Demand, Lower/Upper confidence bounds, Deficit gap | `ai/models/forecaster.py` |
| **Staffing Recommendations** | Capacity Gap Prioritizer | Headcount deficit, critical project deadlines, department role profiles | Recommended hires, Priority (`HIGH`, `MEDIUM`, `LOW`), Budget estimation | `ai/models/forecaster.py` |
| **Enterprise Skill Gap Matrix** | Department Competency Assessment Matrix | Department role requirements vs. validated employee skill levels | Skill Gap Count, Priority, Target upskilling roles | `ai/models/rules_engines.py` |
| **Training Recommendations** | Rule-Based Curriculum Matcher | Identified competency deficits, tenure, and department learning pathways | Personalized course recommendations, Rationale | `ai/models/rules_engines.py` |
| **Intelligent Shift & Resource Matcher** | Constraint-Satisfaction Heuristic | Overtime balance, shift history, project skill requirements, employee availability | Shift recommendations (fatigue prevention), Project resource allocations | `ai/models/rules_engines.py` |

---

## 3. Directory Structure

```text
HR_Automation/
├── ai/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── extractor.py             # MongoDB extraction excluding protected attributes
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── cleaner.py               # Missing value imputation, datetime parsing, outlier handling
│   ├── features/
│   │   ├── __init__.py
│   │   └── feature_builder.py       # Rolling window attendance, tenure, overtime, KPI features
│   ├── models/
│   │   ├── __init__.py
│   │   ├── absenteeism.py           # Random Forest absenteeism classifier
│   │   ├── attrition.py             # Gradient Boosting attrition model
│   │   ├── anomaly_detector.py      # Isolation Forest attendance anomaly detector
│   │   ├── forecaster.py            # Workforce demand & staffing advice
│   │   └── rules_engines.py         # Transparent productivity, skill gap, shift, & training rules
│   ├── training/
│   │   ├── __init__.py
│   │   └── train_all.py             # Master training script; writes to models/
│   └── inference/
│       ├── __init__.py
│       └── run_predictions.py       # Batch inference engine; populates MongoDB
├── models/                          # Persisted model binaries & metadata
│   ├── model_metadata.json          # Model governance, metrics, and training timestamps
│   ├── absenteeism/
│   │   ├── model.joblib
│   │   └── metadata.json
│   ├── attrition/
│   │   ├── model.joblib
│   │   └── metadata.json
│   └── attendance_anomaly/
│       ├── model.joblib
│       └── metadata.json
├── backend/
│   ├── schemas/ai.py                # 11 Pydantic response models
│   ├── services/ai_service.py       # Business logic, query filters, fallback harmonization
│   └── routers/ai.py                # 14 FastAPI endpoints mounted under /api/v1/ai
├── frontend/src/
│   ├── types/ai.ts                  # TypeScript AI interfaces
│   ├── services/aiService.ts        # Axios API client
│   ├── pages/ai/
│   │   └── AIIntelligencePage.tsx   # 7-Tab Unified AI Workforce Intelligence Dashboard
│   └── pages/dashboard/
│       ├── HRDashboard.tsx          # Embedded AI Risk Pulse widget
│       └── ManagerDashboard.tsx     # Embedded Team Absenteeism & Anomaly widget
└── tests/
    ├── test_ai_pipeline.py          # Pytest suite for extraction, feature engineering, and models
    └── test_ai_api.py               # Pytest suite for RBAC, self-scoping, and API responses
```

---

## 4. REST API Reference (`/api/v1/ai/*`)

All AI endpoints require a valid JWT Bearer token in the `Authorization` header.

| Method | Endpoint | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/api/v1/ai/absenteeism` | `HR`, `ADMIN`, `MANAGER` | Retrieve absenteeism risk predictions (filterable by `department_id`, `risk_band`). |
| `GET` | `/api/v1/ai/absenteeism/{employee_id}` | `EMPLOYEE` (self only), `MANAGER` (team only), `HR`, `ADMIN` | Get absenteeism risk, probability, and top feature drivers for an employee. |
| `GET` | `/api/v1/ai/attrition` | `HR`, `ADMIN` | Retrieve organization-wide attrition risk distribution. Managers and Employees forbidden. |
| `GET` | `/api/v1/ai/attrition/{employee_id}` | `HR`, `ADMIN` | Get detailed attrition drivers and risk scores for a specific employee. |
| `GET` | `/api/v1/ai/attendance-anomalies` | `HR`, `ADMIN`, `MANAGER` | List unsupervised anomalies flagged by Isolation Forest (filterable by `severity`). |
| `GET` | `/api/v1/ai/productivity` | `HR`, `ADMIN`, `MANAGER` | Retrieve productivity scorecards across departments. |
| `GET` | `/api/v1/ai/productivity/{employee_id}` | `EMPLOYEE` (self only), `MANAGER` (team only), `HR`, `ADMIN` | Retrieve transparent productivity score breakdown and component calculations. |
| `GET` | `/api/v1/ai/workforce-forecast` | `HR`, `ADMIN` | Retrieve headcount demand projections, lower/upper bounds, and projected gaps. |
| `GET` | `/api/v1/ai/staffing-recommendations` | `HR`, `ADMIN` | Get actionable department staffing advice and estimated budget requirements. |
| `GET` | `/api/v1/ai/skill-gaps` | `HR`, `ADMIN`, `MANAGER` | Retrieve enterprise skill gap matrix across departments. |
| `GET` | `/api/v1/ai/training-recommendations/{employee_id}` | `EMPLOYEE` (self only), `MANAGER` (team only), `HR`, `ADMIN` | Get personalized training and upskilling pathways. |
| `GET` | `/api/v1/ai/shift-recommendations` | `HR`, `ADMIN`, `MANAGER` | Retrieve fatigue-aware shift allocations based on overtime and historical hours. |
| `GET` | `/api/v1/ai/resource-allocations` | `HR`, `ADMIN`, `MANAGER` | Retrieve project skill matching and staffing allocations. |
| `GET` | `/api/v1/ai/models/metadata` | `EMPLOYEE`, `MANAGER`, `HR`, `ADMIN` | Get AI model governance metadata, training metrics, features, and fairness guarantees. |

---

## 5. Operations & Execution Guide

### 1. Training All Models Offline
```powershell
# From project root: HR_Automation/
python -m ai.training.train_all
```
*Outputs: Generates serialized model artifacts in `models/` and summary catalog in `models/model_metadata.json`.*

### 2. Executing Batch Inference
```powershell
# From project root: HR_Automation/
python -m ai.inference.run_predictions
```
*Outputs: Computes batch predictions for all 200 employees, 9 departments, and active projects; synchronizes into MongoDB collections.*

### 3. Running Automated Tests
```powershell
# Run the complete test suite (Database, Backend API, AI Pipeline, AI REST Endpoints):
python -m pytest tests/ -v

# Run AI-specific tests only:
python -m pytest tests/test_ai_pipeline.py tests/test_ai_api.py -v
```

### 4. Running Integration & Demo Verification
```powershell
# Run the live 7-scenario integration script against the FastAPI server:
python scripts/verify_ai_integration.py
```

### 5. Running Frontend Tests & Production Build
```powershell
cd frontend
npm test -- --watchAll=false
npm run build
```

---

## 6. Frontend Navigation & User Flows

The React frontend includes a dedicated **Workforce AI** interface accessible via the sidebar or directly at `/ai-intelligence`:

1. **Model Governance Banner**:
   - Displays real-time model version, fairness confirmation (protected attributes excluded), and decision-support disclaimers.
2. **7 Interactive Functional Tabs**:
   - **Attrition Vulnerability**: Organization risk matrix, High/Medium/Low distribution chart, and proactive retention actions.
   - **Absenteeism Risk**: Attendance risk probabilities, top contributing drivers, and historical duration stats.
   - **Attendance Anomalies**: Unsupervised Isolation Forest flags, timestamped clock anomalies, and severity ratings.
   - **Workforce Planning**: Q3-2026 departmental headcount forecast, capacity gaps, and estimated recruitment budgets.
   - **Productivity Scorecards**: Transparent 0-100 scores with full component breakdown (KPIs, goals, timesheets, attendance).
   - **Skills & Curriculum**: Enterprise skill deficit matrix and personalized employee training pathways.
   - **Smart Allocations**: Fatigue-aware shift scheduling recommendations and project skill matching.
3. **Dashboard Pulse Widgets**:
   - **HR Dashboard**: Embedded AI Workforce Pulse card summarizing high attrition vulnerabilities, predicted demand gaps, and anomaly flags.
   - **Manager Dashboard**: Embedded Team Attendance Anomaly & Absenteeism alert card for department leaders.
