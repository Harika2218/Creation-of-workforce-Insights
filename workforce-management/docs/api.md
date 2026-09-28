# FastAPI REST API Backend Documentation
## AI-Powered Workforce Management Automation System (Phase 3)

This document provides complete technical documentation for the FastAPI REST API backend service connecting to MongoDB (`hr_automation`).

---

## 1. Getting Started

### Prerequisites
- Python 3.14+
- MongoDB 8.x running locally (`mongodb://localhost:27017/`) or MongoDB Atlas
- Environment configuration file `.env`

### Starting the FastAPI Server
To launch the live backend server:
```powershell
# From the project root: HR_Automation/
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Interactive Documentation URLs
Once the server is running:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema (JSON)**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- **Live Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 2. Authentication & Demo Credentials

Authentication uses signed JWT bearer tokens (`HS256`, 8-hour expiry). Include the token in the HTTP `Authorization` header:
```text
Authorization: Bearer <your_jwt_access_token>
```

### Demo Accounts for Testing & Development
| Role | Email | Password | Linked Employee ID | Permissions |
|---|---|---|---|---|
| **ADMIN** | `admin@demo.com` | `Demo@2026` | `EMP001` | Unrestricted system-wide access |
| **HR** | `hr@demo.com` | `Demo@2026` | `EMP003` | Full employee lifecycle, company payroll, leaves, reports |
| **MANAGER** | `manager@demo.com` | `Demo@2026` | `EMP002` | Scoped team attendance, leaves, timesheets, shifts |
| **EMPLOYEE** | `employee@demo.com` | `Demo@2026` | `EMP050` | Self-service profile, attendance clocking, own leaves, timesheets, payslips |

---

## 3. Role-Based Access Control (RBAC) Matrix

| Endpoint Group | `EMPLOYEE` | `MANAGER` | `HR` | `ADMIN` |
|---|---|---|---|---|
| `/auth/login`, `/auth/me` | Allowed | Allowed | Allowed | Allowed |
| `/employees` (List/Search) | Allowed | Allowed | Allowed | Allowed |
| `/employees` (Create/Update/Deactivate) | Forbidden | Forbidden | **Allowed** | **Allowed** |
| `/departments` (Create/Update) | Forbidden | Forbidden | **Allowed** | **Allowed** |
| `/attendance/check-in`, `/check-out` | Self Only | Self Only | Any Employee | Any Employee |
| `/payroll/summary` | **Forbidden (403)** | **Forbidden (403)** | **Allowed** | **Allowed** |
| `/payroll/employee/{id}` | Self Only | Forbidden (403) | **Allowed** | **Allowed** |
| `/leave/requests` (Apply) | Self | Self | Self / Any | Any |
| `/leave/requests/{id}/approve` | Forbidden | **Team Only** | **Allowed** | **Allowed** |
| `/manager/team/*` | **Forbidden (403)** | **Own Team** | **Allowed** | **Allowed** |
| `/hr/summary` | **Forbidden (403)** | **Forbidden (403)** | **Allowed** | **Allowed** |
| `/reports/*` | Forbidden | Scoped | **Allowed** | **Allowed** |

---

## 4. Complete API Endpoints Catalog (75 Unique Endpoints)

### System & Health
- `GET /` - Root service metadata
- `GET /api/v1/health` - MongoDB database connectivity and status

### Authentication
- `POST /api/v1/auth/login` - Obtain JWT bearer token with credentials
- `GET /api/v1/auth/me` - Get profile of authenticated user

### Employees
- `GET /api/v1/employees` - List employees with pagination and filters (`department_id`, `role`, `location_id`, `employment_status`, `search`)
- `GET /api/v1/employees/{employee_id}` - Get employee details
- `GET /api/v1/employees/{employee_id}/profile` - Enriched profile with department, location, manager, skills, leave balances
- `POST /api/v1/employees` - Onboard new employee (validates unique ID, unique email, referenced department/location/manager)
- `PUT /api/v1/employees/{employee_id}` - Update employee profile
- `DELETE /api/v1/employees/{employee_id}` - Soft deactivation (`employment_status = "Deactivated"`)

### Departments
- `GET /api/v1/departments` - List departments with active employee counts
- `GET /api/v1/departments/{department_id}` - Get department by ID
- `POST /api/v1/departments` - Create department
- `PUT /api/v1/departments/{department_id}` - Update department

### Attendance & GPS Geofencing
- `POST /api/v1/attendance/check-in` - Clock in with GPS coordinates, method validation, duplicate prevention
- `POST /api/v1/attendance/check-out` - Clock out with automatic work hours and overtime calculation
- `GET /api/v1/attendance` - Query attendance history with pagination and status filters
- `GET /api/v1/attendance/summary` - Aggregated attendance metrics (present, absent, late, overtime, rate)
- `GET /api/v1/attendance/{employee_id}` - Attendance logs for specific employee

### Shifts
- `GET /api/v1/shifts` - List shift templates (General, Morning, Evening, Night)
- `GET /api/v1/shifts/{shift_id}` - Get shift details
- `POST /api/v1/shifts` - Create new shift
- `GET /api/v1/shifts/employee/{employee_id}` - Employee active shift schedule
- `POST /api/v1/shifts/assign` - Assign shift schedule to employee
- `POST /api/v1/shifts/swap-request` - Submit shift swap request
- `GET /api/v1/shifts/swap-requests` - Query swap requests
- `PUT /api/v1/shifts/swap-requests/{swap_id}` - Manager approval/rejection of shift swaps

### Leave Management
- `GET /api/v1/leave/types` - Available leave types (Annual, Sick, Casual, Emergency, Maternity/Paternity)
- `GET /api/v1/leave/balance/{employee_id}` - Employee leave balances
- `GET /api/v1/leave/requests` - Query leave applications with status filtering
- `POST /api/v1/leave/requests` - Apply for leave (validates balance and date order)
- `GET /api/v1/leave/requests/{leave_id}` - Single leave application details
- `POST /api/v1/leave/requests/{leave_id}/approve` - Manager approval and balance deduction
- `POST /api/v1/leave/requests/{leave_id}/reject` - Manager rejection with reason

### Holidays
- `GET /api/v1/holidays` - Official company holiday calendar
- `POST /api/v1/holidays` - Create holiday
- `PUT /api/v1/holidays/{holiday_id}` - Update holiday
- `DELETE /api/v1/holidays/{holiday_id}` - Delete holiday

### Timesheets
- `GET /api/v1/timesheets` - Query daily work logs with pagination
- `POST /api/v1/timesheets` - Submit work log (`billable + non_billable == hours_worked`)
- `GET /api/v1/timesheets/{timesheet_id}` - Get timesheet entry
- `POST /api/v1/timesheets/{timesheet_id}/approve` - Manager approval
- `POST /api/v1/timesheets/{timesheet_id}/reject` - Manager rejection with reason

### Projects
- `GET /api/v1/projects` - List active projects (Project Alpha, Beta, etc.)
- `GET /api/v1/projects/{project_id}` - Get project details
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/{project_id}` - Update project

### Payroll (RBAC Protected)
- `GET /api/v1/payroll` - Query payroll records
- `GET /api/v1/payroll/{payroll_id}` - Specific payslip
- `GET /api/v1/payroll/employee/{employee_id}` - Employee payslip history
- `GET /api/v1/payroll/summary` - Company payroll disbursement totals

### Performance
- `GET /api/v1/performance` - Performance appraisals
- `GET /api/v1/performance/{employee_id}` - Employee appraisal history
- `POST /api/v1/performance` - Submit appraisal review

### Skills & Training
- `GET /api/v1/skills` - Enterprise skills catalog
- `GET /api/v1/skills/employee/{employee_id}` - Employee skill proficiencies
- `POST /api/v1/skills/employee/{employee_id}` - Map skill to employee profile
- `GET /api/v1/training` - Training history and AI recommendations
- `GET /api/v1/training/employee/{employee_id}` - Employee training records
- `GET /api/v1/training/programs` - Training course catalog

### Manager Portal
- `GET /api/v1/manager/team` - Reporting direct reports
- `GET /api/v1/manager/team/summary` - Team headcount, present, on leave, pending approvals
- `GET /api/v1/manager/team/attendance` - Team attendance records
- `GET /api/v1/manager/team/leave` - Team leave applications
- `GET /api/v1/manager/team/shifts` - Team shift schedules

### HR Analytics
- `GET /api/v1/hr/summary` - Global overview metrics (headcount, active, notice, payroll, attrition)
- `GET /api/v1/hr/employee-summary` - Department and status distributions

### Reports
- `GET /api/v1/reports/attendance` - Attendance breakdown by status
- `GET /api/v1/reports/overtime` - Top overtime performers
- `GET /api/v1/reports/leave` - Company leave utilization
- `GET /api/v1/reports/payroll` - Historical compensation trends
- `GET /api/v1/reports/department-performance` - Average KPI and productivity by department

### Notifications
- `GET /api/v1/notifications` - Get current user notifications
- `POST /api/v1/notifications` - Dispatch notification
- `PUT /api/v1/notifications/{notification_id}/read` - Mark notification as read

---

## 5. Automated Testing Instructions

Run the complete test suite:
```powershell
# Run backend API tests (24 test cases)
pytest tests/test_backend_api.py -v

# Run database integrity tests (10 test cases)
pytest tests/test_database.py -v

# Run all tests together (34 test cases)
pytest tests/ -v

# Run live server verification
python scripts/verify_live_api.py
```
