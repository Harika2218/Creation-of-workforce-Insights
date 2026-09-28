# AI / ML WORKFORCE INTELLIGENCE ARCHITECTURE DIAGRAM

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** `docs/diagrams/ai_ml_architecture.md`  

---

```mermaid
graph TD
    subgraph Data_Source ["1. Raw Data Extraction"]
        DB_Att["db.attendance (Punches, Late Minutes, Locations)"]
        DB_Emp["db.employees (Tenure, Department, Role)"]
        DB_Leave["db.leave_requests (Frequency, Unplanned Leave)"]
        DB_Time["db.timesheets (Project Hours, Billable Ratio)"]
        DB_Goals["db.employee_goals (OKR Completion %)"]
    end

    subgraph Feature_Engineering ["2. Feature Pipeline & Preprocessing"]
        Extractor["ai.data.extractor.DataExtractor"]
        FeatBuilder["ai.features.feature_builder.FeatureBuilder"]
        TemporalSplit["Strict 30-Day Temporal Rolling Windows"]
        ProtectedFilter["Fairness Filter (Excludes Gender, DOB, Religion)"]
    end

    subgraph Model_Zoo ["3. Supervised, Unsupervised & Time-Series Models"]
        Model_Abs["Absenteeism Model
        Random Forest (Acc: 72.0%, F1: 0.36)
        models/absenteeism/model.joblib"]

        Model_Att["Attrition Risk Model
        Gradient Boosting (Acc: 98.0%, ROC-AUC: 0.968)
        models/attrition/model.joblib"]

        Model_Anom["Attendance Anomaly Detector
        Isolation Forest (Contamination: 3.0%)
        models/attendance_anomaly/model.joblib"]

        Model_Fore["Workforce Demand Forecaster
        Holt-Winters Exponential Smoothing
        models/workforce_forecasting/"]

        Rule_Prod["Composite Productivity Engine
        Linear Normalization: 0.35Att + 0.40Bill + 0.25Goal"]

        Engine_Sim["Scenario Simulation Engine
        Deterministic Sensitivity Modeling"]
    end

    subgraph Human_In_The_Loop ["4. Decision Support & Human Governance"]
        ProbScore["Probabilistic Scores (0.0 to 1.0) with Uncertainty Intervals"]
        TopDrivers["Explainable Drivers (e.g. 'High Overtime Fatigue + 14 Late Days')"]
        ManagerIntervention["Manager / HR Strategic Review ONLY"]
        Disclaimers["Zero Autonomous Dismissals, Wage Cuts, or Sanctions"]
    end

    DB_Att & DB_Emp & DB_Leave & DB_Time & DB_Goals --> Extractor
    Extractor --> FeatBuilder --> TemporalSplit --> ProtectedFilter

    ProtectedFilter --> Model_Abs
    ProtectedFilter --> Model_Att
    ProtectedFilter --> Model_Anom
    ProtectedFilter --> Model_Fore
    ProtectedFilter --> Rule_Prod
    ProtectedFilter --> Engine_Sim

    Model_Abs & Model_Att & Model_Anom & Model_Fore & Rule_Prod & Engine_Sim --> ProbScore
    ProbScore --> TopDrivers --> ManagerIntervention --> Disclaimers
```
