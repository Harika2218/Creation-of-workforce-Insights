# Final Engineering Handoff Document

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Enterprise Project Handoff & Governance Specification  
**Phase:** 13 — Final Consolidation  
**Target Audience:** Enterprise HR Technology Consultants, Solution Architects, Site Reliability Engineers, and Engineering Leadership  

---

## 1. Project Overview

**InnovateCorp HRvantage** is an autonomous, full-stack workforce management automation platform. It is engineered to replace fragmented legacy HR spreadsheets, manual badge lines, and isolated leave trackers with an intelligent, centralized system.

The platform provides end-to-end management for employee profiles, geofenced GPS and QR attendance telemetry, rotational shift scheduling, multi-tiered leave approvals, weekly billable timesheets, payroll input automation, and proactive workforce intelligence.

---

## 2. System Architecture

The application adopts a decoupled, multi-tiered architecture:
- **Presentation Tier:** React 19 Single Page Application and Progressive Web App (PWA) with a WebGL Three.js ambient background canvas and Framer Motion micro-interactions.
- **Security Perimeter:** OWASP security response headers, request body size limits (15 MB), tiered IP rate limiting, JWT HS256 authentication, and authoritative backend RBAC.
- **API Tier:** FastAPI (ASGI) with Starlette, asynchronous lifespan management, 103 paths, 124 HTTP operations, and Pydantic v2 data models.
- **Data Tier:** MongoDB 7.0 document cluster enforcing relational-style unique indexes, compound foreign-key constraints, and immutable audit logs across 200 synthetic employees (`EMP001`–`EMP200`).
- **Intelligence Layer:** Scikit-learn Random Forest and time-series pipelines for attrition prediction, absenteeism forecasting, and capacity planning.
- **Policy RAG:** Dual-mode dense TF-IDF 512D vector embeddings and term-matching re-ranking with explicit citation provenance.
- **Integration Layer:** Outbound connectors with circuit breaker fault tolerance for Slack, Teams, Google Calendar, SAP, and Entra ID.

---

## 3. Technology Stack

- **Frontend:** React 19.2.8, TypeScript ~6.0.2, Vite 8.3.0, React Router DOM 7.18.4, Three.js 0.186, Framer Motion 13.4, Recharts 3.10, Axios 1.20.
- **Backend:** Python 3.10+, FastAPI >=0.115, Starlette, Uvicorn, Pydantic v2, PyMongo 4.8, PyJWT 2.9, Cryptography 43.0.
- **Database:** MongoDB Community Edition 7.0 on `localhost:27017`.
- **Machine Learning:** scikit-learn >=1.5, NumPy >=1.26, Pandas >=2.2, joblib >=1.4, SciPy >=1.14.
- **DevOps & Monitoring:** Docker, Docker Compose, Prometheus Client 0.20, python-json-logger 3.0, psutil 6.0, GitHub Actions CI.

---

## 4. Key Platform Features

1. **Employee Management:** Master records for 200 employees across 6 departments with assigned managers and job profiles.
2. **Attendance Telemetry:** GPS geofencing (InnovateCorp HQ boundary), QR code kiosk generation, 15-minute grace period enforcement, and automatic overtime calculation.
3. **Leave Management:** 4 categorized leave types (Annual, Casual, Sick, Parental), dynamic balance deduction, and one-tap manager approvals.
4. **Rotational Shifts:** Morning, General, Evening, and Night shifts, monthly roster view, and peer-to-peer swap requests with supervisor sign-off.
5. **Project Timesheets:** Daily activity logging by project code and billing status, weekly submission, and managerial auditing.
6. **Payroll Input Synchronization:** Aggregates approved attendance hours, overtime bonuses, and unpaid leave deductions into gross-to-net payroll records.
7. **Performance Scorecards:** Quarterly KPI tracking, self-evaluations, manager reviews, and department scorecards.
8. **Notification Automation:** Synchronous in-app alert streams and webhook notifications on key employee lifecycle events.

---

## 5. Machine Learning & Workforce Intelligence

- **Attrition Risk Predictor:** Random Forest classifier estimating turnover risk (0.0 to 1.0) with top 3 explainable drivers (overtime ratio, tenure, commute distance).
- **Absenteeism Forecasting:** Time-series anomaly scoring highlighting upcoming attendance deficits.
- **Capacity Planning:** Rolling-average projection model forecasting departmental headcount needs.
- **Skill Gap Recommender:** Matches employee competencies against upcoming project requirements.

---

## 6. Grounded RAG & AI HR Assistant

- **Document Corpus:** Authoritative markdown policies (`leave_policy.md`, `attendance_policy.md`, `remote_work_policy.md`, `code_of_conduct.md`, `benefits_guide.md`).
- **Chunking & Indexing:** Header-aware hierarchical chunker (200–500 words, 50-word overlap) stored in `rag_policy_vectors`.
- **Retrieval Engine:** Hybrid cosine vector similarity ($\ge 0.08$) and keyword section boost.
- **Provenance & Citations:** Every answer returns source document title, section heading, confidence score, and text excerpt.
- **Zero-Cost Offline Support:** Pluggable local deterministic grounding engine operates completely offline without external API keys.

---

## 7. Security & Governance

- **Authoritative RBAC:** Four distinct roles (`EMPLOYEE`, `MANAGER`, `HR`, `ADMIN`). Backend dependencies (`require_role`, `require_self_or_roles`) are 100% authoritative.
- **JWT Integrity:** Algorithm whitelisted to `HS256`. Active account status re-verified in MongoDB on every request.
- **OWASP Response Headers:** CSP, HSTS, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`).
- **Tiered Rate Limiting:** 10/min auth, 30/min AI, 120/min general with RFC headers and 300s brute-force lockout.
- **Audit Logging & Redaction:** Synchronous audit log records all sensitive actions; automated filter masks PII and secrets in logs.

---

## 8. Enterprise Integrations

- **Pre-Configured Adapters:** Slack Webhooks, Microsoft Teams Activity Feed, Google Workspace Calendar, Microsoft Entra ID (SSO), and ZKTeco Biometric Terminals.
- **Circuit Breaker:** Outbound calls to external providers are guarded with 5-second timeouts. If a provider is unreachable, the system records the event to audit logs and falls back gracefully.
- **Honest Status:** Unconfigured external SaaS systems are categorized as `BLOCKED_EXTERNAL_DEPENDENCY` without fabricating mock success.

---

## 9. Mobile & Progressive Web App (PWA)

- **Responsive Viewports:** Fluid mobile layouts for iOS and Android.
- **Offline Attendance Queue:** Check-in punches taken while disconnected are stored in browser IndexedDB and automatically synced to the server upon reconnection.
- **PWA Manifest:** W3C-compliant manifest supporting home-screen installation and standalone app launching.

---

## 10. Database Architecture & Integrity

- **Database:** MongoDB Community 7.0 (`hr_automation`).
- **Relational Integrity Baseline:** Validated across 28 automated checks:
  - Exactly 200 employee records (`EMP001`–`EMP200`).
  - 24,600 attendance rows.
  - 816 leave balance records.
  - 1,200 payroll records.
  - Zero duplicate IDs, zero orphan records, zero self-managing cycles.

---

## 11. Deployment Architecture

- **Multi-Stage Dockerfile:** Produces minimal production images with non-root security.
- **Docker Compose:** Orchestrates FastAPI, React static build, and MongoDB 7.0 with container health checks.
- **CI/CD:** GitHub Actions workflow executing linting, Pytest, Vitest, and Docker container builds.

---

## 12. Testing & Quality Assurance Summary

- **Total Automated Tests:** **122 Tests (100% Pass Rate)**
  - **Backend (Pytest):** 87 tests passing across 10 suites (`tests/test_*.py`).
  - **Frontend (Vitest):** 35 tests passing across 8 suites (`frontend/src/__tests__/`).
  - **Relational Integrity:** 28 / 28 automated database assertions pass.
  - **OpenAPI Schema:** 103 paths, 124 HTTP operations verified in `docs/openapi.json`.

---

## 13. Known Limitations

1. **External SaaS Credentials:** Connecting live Slack, Teams, or SAP instances requires customer-supplied API keys (`BLOCKED_EXTERNAL_DEPENDENCY`).
2. **Browser Hardware Permissions:** Geolocation attendance requires the user to grant location permissions in the browser (`BLOCKED_BROWSER_DEPENDENCY`).
3. **Payroll Scope:** The system calculates gross-to-net payroll inputs; direct bank clearing (NACHA / ISO 20022) requires integration with a licensed bank gateway.
4. **Machine Learning Scope:** Models utilize classical statistical and ensemble ML (scikit-learn) rather than deep neural networks to prioritize interpretability.

---

## 14. Future Scope

1. Direct bank ACH gateway integration for one-click salary disbursement.
2. Native Capacitor / React Native wrapper for mobile fingerprint hardware sensors.
3. Redis distributed caching tier for multi-region clustering.
4. WebRTC video interview module embedded in the recruitment portal.

---

## 15. Setup & Running Instructions

### 15.1 Quick Start
```bash
# 1. Start MongoDB
Start-Service MongoDB

# 2. Setup Backend Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Seed Database & Validate Baseline
python scripts/generate_synthetic_data.py
python scripts/validate_database.py

# 4. Start Backend Server
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 5. Start Frontend Dev Server (in frontend/ directory)
cd frontend
npm install
npm run dev
```

---

## 16. Demo User Accounts

| Role | Email Address | Password | Primary Workflow |
| :--- | :--- | :--- | :--- |
| **Employee** | `employee@demo.com` | `Demo@2026` | GPS Punch, Leave Request, Chatbot |
| **Manager** | `manager@demo.com` | `Demo@2026` | Team Roster, Leave Approval |
| **HR** | `hr@demo.com` | `Demo@2026` | 200 Employees, Payroll, AI Models |
| **Admin** | `admin@demo.com` | `Demo@2026` | User RBAC, Integrations, Audit Logs |

---

## 17. Important Environment Variables

| Variable Name | Default Value (Dev) | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Set to `production` in live deployments |
| `DEBUG` | `false` | Disables debug stack traces in production |
| `MONGODB_URI` | `mongodb://localhost:27017/hr_automation` | MongoDB connection URI |
| `JWT_SECRET_KEY` | *(Set strong random secret)* | 256-bit cryptographic signing key |
| `JWT_ALGORITHM` | `HS256` | Strictly enforced signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | JWT token validity window (8 hours) |
| `RAG_EMBEDDING_PROVIDER` | `tfidf` | `tfidf` (offline) or `openai` |
| `RAG_SIMILARITY_THRESHOLD` | `0.08` | Minimum cosine similarity for retrieval |
| `LLM_PROVIDER` | `local` | `local` (offline grounded) or `openai` |
| `RATE_LIMIT_ENABLED` | `true` | Enables IP rate limiting middleware |
