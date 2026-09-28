# FINAL SYSTEM ARCHITECTURE & DATA FLOW SPECIFICATION

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Final System Architecture & Data Flow Diagrams  
**Phase:** 13 — Final Consolidation  
**Version:** 1.0  
**Format:** Maintainable Mermaid Diagram Architecture  

---

## 1. High-Level Enterprise System Topology

```mermaid
flowchart TD
    subgraph ClientTier ["Client Application Tier (React 19 + Vite + PWA + Three.js)"]
        UI_Desktop["Desktop Web Application<br/>(3D Canvas & Dense Tables)"]
        UI_Mobile["Mobile PWA Application<br/>(Touch Nav & Offline Queue)"]
        SW["Service Worker (sw.js)<br/>Safe Shell Caching"]
    end

    subgraph IngressTier ["Edge & Ingress Network Tier"]
        PROXY["Nginx Reverse Proxy / TLS Termination<br/>- HTTPS / WSS Enforcement<br/>- Security Headers (CSP, HSTS)<br/>- Static Asset Caching"]
    end

    subgraph BackendTier ["FastAPI ASGI Application Core (Port 8000)"]
        SEC_MIDDLEWARE["Security & Defense Middlewares<br/>- CorrelationIdMiddleware (X-Request-ID)<br/>- RateLimitMiddleware (Tiered Limits)<br/>- SecurityHeadersMiddleware (OWASP)<br/>- SecurityRedactionFilter (PII Sanitization)"]
        
        AUTH_RBAC["Identity & RBAC Engine<br/>- JWT HS256 Token Validator<br/>- RFC 6238 TOTP MFA<br/>- require_role / require_self_or_roles"]
        
        ROUTERS["14 Modular REST Routers<br/>Employees, Attendance, Shifts, Leave,<br/>Timesheets, Payroll, Performance, AI,<br/>Chatbot, Notifications, Integrations, Health"]
        
        SERVICES["Core Business Domain Services<br/>AttendanceService, LeaveService,<br/>ShiftService, PayrollService, AIService"]
        
        SCHEDULER["Lifespan Workflow Scheduler<br/>& Centralized EventBus Engine"]
    end

    subgraph DataTier ["Persistence & Vector Store Tier"]
        MONGO[("MongoDB 7.0 Document Store<br/>- 52 Collections<br/>- Connection Pooling (50)<br/>- Compound B-tree Indexes")]
        POLICY_DOCS["Authentic Corporate Policy Corpus<br/>(Employee Handbook, Leave, Travel)"]
    end

    subgraph IntelligenceTier ["AI/ML & RAG Intelligence Tier"]
        AI_MODELS["Scikit-Learn ML Pipelines<br/>- Attrition Probability (Random Forest)<br/>- Absenteeism Predictor<br/>- 30/90-Day Headcount Forecaster<br/>- Attendance Anomaly Detector"]
        RAG_CORE["RAG Conversational Engine<br/>- TF-IDF / Vector Embeddings<br/>- Grounded Policy Retrieval<br/>- Citation Engine (Doc, Sec, Page)"]
    end

    subgraph IntegrationTier ["External Enterprise Integration Layer"]
        CIRCUIT_BREAKERS["Fault Isolation Circuit Breakers<br/>(Closed / Open / Half-Open)"]
        CONNECTORS["Hexagonal Connectors<br/>- MS Teams (Adaptive Cards)<br/>- Slack (Block Kit)<br/>- MS Graph & Google Calendar<br/>- SAP ERP & Oracle HCM<br/>- ZKTeco Biometric Kiosks"]
    end

    ClientTier -->|HTTPS / WSS| PROXY
    PROXY --> SEC_MIDDLEWARE
    SEC_MIDDLEWARE --> AUTH_RBAC
    AUTH_RBAC --> ROUTERS
    ROUTERS --> SERVICES
    SERVICES --> MONGO
    SERVICES --> SCHEDULER
    SCHEDULER --> MONGO

    ROUTERS -->|Inference Queries| AI_MODELS
    ROUTERS -->|Conversational QA| RAG_CORE
    RAG_CORE --> POLICY_DOCS

    ROUTERS --> CIRCUIT_BREAKERS
    CIRCUIT_BREAKERS --> CONNECTORS
```

---

## 2. Comprehensive Data Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Employee as Staff Employee (Alex Chen)
    participant Client as React PWA Client
    participant Proxy as Nginx Ingress
    participant API as FastAPI Backend
    participant Auth as RBAC & Auth Engine
    participant DB as MongoDB 7.0
    participant EventBus as Workflow EventBus
    participant Notif as Notification Engine
    actor Manager as Team Manager (Sarah Jenkins)

    Note over Employee, Manager: End-to-End Workflow: Attendance Punch & Geofence Check

    Employee->>Client: Clicks "Clock In" (with GPS coords)
    Client->>Proxy: POST /api/v1/attendance/check-in + Bearer JWT
    Proxy->>API: Forwards request with X-Request-ID
    API->>Auth: Validate JWT & active account status
    Auth-->>API: Authorized (EMP004)
    API->>API: Compute Haversine distance (GPS vs Office HQ)
    alt Within 500m geofence radius
        API->>DB: Insert attendance record (check_in=Now, status=Present)
        API->>EventBus: Dispatch Event: ATTENDANCE_PUNCH_RECORDED
        EventBus->>Notif: Create in-app notification
        Notif->>DB: Save to notifications collection (recipient=EMP004)
        API-->>Client: HTTP 200 OK (Verified attendance)
        Client-->>Employee: Visual confirmation & active timer
    else Outside 500m radius
        API-->>Client: HTTP 400 Bad Request (Outside geofence threshold)
        Client-->>Employee: Error: "You are 1,200m away from office"
    end

    Note over Employee, Manager: End-to-End Workflow: Leave Application & Approval

    Employee->>Client: Submits Casual Leave request (2 days)
    Client->>API: POST /api/v1/leave/requests
    API->>DB: Validate leave balance ($Allocated = Used + Remaining$)
    API->>DB: Insert leave_request (status=Pending, manager_id=EMP003)
    API->>EventBus: Dispatch Event: LEAVE_APPLICATION_SUBMITTED
    EventBus->>Notif: Generate alert for Manager (EMP003)
    Notif->>DB: Save notification (recipient=EMP003)
    Notif-->>Manager: Real-time WebSocket badge update
    Manager->>Client: Opens Manager Dashboard & reviews leave
    Manager->>API: POST /api/v1/leave/requests/{id}/approve
    API->>Auth: Verify caller role == MANAGER and caller manages EMP004
    API->>DB: Update leave_request (status=Approved)
    API->>DB: Deduct 2 days from EMP004 leave_balances
    API->>EventBus: Dispatch Event: LEAVE_APPLICATION_APPROVED
    EventBus->>Notif: Generate approval alert for Employee (EMP004)
    Notif->>DB: Save notification
    Notif-->>Employee: In-app notification: "Your leave has been APPROVED"
```

---

## 3. RAG Conversational Retrieval Architecture

```mermaid
flowchart TD
    DOCS["Corporate Policy Documents<br/>(PDF, DOCX, TXT)"] --> PARSER["Document Text Parser"]
    PARSER --> CHUNKER["Semantic Text Chunker<br/>(500 tokens with 50-token overlap)"]
    CHUNKER --> EMBEDDER["Vector Embedding Engine<br/>(TF-IDF Matrix / OpenAI Embeddings)"]
    EMBEDDER --> VEC_STORE["Vector Store & Inverted Index<br/>(rag_chunks collection)"]

    USER_QUERY["Employee Query<br/>'What is the notice period?'"] --> GUARD["Prompt Injection Defense<br/>& RBAC Authorization Filter"]
    GUARD --> RETRIEVER["Similarity Search Engine<br/>(Cosine Similarity Threshold >= 0.08)"]
    VEC_STORE --> RETRIEVER
    RETRIEVER --> CONTEXT["Top-4 Grounded Chunks + Metadata<br/>(Document Title, Section, Page Number)"]
    CONTEXT --> PROMPT["Augmented Generation Prompt<br/>(System instructions: Cite facts only)"]
    USER_QUERY --> PROMPT
    PROMPT --> LLM["LLM Synthesis Engine<br/>(Deterministic Grounded Reasoner)"]
    LLM --> RESPONSE["Structured Answer with Exact Citations:<br/>'[Employee Handbook, Section 9.1, Page 42]'"]
```

---

## 4. Hexagonal Integration Layer & Circuit Breaker Model

```mermaid
stateDiagram-v2
    [*] --> CLOSED : Initial State (Normal Operation)
    
    CLOSED --> OPEN : Consecutive Failures >= 5 or Latency Timeout
    note right of CLOSED
        Passes all traffic to external provider.
        Tracks success/failure metrics.
    end note

    OPEN --> HALF_OPEN : Recovery Timeout (60 Seconds Elapsed)
    note right of OPEN
        Tripped state. Immediately fails fast.
        Calls mock provider or falls back safely.
        Core HR operations unaffected.
    end note

    HALF_OPEN --> CLOSED : Probe Request Succeeds
    HALF_OPEN --> OPEN : Probe Request Fails
    note right of HALF_OPEN
        Sends single probe request.
        If healthy: reset failure counter.
        If unhealthy: trip back to OPEN.
    end note
```
