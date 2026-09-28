# SYSTEM ARCHITECTURE — AI-POWERED WORKFORCE MANAGEMENT SYSTEM

## 1. High-Level Enterprise System Architecture

```text
                    ┌────────────────────────────────────────────────────────┐
                    │                    External Systems                    │
                    │  (M365, Teams, Slack, Google, SAP, Oracle, Biometrics) │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                                                ↓
                    ┌────────────────────────────────────────────────────────┐
                    │                   Integration Layer                    │
                    │   Connectors • Circuit Breakers • Sync • HMAC Webhooks  │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                                                ↓
┌─────────────────────────┐             ┌──────────────────────────────────┐
│  React 19 + Three.js    │ ──────────→ │         FastAPI Backend          │
│  (3D Canvas & Dashboards)│             │  (REST API, Auth/RBAC, Lifespan) │
└─────────────────────────┘             └────────────────┬─────────────────┘
                                                         │
                                                         ↓
                                                ┌──────────────────┐
                                                │ MongoDB Database │
                                                │  (hr_automation) │
                                                └──────────────────┘
                                                         ↑
                             ┌───────────────────────────┼───────────────────────────┐
                             │                           │                           │
                    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
                    │  AI/ML Pipeline │         │  HR Chatbot RAG │         │ Workflow Engine │
                    │ (Predict / Fore)│         │(Vector / QA Gro)│         │ (Rules & Alerts)│
                    └────────┬────────┘         └────────┬────────┘         └────────┬────────┘
                             │                           │                           │
                             └───────────────────────────┼───────────────────────────┘
                                                         │
                                                         ↓
                                                ┌──────────────────┐
                                                │  Notifications   │
                                                │(In-App/Email/Chat)│
                                                └──────────────────┘
```

---

## 2. Integration Layer Architecture

The integration layer (`backend/integrations/`) is built on clean hexagonal architecture principles:

1. **Connector Abstraction (`backend/integrations/base/connector.py`):**
   - Each integration inherits from `BaseConnector`.
   - Mandates non-destructive `test_connection()` with latency measurements.
   - Enforces `is_configured()` checks based on environment variables.
   - Houses a dedicated `CircuitBreaker` and exponential backoff retry mechanism.

2. **Fault Isolation via Circuit Breakers (`backend/integrations/base/circuit_breaker.py`):**
   - State machine: `CLOSED` (normal), `OPEN` (tripped after threshold failures), `HALF_OPEN` (recovery probe).
   - If Teams, Slack, SAP, or Biometrics fail or timeout, the failure is isolated. Core HR services, logins, and database operations proceed unaffected.

3. **External Event Dispatchers & Adapters:**
   - **Email:** `backend/integrations/email/` with `SMTPProvider`, `SendGridProvider`, `AmazonSESProvider`, and `MockEmailProvider`.
   - **Collaboration Messaging:** `backend/integrations/messaging/` with Microsoft Teams (Adaptive Cards) and Slack (Block Kit).
   - **Calendar Sync:** `backend/integrations/calendar/` with Microsoft Graph API and Google Calendar API v3 adapters.
   - **Enterprise Identity:** `backend/integrations/identity/` supporting Azure Entra ID / OIDC and Active Directory / LDAPS.
   - **Enterprise ERP & HRMS:** `backend/integrations/erp/` (SAP S/4HANA OData) and `backend/integrations/hrms/` (Oracle Fusion HCM).
   - **Biometric Attendance:** `backend/integrations/biometric/` (ZKTeco Push protocol, terminal punch parser, employee PIN mapping).
   - **Location Geofencing:** `backend/integrations/geofence/` (Server-side Haversine validation, accuracy bounds, anti-spoofing velocity checks).

4. **Synchronization Manager (`backend/integrations/sync.py`):**
   - Tracks every manual and scheduled synchronization run in MongoDB collection `integration_sync_history`.
   - Logs `sync_id`, `started_at`, `completed_at`, `status` (`SUCCESS`, `PARTIAL`, `FAILED`), and delta metrics (`records_read`, `records_created`, `records_updated`, `records_failed`).

5. **Inbound Webhooks & Security (`backend/integrations/webhooks.py`):**
   - Central endpoint: `POST /api/v1/integrations/webhooks/{provider}`.
   - Enforces HMAC-SHA256 signature verification (`X-Webhook-Signature`).
   - Implements replay protection (5-minute timestamp sliding window).
   - Deduplicates incoming events using external event IDs before routing to the workflow engine.

---

## 3. Data Flow & Security Boundaries

```text
[External System] --(HTTPS + HMAC / Bearer)--> [Integration Router]
                                                      │
                                          [Signature & Schema Validation]
                                                      │
                                            [Circuit Breaker Wrap]
                                                      │
                                           [Data Mapper & Transform]
                                                      │
                                           [Event Bus / Idempotency]
                                                      │
                                        [Business Services & MongoDB]
                                                      │
                                        [Audit Log Entry Created]
```

### Privacy & Data Minimization Guardrails:
- **No AI Exfiltration:** Internal AI predictions (attrition risk scores, absenteeism forecasts, productivity indexes) remain within internal RBAC authorization boundaries and are never dispatched to external chat channels.
- **Biometric Minimization:** Central MongoDB never stores raw biometric templates, facial landmark geometry, or fingerprint minutiae. Terminals perform edge matching and transmit cryptographically signed tokens.
- **Strict 200 Employee Invariant:** The core dataset of 200 employees (`EMP001`–`EMP200`) is preserved with strict reference integrity.

---

## 4. Mobile, PWA & Accessibility Architecture (Phase 11)

### 4.1 Client Layer Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Responsive Client Application                        │
│   (Desktop Desktop/Laptop • Tablet • Mobile Viewports • Touch Targets) │
├───────────────────────────────────┬────────────────────────────────────┤
│         PWA Shell Layer           │       Presentation / 3D Canvas     │
│  - Web App Manifest (standalone)  │  - Responsive Canvas Clamping      │
│  - Service Worker (Safe Cache)    │  - DPR Clamping [1, 1] on Mobile   │
│  - Install Prompt Management      │  - Reduced-Motion Fallback to 2D   │
│  - Update Notification Listener   │  - Accessible Overlays & ARIA      │
├───────────────────────────────────┴────────────────────────────────────┤
│                   Offline & Connectivity Orchestration                 │
│  - Network State Sentinel (online / offline / reconnecting)            │
│  - Offline Attendance Safety Queue (PENDING_SERVER_VERIFICATION)        │
│  - Reconnect Auto-Synchronization via Authoritative FastAPI Endpoints  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS (API & WebSocket)
                                    ↓
                     ┌──────────────────────────────┐
                     │       FastAPI Backend        │
                     │  (Authoritative Verification)│
                     └──────────────────────────────┘
```

### 4.2 Safe Service Worker Caching Boundary
- **Precaching Strategy:** Pre-caches only application shell assets (`/`, `/index.html`, `/manifest.json`, static SVG brand icons, enterprise fonts).
- **Network-Only Boundary:** All API calls (`/api/*`), token requests, authentication flows, and WebSockets strictly bypass the cache.
- **Offline Guardrail:** If an API request is made while disconnected, the service worker returns an immediate `503 Service Unavailable` JSON response indicating offline status. Sensitive employee records, salary data, PII, and internal AI risk scores are **never** persisted in browser HTTP cache.

### 4.3 Attendance Offline Safety Protocol
1. **No Client Self-Approval:** A punch captured while offline is never displayed as approved or marked as "Present". It is assigned status `PENDING_SERVER_VERIFICATION`.
2. **Encapsulated Event:** Punch metadata (local timestamp, device event ID, coordinates, punch type, biometric method) is persisted to local storage queue.
3. **Server-Authoritative Validation:** Upon network restoration, events are transmitted to `/attendance/check-in`. The backend evaluates geofence bounds, shift schedule, duplicate timestamps, and anomaly status before recording the attendance record.

### 4.4 Mobile Navigation & Adaptive Ergonomics
- **Role-Aware Bottom Nav:** Provides primary touch targets (>= 48px) for Employee, Manager, and HR/Admin personas.
- **Collapsible Drawer Navigation:** Desktop sidebar gracefully transforms into an off-canvas drawer with backdrop dismissal on mobile devices (`<= 768px`).
- **WCAG 2.1 AA Compliance:** Color redundancy, high-contrast text, visible `:focus-visible` styling rings, screen-reader text utilities (`.sr-only`), and `prefers-reduced-motion` compliance.

---

## 5. Phase 12 Production Infrastructure, Security & Reliability

### 5.1 Containerization & Process Isolation
- **Backend Service:** Multi-worker Uvicorn ASGI server running inside `python:3.11-slim` container under non-root user `appuser` (UID 10001). Healthcheck calls `/api/v1/health/live`.
- **Frontend Service:** Multi-stage `node:20-alpine` builder with `nginx:1.27-alpine-slim` serving production assets with gzip, SPA fallback, and API reverse proxying.
- **Orchestration:** `docker-compose.yml` declaring dependency health checks, persistent MongoDB volumes, and private bridge networks.

### 5.2 Enterprise Security Hardening
- **OWASP Headers:** CSP, HSTS (`max-age=31536000`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Permissions-Policy`.
- **API Rate Limiting:** In-memory sliding window limiter protecting auth endpoints (10/min), AI/chatbot (30/min), and general routes (120/min), plus brute-force lockout for repeated failed logins.
- **Payload Size Clamping:** Rejects request bodies exceeding 15 MB with HTTP 413.
- **Log Redaction Filter:** Scrubs passwords, bearer tokens, credit cards, and national tax IDs (PAN/SSN) from log streams.

### 5.3 Observability & Error Monitoring
- **Distributed Correlation Tracing:** `X-Request-ID` and `X-Correlation-ID` propagated through `ContextVar` to all structured JSON log entries.
- **Health Probes:** Liveness probe (`/api/v1/health/live`) and Dependency Readiness probe (`/api/v1/health/ready`) auditing MongoDB, AI models, scheduler, and integrations.
- **Metrics Telemetry:** `/api/v1/metrics` exposing Prometheus text and structured JSON formats.
- **Error Tracking Abstraction:** `ErrorTracker` supporting Sentry/OpenTelemetry with local structured JSON fallback.

### 5.4 Business Continuity & Disaster Recovery
- **Backup Utility:** Logical dumps (`scripts/backup_database.py`) with SHA-256 verification and metadata manifest.
- **Restore Procedure:** Automated restore utility (`scripts/restore_database.py`) rebuilding production indexes with 100% data parity.
- **RPO / RTO Targets:** RPO < 1 Hour; RTO < 2 Hours.

---

## 6. Phase 14 Advanced Enterprise Subsystems

### 6.1 Multi-Location & Multi-Campus Geofencing
- **Dedicated Locations Router:** `/api/v1/locations` managing 5 enterprise campuses (`LOC01`–`LOC05`) with stationed employee counts and regional holiday rosters.
- **Multi-Campus Resolution:** Verifies device coordinates against home and branch campuses. Inter-campus business travel is recognized as `BRANCH_CAMPUS_VISIT` with zero false anomalies.
- **Impossible Velocity Anomaly Engine:** Calculates physical travel speed between consecutive punches; velocities $>800\text{ km/h}$ over distances $>5\text{ km}$ flag `Suspicious Teleportation` for human review.

### 6.2 Contractor & Vendor Workforce Isolation
- **Collection Segregation:** Vendor personnel and hourly billing records are stored in isolated collections `contractors` and `contractor_timesheets`, preserving the exact 200 regular employee baseline (`EMP001`–`EMP200`).
- **Access Boundary:** Contractors are strictly quarantined from internal employee payroll, leave balances, and company-confidential benefits.

### 6.3 Skills Intelligence & Explainable Training Engine
- **Role Competency Matrix:** Evaluates employee skill proficiencies (`Beginner` to `Expert`) against department requirements, outputting gap magnitudes, priorities (`CRITICAL`, `HIGH`, `MEDIUM`), and readiness percentages.
- **Explainable Course Matching:** Suggests courses from `training_programs` accompanied by transparent rationales and mandatory non-punitive decision-support disclaimers.

### 6.4 Strategic Workforce Scenario Simulation
- **Deterministic Modeling Engine:** `POST /api/v1/ai/simulation` models strategic "what-if" scenarios (`DEMAND_INCREASE`, `WORKFORCE_REDUCTION`, `ATTRITION_SPIKE`, `NEW_PROJECT_SKILLS`, `SHIFT_CAPACITY_CHANGE`).
- **Cost & Staffing Projections:** Computes headcount requirements, monthly payroll deltas, and external hiring vs internal reallocation splits.
- **Strict Labeling:** Outputs are permanently labeled as `Scenario Simulation` for executive decision support rather than factual forecasts.

### 6.5 Continuous Rule-Based Compliance Alerting
- **Automated Rule Evaluation:** Continuously scans live data for excessive overtime (>12h/wk), missing checkouts, unresolved telemetry flags, and expiring vendor SOWs.
- **Human-in-the-Loop Review:** Alerts require supervisory review (`In_Review`, `Resolved`) with review justification notes; automated adverse disciplinary action is strictly prevented.

### 6.6 Voice-Enabled HR Assistant (Web Speech API)
- **Hands-Free Speech Interaction:** Incorporates native W3C `SpeechRecognition` (Speech-to-Text) and `window.speechSynthesis` (Text-to-Speech) into the chatbot client.
- **Zero Security Bypass:** Voice input strictly populates prompt text and routes through the authenticated `/api/v1/chatbot/chat` pipeline with full RAG citation verification and role scoping.


