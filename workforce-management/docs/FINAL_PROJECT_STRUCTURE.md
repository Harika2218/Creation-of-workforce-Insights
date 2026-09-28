# Final Project Structure & Directory Topology

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Project Structure & Repository Organization  
**Phase:** 13 — Final Consolidation  

---

## 1. Top-Level Directory Organization

```text
HR_Automation/
├── .github/                  # CI/CD workflows and automated actions
│   └── workflows/
│       └── ci.yml            # Linting, testing, and Docker validation pipeline
├── ai/                       # Classical ML Training, Feature Engineering & Estimators
│   ├── evaluation/           # Cross-validation, fairness, and accuracy metrics
│   ├── features/             # Time-series and tabular feature extractors
│   ├── inference/            # Prediction engines (attrition, absenteeism, forecasting)
│   ├── models/               # Serialized .joblib model artifacts
│   └── training/             # Scikit-learn training scripts
├── backend/                  # FastAPI Asynchronous REST Application
│   ├── ai/
│   │   └── chatbot/          # Grounded RAG chatbot, guardrails, and intent classifier
│   ├── middleware/           # Security headers, rate limiting, and exception handlers
│   ├── monitoring/           # Prometheus metrics export & telemetry
│   ├── rag/                  # Document chunking, TF-IDF vectorizer, and vector store
│   ├── routers/              # 14 modular REST routers (auth, attendance, payroll, etc.)
│   ├── schemas/              # Pydantic v2 request and response data models
│   ├── security/             # JWT, password salting, RBAC dependencies, and secrets
│   ├── services/             # Core domain business logic engines
│   ├── config.py             # Central Pydantic BaseSettings environment manager
│   └── main.py               # Application entrypoint with ASGI async lifespan
├── backups/                  # Database backup scripts and disaster recovery snapshots
├── data/                     # Raw seed records, policy markdown files, and geofences
│   └── policies/             # Authoritative HR policy markdown documents (RAG source)
├── database/                 # MongoDB database connection pool and schema definitions
├── docs/                     # Comprehensive Phase 1–13 system documentation
│   ├── architecture/         # System topology diagrams and Mermaid specifications
│   ├── openapi.json          # Complete exported OpenAPI 3.1.0 API specification
│   └── [40+ Markdown Docs]  # Audits, guides, reports, runbooks, and baselines
├── frontend/                 # React 19 + TypeScript + Vite Single Page Application & PWA
│   ├── public/               # Static assets, favicon, and PWA web manifest
│   ├── src/
│   │   ├── __tests__/        # Vitest frontend unit and component tests
│   │   ├── components/       # Reusable UI widgets, cards, dialogs, and 3D canvas
│   │   │   └── 3d/           # Three.js / React Three Fiber interactive background
│   │   ├── context/          # React contexts (AuthContext, ThemeContext)
│   │   ├── pages/            # Role-specific dashboard views and feature modules
│   │   ├── services/         # Axios REST API client and IndexedDB offline store
│   │   ├── App.tsx           # Router navigation layout and protected routes
│   │   └── main.tsx          # React application root entrypoint
│   ├── package.json          # Frontend npm dependencies and scripts
│   ├── tsconfig.json         # TypeScript compiler configuration
│   └── vite.config.ts        # Vite build and PWA configuration
├── models/                   # Global model cache and evaluation artifacts
├── reports/                  # Automated verification and load testing reports
│   └── load_test_report.json # Empirical benchmark results (162.64 RPS, 48.2ms latency)
├── scripts/                  # Administration and synthetic verification utilities
│   ├── generate_synthetic_data.py # Seeds exact 200 employees (EMP001–EMP200)
│   ├── validate_database.py       # 28-point MongoDB relational-integrity validator
│   └── test_backend_live.py       # Live API endpoint smoke test runner
├── tests/                    # Backend Pytest test suites (87 passing tests)
│   ├── test_ai_workforce.py  # ML prediction and feature testing
│   ├── test_attendance.py    # Geofence check-in, check-out, and anomaly testing
│   ├── test_auth_rbac.py     # JWT authentication and role-boundary testing
│   ├── test_chatbot.py       # RAG retrieval and citation grounding tests
│   ├── test_database_integrity.py # Relational integrity assertions
│   ├── test_integrations.py  # External connector and circuit breaker tests
│   ├── test_leave.py         # Leave accruals, requests, and manager approvals
│   ├── test_payroll.py       # Overtime, deduction, and payslip calculation tests
│   ├── test_pwa_offline.py   # Offline queueing and sync validation
│   └── test_shifts.py        # Rotational shift allocation and swap tests
├── .dockerignore             # Docker build exclusion rules
├── .env.example              # Canonical reference environment variables
├── .gitignore                # Git repository exclusion rules
├── Dockerfile                # Production multi-stage Docker build specification
├── docker-compose.yml        # Multi-container orchestration specification
├── README.md                 # Complete platform documentation and quickstart
└── requirements.txt          # Python production dependencies specification
```

---

## 2. Directory Separation Rules

1. **Separation of Presentation and Backend**:
   - `frontend/` contains only client-side browser code (React, Vite, Three.js, CSS). It communicates with the backend strictly via JSON REST APIs over HTTP(S).
2. **Separation of Storage and Logic**:
   - `backend/` handles API routing, authentication, and validation.
   - `database/` manages MongoDB connection pools and collection indexing.
3. **Decoupled AI & Analytics**:
   - `ai/` contains model training, feature extraction, and offline pipelines.
   - `backend/ai/` contains the online inference adapters and RAG chatbot services.
4. **Isolated Test Suites**:
   - Backend tests are maintained in `tests/` and run via `pytest`.
   - Frontend tests are maintained in `frontend/src/__tests__/` and run via `vitest`.
