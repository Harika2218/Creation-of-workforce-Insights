# Verified Technology Stack Specification

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Technology Stack Verification & Provenance  
**Phase:** 13 — Final Consolidation  

---

## 1. Overview & Verification Standard

This document catalogs **only the technologies, frameworks, libraries, and tools actively implemented and validated** within the codebase. No planned, theoretical, or unintegrated technologies are listed.

---

## 2. Frontend Technologies

| Category | Technology | Version | Purpose in System | Evidence / Location |
| :--- | :--- | :--- | :--- | :--- |
| **Core Framework** | React | 19.2.8 | Single Page Application component tree, state management, hooks | `frontend/package.json` |
| **Language** | TypeScript | ~6.0.2 | Static typing, interface contracts, compile-time safety | `frontend/tsconfig.json` |
| **Build Tooling** | Vite | 8.3.0 | High-speed ESM dev server, production rollup bundling, PWA manifest | `frontend/vite.config.ts` |
| **Routing** | React Router DOM | 7.18.4 | Client-side routing, protected routes, role redirects | `frontend/src/App.tsx` |
| **3D Rendering** | Three.js | 0.186.1 | WebGL 3D ambient workplace scene, interactive floating nodes | `frontend/src/components/3d/` |
| **3D React Bridge** | @react-three/fiber | 9.8.1 | Declarative React wrapper for Three.js canvas management | `frontend/src/components/3d/` |
| **3D Helpers** | @react-three/drei | 10.7.9 | Three.js camera controls, mesh abstractions, shaders | `frontend/src/components/3d/` |
| **Animations** | Framer Motion | 13.4.4 | Smooth UI transitions, modal animations, toast popups | `frontend/src/components/` |
| **Data Visualization** | Recharts | 3.10.1 | Responsive attendance charts, attrition heatmaps, KPI gauges | `frontend/src/pages/` |
| **Iconography** | Lucide React | 1.47.0 | Clean, accessible SVG enterprise iconography | `frontend/src/components/` |
| **HTTP Client** | Axios | 1.20.0 | REST API client with JWT interceptors and error handling | `frontend/src/services/api.ts` |
| **Date Utilities** | date-fns | 4.4.0 | Time arithmetic, calendar rendering, shift intervals | `frontend/src/pages/Shifts.tsx` |
| **Unit Testing** | Vitest | 5.0.1 | Fast Vite-native unit testing runner (35 frontend tests) | `frontend/src/__tests__/` |
| **DOM Testing** | Testing Library | 16.3.3 | User-event and component rendering verification | `frontend/src/__tests__/` |
| **Linting** | Oxlint | 1.81.0 | Fast static JavaScript/TypeScript linting | `frontend/package.json` |

---

## 3. Backend Technologies

| Category | Technology | Version | Purpose in System | Evidence / Location |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | 3.10 / 3.11 | Backend service language, asynchronous runtime | `backend/` |
| **Web Framework** | FastAPI | >=0.115.0 | High-performance asynchronous REST API framework (124 ops) | `backend/main.py` |
| **ASGI Server** | Uvicorn (standard) | >=0.30.0 | Production ASGI HTTP server with uvloop event loop | `backend/main.py` |
| **Validation & Schema**| Pydantic v2 | >=2.8.0 | Strict request/response typing, serialization, BaseSettings | `backend/schemas/` |
| **HTTP Protocol Engine**| Starlette | >=0.38.0 | Underlying ASGI core, middleware pipeline, exception handling | `backend/middleware/` |
| **Database Driver** | PyMongo | >=4.8.0 | Official MongoDB Python driver with connection pooling | `database/mongodb.py` |
| **Token Authentication**| PyJWT | >=2.9.0 | JWT generation, verification, and HS256 algorithm enforcement | `backend/security/jwt.py` |
| **Cryptography** | Cryptography | >=43.0.0 | Cryptographic primitives, HMAC webhook signatures, salting | `backend/security/` |
| **HTTP Client** | HTTPX | >=0.27.0 | Async HTTP client for external connector health checks | `backend/services/` |
| **Unit & Integration** | Pytest | >=8.3.0 | Comprehensive automated test execution (87 tests) | `tests/` |
| **Synthetic Seeding** | Faker | >=26.0.0 | Deterministic mock data generation for baseline verification | `scripts/` |

---

## 4. Database & Storage

| Category | Technology | Version | Purpose in System | Evidence / Location |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Database** | MongoDB Community | 7.0 | Document store for 200 employees, 24,600 attendance records | `database/mongodb.py` |
| **Client Storage** | IndexedDB | Modern W3C | Browser-side offline attendance queue and cache | `frontend/src/services/offline.ts` |

---

## 5. Machine Learning & RAG Subsystem

| Category | Technology | Version | Purpose in System | Evidence / Location |
| :--- | :--- | :--- | :--- | :--- |
| **ML Framework** | scikit-learn | >=1.5.0 | Random Forest, Logistic Regression, Gradient Boosting models | `ai/training/` |
| **Model Serialization**| joblib | >=1.4.0 | Efficient serialization of trained scikit-learn estimators | `ai/models/` |
| **Numerical Arrays** | NumPy | >=1.26.0 | Feature vector manipulation and cosine similarity calculations | `backend/rag/` |
| **Data Processing** | Pandas | >=2.2.0 | Time series feature engineering and tabular rollups | `ai/features/` |
| **Embeddings (Local)**| TfidfVectorizer | scikit-learn | 512D deterministic offline embeddings for RAG policies | `backend/rag/embeddings.py` |
| **RAG Vector Storage** | MongoDB Collections | Native | Inverted index & cosine vector search collection | `backend/rag/vector_store.py` |

---

## 6. DevOps, Monitoring & Infrastructure

| Category | Technology | Version | Purpose in System | Evidence / Location |
| :--- | :--- | :--- | :--- | :--- |
| **Container Engine** | Docker | Engine 24+ | Multi-stage image builds for frontend and backend | `Dockerfile` |
| **Orchestration** | Docker Compose | Compose v2 | Multi-container stack (FastAPI + React + MongoDB) | `docker-compose.yml` |
| **CI / CD** | GitHub Actions | Workflows | Automated PR linting, Pytest, Vitest, and Docker builds | `.github/workflows/` |
| **Metrics Telemetry** | Prometheus Client | >=0.20.0 | Exposes `/metrics` endpoint with request latencies and memory | `backend/monitoring/` |
| **Structured Logging** | python-json-logger | >=3.0.0 | Structured JSON logging with security PII redaction | `backend/monitoring/` |
| **System Diagnostics** | psutil | >=6.0.0 | Host CPU, memory, and disk telemetry for health endpoint | `backend/routers/health.py` |
