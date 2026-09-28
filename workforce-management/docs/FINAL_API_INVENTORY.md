# FINAL API INVENTORY & REST ENDPOINT CATALOG — PHASE 15

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document Reference:** `docs/FINAL_API_INVENTORY.md`  
**API Specification:** OpenAPI 3.1.0 (`docs/openapi.json`)  
**Total Production Endpoints:** **141 Operations across 118 Paths**  
**Protocol & Format:** JSON over HTTPS / ASGI FastAPI  
**Authentication Standard:** HTTP Authorization Header `Bearer <JWT_TOKEN>`  

---

## 1. Authentication & Identity Management (`/api/v1/auth`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/auth/login` | Authenticate credentials & issue JWT tokens | No | Public | `LoginRequest` | `TokenResponse` | 400, 401, 429 |
| `POST` | `/api/v1/auth/refresh` | Exchange valid refresh token for new access token | Yes | All Roles | `RefreshTokenRequest` | `TokenResponse` | 401, 429 |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile and scopes | Yes | All Roles | None | `UserResponse` | 401 |
| `POST` | `/api/v1/auth/logout` | Terminate session and invalidate token | Yes | All Roles | None | `MessageResponse` | 401 |
| `POST` | `/api/v1/auth/mfa/setup` | Generate Base32 TOTP secret and QR barcode URI | Yes | All Roles | None | `MFASetupResponse` | 401 |
| `POST` | `/api/v1/auth/mfa/enable` | Verify 6-digit TOTP code and enable 2FA | Yes | All Roles | `MFAVerifyRequest` | `MessageResponse` | 400, 401 |
| `POST` | `/api/v1/auth/mfa/disable` | Deactivate 2FA for authenticated user | Yes | All Roles | `MFAVerifyRequest` | `MessageResponse` | 400, 401 |
| `GET` | `/api/v1/auth/roles` | List all available RBAC roles | Yes | All Roles | None | `List[RoleResponse]` | 401 |

---

## 2. Employee Management (`/api/v1/employees`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/employees` | Search and paginate workforce directory | Yes | All Roles | Query params | `EmployeeListResponse` | 401 |
| `POST` | `/api/v1/employees` | Onboard new employee into organization | Yes | `ADMIN`, `HR` | `EmployeeCreate` | `EmployeeResponse` | 400, 401, 403 |
| `GET` | `/api/v1/employees/{id}` | Get employee profile by employee ID | Yes | All Roles | None | `EmployeeResponse` | 401, 404 |
| `PUT` | `/api/v1/employees/{id}` | Update employee demographic and job fields | Yes | `ADMIN`, `HR` | `EmployeeUpdate` | `EmployeeResponse` | 400, 401, 403, 404 |
| `DELETE`| `/api/v1/employees/{id}` | Soft-deactivate employee account | Yes | `ADMIN`, `HR` | None | `MessageResponse` | 401, 403, 404 |
| `GET` | `/api/v1/employees/{id}/profile` | Complete profile with manager and direct reports | Yes | Self / Privileged | None | `FullProfileResponse` | 401, 403, 404 |
| `GET` | `/api/v1/employees/{id}/org-chart` | Hierarchical management tree for employee | Yes | All Roles | None | `OrgChartNode` | 401, 404 |

---

## 3. Department Management (`/api/v1/departments`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/departments` | List all corporate departments and headcounts | Yes | All Roles | None | `List[DepartmentResponse]` | 401 |
| `POST` | `/api/v1/departments` | Create new department | Yes | `ADMIN`, `HR` | `DepartmentCreate` | `DepartmentResponse` | 400, 401, 403 |
| `GET` | `/api/v1/departments/{id}` | Retrieve department details and manager info | Yes | All Roles | None | `DepartmentResponse` | 401, 404 |
| `PUT` | `/api/v1/departments/{id}` | Update department metadata or department head | Yes | `ADMIN`, `HR` | `DepartmentUpdate` | `DepartmentResponse` | 400, 401, 403, 404 |

---

## 4. Attendance & Geofenced Clocking (`/api/v1/attendance`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/attendance/check-in` | Punch clock-in with GPS / Geofence validation | Yes | All Roles | `PunchRequest` | `AttendanceResponse` | 400, 401 |
| `POST` | `/api/v1/attendance/check-out` | Punch clock-out and calculate total hours | Yes | All Roles | `PunchRequest` | `AttendanceResponse` | 400, 401 |
| `POST` | `/api/v1/attendance/qr-punch` | Clock-in using time-sensitive dynamic QR token | Yes | All Roles | `QRPunchRequest` | `AttendanceResponse` | 400, 401 |
| `POST` | `/api/v1/attendance/biometric-sync` | Ingest punch payload from hardware terminal | Yes | `ADMIN`, `HR` | `BiometricPunchBatch` | `BatchSyncResponse` | 400, 401, 403 |
| `GET` | `/api/v1/attendance/today` | Fetch today's punch state for current user | Yes | All Roles | None | `AttendanceResponse` | 401 |
| `GET` | `/api/v1/attendance/history` | Historical attendance logs with date filtering | Yes | Self / Privileged | Query params | `List[AttendanceResponse]` | 401, 403 |
| `GET` | `/api/v1/attendance/anomalies` | Fetch Isolation Forest flagged attendance anomalies | Yes | `ADMIN`, `HR`, `MANAGER` | Query params | `List[AnomalyResponse]` | 401, 403 |
| `GET` | `/api/v1/attendance/stats` | Monthly presence, absence, and late-in stats | Yes | Self / Privileged | Query params | `AttendanceStats` | 401 |

---

## 5. Shift Scheduling & Peer Swaps (`/api/v1/shifts`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/shifts` | List configured shifts (Morning, Evening, Night) | Yes | All Roles | None | `List[ShiftResponse]` | 401 |
| `POST` | `/api/v1/shifts` | Define new shift window and grace period | Yes | `ADMIN`, `HR` | `ShiftCreate` | `ShiftResponse` | 400, 401, 403 |
| `GET` | `/api/v1/shifts/{id}` | Get specific shift details | Yes | All Roles | None | `ShiftResponse` | 401, 404 |
| `POST` | `/api/v1/shifts/assign` | Assign shift schedule to employee | Yes | `ADMIN`, `HR`, `MANAGER` | `ShiftAssignRequest` | `MessageResponse` | 400, 401, 403 |
| `GET` | `/api/v1/shifts/employee/{id}` | Get current scheduled shift for employee | Yes | Self / Privileged | None | `EmployeeShiftResponse` | 401, 403, 404 |
| `POST` | `/api/v1/shifts/swap-request` | Initiate peer-to-peer shift swap proposal | Yes | `EMPLOYEE` | `ShiftSwapCreate` | `ShiftSwapResponse` | 400, 401 |
| `GET` | `/api/v1/shifts/swap-requests` | List shift swap requests for team / department | Yes | `MANAGER`, `HR` | Query params | `List[ShiftSwapResponse]` | 401, 403 |
| `PUT` | `/api/v1/shifts/swap-requests/{id}` | Manager approve or reject swap request | Yes | `MANAGER`, `HR` | `SwapDecision` | `ShiftSwapResponse` | 400, 401, 403, 404 |

---

## 6. Leave Management (`/api/v1/leave` & `/api/v1/holidays`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/leave/requests` | List leave requests with status filtering | Yes | Self / Privileged | Query params | `List[LeaveResponse]` | 401 |
| `POST` | `/api/v1/leave/requests` | Submit formal leave application | Yes | All Roles | `LeaveCreateRequest` | `LeaveResponse` | 400, 401 |
| `GET` | `/api/v1/leave/requests/{id}` | Get individual leave request details | Yes | Self / Privileged | None | `LeaveResponse` | 401, 404 |
| `PUT` | `/api/v1/leave/requests/{id}/approve`| Manager approval and quota deduction | Yes | `MANAGER`, `HR` | None | `LeaveResponse` | 400, 401, 403, 404 |
| `PUT` | `/api/v1/leave/requests/{id}/reject` | Manager rejection with reason | Yes | `MANAGER`, `HR` | `LeaveRejectRequest` | `LeaveResponse` | 400, 401, 403, 404 |
| `GET` | `/api/v1/leave/balances/{id}` | Get remaining leave balances per category | Yes | Self / Privileged | None | `LeaveBalanceResponse` | 401, 404 |
| `GET` | `/api/v1/holidays` | List corporate and regional paid holidays | Yes | All Roles | Query params | `List[HolidayResponse]` | 401 |

---

## 7. Timesheets & Project Hours (`/api/v1/timesheets`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/timesheets` | Query weekly timesheets with pagination | Yes | Self / Privileged | Query params | `List[TimesheetResponse]` | 401 |
| `POST` | `/api/v1/timesheets` | Create or update weekly timesheet draft | Yes | All Roles | `TimesheetCreate` | `TimesheetResponse` | 400, 401 |
| `GET` | `/api/v1/timesheets/{id}` | Get specific timesheet breakdown | Yes | Self / Privileged | None | `TimesheetResponse` | 401, 404 |
| `PUT` | `/api/v1/timesheets/{id}/status` | Submit or approve/reject weekly timesheet | Yes | `MANAGER`, `HR` | `TimesheetStatusUpdate` | `TimesheetResponse` | 400, 401, 403, 404 |
| `GET` | `/api/v1/timesheets/projects` | List active billable projects | Yes | All Roles | None | `List[ProjectResponse]` | 401 |

---

## 8. Payroll & Compensation (`/api/v1/payroll`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/payroll` | Enterprise payroll records with period filter | Yes | `ADMIN`, `HR` | Query params | `List[PayrollResponse]` | 401, 403 |
| `POST` | `/api/v1/payroll/calculate` | Execute monthly payroll batch run | Yes | `ADMIN`, `HR` | `PayrollRunRequest` | `PayrollRunSummary` | 400, 401, 403 |
| `GET` | `/api/v1/payroll/employee/{id}` | Historical payslips for target employee | Yes | Self / Privileged | Query params | `List[PayrollResponse]` | 401, 403, 404 |
| `GET` | `/api/v1/payroll/payslip/{id}` | Detailed digital payslip breakdown | Yes | Self / Privileged | None | `PayslipDetailResponse` | 401, 403, 404 |
| `GET` | `/api/v1/payroll/export` | Export payroll records in CSV / JSON | Yes | `ADMIN`, `HR` | Query params | Streaming File | 401, 403 |

---

## 9. Performance Management (`/api/v1/performance`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/performance/reviews` | List appraisal reviews with role scoping | Yes | Self / Privileged | Query params | `List[ReviewResponse]` | 401 |
| `POST` | `/api/v1/performance/reviews` | Submit performance review / appraisal | Yes | `MANAGER`, `HR` | `ReviewCreate` | `ReviewResponse` | 400, 401, 403 |
| `GET` | `/api/v1/performance/goals/{id}` | Fetch active employee OKR goals | Yes | Self / Privileged | None | `List[GoalResponse]` | 401, 404 |
| `PUT` | `/api/v1/performance/goals/{id}` | Update OKR goal progress percentage | Yes | Self / Privileged | `GoalProgressUpdate` | `GoalResponse` | 400, 401, 404 |
| `GET` | `/api/v1/performance/scorecards/{id}` | Holistic employee performance scorecard | Yes | Self / Privileged | None | `ScorecardResponse` | 401, 404 |

---

## 10. Skills Gap & Competency Engine (`/api/v1/skills`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/skills/catalog` | Master directory of recognized technical skills | Yes | All Roles | None | `List[SkillItem]` | 401 |
| `GET` | `/api/v1/skills/employee/{id}` | Employee verified skill proficiency matrix | Yes | Self / Privileged | None | `EmployeeSkillsResponse` | 401, 404 |
| `GET` | `/api/v1/skills/gap-analysis` | Explainable skill gap comparison vs role benchmark | Yes | `ADMIN`, `HR`, `MANAGER` | Query params | `SkillGapAnalysisResult` | 401, 403 |

---

## 11. Training & Upskilling (`/api/v1/training`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/training/catalog` | Catalog of corporate training courses | Yes | All Roles | None | `List[CourseResponse]` | 401 |
| `GET` | `/api/v1/training/recommendations`| Targeted training recommendations for skill gaps | Yes | Self / Privileged | Query params | `List[TrainingRecommendation]` | 401, 403 |
| `POST` | `/api/v1/training/enroll` | Enroll employee in corporate course | Yes | Self / Privileged | `EnrollmentRequest` | `EnrollmentResponse` | 400, 401 |

---

## 12. Manager Operations (`/api/v1/manager`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/manager/team-attendance` | Real-time presence status of direct reports | Yes | `MANAGER`, `HR` | None | `TeamAttendanceSummary` | 401, 403 |
| `GET` | `/api/v1/manager/pending-approvals` | Consolidated approval inbox (leaves, swaps) | Yes | `MANAGER`, `HR` | None | `PendingApprovalsList` | 401, 403 |
| `GET` | `/api/v1/manager/team-utilization` | Weekly project utilization and billable hours | Yes | `MANAGER`, `HR` | Query params | `TeamUtilizationReport` | 401, 403 |

---

## 13. HR Analytics & Executive Overview (`/api/v1/hr`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/hr/dashboard` | Workforce summary KPIs (headcount, attrition) | Yes | `ADMIN`, `HR` | None | `HRDashboardResponse` | 401, 403 |
| `GET` | `/api/v1/hr/executive-summary` | Consolidated executive metrics for leadership | Yes | `ADMIN`, `HR` | None | `ExecutiveSummaryResponse` | 401, 403 |
| `GET` | `/api/v1/hr/attrition-analysis` | Detailed churn drivers and exit trends | Yes | `ADMIN`, `HR` | None | `AttritionAnalysisResponse` | 401, 403 |

---

## 14. Enterprise Reports Engine (`/api/v1/reports`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/reports/attendance` | Comprehensive attendance audit report | Yes | `ADMIN`, `HR` | Query params | `ReportDataResponse` | 401, 403 |
| `GET` | `/api/v1/reports/payroll` | Financial tax liability and disbursement report | Yes | `ADMIN`, `HR` | Query params | `ReportDataResponse` | 401, 403 |
| `GET` | `/api/v1/reports/export` | Download generated report in CSV / Excel | Yes | `ADMIN`, `HR` | Query params | Streaming File | 401, 403 |

---

## 15. Notifications & Workflows (`/api/v1/notifications` & `/api/v1/workflows`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/notifications` | Get user notifications with filtering | Yes | All Roles | Query params | `List[NotificationItem]` | 401 |
| `GET` | `/api/v1/notifications/unread-count`| Get unread notification badge counter | Yes | All Roles | None | `UnreadCountResponse` | 401 |
| `PATCH` | `/api/v1/notifications/{id}/read` | Mark individual notification as read | Yes | All Roles | None | `NotificationItem` | 401, 404 |
| `POST` | `/api/v1/notifications/read-all` | Mark all user notifications as read | Yes | All Roles | None | `MessageResponse` | 401 |
| `GET` | `/api/v1/notifications/preferences` | Get user delivery channel preferences | Yes | All Roles | None | `PreferencesResponse` | 401 |
| `PUT` | `/api/v1/notifications/preferences` | Update notification channel preferences | Yes | All Roles | `PreferencesUpdate` | `PreferencesResponse` | 400, 401 |
| `GET` | `/api/v1/workflows/status` | Automation scheduler & rule engine state | Yes | `ADMIN`, `HR` | None | `SchedulerStatusResponse` | 401, 403 |
| `POST` | `/api/v1/workflows/run-scheduled` | Manually trigger scheduled HR rule passes | Yes | `ADMIN`, `HR` | None | `WorkflowRunResponse` | 401, 403 |

---

## 16. AI Workforce Intelligence & Simulation (`/api/v1/ai`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/ai/absenteeism-risk` | ML predicted absenteeism risk for upcoming shift | Yes | `ADMIN`, `HR`, `MANAGER` | Query params | `List[AbsenteeismRisk]` | 401, 403 |
| `GET` | `/api/v1/ai/attrition-risk` | Attrition risk index and explainable risk factors | Yes | `ADMIN`, `HR` | Query params | `List[AttritionRisk]` | 401, 403 |
| `GET` | `/api/v1/ai/demand-forecast` | 30-day time-series workforce demand forecast | Yes | `ADMIN`, `HR` | Query params | `List[DemandForecast]` | 401, 403 |
| `GET` | `/api/v1/ai/staffing-recommendations`| Recommended staffing levels per department | Yes | `ADMIN`, `HR`, `MANAGER` | None | `List[StaffingRecommendation]` | 401, 403 |
| `GET` | `/api/v1/ai/productivity-scores` | Composite productivity scoring across workforce | Yes | `ADMIN`, `HR`, `MANAGER` | Query params | `List[ProductivityScore]` | 401, 403 |
| `POST` | `/api/v1/ai/simulation` | Deterministic workforce scenario simulation | Yes | `ADMIN`, `HR` | `SimulationRequest` | `SimulationResult` | 400, 401, 403 |

---

## 17. AI HR Policy Assistant & RAG (`/api/v1/chatbot`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/chatbot/query` | Conversational RAG query with exact citations | Yes | All Roles | `ChatbotQueryRequest` | `ChatbotQueryResponse` | 400, 401, 429 |
| `GET` | `/api/v1/chatbot/history` | Retrieve user conversation history | Yes | All Roles | Query params | `List[ChatMessageResponse]` | 401 |
| `DELETE`| `/api/v1/chatbot/history` | Clear conversational context | Yes | All Roles | None | `MessageResponse` | 401 |

---

## 18. Multi-Campus Location Management (`/api/v1/locations`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/locations` | List corporate campus locations and geofences | Yes | All Roles | None | `List[LocationResponse]` | 401 |
| `POST` | `/api/v1/locations` | Register new office campus / geofence | Yes | `ADMIN`, `HR` | `LocationCreate` | `LocationResponse` | 400, 401, 403 |
| `GET` | `/api/v1/locations/{id}` | Get specific campus geofence coordinates | Yes | All Roles | None | `LocationResponse` | 401, 404 |
| `PUT` | `/api/v1/locations/{id}` | Update campus geofence radius or coordinates | Yes | `ADMIN`, `HR` | `LocationUpdate` | `LocationResponse` | 400, 401, 403, 404 |

---

## 19. Contractor & Vendor Management (`/api/v1/contractors`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/contractors` | List third-party contractors and vendors | Yes | `ADMIN`, `HR` | Query params | `List[ContractorResponse]` | 401, 403 |
| `POST` | `/api/v1/contractors` | Onboard contractor with vendor agency & rate card | Yes | `ADMIN`, `HR` | `ContractorCreate` | `ContractorResponse` | 400, 401, 403 |
| `GET` | `/api/v1/contractors/timesheets` | Query contractor timesheets and vendor billing | Yes | `ADMIN`, `HR` | Query params | `List[ContractorTimesheetResponse]`| 401, 403 |
| `POST` | `/api/v1/contractors/timesheets`| Submit contractor billable hours | Yes | `ADMIN`, `HR` | `ContractorTimesheetCreate` | `ContractorTimesheetResponse` | 400, 401, 403 |

---

## 20. Statutory Compliance Rule Engine (`/api/v1/compliance`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/compliance/rules` | List active regulatory labor compliance rules | Yes | `ADMIN`, `HR` | None | `List[ComplianceRule]` | 401, 403 |
| `GET` | `/api/v1/compliance/violations` | Query active violations (overtime breaches, rest limits) | Yes | `ADMIN`, `HR` | Query params | `List[ComplianceViolation]` | 401, 403 |
| `POST` | `/api/v1/compliance/resolve/{id}`| Record compliance resolution and audit remarks | Yes | `ADMIN`, `HR` | `ResolveViolationRequest` | `ComplianceViolation` | 400, 401, 403, 404 |

---

## 21. External Integrations & Connectors (`/api/v1/integrations`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/integrations` | List connector health and configuration state | Yes | `ADMIN` | None | `List[IntegrationHealth]` | 401, 403 |
| `GET` | `/api/v1/integrations/{name}` | Get individual integration status | Yes | `ADMIN` | None | `IntegrationHealth` | 401, 403, 404 |
| `POST` | `/api/v1/integrations/{name}/test` | Trigger non-destructive connection probe | Yes | `ADMIN` | None | `TestConnectionResult` | 401, 403, 404 |
| `POST` | `/api/v1/integrations/{name}/sync` | Trigger manual data synchronization pass | Yes | `ADMIN` | None | `SyncResultResponse` | 401, 403, 404 |
| `GET` | `/api/v1/integrations/{name}/sync-history`| Telemetry history of connector sync runs | Yes | `ADMIN` | None | `List[SyncHistoryItem]` | 401, 403, 404 |
| `POST` | `/api/v1/integrations/webhooks/{provider}`| Ingest inbound webhook with HMAC verification | No | Provider HMAC | Webhook payload | `MessageResponse` | 400, 401, 429 |

---

## 22. System Administration, Audit Logs & Health (`/api/v1/admin`, `/health`, `/ready`)

| Method | Path | Summary / Purpose | Auth | Roles | Request Body | Response Body | Error Codes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/admin/audit-logs` | Query system audit trail with user and IP filters | Yes | `ADMIN` | Query params | `List[AuditLogResponse]` | 401, 403 |
| `GET` | `/health` | Liveness health check | No | Public | None | `HealthStatus` | None |
| `GET` | `/ready` | Deep readiness check (DB, AI models, scheduler) | No | Public | None | `ReadinessStatus` | 503 |
| `GET` | `/api/v1/metrics` | Prometheus metrics exposition format | No | Public / Monitor | Query params | Text / JSON Metrics | None |
| `GET` | `/api/v1/docs` | Swagger OpenAPI UI | No | Public | None | HTML UI | None |
| `GET` | `/api/v1/redoc` | ReDoc OpenAPI UI | No | Public | None | HTML UI | None |
| `GET` | `/api/v1/openapi.json` | Complete OpenAPI 3.1.0 JSON specification | No | Public | None | JSON Document | None |
