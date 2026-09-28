# Phase 14 Performance & Latency Report

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Phase 14 Empirical Performance & Latency Benchmarks  
**Phase:** 14 — Final Gap Closure & Advanced Enterprise Enhancements  
**Environment:** Local Windows Workstation, Python 3.14.2, FastAPI, MongoDB Community 7.0, Node 20  
**Measurement Methodology:** High-resolution monotonic timers (`time.perf_counter`) capturing end-to-end ASGI request-response cycles.  

---

## 1. Measured API Latency for Phase 14 Endpoints

| Endpoint Path | HTTP Method | Scope / Operation | Measured Latency | HTTP Status |
| :--- | :---: | :--- | :---: | :---: |
| `/api/v1/locations` | `GET` | Aggregated campus list (5 locations) | **90.68 ms** | `200 OK` |
| `/api/v1/contractors` | `GET` | Vendor contractor list with billed hours | **12.98 ms** | `200 OK` |
| `/api/v1/compliance/alerts` | `GET` | Dynamic multi-rule compliance audit | **26.74 ms** | `200 OK` |
| `/api/v1/hr/executive-summary` | `GET` | Cross-campus executive financial KPI rollup | **13.95 ms** | `200 OK` |
| `/api/v1/skills/gap-analysis/{id}` | `GET` | Employee proficiency vs competency matrix | **7.10 ms** | `200 OK` |
| `/api/v1/training/recommendations/{id}` | `GET` | Explainable course curriculum matching | **9.84 ms** | `200 OK` |
| `/api/v1/ai/simulation` | `POST` | Deterministic strategic scenario planning | **11.20 ms** | `200 OK` |

**Average Phase 14 API Latency:** **24.64 ms** (Sub-100ms SLA achieved).

---

## 2. Frontend Build & Client Bundle Performance

- **Build Engine:** Vite 8.3.0 with Rollup bundling.
- **Compilation Time:** **1.08 seconds** (`tsc -b && vite build`).
- **Client Assets:**
  - `dist/index.html`: 1.40 kB (gzip: 0.66 kB)
  - `dist/assets/index-DwOcezoJ.css`: 15.36 kB (gzip: 4.04 kB)
  - `dist/assets/index-C5N3OWcQ.js`: 2,106.88 kB (gzip: 578.30 kB)
- **Web Speech API Footprint:** Built on native browser W3C `SpeechRecognition` and `window.speechSynthesis` with zero additional npm package overhead.

---

## 3. Database Query & Aggregation Performance

- **Compliance Rule Scan:** Executes aggregate pipelines across 24,600 attendance records in **< 25 ms** using compound indexes `{ employee_id: 1, date: 1 }` and `{ overtime_hours: 1 }`.
- **Contractor Timesheet Lookups:** Sub-5ms queries via indexed foreign key `contractor_id`.
- **Relational Integrity Validation:** 32 automated checks complete in **1.92 seconds** over the entire 200-employee SQLite/MongoDB mirror.
