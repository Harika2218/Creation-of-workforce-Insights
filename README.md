# Creation-of-workforce-Insights

A comprehensive enterprise repository combining workforce data analytics, machine learning research tasks, and a full-stack, autonomous Workforce Management Automation System.

---

## Repository Contents

### 1. Research & Analytics Tasks (Repository Root)
- **[`Model_Research.ipynb`](./Model_Research.ipynb)** — Machine learning research, feature analysis, and modeling methodologies for workforce insights.
- **[`Python_Task.ipynb`](./Python_Task.ipynb)** — Exploratory data analysis, employee metrics processing, and Python analytics.
- **[`SQL_TASK.ipynb`](./SQL_TASK.ipynb)** — Relational database queries, schema structuring, and workforce SQL operations.
- **[`LICENSE`](./LICENSE)** — MIT License governing this repository.

---

### 2. Autonomous Workforce Management Automation System (`workforce-management/`)
The **[`workforce-management/`](./workforce-management)** directory contains the complete, production-ready **InnovateCorp HRvantage** enterprise platform:

- **Backend (FastAPI / Python 3.12):** Asynchronous REST API exposing 141 operations across 118 paths with sub-20ms latency and 4-tier Role-Based Access Control (RBAC).
- **Frontend (React 19 / TypeScript / Vite):** Modern single-page application with PWA offline caching and an interactive Three.js 3D WebGL campus globe.
- **Database (MongoDB 7.0 Community):** Validated on an exact 200 regular employee baseline (`EMP001`–`EMP200`) with 100% relational integrity across 32 automated checks.
- **Predictive AI Engine (Scikit-learn / Statsmodels):** Absenteeism prediction (Random Forest, 72% acc), Attrition risk scoring (98% acc, 0.968 ROC-AUC), Isolation Forest anomaly detection, and Holt-Winters 30-day demand forecasting.
- **Grounded Conversational RAG Assistant:** HR policy chatbot featuring speech-to-text, verifiable section citations, prompt injection guardrails, and a pre-retrieval authorization gate.
- **Docker Production Deployment:** Multi-stage `Dockerfile` and `docker-compose.yml` for turnkey containerized orchestration.

> **Full Documentation & Runbook:** See **[`workforce-management/README.md`](./workforce-management/README.md)** for architecture diagrams, setup instructions, demo credentials, and API specifications.