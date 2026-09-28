# PRODUCTION & STAGING DEPLOYMENT RUNBOOK

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Standard Operating Procedure (SOP) — Deployment Runbook  
**Target Environments:** Staging / Production  
**Version:** 1.0 (Phase 12)  

---

## 1. Overview & Prerequisites

This runbook guides Site Reliability Engineers (SRE) and DevOps teams through the step-by-step procedure to deploy the system into a containerized staging or production environment.

### Target Host Prerequisites:
- **Operating System:** Linux (Ubuntu 22.04 LTS / Debian 12 / RHEL 9) or Windows Server 2022
- **Hardware:** Minimum 4 vCPU, 8 GB RAM, 50 GB SSD storage
- **Runtime:** Docker Engine 24.0+ and Docker Compose v2.20+ installed
- **Network Ingress:** Ports 80 (HTTP) and 443 (HTTPS) accessible
- **Database:** MongoDB 7.0+ (local container or MongoDB Atlas cluster)

---

## 2. Step-by-Step Deployment Procedure

### Step 1: Environment Preparation & Secret Configuration
1. Clone the repository into the deployment directory:
   ```bash
   git clone <enterprise-repo-url> /opt/hr-workforce
   cd /opt/hr-workforce
   ```
2. Copy the production environment template:
   ```bash
   cp .env.production.example .env
   ```
3. Generate high-entropy cryptographic keys and inject credentials:
   ```bash
   # Generate 256-bit JWT secret
   JWT_KEY=$(openssl rand -hex 32)
   sed -i "s/CHANGE_ME_IN_PRODUCTION_TO_HIGH_ENTROPY_256BIT_SECRET/$JWT_KEY/g" .env

   # Set production MongoDB URI and database name
   # nano .env
   ```
4. Verify file permissions on `.env` (restrict read access):
   ```bash
   chmod 600 .env
   ```

### Step 2: Preparing MongoDB & Initial Database Seeding
If deploying against a brand-new MongoDB cluster:
1. Verify connectivity:
   ```bash
   python -c "from database.mongodb import check_connection; print(check_connection())"
   ```
2. Seed the 200 synthetic employees and baseline historical data:
   ```bash
   python database/seed_database.py
   ```
3. Validate data invariants and constraints:
   ```bash
   python database/validate_database.py
   # Expect: VALIDATION SUMMARY: PASSED (28 / 28 checks)
   ```

### Step 3: Building Container Images
1. Build both Backend and Frontend production images using Docker Buildx:
   ```bash
   docker compose build --no-cache
   ```
2. Verify image security and size:
   ```bash
   docker images | grep hr-
   ```

### Step 4: Starting Services & Applying Indexes
1. Launch services in detached mode:
   ```bash
   docker compose up -d
   ```
2. Verify container states:
   ```bash
   docker compose ps
   # Expected: hr_mongodb (healthy), hr_backend (healthy), hr_frontend (healthy)
   ```
3. The backend container automatically triggers index reconciliation (`ensure_indexes`) and RAG document indexing during its lifespan startup sequence.

---

## 3. Post-Deployment Verification & Smoke Testing

Execute the automated verification sequence against the deployment:

### Step 5: Liveness & Readiness Probes
```bash
# Liveness probe
curl -i http://localhost:8000/api/v1/health/live
# Expected: HTTP/1.1 200 OK {"status":"alive", ...}

# Readiness probe
curl -i http://localhost:8000/api/v1/health/ready
# Expected: HTTP/1.1 200 OK {"status":"healthy", "dependencies":{...}}
```

### Step 6: Security Headers & Correlation ID Verification
```bash
curl -i http://localhost:8000/api/v1/health/live
# Verify response headers contain:
# X-Request-ID: REQ_...
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Content-Security-Policy: default-src 'self' ...
```

### Step 7: Authentication Smoke Test
Test login with the four standard enterprise personas (Password: `Demo@2026`):
```bash
# Admin Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"Demo@2026"}'

# Employee Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@demo.com","password":"Demo@2026"}'
```

### Step 8: Frontend & PWA Verification
1. Access `http://localhost/` (or production domain) in Chrome/Firefox.
2. Verify login screen loads cleanly without console errors.
3. Open DevTools > Application > Manifest:
   - Verify name: `AI-Powered Workforce Management Automation System`.
   - Verify Service Worker `sw.js` is registered and active.
4. Test responsive layout on mobile breakpoint (`<= 768px`) to ensure bottom navigation and slide-out drawer function properly.

### Step 9: Observability & Metrics Scrape
Confirm metrics endpoint responds with valid Prometheus data:
```bash
curl http://localhost:8000/api/v1/metrics
# Expected:
# # HELP hr_http_requests_total Total HTTP requests
# hr_http_requests_total ...
```

---

## 4. Operational Monitoring & Routine Maintenance

### Log Inspection
Inspect structured application logs in real-time:
```bash
# Backend logs
docker compose logs -f backend

# Frontend Nginx access logs
docker compose logs -f frontend
```

### Automated Backup Execution
Configure a crontab entry for daily automated backups at 02:00 UTC:
```bash
0 2 * * * cd /opt/hr-workforce && /usr/bin/python3 scripts/backup_database.py >> /var/log/hr_backup.log 2>&1
```

---

## 5. Emergency Rollback Procedure

If severe defects are discovered post-deployment:

1. Revert container image tags in `docker-compose.yml` to the prior stable release:
   ```bash
   docker compose down
   docker compose up -d
   ```
2. If database restoration is required:
   ```bash
   python scripts/restore_database.py backups/<pre-deployment-backup>.tar.gz hr_automation --drop
   python database/validate_database.py
   ```
3. Verify system health:
   ```bash
   curl -f http://localhost:8000/api/v1/health/ready
   ```
