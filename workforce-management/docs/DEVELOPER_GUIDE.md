# Developer Guide & Engineering Handbook

## 1. Introduction

Welcome to the **InnovateCorp HRvantage** Developer Guide. This document provides technical instructions for software engineers, QA automation engineers, and DevOps specialists to set up, build, test, and contribute to the platform.

---

## 2. Architecture & Tech Stack Overview

- **Backend:** Python 3.10+, FastAPI (ASGI), Pydantic v2, PyMongo, Uvicorn
- **Frontend:** React 19, TypeScript, Vite, TailwindCSS / Vanilla CSS, Three.js, Lucide Icons
- **Database:** MongoDB Community / Enterprise 7.0+
- **Machine Learning:** scikit-learn, joblib, statsmodels, NumPy, Pandas
- **RAG & NLP:** TF-IDF 512D Vectorizer, OpenAI-compatible connector, Header-aware markdown chunker
- **Testing:** Pytest (Backend, 87+ tests), Vitest & React Testing Library (Frontend, 35+ tests)
- **Containerization:** Docker, Docker Compose multi-stage builds

---

## 3. Repository Directory Structure

```text
HR_Automation/
├── backend/                  # FastAPI ASGI Application
│   ├── ai/                   # AI Chatbot orchestration & services
│   ├── middleware/           # Security headers, rate limiting, exception handling
│   ├── monitoring/           # Prometheus metrics & health instrumentation
│   ├── rag/                  # RAG indexing, chunker, vector store, retriever
│   ├── routers/              # 14 REST API routers (auth, employees, attendance, etc.)
│   ├── schemas/              # Pydantic v2 request & response schemas
│   ├── security/             # JWT, password salting, RBAC deps, secrets manager
│   ├── services/             # Core business logic services
│   ├── config.py             # Central Pydantic BaseSettings configuration
│   └── main.py               # FastAPI entrypoint with async lifespan
├── frontend/                 # React 19 + TypeScript + Vite SPA / PWA
│   ├── src/
│   │   ├── __tests__/        # Vitest frontend unit and component tests
│   │   ├── components/       # Reusable UI components & 3D canvas
│   │   ├── context/          # AuthContext, NotificationContext, ThemeContext
│   │   ├── pages/            # Role dashboards, Attendance, Leave, Shifts, Payroll, etc.
│   │   ├── services/         # Axios API clients & IndexedDB offline store
│   │   └── App.tsx           # Router & navigation layout
│   ├── package.json          # Frontend dependencies & scripts
│   └── vite.config.ts        # Vite build & PWA plugin configuration
├── ai/                       # Classical ML Training & Inference Pipelines
│   ├── evaluation/           # Model validation & cross-validation metrics
│   ├── features/             # Feature engineering pipelines
│   ├── inference/            # Absenteeism, attrition, and forecasting estimators
│   ├── models/               # Saved model artifacts (.joblib / .pkl)
│   └── training/             # Scikit-learn training scripts
├── database/                 # MongoDB database connections and schema helpers
├── docs/                     # Architecture, API inventory, reports, and runbooks
├── scripts/                  # Synthetic data generators, validation, and maintenance
├── tests/                    # Backend Pytest test suites (unit, integration, security)
├── docker-compose.yml        # Multi-container orchestration definition
└── Dockerfile                # Production multi-stage Docker build
```

---

## 4. Local Development Environment Setup

### 4.1 Prerequisites
- **Python:** 3.10 or 3.11
- **Node.js:** v18.0.0+ (Node 20+ recommended) and npm 9+
- **MongoDB:** Version 6.0 or 7.0 running on `localhost:27017`
- **Git**

### 4.2 Database Setup & Verification
Ensure MongoDB is running locally:
```bash
# Verify MongoDB service status (Windows PowerShell)
Get-Service MongoDB

# Or start MongoDB service if stopped
Start-Service MongoDB

# Alternatively, run via Docker
docker run -d --name mongo-hr -p 27017:27017 mongo:7.0
```

### 4.3 Backend Setup
1. Open a terminal in the project root:
   ```bash
   cd c:\Users\evuri\Downloads\HR_Automation
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Copy `.env.example` to `.env` (or configure via environment):
   ```ini
   ENVIRONMENT=development
   DEBUG=true
   MONGODB_URI=mongodb://localhost:27017/hr_automation
   JWT_SECRET_KEY=hrvantage-dev-insecure-secret-key-replace-in-prod-2026
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=480
   RAG_EMBEDDING_PROVIDER=tfidf
   RAG_SIMILARITY_THRESHOLD=0.08
   LLM_PROVIDER=local
   ```

### 4.4 Synthetic Database Seeding & Validation
Seed the exact 200-employee baseline (`EMP001`–`EMP200`):
```bash
# Generate and seed complete database
python scripts/generate_synthetic_data.py

# Verify MongoDB integrity across 28 checks
python scripts/validate_database.py
```

### 4.5 Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Verify Vite development build:
   ```bash
   npm run build
   ```

---

## 5. Running the Application Locally

### 5.1 Starting the Backend Server
From the project root:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### 5.2 Starting the Frontend Dev Server
In a separate terminal:
```bash
cd frontend
npm run dev
```
- Web Application URL: `http://localhost:5173`

---

## 6. Running Test Suites

### 6.1 Backend Tests (Pytest)
Run all backend unit, integration, and security tests:
```bash
# Run complete test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=backend --cov-report=term-missing

# Run specific domain test
pytest tests/test_auth_rbac.py -v
```

### 6.2 Frontend Tests (Vitest)
From the `frontend/` directory:
```bash
# Run all frontend tests once
npm test -- --run

# Run with test coverage
npm test -- --coverage
```

### 6.3 Database Integrity Suite
Run the 28-point automated validation script:
```bash
python scripts/validate_database.py
```

---

## 7. AI Model & RAG Pipeline Maintenance

### 7.1 Retraining Workforce Intelligence Models
If new historical attendance or employee records are added:
```bash
# Train attrition and absenteeism models
python ai/training/train_models.py
```
Trained `.joblib` estimators are saved to `ai/models/` and loaded dynamically by `ai/inference/`.

### 7.2 Re-indexing RAG Policy Documents
To update HR policy documents or rebuild the vector index:
1. Place updated markdown policy files in `data/policies/`.
2. Run the policy ingestion service:
   ```bash
   python -c "from backend.rag.indexing_service import RAGIndexingService; RAGIndexingService().index_all_policies()"
   ```
3. Verify chunk counts in the `rag_policy_vectors` collection in MongoDB.

---

## 8. Docker & Production Deployment

### 8.1 Multi-Container Docker Compose
Start the full stack (FastAPI backend + Vite production build + MongoDB 7.0):
```bash
docker-compose up -d --build
```
Verify container status:
```bash
docker-compose ps
```

### 8.2 Health Checks
The Docker Compose configuration includes automated health checks:
- Backend: `curl -f http://localhost:8000/api/v1/health || exit 1`
- MongoDB: `mongosh --eval "db.adminCommand('ping')"`

---

## 9. CI/CD Pipeline (`.github/workflows/ci.yml`)

The repository includes GitHub Actions CI workflows that execute on every pull request and push to `main`:
1. **Linting & Formatting:** `black`, `isort`, `flake8` for Python; `eslint` for frontend.
2. **Backend Automated Tests:** Runs Pytest against a containerized MongoDB service.
3. **Frontend Automated Tests & Type Checking:** Runs `tsc -b && vitest --run`.
4. **Data Integrity Check:** Validates 200-employee synthetic schema.
5. **Docker Build:** Builds backend and frontend production container images to verify Dockerfile validity.

---

## 10. Troubleshooting & FAQ

| Symptom | Probable Cause | Resolution |
| :--- | :--- | :--- |
| `FastAPI: ConnectionRefusedError` | MongoDB service is stopped. | Run `Start-Service MongoDB` in PowerShell or start Docker Mongo. |
| `HTTP 429 Too Many Requests in tests` | Rate limiter triggering during high-frequency tests. | `TestClient` automatically bypasses limits in test mode. Ensure `ENVIRONMENT != production`. |
| `RAG answers with 'Insufficient policy info'` | Policy documents have not been indexed into MongoDB. | Execute `RAGIndexingService().index_all_policies()`. |
| `Frontend 3D background falls back to gradient` | WebGL disabled in browser or low-end GPU. | Normal behavior: the 3D canvas includes a graceful CSS fallback without blocking functionality. |
| `PyMongo NotImplementedError on bool(db)` | `if db:` checked on Database object in PyMongo 4+. | Use `if db is not None:` as patched in `database/mongodb.py`. |
