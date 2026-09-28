# Final System Metrics & Empirical Factsheet

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Empirical System Telemetry & Metrics  
**Phase:** 13 — Final Consolidation  
**Audit Timestamp:** September 2026  

---

## 1. Core Data & Database Metrics

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Total Active Employee Records** | **200** | MongoDB `employees` (`EMP001`–`EMP200`), exactly 200 rows |
| **Total MongoDB Collections** | **52** | Verified via `db.list_collection_names()` |
| **Total Attendance Records** | **24,600** | MongoDB `attendance` collection |
| **Total Leave Balance Records** | **816** | MongoDB `leave_balances` collection |
| **Total Processed Payroll Records**| **1,200** | MongoDB `payroll_records` collection |
| **Database Relational Integrity Checks** | **28 / 28 Passed (100%)** | `scripts/validate_database.py` automated audit |
| **Duplicate Employee IDs** | **0** | Verified unique constraint on `employee_id` |
| **Self-Managing Employees** | **0** | Verified hierarchy acyclicity |
| **Orphan Attendance / Leave Records** | **0** | Relational foreign-key reference validation |

---

## 2. API & Backend Architecture Metrics

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Unique REST API Paths** | **103** | FastAPI OpenAPI 3.1.0 schema export (`docs/openapi.json`) |
| **Total HTTP REST Operations** | **124** | 103 paths across GET, POST, PUT, DELETE, PATCH |
| **Modular REST API Routers** | **14** | `backend/routers/` + Chatbot + Integrations + Health |
| **Pydantic Validation Schemas** | **45+** | `backend/schemas/` request & response models |
| **Backend Automated Tests (Pytest)** | **87 Passed / 0 Failed** | 10 test suites in `tests/test_*.py` (100% pass rate) |
| **Rate Limit Tiers Enforced** | **3** | Auth (10/min), AI/RAG (30/min), General (120/min) |
| **Maximum Request Body Limit** | **15 MB** | Starlette payload clamping middleware |
| **JWT Signature Algorithm** | **HS256 (Locked)** | PyJWT with disabled algorithm-confusion |

---

## 3. Frontend & User Interface Metrics

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Frontend Framework** | **React 19.2.8** | `frontend/package.json` |
| **Frontend Build Time (Vite)** | **1.17 seconds** | `tsc -b && vite build` clean rollup compilation |
| **Frontend Automated Tests (Vitest)**| **35 Passed / 0 Failed** | 8 test suites in `frontend/src/__tests__/` (100% pass rate) |
| **Application Client Routes** | **24 routes** | `frontend/src/routes/AppRoutes.tsx` |
| **Interactive 3D Engine** | **Three.js 0.186.1** | `@react-three/fiber` & `@react-three/drei` ambient canvas |
| **Responsive Viewports Tested** | **3** | Mobile (375x812), Tablet (768x1024), Desktop (1920x1080) |
| **PWA Web Manifest & Service Worker**| **Active** | `manifest.json`, IndexedDB offline queue |

---

## 4. Artificial Intelligence & Analytics Metrics

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Trained Machine Learning Models** | **3 Models** | Attrition (Random Forest), Absenteeism, Capacity |
| **Explainability Metric** | **Top 3 Features** | Overtime ratio, tenure, commute distance |
| **RAG Policy Vector Dimension** | **512 Dimensions** | TF-IDF Sublinear N-Gram Vectorizer (`backend/rag/embeddings.py`) |
| **RAG Document Chunking Overlap** | **50 Words** | Header-aware markdown chunker (`backend/rag/chunker.py`) |
| **RAG Retrieval Similarity Threshold**| **0.08 Cosine Sim** | Minimum threshold for candidate inclusion |
| **Chatbot Fallback Modes** | **2 Modes** | Local deterministic grounded engine + OpenAI cloud adapter |

---

## 5. Performance & Load Benchmarks

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Sustained API Throughput** | **162.64 requests/sec** | `reports/load_test_report.json` |
| **Mean Request Latency** | **48.2 ms** | 150 concurrent requests load run |
| **Median (P50) Latency** | **45.56 ms** | Load testing report |
| **95th Percentile (P95) Latency** | **84.43 ms** | Load testing report |
| **99th Percentile (P99) Latency** | **112.17 ms** | Load testing report |
| **HTTP Error Rate Under Load** | **0.00% (0 errors)** | 150/150 successful responses |

---

## 6. Project Governance & Documentation Metrics

| Metric | Measured Value | Verification Source |
| :--- | :---: | :--- |
| **Total Markdown Documentation Files**| **46 Documents** | Root `docs/` technical library |
| **Exported OpenAPI Specification Size**| **286.5 KB** | Complete `docs/openapi.json` |
| **Enterprise Integration Connectors** | **7 Connectors** | Slack, Teams, Google, SAP, Oracle, Entra ID, Biometric |
| **Total Test Assertions Across Stack** | **122 Automated Tests** | 87 Pytest backend + 35 Vitest frontend |
| **Overall Automated Test Pass Rate** | **100.0%** | Zero failing tests across both test runners |
