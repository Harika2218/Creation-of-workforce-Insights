# Privacy & Data Handling Specification: GDPR-Ready Architecture

## Legal Disclaimer & Scope
> **NOTICE**: This document outlines the **GDPR-ready design / privacy-ready architecture** implemented within the AI-Powered Workforce Management Automation System. It does not constitute formal legal compliance certification, which requires organizational policy governance, statutory legal audits, and specific territorial legal review.

---

## 1. Principles of Privacy by Design

The platform adheres to key principles from modern international data protection standards (including the EU General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and India Digital Personal Data Protection Act (DPDP)):

1. **Lawfulness, Fairness, and Transparency**: Processing of personal employee records is restricted to legitimate employment operational workflows (time tracking, payroll computation, shift scheduling).
2. **Purpose Limitation**: Personal workforce information collected for attendance and compensation is never repurposed for unannounced automated profiling or external monetization.
3. **Data Minimization**: APIs and database queries return only the minimal necessary data attributes required for a specific role or screen view.
4. **Accuracy**: Comprehensive database integrity constraints prevent corrupted, out-of-sync, or duplicate records.
5. **Storage Limitation**: Documented retention schedules ensure operational data is archived or purged after regulatory periods expire.
6. **Integrity and Confidentiality (Security)**: Endpoints require authenticated JWT tokens with cryptographic signature validation, password hashing with salts, and strict role-based access control.
7. **Accountability & Auditability**: Every state-modifying action (create, update, approve, delete) is immutably logged to the MongoDB `audit_logs` collection.

---

## 2. Personal & Sensitive Data Inventory

The system processes the following categories of workforce personal data:

| Category | Data Fields | Sensitivity Level | Access Boundaries |
| :--- | :--- | :--- | :--- |
| **Identity & Contact** | Full name, corporate email, phone number, address, date of birth | Standard Personal Data | Self, Direct Manager, HR, Admin |
| **Employment Details** | Employee ID, designation, department, joining date, reporting manager | Internal Operational Data | Company-wide directory / Self |
| **Financial & Payroll** | Basic salary, HRA, bonuses, deductions, net compensation, bank details | Highly Sensitive Financial Data | Self (Employee) and HR/Admin only. **Never accessible to peer employees or department managers.** |
| **Biometric & Physical** | Clock-in timestamps, GPS coordinates, geofence validation results | Sensitive Operational Data | Self, Manager (attendance status only), HR |
| **Health & Leave** | Medical leave records, sick leave justifications, doctor notes | Special Category Health Data | Self, HR Administration |
| **AI Behavioral Insights** | Absenteeism probability, attrition risk score, productivity ratings | Decision-Support Inference Data | HR Administration & Authorized Managers |

---

## 3. Access Control & Tenant Data Isolation (RBAC)

The system enforces multi-tiered Role-Based Access Control across four canonical roles:

```text
               +----------------------------------+
               |        ADMIN (System Admin)      |
               | - Full system configuration      |
               | - Audit log inspection           |
               | - User account management        |
               +----------------------------------+
                                |
               +----------------------------------+
               |          HR (People Ops)         |
               | - Complete employee directory    |
               | - Organization-wide payroll      |
               | - AI Workforce intelligence      |
               | - Compliance monitoring          |
               +----------------------------------+
                                |
               +----------------------------------+
               |      MANAGER (Team Lead)         |
               | - Scoped to direct reports only  |
               | - Shift & leave approvals        |
               | - Team productivity metrics      |
               | - NO access to employee salaries |
               +----------------------------------+
                                |
               +----------------------------------+
               |     EMPLOYEE (Self-Service)      |
               | - Scoped strictly to own ID      |
               | - Own attendance, leave, shifts  |
               | - Own payslips & profile         |
               | - Zero peer record visibility    |
               +----------------------------------+
```

### Self-Service Scoping Invariant
When an authenticated request from an `EMPLOYEE` role hits `/api/v1/payroll/employee/{id}` or `/api/v1/attendance`:
1. The backend extracts `user["employee_id"]` from the cryptographically verified JWT token.
2. If the request attempts to query an `employee_id` other than the user's own ID, the backend immediately terminates the request with `HTTP 403 FORBIDDEN`.
3. Parameter tampering cannot bypass this boundary.

---

## 4. Multi-Factor Authentication (MFA) & Cryptographic Security

- **Password Storage**: Passwords are never stored in plaintext. They are hashed using SHA-256 with salts matching cryptographic storage standards.
- **Token Security**: Tokens are generated using JSON Web Tokens (JWT) signed via HMAC-SHA256 (`HS256`) with an 8-hour lifetime. Tampered or expired signatures are automatically rejected.
- **MFA (RFC 6238 TOTP)**: Users can configure multi-factor authentication using standard Authenticator applications (Google Authenticator, Microsoft Authenticator, Authy). When active, login requires both the password and a synchronized 6-digit TOTP code.

---

## 5. Audit Logging & Immutable Trails

The system logs all write operations to `db.audit_logs`:
- **Actor Identification**: Authenticated `user_id` and `employee_id`.
- **Action Type**: E.g., `LEAVE_APPROVED`, `TIMESHEET_SUBMITTED`, `PAYROLL_UPDATED`, `MFA_ENABLED`.
- **Target Entity**: E.g., `LV_A1B2C3`, `EMP004`.
- **Timestamp**: UTC ISO-8601 formatted timestamp.
- **IP / User-Agent**: Network origin metadata.
- **Data Minimization in Logs**: Passwords, authorization bearer tokens, and confidential bank numbers are explicitly sanitized and never stored in audit records.

---

## 6. Data Subject Rights (DSR) Implementation

The system architecture facilitates compliance with international data subject requests:

1. **Right of Access (Article 15 GDPR)**:
   - Employees can query their complete profile, leave balances, attendance logs, and payslips directly through the Employee Self-Service (ESS) portal.
   - HR can export an employee's comprehensive dossier via `/api/v1/employees/{id}`.

2. **Right to Rectification (Article 16 GDPR)**:
   - Employees can submit profile updates or raise discrepancy tickets with HR administration.

3. **Right to Erasure ("Right to be Forgotten" - Article 17 GDPR)**:
   - When an employee departs, their status is set to `Terminated` or `Archived`.
   - In production deployments requiring physical record erasure, an administrative script purges personal contact details while retaining anonymized attendance/payroll totals required by statutory labor accounting laws.

4. **Right to Restriction of Processing (Article 18 GDPR)**:
   - Inactive accounts (`is_active: 0`) are immediately blocked from all interactive logins and automated notifications.

---

## 7. Responsible AI & Anti-Bias Controls

1. **Decision Support, Not Automated Decisions**:
   - AI predictions (attrition probability, absenteeism likelihood, skill gaps) are clearly displayed as **advisory indicators** with contributing factor breakdowns.
   - No automated disciplinary action or employment termination can be executed autonomously by the AI models.

2. **Protected Attributes Exclusion**:
   - Training features for attrition and absenteeism models explicitly exclude sensitive protected attributes: gender, religion, race, national origin, and marital status.
   - Features are strictly operational: tenure, overtime hours, leave utilization, commute distance, and performance evaluation metrics.

---

## 8. Backup, Retention & Disaster Recovery Architecture

- **Active Operational Database**: Local MongoDB / MongoDB Atlas with Replica Sets.
- **Standard Backup Procedure**:
  ```bash
  # Daily encrypted archive backup procedure
  mongodump --uri="mongodb://localhost:27017/hr_automation" --archive=backup_hr_$(date +%Y%m%d).gz --gzip
  ```
- **Retention Schedule**:
  - Attendance Records: Retained for 3 years (statutory labor law compliance).
  - Payroll Records: Retained for 7 years (tax and audit compliance).
  - Temporary Notification Logs: Retained for 90 days.
  - Audit Logs: Retained for 5 years in write-once storage.
