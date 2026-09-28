# Project Viva & Technical Defense Preparation Guide

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Technical Defense Questions & Authoritative Answers  
**Phase:** 13 — Final Consolidation  

---

## 1. System Architecture & Framework Selection

### Q1: Why did you choose FastAPI over Flask or Django?
**Answer:**
FastAPI offers asynchronous concurrency natively via ASGI (Starlette) and uvloop, allowing high I/O throughput for real-time attendance telemetry and chat streams. It integrates Pydantic v2 for automatic, high-performance request/response data validation and serialization. Additionally, FastAPI automatically generates standards-compliant OpenAPI 3.1.0 specifications and interactive Swagger documentation directly from code type hints.

### Q2: Why did you choose React 19 for the frontend?
**Answer:**
React 19 provides modern component modularity, improved server/client hooks, and seamless virtual DOM reconciliation. Pairing React with Vite enables sub-second Hot Module Replacement (HMR) and optimized rollup production bundles. Furthermore, React integrates cleanly with Three.js via `@react-three/fiber` for enterprise 3D canvas rendering and Framer Motion for responsive UI micro-interactions.

### Q3: Why REST APIs instead of GraphQL or gRPC?
**Answer:**
REST over HTTP/JSON is the enterprise standard for interoperable web architectures. It offers straightforward stateless caching, standard HTTP status codes (`200`, `201`, `400`, `401`, `403`, `404`, `429`), broad compatibility with edge reverse proxies and WAFs, and zero friction when integrating third-party enterprise tools like Slack webhooks or SAP connectors.

### Q4: How does authentication and session management work?
**Answer:**
Authentication is stateless and token-based using JSON Web Tokens (JWT). Upon verifying the user's email and salted SHA-256 password hash, the backend issues a signed JWT containing claims (`sub`, `role`, `employee_id`, `iat`, `exp`). The token is sent in the `Authorization: Bearer <token>` header for subsequent requests. The backend explicitly enforces the `HS256` signature algorithm and validates that the account remains active (`is_active == 1`) in MongoDB on every request.

### Q5: How is Role-Based Access Control (RBAC) enforced?
**Answer:**
RBAC enforcement is **authoritative on the backend**. While the frontend uses role claims to adapt navigation menus and buttons, the FastAPI backend guards all sensitive endpoints using reusable FastAPI dependencies (`require_role` and `require_self_or_roles`). If an `EMPLOYEE` attempts to invoke an endpoint restricted to `MANAGER`, `HR`, or `ADMIN`, the backend immediately rejects the request with `HTTP 403 Forbidden`.

---

## 2. Database & Data Modeling

### Q6: Why MongoDB instead of a relational database like PostgreSQL?
**Answer:**
Workforce management involves heterogeneous, semi-structured records: flexible policy vector metadata, event-driven notification payloads with variable schemas, and rich time-series attendance records with geospatial coordinates. MongoDB 7.0 provides high write throughput for concurrent punch telemetry, dynamic document indexing, and native JSON storage, while our application layer enforces relational-style integrity constraints.

### Q7: What are the primary MongoDB collections in the system?
**Answer:**
1. `employees`: Master employee records, job profiles, departments, managers (200 records: `EMP001`–`EMP200`).
2. `users`: Credentials, password salts, roles, and active states.
3. `attendance`: Daily punch timestamps, geofences, durations, and anomaly flags (24,600+ records).
4. `leave_balances`: Categorized leave quotas, used days, and accruals (816 records).
5. `leave_requests`: Leave applications, approval states, and manager review comments.
6. `shifts`: Rotational shift rosters and peer swap requests.
7. `timesheets`: Weekly billable project hours and approval states.
8. `payroll`: Processed monthly compensation, overtime inputs, and tax deductions.
9. `rag_policy_vectors`: Chunked policy text and 512D vector embeddings.
10. `audit_logs`: Immutable security and transactional audit events.

### Q8: How are entity relationships maintained in a document database?
**Answer:**
Relationships are maintained through normalized foreign-key references (e.g., `employee_id`, `department_id`, `manager_id`). Relational integrity is validated using compound database indexes and enforced through service-layer lifecycle hooks (e.g., verifying an employee exists before creating an attendance record, ensuring managers are active employees).

### Q9: What indexes are configured and why?
**Answer:**
- Unique single-field indexes on `employee_id`, `email`, and `user_id` to prevent duplicates.
- Compound indexes such as `{ employee_id: 1, date: 1 }` on `attendance` to guarantee at most one attendance record per employee per day and enable $O(1)$ daily lookups.
- Range indexes on timestamps (`created_at`, `timestamp`) for fast audit log filtering and chronological reporting.

---

## 3. AI & Workforce Intelligence

### Q10: Why did you use scikit-learn instead of Deep Learning / PyTorch?
**Answer:**
Enterprise workforce intelligence requires **interpretability, auditability, and fairness**. Deep neural networks operate as black boxes, making it difficult to justify why an employee was flagged as an attrition risk. Scikit-learn Random Forests and Logistic Regression models provide transparent feature importances, train in seconds without requiring expensive GPU infrastructure, and run with minimal memory overhead in containerized environments.

### Q11: How is employee attrition predicted?
**Answer:**
The attrition engine extracts engineered features from employee records: tenure, overtime ratio, compensation percentile relative to role, commute distance, recent leave frequency, and performance review scores. An ensemble classifier evaluates the feature vector and outputs a probability score (0.0 to 1.0) along with the top 3 contributing factors, allowing HR to implement proactive retention strategies.

### Q12: How does attendance anomaly detection work?
**Answer:**
The anomaly engine applies rule-based thresholds and statistical z-score modeling to attendance telemetry. Anomalies are flagged when:
1. GPS coordinates fall outside designated office geofence radiuses.
2. Check-in timestamps deviate by more than the 15-minute grace period from the assigned shift start.
3. Multiple punches occur within an implausible duration (rapid-fire duplicate detection).

### Q13: How is workforce capacity and demand forecasted?
**Answer:**
The forecasting service uses time-series rolling moving averages and seasonal trend decomposition across historical attendance, approved leave, and project timesheet records to project required departmental headcount over upcoming quarters.

### Q14: How are skill gaps detected and staffing recommendations generated?
**Answer:**
The system matches current employee skill matrices against project requirements stored in timesheet and departmental profile schemas. Where required competency hours exceed available trained personnel, the recommender proposes internal department reassignments or targeted training modules.

---

## 4. Grounded RAG & AI HR Assistant

### Q15: What is RAG and why is it necessary for HR?
**Answer:**
Retrieval-Augmented Generation (RAG) is an architectural pattern that retrieves relevant external knowledge documents before passing them as context to a language model to generate an answer. In HR, RAG is critical because standard LLMs hallucinate rules, fabricate leave entitlements, and lack access to company-specific policies.

### Q16: How are policy documents processed and indexed?
**Answer:**
Authoritative markdown documents (`leave_policy.md`, `attendance_policy.md`, etc.) are parsed using a hierarchical, header-aware chunker (`backend/rag/chunker.py`). Text is split into 200–500 word sections with a 50-word overlap, preserving section headings and eligible roles. Each chunk is vectorized into a 512-dimensional embedding and stored in MongoDB `rag_policy_vectors`.

### Q17: How is policy retrieval performed?
**Answer:**
Retrieval uses a **hybrid approach**:
1. Dense vector similarity computes the cosine distance between the user query embedding and stored policy chunk embeddings.
2. Term-matching re-ranking boosts chunks containing exact keyword matches (e.g. "15 minutes", "paternity", "maternity") or matching section headers.
3. Candidate chunks below the similarity threshold (0.08) are filtered out.

### Q18: How are citations generated and grounding guaranteed?
**Answer:**
The context passed to the LLM explicitly binds each chunk to a source identifier. The response generator references the exact source document name, section heading, and confidence score. If the retrieved context does not contain the answer, the engine states that company policy does not specify the answer, eliminating fabricated guidelines.

### Q19: How is unauthorized data access prevented in the chatbot?
**Answer:**
The RAG pipeline enforces **data scoping at the database level**. Vector queries include an `$in` role filter (`applicable_roles`). Employees cannot retrieve policy excerpts tagged for executives. Furthermore, the `AuthorizationGate` blocks employees from asking personal queries about other employees' salaries or performance ratings.

---

## 5. Security & DevSecOps

### Q20: How does JWT signature validation protect against tampering?
**Answer:**
The backend signs tokens using HMAC-SHA256 with a private server secret. When verifying the token, `jwt.decode` enforces `algorithms=["HS256"]`. If a malicious client attempts to modify the role claim from `EMPLOYEE` to `ADMIN`, the cryptographic signature check fails, returning `HTTP 401 Unauthorized`.

### Q21: How are passwords protected?
**Answer:**
Passwords are never stored in plaintext. They are salted with a cryptographically secure random value and hashed using SHA-256 with multiple iterations. Salting prevents rainbow-table lookups and ensures that identical passwords yield different stored hashes.

### Q22: How do you prevent sensitive data leaks in logs?
**Answer:**
All logging pipelines pass through a custom `SecurityRedactionFilter` that intercepts log records and substitutes sensitive patterns (passwords, JWT tokens, credit card numbers, tax IDs, and database credentials) with `***REDACTED***`.

### Q23: What security headers are applied to HTTP responses?
**Answer:**
The `SecurityHeadersMiddleware` injects:
- `Content-Security-Policy`: Blocks unauthorized script execution and clickjacking frames.
- `Strict-Transport-Security`: Mandates HTTPS transport in production.
- `X-Content-Type-Options: nosniff`: Prevents MIME-type confusion attacks.
- `X-Frame-Options: DENY`: Prevents UI clickjacking attacks.
- `Permissions-Policy`: Restricts camera and geolocation access to the application origin.

---

## 6. Integrations & Circuit Breakers

### Q24: How are external systems integrated without compromising stability?
**Answer:**
External systems (Slack, Teams, Google Calendar, SAP) are integrated using the Adapter Pattern behind asynchronous service boundaries. Calls are wrapped with strict timeout limits (5 seconds) and circuit breakers. If an external service experiences downtime or network latency, the circuit breaker trips, allowing core HR operations to proceed unimpeded while logging the failure to `audit_logs`.

### Q25: Why are unconfigured integrations marked as `BLOCKED_EXTERNAL_DEPENDENCY`?
**Answer:**
In accordance with professional engineering ethics, we never fabricate fake success responses for external cloud providers when live enterprise credentials or active cloud tenants are not present. Connectors are fully coded and tested with mock fixtures, but reported honestly as blocked on external dependencies.

---

## 7. Progressive Web App (PWA) & Mobile

### Q26: What makes this application a Progressive Web App (PWA)?
**Answer:**
It includes a W3C-compliant `manifest.json` defining application metadata, icons, and display mode (`standalone`), along with a Service Worker that caches static assets for offline launching and intercepting network failures.

### Q27: How does offline attendance punch-in work?
**Answer:**
When an employee punches in while disconnected from the internet, the client records the punch timestamp and device coordinates into browser IndexedDB. Once network connectivity is restored, the service worker detects the online event, uploads the queued punch to the backend, and clears the local cache.

### Q28: Why is offline attendance not automatically approved?
**Answer:**
Because client device clocks and offline coordinates can be spoofed, security governance dictates that offline punches must be flagged as `OFFLINE_SYNCED` and require manager or HR verification to ensure attendance integrity.
