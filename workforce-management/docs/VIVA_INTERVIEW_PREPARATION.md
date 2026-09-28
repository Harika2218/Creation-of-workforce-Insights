# COMPREHENSIVE TECHNICAL VIVA & INTERVIEW PREPARATION GUIDE

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document Reference:** `docs/VIVA_INTERVIEW_PREPARATION.md`  
**Classification:** Academic & Technical Defense Preparation  

---

## 1. SYSTEM ARCHITECTURE

### Q1: Why did you choose MongoDB instead of a pure relational database like PostgreSQL?
**Answer:** While workforce data has relational aspects, HR automation involves diverse, evolving document schemas: semi-structured biometric punch logs, multi-factor notification preferences, conversational chatbot message histories, and flexible JSON payroll component structures. MongoDB 7.0 provides document flexibility, horizontal scaling, and rich aggregation pipelines. To maintain relational integrity, we enforced strict schema validation via Pydantic v2 on the backend and validated all foreign keys using an automated SQLite relational test suite.

### Q2: Why FastAPI instead of Django or Flask?
**Answer:** FastAPI was selected for three primary technical reasons:
1. **Asynchronous Throughput:** Built on Starlette and ASGI, FastAPI handles asynchronous I/O natively, enabling high concurrency (>162 req/sec) without thread starvation.
2. **Native Typing & Validation:** Deep integration with Pydantic v2 provides automatic request parsing, runtime data validation, and serialization with zero boilerplate.
3. **Automated OpenAPI Generation:** It automatically generates standards-compliant OpenAPI 3.1.0 and Swagger/ReDoc interfaces directly from route signatures.

### Q3: Why React 19 for the frontend?
**Answer:** React 19 provides component-based reusability, efficient reconciliation, and seamless integration with TypeScript. In our architecture, the single-page application (SPA) communicates with the backend via REST, keeping presentation logic completely decoupled from backend persistence. React's ecosystem also made it straightforward to integrate Three.js WebGL rendering for 3D campus visualization and Web App Manifest / Service Workers for offline PWA capabilities.

### Q4: Why REST APIs over GraphQL or gRPC?
**Answer:** REST over HTTP/JSON is the enterprise standard for HR interoperability. It enables straightforward caching, granular HTTP status codes (`200`, `201`, `400`, `401`, `403`, `422`, `429`), standard OAuth2/JWT header authorization, and direct compatibility with enterprise API gateways, webhooks, and browser fetch APIs.

### Q5: How does authentication work?
**Answer:** Authentication is stateless and token-based. Upon submitting credentials to `POST /api/v1/auth/login`, the backend verifies the user's email and compares the password against the stored bcrypt hash using Passlib. If valid, it generates an HMAC-SHA256 signed JSON Web Token (JWT) containing the `user_id`, `employee_id`, and `role` claims, valid for 60 minutes. Subsequent requests supply this token in the `Authorization: Bearer <token>` header, which is unpacked and verified by FastAPI's `get_current_user` dependency.

### Q6: How does Role-Based Access Control (RBAC) work across the system?
**Answer:** RBAC is enforced at two distinct layers:
1. **Backend Layer:** Router endpoints use FastAPI dependency injection with a `RoleChecker(["ADMIN", "HR", "MANAGER"])` class. If the decoded token role does not match, FastAPI halts execution and returns `HTTP 403 Forbidden` before running business logic.
2. **Frontend Layer:** React Router views are wrapped in a `<ProtectedRoute allowedRoles={[...]} />` guard component that conditionally renders authorized views and redirects unauthorized users.

---

## 2. DATABASE DESIGN & INTEGRITY

### Q7: Why these specific collections?
**Answer:** The database schema is organized into modular collections separating core identities (`employees`, `users`, `departments`, `locations`), operational transactions (`attendance`, `shifts`, `leave_requests`, `timesheets`), financial ledgers (`payroll_records`), and intelligent/transient services (`attrition_predictions`, `chatbot_conversations`, `audit_logs`). This separation ensures that high-volume transactional logs (such as 24,600 attendance punches) do not impact employee directory queries.

### Q8: How are relationships handled in MongoDB?
**Answer:** Relationships are maintained through explicit alphanumeric identifiers (e.g., `employee_id`, `department_id`, `manager_id`). In high-frequency operational queries, referenced data is resolved using MongoDB `$lookup` aggregation stages or multi-step batch queries. Relational consistency is guarded at write time by Pydantic validators and verified through an automated foreign key check suite.

### Q9: What indexes are used, and why?
**Answer:**
- **Unique Indexes:** `employees.employee_id`, `employees.email`, `users.user_id`, and `audit_logs.log_id` to guarantee primary key uniqueness and prevent duplicate records.
- **Compound Indexes:** `attendance (employee_id, date)` and `payroll_records (employee_id, month, year)` to ensure $O(\log N)$ point lookups for historical queries and eliminate full collection scans.

---

## 3. ATTENDANCE & GEOLOCATION

### Q10: How does GPS validation work?
**Answer:** When an employee clicks "Clock In", the frontend requests device GPS coordinates via the HTML5 Geolocation API (`navigator.geolocation.getCurrentPosition`). These coordinates (latitude, longitude, accuracy) are transmitted over HTTPS to `POST /api/v1/attendance/check-in`.

### Q11: How does geofencing work mathematically?
**Answer:** The backend resolves the coordinates against our registered corporate campuses (`LOC01`–`LOC04`) using the **Haversine formula**, which computes the great-circle distance between two points on a spherical Earth:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
If the calculated distance to the nearest campus exceeds its declared radius (e.g., 500 meters), the punch is rejected with `HTTP 400 Bad Request`.

### Q12: How would physical biometric integration work in production?
**Answer:** Physical biometric punch terminals communicate over TCP/IP or HTTP push protocols. We implemented a dedicated ingestion endpoint (`POST /api/v1/attendance/biometric-sync`) that accepts device serial numbers, employee badge IDs, biometric match scores, and timestamps. A background device listener converts proprietary hardware payloads into standardized attendance documents.

---

## 4. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING

### Q13: How is absenteeism predicted?
**Answer:** We train a supervised **Random Forest Classifier** (`ai/models/absenteeism.py`) on rolling 30-day temporal features: attendance rate, late arrival count, average late minutes, overtime hours, and recent unplanned absences. It computes an absence probability score for the upcoming week.

### Q14: How is attrition predicted?
**Answer:** We employ a **Gradient Boosting / Random Forest Classifier** trained on tenure, promotion history, overtime ratios, salary competitiveness, and review scores. The model outputs a continuous attrition probability and highlights the top 3 contributing factors (e.g., excessive overtime imbalance or below-band compensation).

### Q15: How does attendance anomaly detection work?
**Answer:** Anomaly detection is unsupervised using an **Isolation Forest** model (`ai/models/anomaly_detector.py`) with a 3.0% contamination factor. It isolates abnormal data points across 4 dimensions: clock-in minute of the day, shift duration, distance from campus center, and day of the week, flagging unusual punch behaviors without requiring manual labels.

### Q16: How is workforce demand forecasting performed?
**Answer:** We use **Holt-Winters Exponential Smoothing** on 180 days of aggregated timesheet data across 9 departments, modeling baseline demand, additive trends, and weekly seasonal variations to project 30-day staffing requirements.

### Q17: How is employee productivity calculated?
**Answer:** We use a normalized multi-factor composite formula:
$$\text{Productivity} = (0.35 \times \text{Attendance Compliance}) + (0.40 \times \text{Billable Ratio}) + (0.25 \times \text{OKR Goal Progress})$$
yielding an objective score bounded between 0.0 and 100.0.

### Q18: How are skill gaps identified?
**Answer:** We compare an employee's verified skill vector against standardized role proficiency benchmarks (1–5 scale). Skill gaps are computed as $\Delta = \max(0, \text{Benchmark} - \text{Current})$, and an automated recommendation rule matches gaps to relevant corporate training courses.

---

## 5. RETRIEVAL-AUGMENTED GENERATION (RAG) & CHATBOT

### Q19: What is RAG and why use it for HR?
**Answer:** RAG combines information retrieval with language model generation. Instead of fine-tuning an LLM (which is expensive and prone to hallucinating outdated facts), RAG searches authoritative corporate policy documents at query time and passes relevant excerpts into the prompt context, ensuring accurate, grounded answers.

### Q20: How are documents chunked and indexed?
**Answer:** Official policy documents in `data/hr_policies/` are chunked using recursive character splitting into **500-character segments with 100-character overlap**. Chunks are tagged with metadata (`doc_id`, `category`, `section`, `effective_date`) and indexed using TF-IDF / vector representations.

### Q21: How do you prevent unauthorized salary or PII leaks in the chatbot?
**Answer:** We implemented an **Authorization Gate** (`backend/ai/chatbot/authorization.py`) that executes **BEFORE** any retrieval or database lookup. If an employee queries a colleague's salary or company-wide payroll, the gate detects the intent and caller role, blocking the request immediately with `HTTP 403` without querying the database or vector store.

---

## 6. SECURITY & DEPLOYMENT

### Q22: How are passwords stored and verified?
**Answer:** Passwords are never stored in plaintext. They are salted and hashed using **Bcrypt (work factor 12)** via Passlib. Verification uses constant-time comparison to prevent timing attacks.

### Q23: How are secrets protected?
**Answer:** All sensitive configuration is loaded via environment variables and `.env` files using `pydantic-settings`. `.gitignore` explicitly prevents `.env`, private keys, local databases, and temporary artifacts from being committed.

### Q24: How does Docker containerization work?
**Answer:** We provide a multi-container `docker-compose.yml` defining three isolated services:
1. `backend`: FastAPI Python 3.12 container with Uvicorn ASGI workers.
2. `frontend`: Node/Nginx Alpine container serving optimized Vite static bundles.
3. `database`: MongoDB 7.0 Community container with named volume persistence (`mongo_data`).

### Q25: How are health and readiness checks implemented?
**Answer:** We expose two dedicated probes:
- `GET /health` (Liveness): Returns `HTTP 200` to confirm the ASGI process is running.
- `GET /ready` (Readiness): Pings the MongoDB connection pool and confirms AI models are loaded in memory before accepting traffic.

---

## 7. ENGINEERING RESILIENCE & EDGE CASES

### Q26: What happens if MongoDB goes down?
**Answer:** The FastAPI connection pool catches connection timeouts gracefully. The `GET /ready` probe immediately returns `HTTP 503 Service Unavailable`, preventing reverse proxies (like Nginx or Kubernetes ingress) from routing traffic to an unhealthy instance.

### Q27: How are duplicate events prevented in the notification system?
**Answer:** The notification service implements a deduplication filter that checks for identical event signatures (same `user_id`, `event_type`, and target entity) within a sliding time window (e.g., 5 minutes) before persisting new notifications.
