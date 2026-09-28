# PRODUCTION DEPLOYMENT ARCHITECTURE DIAGRAM

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** `docs/diagrams/deployment_architecture.md`  

---

```mermaid
graph TB
    subgraph Edge_Network ["Edge Network & Reverse Proxy"]
        DNS["Enterprise DNS (api.hrvantage.internal)"]
        SSL["TLS Termination (HTTPS :443)"]
        Nginx["Nginx Reverse Proxy / Load Balancer"]
    end

    subgraph Container_Orchestration ["Docker Compose Runtime Environment"]
        subgraph Frontend_Container ["Container 1: Frontend SPA / PWA"]
            ViteDist["Nginx Alpine Static Server (:80 / :5173)
            • Built via Vite 8.3 / React 19
            • Service Worker (sw.js) for PWA Offline Caching"]
        end

        subgraph Backend_Container ["Container 2: FastAPI ASGI Service (:8000)"]
            FastAPIServer["Uvicorn Workers (4 Asynchronous Workers)
            • Python 3.12+ Runtime
            • Health Probes: GET /health, GET /ready
            • Serialized AI Models Loaded in Memory"]
        end

        subgraph Database_Container ["Container 3: MongoDB 7.0 Engine (:27017)"]
            MongoInstance["MongoDB Community Server 7.0
            • WiredTiger Storage Engine
            • Named Docker Volume (mongo_data)
            • Database: hr_automation"]
        end
    end

    subgraph Observability_Backups ["Observability & Backup Layer"]
        MetricsEndpoint["Prometheus Metrics (/api/v1/metrics)"]
        AuditTrail["Audit Logs Collection"]
        BackupUtility["scripts/backup_database.py (Daily tar.gz snapshots)"]
    end

    DNS --> SSL --> Nginx
    Nginx -->|Route / & /assets| Frontend_Container
    Nginx -->|Route /api/v1 & /health| Backend_Container

    Backend_Container -->|PyMongo Connection Pool| Database_Container
    Backend_Container --> MetricsEndpoint
    Backend_Container --> AuditTrail
    Database_Container --> BackupUtility
```
