# FINAL ROLE-BASED ACCESS CONTROL (RBAC) SECURITY MATRIX

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Final RBAC Matrix & Privilege Enforcement Specification  
**Phase:** 13 — Final Consolidation  
**Version:** 1.0  
**Security Model:** Authoritative Backend Enforcement + Role-Aware Frontend Adaptation  

---

## 1. Core Principle: Backend is Authoritative

While the React 19 frontend adapts navigation items, action buttons, and dashboard views based on the client's decoded JWT role, **client-side hiding is purely ergonomic and never trusted for security**. 

Every incoming request to the FastAPI backend is independently validated against:
1. **Cryptographic Signature:** JWT token signature verified with high-entropy secret (`HS256`).
2. **Account State:** Verification that the user document exists in MongoDB and `is_active == 1`.
3. **Role Scoping (`require_role`):** Role claims validated against the endpoint's allowed roles.
4. **Self/Ownership Scoping (`require_self_or_roles`):** Prevents peer-to-peer data snooping. Standard employees can only access records matching their authenticated `employee_id`.

---

## 2. Comprehensive RBAC Permissions Matrix

| Functional Domain | Resource / Action | EMPLOYEE | MANAGER | HR | ADMIN | Backend Dependency Enforcement |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Authentication** | Login, Refresh, Logout, MFA Setup | Allowed | Allowed | Allowed | Allowed | `get_current_user` |
| **Workforce Directory**| View Employee Directory | Scoped (Basic) | Scoped (Team) | Full | Full | `get_current_user` |
| | Onboard New Employee | Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| | Edit Employee Profile | Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| | Deactivate Employee | Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| **Attendance** | Check-in / Check-out (Self) | Allowed | Allowed | Allowed | Allowed | `get_current_user` |
| | View Attendance History (Self) | Allowed | Allowed | Allowed | Allowed | `require_self_or_roles(["HR", "ADMIN", "MANAGER"])` |
| | View Attendance History (Others) | Denied (403) | Scoped (Direct Reports) | Full | Full | `require_self_or_roles(["HR", "ADMIN"])` + Team check |
| | Audit Attendance Anomalies | Denied (403) | Scoped (Team) | Full | Full | `require_role(["ADMIN", "HR", "MANAGER"])` |
| **Shifts** | View Shift Roster | Scoped (Self) | Scoped (Team) | Full | Full | `require_self_or_roles(["HR", "ADMIN", "MANAGER"])` |
| | Submit Shift Swap Request | Allowed | Allowed | Allowed | Allowed | `get_current_user` |
| | Approve / Reject Shift Swap | Denied (403) | Allowed (Team) | Allowed | Allowed | `require_role(["MANAGER", "HR", "ADMIN"])` |
| | Create / Modify Shift Definitions | Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| **Leave Management** | View Leave Balances (Self) | Allowed | Allowed | Allowed | Allowed | `require_self_or_roles(["HR", "ADMIN", "MANAGER"])` |
| | View Leave Balances (Others) | Denied (403) | Scoped (Team) | Full | Full | `require_self_or_roles(["HR", "ADMIN"])` |
| | Submit Leave Request (Self) | Allowed | Allowed | Allowed | Allowed | `get_current_user` |
| | Approve / Reject Leave | Denied (403) | Allowed (Team) | Allowed | Allowed | `require_role(["MANAGER", "HR", "ADMIN"])` |
| **Timesheets** | Log Billable / Non-Billable Hours | Allowed | Allowed | Allowed | Allowed | `get_current_user` |
| | Approve / Reject Timesheets | Denied (403) | Allowed (Team) | Allowed | Allowed | `require_role(["MANAGER", "HR", "ADMIN"])` |
| **Payroll** | View Own Historical Payslips | Allowed | Allowed | Allowed | Allowed | `require_self_or_roles(["HR", "ADMIN"])` |
| | View Other Employees' Payslips | **Denied (403)** | **Denied (403)** | Allowed | Allowed | `require_self_or_roles(["HR", "ADMIN"])` |
| | View Monthly Payroll Cost Analytics| Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| **Workforce AI** | Query Own AI Insights (Attrition/Gaps)| Allowed | Allowed | Allowed | Allowed | `verify_employee_access` |
| | Query Peer AI Insights | **Denied (403)** | Scoped (Team) | Full | Full | `verify_employee_access` |
| | 30/90-Day Headcount Forecasting | Denied (403) | Denied (403) | Allowed | Allowed | `require_role(["ADMIN", "HR"])` |
| | Staffing & Fatigue Recommendations | Denied (403) | Allowed (Team) | Allowed | Allowed | `require_role(["ADMIN", "HR", "MANAGER"])` |
| **Performance** | View Own Appraisal Review | Allowed | Allowed | Allowed | Allowed | `require_self_or_roles(["HR", "ADMIN", "MANAGER"])` |
| | Create Appraisal Review | Denied (403) | Allowed (Team) | Allowed | Allowed | `require_role(["MANAGER", "HR", "ADMIN"])` |
| **Administration** | User Account Management & Roles | Denied (403) | Denied (403) | Denied (403) | Allowed | `require_role(["ADMIN"])` |
| | System Audit Logs (`audit_logs`) | Denied (403) | Denied (403) | Denied (403) | Allowed | `require_role(["ADMIN"])` |
| | External Connectors & Sync History | Denied (403) | Denied (403) | Denied (403) | Allowed | `require_role(["ADMIN"])` |
| | Inbound Webhooks (`HMAC-SHA256`) | Denied (403) | Denied (403) | Denied (403) | Allowed | `verify_webhook_signature` |

---

## 3. Negative Security Test Evidence

The automated test suite (`tests/test_production_verification.py`) rigorously validates that privilege escalations are decisively blocked with HTTP 401 or HTTP 403:

### Test Case 1: Employee Attempting to Access HR Onboarding Endpoint
- **Action:** Authenticated `employee@demo.com` (`EMP004`) executes `POST /api/v1/employees`.
- **Backend Response:** `HTTP 403 Forbidden` (`detail: Access forbidden: requires one of the following roles: ADMIN, HR`).
- **Assertion:** `assert res.status_code == 403`. Verified passing.

### Test Case 2: Employee Attempting to Snooping Peer Payslips
- **Action:** Authenticated `employee@demo.com` (`EMP004`) executes `GET /api/v1/payroll/employee/EMP002`.
- **Backend Response:** `HTTP 403 Forbidden` (`detail: Access forbidden: you do not have permission to access another employee's records`).
- **Assertion:** `assert res.status_code == 403`. Verified passing.

### Test Case 3: Manager Attempting to View System Audit Logs
- **Action:** Authenticated `manager@demo.com` (`EMP003`) executes `GET /api/v1/reports/audit-logs`.
- **Backend Response:** `HTTP 403 Forbidden` (`detail: Access forbidden: requires one of the following roles: ADMIN`).
- **Assertion:** `assert res.status_code == 403`. Verified passing.

### Test Case 4: Manager Attempting to Trigger External Integration Sync
- **Action:** Authenticated `manager@demo.com` (`EMP003`) executes `POST /api/v1/integrations/teams/sync`.
- **Backend Response:** `HTTP 403 Forbidden` (`detail: Access forbidden: requires one of the following roles: ADMIN`).
- **Assertion:** `assert res.status_code == 403`. Verified passing.

### Test Case 5: Unauthenticated Client Accessing Protected Resource
- **Action:** Client sends `GET /api/v1/attendance/today` with no `Authorization` header.
- **Backend Response:** `HTTP 401 Unauthorized` (`detail: Authentication credentials were not provided or invalid`).
- **Assertion:** `assert res.status_code == 401`. Verified passing.
