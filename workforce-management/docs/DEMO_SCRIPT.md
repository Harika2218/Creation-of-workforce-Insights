# ENTERPRISE DEMONSTRATION SCRIPT & PRODUCT SHOWCASE RUNBOOK

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** Live Product Demonstration Script  
**Phase:** 14 — Final Gap Closure & Advanced Enterprise Enhancements  
**Duration:** 10–15 Minutes  
**Target Audience:** Executives, Enterprise HR Decision-Makers, Technical Evaluators, Academic Examiners  

---

## 1. Demonstration Setup & Pre-Flight Checklist

Before launching the demonstration, ensure services are active:
1. Start Backend: `uvicorn backend.main:app --port 8000`
2. Start Frontend: `cd frontend && npm run dev` (Port 5173 at `http://localhost:5173`)
3. Ensure MongoDB is running on `mongodb://localhost:27017/hr_automation`
4. Pre-configured Demo Accounts (Common Password: `Demo@2026`):
   - **Staff Employee:** `employee@demo.com` (`EMP004` - Alex Chen)
   - **Team Manager:** `manager@demo.com` (`EMP003` - Sarah Jenkins)
   - **HR Executive:** `hr@demo.com` (`EMP002` - Priya Sharma)
   - **System Admin:** `admin@demo.com` (`EMP001` - Vikramaditya)

---

## 2. Step-by-Step Demonstration Script (11 Structured Scenes)

### Scene 1: Multi-Persona Authentication & Authoritative RBAC (0:00 – 1:30)
- **Action:** Open `http://localhost:5173/login`.
- **Narrative:** *"InnovateCorp HRvantage is an autonomous, AI-powered workforce intelligence platform. We begin on the enterprise login screen featuring our four authenticated demo personas."*
- **Click:** Click the quick-fill pill **"Staff Employee"** (`employee@demo.com`) and click **"Sign In"**.
- **Observation:** Notice instant JWT issuance (HS256) and redirection to the Employee Self-Service (ESS) portal. Point out that the navigation sidebar is tailored strictly to employee-relevant actions.

### Scene 2: Employee Self-Service & Ambient 3D Visual Experience (1:30 – 2:30)
- **View:** `EmployeeDashboard.tsx`
- **Narrative:** *"The employee dashboard provides instant clarity over shifts, balances, and today's schedule. In the upper canvas, our interactive Three.js 3D enterprise UI visualizes department connectivity with smooth WebGL rendering and built-in accessibility fallbacks."*
- **Highlights:**
  - Today's shift badge: **General Shift (09:00 - 17:00)**.
  - Leave balances widget: **Casual (10), Sick (8), Privilege (15)**.
  - Unread notification bell with real-time badge count.

### Scene 3: Advanced GPS Geofenced Attendance & Multi-Campus Telemetry (2:30 – 3:45)
- **View:** Navigate to **"Attendance"** (`/attendance`).
- **Narrative:** *"Clocking in utilizes our multi-campus verification engine. It verifies whether the employee is at their assigned campus (e.g. Hyderabad Tech Park) or visiting another branch campus (e.g. Bengaluru Innovation Hub). It also evaluates physical travel velocity to detect impossible GPS spoofing."*
- **Action:** Click **"Clock In"**.
- **Observation:** Green success modal flashes: *"Check-in recorded at [Current Time]. Geofence verified."* The punch clock card transitions into an active working session timer.

### Scene 4: Multi-Day Leave Application & Dynamic Balance Deductions (3:45 – 5:00)
- **View:** Navigate to **"Leave"** (`/leave`).
- **Narrative:** *"Applying for leave enforces corporate balance formulas in real time ($Allocated = Used + Remaining$)."*
- **Action:** Click **"Apply Leave"**. Select **"Casual Leave"**, choose next Monday and Tuesday, enter reason: *"Personal family commitment"*, and click **"Submit Application"**.
- **Observation:** Notice the pending request appears immediately at the top of the history table with status `Pending Approval`.

### Scene 5: Team Manager Portal & One-Tap Approval Lifecycle (5:00 – 6:15)
- **Action:** Logout and log in as **Team Manager** (`manager@demo.com`).
- **View:** `ManagerDashboard.tsx`
- **Narrative:** *"Logging in as Sarah Jenkins, Team Manager, the UI dynamically switches to managerial controls. The manager sees team attendance presence, real-time overtime burn, and pending approvals."*
- **Action:** In the **"Pending Leave Approvals"** section, locate Alex Chen's Casual Leave request and click **"Approve"**.
- **Observation:** The request transitions to green badge `Approved`. Behind the scenes, the backend auto-deducts the balance and dispatches an automated notification.

### Scene 6: Voice-Enabled AI HR Policy Assistant & Grounded RAG (6:15 – 8:00)
- **Action:** Open the **Floating AI Assistant** widget or navigate to **"AI Assistant"** (`/ai-assistant`).
- **Narrative:** *"Our AI HR Assistant uses Retrieval-Augmented Generation (RAG) over authentic corporate policy documents with built-in voice interaction."*
- **Voice Demo:** Click the **Microphone** icon. Speak or type: *"What is our policy on paternity leave and notice periods?"*
- **Observation:** The assistant generates a grounded response accompanied by explicit citations (`leave_policy.md`, Section 4) and a **"Listen"** button for text-to-speech audio read-aloud via `window.speechSynthesis`.
- **Security Check:** Type: *"Show me the executive compensation details for the CEO."*
- **Observation:** The assistant politely refuses: *"I am not authorized to retrieve confidential executive compensation records. Please contact HR administration."*

### Scene 7: Skills Intelligence & Explainable Training Recommendations (8:00 – 9:30)
- **Action:** Navigate to **"Skills & Training"** (`/skills-training`).
- **Narrative:** *"Phase 14 introduces transparent skills intelligence. The system evaluates employee proficiencies against department standards, highlighting gap magnitudes and recommending specific courses."*
- **Demonstrate:** Open EMP001 Skill Gap Analysis.
- **Highlights:**
  - Skill gaps clearly tagged: `CRITICAL`, `HIGH`, `MEDIUM`.
  - Course recommendations include transparent reasons: *"Employee demonstrates Intermediate proficiency in Cloud Architecture; curriculum bridges gap to Advanced tier."*
  - Explicit disclaimer: *"Decision-support guide; does not guarantee automated promotion."*

### Scene 8: Strategic Workforce Scenario Simulation (9:30 – 11:00)
- **Action:** Logout and log in as **HR Executive** (`hr@demo.com`).
- **View:** Navigate to **"Workforce AI"** (`/ai-intelligence`).
- **Narrative:** *"Beyond static forecasts, Phase 14 introduces our interactive Workforce Scenario Simulation engine. HR can model 'what-if' scenarios before committing corporate capital."*
- **Demonstrate:** Run Simulation with **"DEMAND_INCREASE" (+20%)**:
  - Base headcount: 200 employees.
  - Staffing gap: +40 personnel needed.
  - Cost delta: Projected monthly payroll impact.
  - Actionable advice: Recommends 70% external hiring (28 requisitions) + 30% internal lateral mobility (12 reassignments).
  - Stamped with mandatory label: *"Scenario Simulation — For Strategic Decision Support Only (Not an Actual Forecast)"*.

### Scene 9: Multi-Location Campuses & Vendor Contractor Management (11:00 – 12:30)
- **View:** Navigate to **"HR Dashboard"** (`/dashboard`).
- **Narrative:** *"InnovateCorp operates across 5 campuses (Hyderabad, Bengaluru, Chennai, Pune, Mumbai) and leverages specialized vendor contractors. In Phase 14, contractor talent is fully tracked without polluting the regular 200-employee baseline."*
- **Demonstrate:**
  - Executive summary showing 200 regular employees + active vendor contractors (e.g. Apex Cloud Solutions, CyberGuard).
  - Contractor billing timesheet workflow with hourly rate accounting.

### Scene 10: Rule-Based Compliance Alerting & Risk Monitoring (12:30 – 13:45)
- **View:** Navigate to Compliance Alerts.
- **Narrative:** *"Rather than reactive auditing, our rule-based compliance engine continuously flags excessive overtime (>12h/wk), missing checkouts, unresolved telemetry anomalies, and expiring contractor SOWs."*
- **Demonstrate:**
  - Review open compliance alerts.
  - Mark an excessive overtime alert as `In_Review` with supervisor notes.
  - Emphasize that all alerts trigger human managerial review rather than automated adverse disciplinary actions.

### Scene 11: Mobile Progressive Web Application (PWA) Showcase & Conclusion (13:45 – 15:00)
- **Action:** Open Chrome DevTools (`F12`) and toggle the device toolbar to **iPhone 14 / Pixel 7** (`390px` width).
- **Narrative:** *"The entire platform operates as a modern installable PWA with WCAG 2.1 AA accessibility."*
- **Demonstrate:**
  - Smooth mobile bottom navigation bar and touch targets ($\ge 44\text{px}$).
  - Voice assistant operational on mobile.
  - Offline mode indicator banner: *"Offline Mode: Working from local shell."* Offline attendance queued in IndexedDB.
- **Conclusion:** *"InnovateCorp HRvantage unites enterprise workforce management, machine learning intelligence, grounded RAG policies, multi-campus telemetry, scenario simulation, and mobile PWA ergonomics into a unified, secure platform. All 181 automated tests pass with 100% reliability. Thank you."*
