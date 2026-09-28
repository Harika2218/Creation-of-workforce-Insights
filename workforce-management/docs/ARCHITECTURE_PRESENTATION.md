# System Architecture & Technical Presentation

## 1. System Overview

**InnovateCorp HRvantage** is an enterprise-grade AI-powered workforce management automation platform. It is engineered with a modular, decoupled tier structure designed for high availability, sub-50ms API latencies, strict data segregation, and transparent AI-assisted decision making.

---

## 2. Multi-Tier Architecture Pipeline

```text
========================================================================================
                                     USERS
                  (Employees, People Managers, HR Executives, System Admins)
========================================================================================
                                       │
                                       ▼
========================================================================================
                              CLIENT PRESENTATION TIER
          React 19 SPA • Progressive Web App (PWA) • Three.js 3D Enterprise UI
               IndexedDB Offline Punch Queue • Service Worker Cache • Lucide
========================================================================================
                                       │  HTTPS / WSS / JSON
                                       ▼
========================================================================================
                                  SECURITY PERIMETER
             OWASP Security Headers (CSP, HSTS) • Request Body Clamping (15MB)
            Tiered IP Rate Limiter • JWT HS256 Authenticator • Authoritative RBAC
========================================================================================
                                       │
                                       ▼
========================================================================================
                                 FASTAPI REST API TIER
              103 Unique Paths • 124 Operations • Pydantic v2 Serialization
                Async Lifespan Engine • Prometheus Metrics Instrumentation
========================================================================================
                                       │
                                       ▼
========================================================================================
                                BUSINESS SERVICES LAYER
       AttendanceEngine • LeaveManager • ShiftScheduler • TimesheetEngine • Payroll
========================================================================================
                                  │                │
            ┌─────────────────────┘                └─────────────────────┐
            ▼                                                            ▼
==================================                              ========================
         DATA STORAGE TIER                                         AI & WORKFORCE ML
      MongoDB 7.0 Document DB                                      Scikit-Learn Pipeline
  200 Verified Synthetic Records                                  Attrition • Absenteeism
   Unique Indexes • Audit Logs                                    Productivity • Spikes
==================================                              ========================
            ▲                                                            │
            │                                                            ▼
========================================================================================
                             RAG & AI HR CHATBOT SUBSYSTEM
       Header-Aware Chunker • TF-IDF 512D / OpenAI Embeddings • Cosine Similarity
        Grounded Prompt Assembler • Local Offline Fallback Engine • Exact Citations
========================================================================================
                                       │
                                       ▼
========================================================================================
                          NOTIFICATION & WORKFLOW AUTOMATION
      Event-Driven Dispatcher • In-App Alert Stream • Webhooks • Duplicate Prevention
========================================================================================
                                       │
                                       ▼
========================================================================================
                            EXTERNAL ENTERPRISE CONNECTORS
        Microsoft Teams • Slack • Google Workspace • SAP SuccessFactors • Entra ID
                     Resilient Circuit Breaker (Fallback Simulation)
========================================================================================
```

---

## 3. Core Architectural Highlights

### 3.1 Security & Authoritative RBAC
- **Strict Separation of Concerns:** Frontend views adapt dynamically to provide seamless UX, but the **FastAPI backend is the sole authoritative gatekeeper**.
- **Role Enforcement:** Every API endpoint validates the caller's JWT role claims (`EMPLOYEE`, `MANAGER`, `HR`, `ADMIN`). Cross-employee snooping or unprivileged role escalations trigger instantaneous `HTTP 403 Forbidden` responses.
- **Synchronous Audit Logging:** Security-critical events (leave approvals, role adjustments, payroll generation, and authentication events) are immutably written to the `audit_logs` collection.

### 3.2 High-Performance FastAPI Backend
- **Asynchronous I/O:** Built on Starlette and ASGI with modern Python async lifespan management.
- **Verified Throughput:** Benchmarked at **162.64 requests/sec** under sustained concurrent load with an average latency of **48.2ms** and **0% error rate**.
- **Pydantic v2 Data Validation:** Request payloads are strictly typed and validated before reaching business logic handlers.

### 3.3 Relational-Integrity Document Database (MongoDB 7.0)
- **Document Flexibility with Strict Constraints:** Utilizes MongoDB collections with unique compound indexes, ensuring zero duplicate IDs, zero orphan attendance logs, and clean foreign-key-style references across the 200-employee baseline (`EMP001`–`EMP200`).
- **Validated Baseline:** 28 out of 28 automated database integrity assertions pass with zero data corruption.

### 3.4 AI Workforce Intelligence & Statistical Modeling
- **Production-Grade ML:** Employs scikit-learn ensemble classifiers and regression models for employee turnover risk prediction, absenteeism anomaly detection, and capacity forecasting.
- **Explainability First:** Predictions include top contributing risk factors (e.g. overtime ratio, tenure, commute distance, and leave frequency), empowering HR leaders to make informed, fair interventions.

### 3.5 Grounded RAG Policy Intelligence
- **Zero-Hallucination Guardrails:** Combines dense TF-IDF 512D vector embeddings with term-matching re-ranking over authoritative HR policy documents (`leave_policy.md`, `attendance_policy.md`, `remote_work_policy.md`).
- **Citation Provenance:** Every conversational answer includes verified source document metadata, section headers, and confidence scores.
- **Air-Gapped Local Engine:** Fully functional in offline and zero-cost local environments without third-party LLM dependencies.

### 3.6 Resilient External Integration Architecture
- **Adapter & Connector Pattern:** Connectors for Slack, Microsoft Teams, SAP, Oracle HRMS, and Microsoft Entra ID follow a unified interface.
- **Circuit Breaker Protection:** Unconfigured third-party environments fail gracefully into simulation and dry-run modes without blocking core workforce business operations.
