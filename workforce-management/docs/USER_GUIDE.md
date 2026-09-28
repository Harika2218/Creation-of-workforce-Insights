# InnovateCorp HRvantage — Enterprise User Guide

## Welcome to InnovateCorp HRvantage

**InnovateCorp HRvantage** is an enterprise-grade AI-powered workforce management platform that streamlines daily operations, attendance telemetry, shift scheduling, leave workflows, timesheet tracking, payroll inputs, and workforce intelligence.

This user guide provides step-by-step instructions for all four platform roles: **Employee**, **Manager**, **HR Administrator**, and **System Administrator**.

---

## 1. Getting Started & Authentication

### 1.1 Accessing the Platform
1. Open your web browser (Chrome, Edge, Firefox, or Safari) and navigate to the application URL:
   - **Local Environment:** `http://localhost:5173`
   - **Production Environment:** Your company's secure domain (e.g. `https://hr.innovatecorp.internal`)
2. Enter your corporate email and password on the 3D-assisted login screen.
3. If MFA is enabled on your profile, enter the 6-digit TOTP code from Google Authenticator or Microsoft Authenticator.
4. Click **Sign In**. The system will authenticate your credentials and automatically route you to your role-specific dashboard.

> [!TIP]
> **Demo Environment Credentials:**
> - **Employee:** `employee@demo.com` / `Demo@2026`
> - **Manager:** `manager@demo.com` / `Demo@2026`
> - **HR Specialist:** `hr@demo.com` / `Demo@2026`
> - **Administrator:** `admin@demo.com` / `Demo@2026`

---

## 2. Employee User Guide

As an employee, HRvantage provides a self-service hub for your daily work activities.

### 2.1 Daily Attendance & Check-In
1. Navigate to **Attendance** from the navigation bar or use the quick punch widget on your **Employee Dashboard**.
2. **Web / Desktop Check-In:**
   - Click **Punch In**.
   - If prompted by your browser, click **Allow** to share your GPS location. HRvantage validates your coordinates against authorized office geofences (default: InnovateCorp HQ).
   - Once validated, your attendance status updates to **PRESENT** with exact timestamp and geofence tag.
3. **QR Code Attendance:**
   - Click **Show QR Code** on your mobile device to scan at office kiosk terminals.
4. **End of Day:**
   - Click **Punch Out** before concluding your work day. The system calculates total work duration and overtime hours automatically.
5. **Regularization & Attendance History:**
   - View your monthly attendance calendar, late arrivals (15-minute grace period applied), and approved regularizations under the **Attendance History** tab.

### 2.2 Applying for Leave
1. Navigate to **Leave Management**.
2. Review your real-time **Leave Balances** card (Annual, Casual, Sick, Maternity/Paternity).
3. Click **Apply for Leave**.
4. Fill in:
   - **Leave Type**: Select from the dropdown menu.
   - **Date Range**: Choose start and end dates.
   - **Reason**: Brief explanation for your manager.
5. Click **Submit Application**. Your manager receives an immediate notification. You will be notified the instant they approve or reject the request.

### 2.3 Shift Calendar & Swap Requests
1. Navigate to **Shifts**.
2. View your assigned rotational shifts (Morning, General, Evening, Night) on the visual calendar.
3. **Requesting a Shift Swap:**
   - Click on the target shift date.
   - Select **Request Swap**.
   - Choose a qualified peer from your department and specify the swap date.
   - Click **Submit Swap Request**. Once your peer accepts, your manager receives the approval ticket.

### 2.4 Weekly Timesheet Submission
1. Navigate to **Timesheets**.
2. Log your daily work hours broken down by project and client billing category.
3. Verify that total weekly hours match your expected schedule (typically 40.0 hours).
4. Click **Submit Timesheet** at the end of each week for managerial sign-off.

### 2.5 Accessing Payslips
1. Navigate to **Payroll / Payslips**.
2. Select the desired pay period (e.g. `September 2026`).
3. View the complete compensation breakdown:
   - Basic salary, HRA, special allowances, overtime incentives.
   - Deductions: Tax (TDS), Provident Fund, unpaid absence deductions.
4. Click **Download PDF** to export your official company payslip.

### 2.6 AI HR Assistant (Chatbot & Policy Retrieval)
1. Click the **AI Assistant** icon in the bottom right corner or select **AI Chatbot** from the menu.
2. Ask any policy question in plain natural language:
   - *"What is our paternity leave policy?"*
   - *"What are the core collaboration hours for remote work?"*
   - *"How do I claim health insurance for outpatient care?"*
3. The AI provides a grounded, concise answer accompanied by **clickable citations** linking directly to the authoritative company policy document and section.

### 2.7 Notifications
- Click the **Bell Icon** in the top navigation header to view real-time updates regarding leave approvals, shift changes, company holidays, and automated attendance reminders.
- Click **Mark as Read** or configure your notification channel preferences (In-App, Email, Slack/Teams).

---

## 3. Manager User Guide

Managers possess supervisory permissions over their assigned department and direct reports.

### 3.1 Team Attendance & Real-Time Monitoring
1. Navigate to **Manager Dashboard > Team Attendance**.
2. View live status of all direct reports:
   - Present, On Leave, Late Arrival, Shift Off, or Absent.
3. Review flagged attendance anomalies (e.g. repeated late arrivals, early departures, or missed check-outs).

### 3.2 Approving Leave Requests
1. Navigate to **Leave Approvals**.
2. Review pending leave applications with employee details, leave balance history, and team overlap calendar.
3. Click **Approve** or **Reject** (rejections require mandatory feedback comments).
4. The employee is instantly notified, and team shift rosters update automatically.

### 3.3 Shift Allocation & Swap Authorizations
1. Navigate to **Shift Roster**.
2. Use the interactive team roster to reassign shifts, balance morning/evening coverage, and resolve scheduling conflicts.
3. Review pending **Shift Swap Requests** initiated between team members. Click **Approve** to execute the swap in the database.

### 3.4 Timesheet Verification & Approval
1. Navigate to **Timesheet Approvals**.
2. Inspect submitted weekly timesheets for billable project accuracy and overtime claims.
3. Approve valid timesheets or return them with revision notes.

### 3.5 Team Productivity & Workforce Analytics
1. Navigate to **Team Analytics**.
2. Review departmental KPIs:
   - Average weekly hours, project utilization rate, scheduled vs. actual hours.
   - Early warning indicators for employee burnout and excessive overtime.

---

## 4. HR Administrator User Guide

HR Administrators manage enterprise workforce policies, employee master records, payroll inputs, and organizational intelligence.

### 4.1 Employee Lifecycle Management
1. Navigate to **Employees**.
2. Search, filter by department/role, or inspect any of the **200 employee profiles**.
3. **Onboarding a New Employee:**
   - Click **Add Employee**.
   - Enter personal details, assigned department, manager ID, job title, and employment start date.
   - The system automatically provisions user login credentials and baseline leave allocations.
4. **Profile Management:**
   - Update job titles, department transfers, salary structures, and active/inactive status.

### 4.2 Attendance Policy & Anomaly Administration
1. Navigate to **Attendance Analytics**.
2. Inspect organization-wide attendance trends, absenteeism heatmaps, and geofence compliance.
3. Configure office geofence locations and tolerance radiuses under **Settings**.

### 4.3 Payroll Processing & Export
1. Navigate to **Payroll Management**.
2. Click **Run Monthly Payroll Calculation**.
3. The engine automatically synchronizes with:
   - Approved attendance logs and biometric records.
   - Calculated overtime hours.
   - Approved unpaid leave deductions.
4. Review generated payslip records, verify net payout totals, and click **Export Bank ACH / CSV** for finance disbursement.

### 4.4 Performance Management & Scorecards
1. Navigate to **Performance**.
2. Set organizational quarterly KPI targets and competencies.
3. Launch review cycles (Self-Appraisal, Manager Review, HR Calibration).
4. Generate department scorecards and performance distribution graphs.

### 4.5 AI Workforce Intelligence
1. Navigate to **Workforce Intelligence**.
2. **Attrition Risk Prediction**: Inspect ML-predicted turnover probabilities across departments, identifying top retention risk factors.
3. **Absenteeism Forecasting**: Review predicted absence spikes to adjust staffing allocations proactively.
4. **Staffing & Skill Gap Analysis**: View AI-generated recommendations for hiring and training needs based on current department project workloads.

---

## 5. System Administrator User Guide

System Administrators maintain platform security, user accounts, integrations, and operational health.

### 5.1 User Management & Role-Based Access Control (RBAC)
1. Navigate to **Admin > User Management**.
2. Provision new user accounts, reset passwords, and toggle active status.
3. Assign platform roles (`EMPLOYEE`, `MANAGER`, `HR`, `ADMIN`) with immediate authorization enforcement.

### 5.2 External Integrations & Connectors
1. Navigate to **Admin > Integrations**.
2. Inspect the health and synchronization status of enterprise connectors:
   - **Collaboration:** Microsoft Teams, Slack, Google Workspace.
   - **Enterprise HRMS:** SAP SuccessFactors, Oracle Fusion HCM.
   - **Identity:** Microsoft Entra ID (Azure AD).
   - **Hardware:** ZKTeco Biometric Terminals.
3. Click **Test Connection** to verify API endpoint latency and credential validity.
4. Click **Sync Now** to trigger an on-demand bidirectional synchronization run.

### 5.3 Audit Log Inspection & Security Telemetry
1. Navigate to **Admin > Audit Logs**.
2. Search and filter immutable audit records by actor user ID, action type, IP address, or timestamp range.
3. Export audit logs to JSON or CSV for external SIEM integration and compliance reviews.

### 5.4 System Health & Monitoring
1. Navigate to **Admin > System Health** or query `/api/v1/health`.
2. Inspect real-time status of:
   - MongoDB database connection pool and query latency.
   - Background workflow queue and notification dispatchers.
   - Disk usage, memory utilization, and ASGI request throughput.
3. Review database backup status and execute disaster recovery snapshots.

---

## 6. Mobile & Progressive Web App (PWA) Usage

HRvantage is a fully responsive Progressive Web App optimized for iOS and Android smartphones and tablets.

### 6.1 Installing the PWA
- **iOS (Safari):** Open the HRvantage URL, tap the **Share** button, and select **Add to Home Screen**.
- **Android (Chrome):** Tap the **Install App** banner or select **Add to Home screen** from the browser menu.

### 6.2 Mobile Capabilities
- Mobile-optimized attendance check-in with GPS geofencing.
- QR code attendance badge generation.
- Touch-friendly leave applications and manager one-tap approvals.
- Offline attendance queueing: If network connectivity is lost, check-in attempts are saved securely in browser IndexedDB and uploaded when reconnected.

---

## 7. Support & Troubleshooting

If you encounter issues:
1. **Forgot Password:** Contact your HR Administrator or System Administrator to initiate a secure reset token.
2. **GPS Attendance Denied:** Ensure location permissions are set to **Allow** in your browser site settings (`chrome://settings/content/location`).
3. **Internal Error:** Note the incident timestamp and report the issue to your IT Helpdesk with your Employee ID.
