# FINAL SYSTEM DEMONSTRATION RUNBOOK & SCRIPT

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document Reference:** `docs/FINAL_DEMO_SCRIPT.md`  
**Target Duration:** 8 to 10 Minutes  
**Prerequisites:** Backend running on port 8000, Frontend running on port 5173, MongoDB on port 27017.  

---

## DEMONSTRATION OVERVIEW & STEP-BY-STEP RUNBOOK

| Step # | Screen / Feature | What to Click / Action | What to Explain to Evaluators | Technical Concept Demonstrated |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Authentication & Role Selection** | Navigate to `http://localhost:5173/login`. Click quick-fill demo button for **Employee** (`employee@demo.com` / `Demo@2026`). Click "Sign In". | Explain that the system employs stateless JWT authentication with bcrypt password hashing and 4-tier Role-Based Access Control. Show how tokens store role claims. | Stateless JWT auth, Bcrypt hash validation, Role claim injection |
| **2** | **Employee Dashboard (ESS)** | Lands on `/dashboard`. Point out personalized greeting for `EMP050`, upcoming shift banner, remaining leave quotas, and quick punch widget. | Explain Employee Self-Service (ESS) design: workers have immediate visibility into their operational schedule without needing to submit HR tickets. | Component state hydration, Token-scoped REST data loading |
| **3** | **Geofenced GPS Attendance Punch** | Navigate to `/attendance`. Click "Simulate Punch" or "Clock In". Observe prompt verifying coordinates against `LOC01` (Hyderabad Tech Park). | Explain how the backend calculates Haversine distance from campus coordinates and performs impossible velocity checks between consecutive punches to prevent fraud. | Multi-campus Haversine geofencing, Impossible velocity detection, Anomaly logging |
| **4** | **Leave Request Filing** | Navigate to `/leave`. Click "Apply for Leave". Select "Casual Leave" for tomorrow, enter reason "Family function", click "Submit Application". | Explain how the system checks leave balances in real-time and reserves quota in `pending` state, preventing over-allocation before manager approval. | Client-side form validation, Atomic state deduction, Database concurrency |
| **5** | **Manager Approval Workflow** | Log out, log in as **Manager** (`manager@demo.com` / `Demo@2026`). Navigate to `/manager/approvals`. Locate the pending leave request from `EMP050`. Click "Approve". | Explain how managers have visibility strictly into direct reports. Approving triggers balance commitment and automatically sends an in-app alert to the employee. | Multi-tier RBAC scoping, Event-driven notification trigger |
| **6** | **Shift Management & Peer Swap** | Navigate to `/shifts`. View the weekly team roster. Show how shifts are balanced between Morning, Evening, and Night, respecting statutory rest limits. | Explain how shift allocation algorithms prevent worker fatigue and how employees can request peer-to-peer swaps with automated role compatibility verification. | Constraint satisfaction scheduling, Fatigue-aware shift allocation |
| **7** | **Timesheet Submission & Billing** | Navigate to `/timesheets`. Show the weekly grid with project assignments (`PRJ01`, `PRJ02`). Log 8 hours against a billable client milestone. | Explain how daily activity logs separate billable client hours from non-billable overhead, directly feeding project profitability calculations. | Time-tracking data model, Billable utilization analytics |
| **8** | **Payroll Processing & Digital Payslip** | Log out, log in as **HR** (`hr@demo.com` / `Demo@2026`). Navigate to `/payroll`. Open latest payroll batch. Click "View Payslip" for an employee. | Explain the gross-to-net calculation formula: Base + Allowances + Overtime additions - LOP deductions - PF (12%) - Tax. Show the printable digital payslip format. | Financial formula consistency, Attendance-driven payroll sync |
| **9** | **HR Strategic Analytics Dashboard** | Navigate to `/hr`. Show the interactive 3D WebGL globe visualizing multi-campus workforce distribution across Hyderabad, Bengaluru, Pune, and Noida. | Explain how modern WebGL visualization elevates enterprise dashboards while maintaining automatic 2D canvas fallback for low-power mobile or non-WebGL devices. | Three.js WebGL integration, Canvas 2D fallback, Campus telemetry |
| **10** | **AI Workforce Intelligence & Forecaster** | Navigate to `/ai`. Review the 30-day demand forecast (Holt-Winters), absenteeism risk scores, and attrition indicators. Show top explainable risk factors. | Explain the ethical AI framework: models output probabilistic scores with transparent feature importance; all actions remain strictly decision-support with human oversight. | Supervised classification, Time-series exponential smoothing, Explainable AI |
| **11** | **RAG HR Policy Assistant (Voice & Chat)**| Navigate to `/chatbot`. Type: *"What is our parental leave policy and remaining balance?"* or click the microphone for speech-to-text. Observe the cited answer. | Explain the Pre-Retrieval Authorization Gate: the chatbot checks RBAC *before* querying the database, cites exact policy documents, and refuses to hallucinate unknown policies. | RAG vector search, Grounded citation engine, Pre-retrieval RBAC gate, Web Speech API |
| **12** | **Multi-Channel Notification Drawer** | Click the notification bell icon in top navigation. Show real-time alerts for the approved leave and recent attendance punches. | Explain how events from attendance, leave, and scheduler asynchronously populate user notification drawers and integrate with abstracted email/Slack dispatchers. | Asynchronous event dispatcher, Unread badge counters, Channel preferences |
| **13** | **Enterprise Integrations Dashboard** | Navigate to `/integrations`. Show connector health status cards: Slack (Configured), Teams (Foundation), Entra ID & Google (Cloud Blocked). | Explain transparent architectural honesty: the platform differentiates active local connectors from external cloud services requiring paid enterprise subscriptions. | Architectural honesty, Webhook signing, Connector health probes |
| **14** | **Mobile Responsiveness & PWA** | Press `F12` to open DevTools, toggle Device Toolbar (iPhone / Pixel). Reload page. Show responsive drawer navigation and offline capability. | Explain Progressive Web App features: Service Worker (`sw.js`) caches application assets for sub-100ms repeat loads and displays offline warning banners when disconnected. | PWA Service Worker caching, Mobile responsive layout, Offline handling |
| **15** | **Architecture & API Documentation** | Open a new tab to `http://localhost:8000/api/v1/docs` (Swagger UI). Show all 141 operations across 118 paths. | Conclude demonstration by highlighting complete architectural documentation, 100% test pass rate (99 backend tests, 35 frontend tests), and clean codebase design. | OpenAPI 3.1.0 specifications, Pydantic v2 schemas, Production readiness |

---

## EVALUATION FAQ SOUNDBITES

- **Q: How do you guarantee the employee count is strictly 200?**  
  *A: Our data pipeline enforces a strict alphanumeric sequence `EMP001` through `EMP200`. Contractors are isolated in a separate `contractors` collection (`CON001`–`CON003`) to ensure regular employee HR metrics are never diluted.*

- **Q: Does the AI assistant ever leak salary information?**  
  *A: No. We employ an `AuthorizationGate` that inspects the query intent and user role BEFORE performing any semantic vector retrieval or database lookup. If an employee queries a colleague's compensation, it returns an immediate HTTP 403 authorization denial with zero database queries.*

- **Q: What happens if WebGL is disabled or unsupported?**  
  *A: The 3D campus viewer includes a try-catch initialization check that falls back gracefully to a 2D HTML5 canvas schematic, ensuring uninterrupted dashboard accessibility.*
