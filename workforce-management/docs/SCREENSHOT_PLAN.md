# FINAL SCREENSHOT CATALOG & ASSET CAPTURE PLAN

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document Reference:** `docs/SCREENSHOT_PLAN.md`  
**Purpose:** Standardized portfolio, presentation, and user documentation asset catalog  
**Total Screens Cataloged:** Exactly 20 Implemented Screens  

---

## SCREENSHOT INVENTORY & CAPTURE SPECIFICATIONS

| # | Screen Name | Route / URL | Recommended Role | Visual Focal Points & Elements to Highlight |
| :-: | :--- | :--- | :---: | :--- |
| **1** | **Authentication / Login** | `/login` | Public | Clean glassmorphism login card, quick-fill demo role buttons (Admin, HR, Manager, Employee), branding logo. |
| **2** | **Executive HR Dashboard** | `/hr` or `/dashboard` | `HR` | 3D WebGL interactive campus globe, workforce headcount telemetry (200 employees), gender/department ratios. |
| **3** | **Manager Operations Hub** | `/manager` | `MANAGER` | Direct report presence board (Present, Late, On Leave), pending approvals counter, team billable hours chart. |
| **4** | **Employee Dashboard (ESS)**| `/dashboard` | `EMPLOYEE` | Personalized greeting for EMP050, quick clock-in widget, upcoming shift card, leave quota meters. |
| **5** | **Employee Profile & Org** | `/employees/EMP050` | `EMPLOYEE` | Contact information, emergency details, reporting manager card, department badge, and employment tenure. |
| **6** | **GPS Geofenced Attendance** | `/attendance` | `EMPLOYEE` | Multi-campus coordinate badge (LOC01), clock-in/out button, real-time working timer, monthly attendance calendar. |
| **7** | **Leave Request Filing** | `/leave` | `EMPLOYEE` | Leave application modal, remaining balance preview across 4 categories, date picker, reason input field. |
| **8** | **Manager Leave Approval** | `/manager/approvals` | `MANAGER` | Approval inbox card, employee leave details, team calendar overlap check, one-click "Approve" / "Reject" buttons. |
| **9** | **Shift Management & Swap** | `/shifts` | `MANAGER` | Interactive weekly roster grid, shift timing color tags (Morning/Evening/Night), peer swap request drawer. |
| **10** | **Timesheet & Project Hours**| `/timesheets` | `EMPLOYEE` | Weekly task entry table, project assignment dropdown (PRJ01/PRJ02), billable vs non-billable hours indicator. |
| **11** | **Payroll & Digital Payslip** | `/payroll` | `HR` / `EMPLOYEE`| Gross-to-net salary breakdown, deductions table (PF, Tax, LOP), export buttons, printable payslip preview. |
| **12** | **Performance & Scorecards** | `/performance` | `MANAGER` | OKR goal progress bars (0-100%), quarterly appraisal submission card, holistic performance scorecard. |
| **13** | **AI Workforce Analytics** | `/ai` | `HR` | Absenteeism risk radar, attrition prediction heatmaps with explainable risk drivers, model confidence scores. |
| **14** | **Workforce Demand Forecast**| `/ai` (Forecaster) | `HR` | 30-day time-series staffing projection chart (Holt-Winters), department surge bars, staffing recommendations. |
| **15** | **Skills Gap & Training Hub**| `/skills` | `HR` / `MANAGER` | Competency spider chart vs role benchmark, skill deficit scores, recommended training course cards. |
| **16** | **RAG HR Policy Assistant** | `/chatbot` | Any Role | Chat interface with speech-to-text microphone button, grounded answers, clickable policy citation badges. |
| **17** | **Real-Time Notifications** | `/notifications` | Any Role | Notification drawer with unread counter badge, category filters (Attendance, Leave, Shifts), mark-as-read action. |
| **18** | **Integrations Health Board**| `/integrations` | `ADMIN` | Connector status cards (Slack: Configured, Teams: Foundation, Entra/Google: Cloud Blocked), ping latency counters. |
| **19** | **Mobile / PWA View** | Responsive `/dashboard` | `EMPLOYEE` | Mobile viewport layout, mobile bottom bar, offline status indicator banner, PWA install prompt button. |
| **20** | **Settings & Security Center**| `/settings` | `ADMIN` | Active session overview, MFA TOTP setup card, audit log viewer with user/IP filters, security headers info. |

---

## ASSET GUIDELINES
- **Aspect Ratio:** Standard 16:9 for desktop screens (1920x1080); 9:19.5 for mobile PWA captures (iPhone 14/Pixel 7 profile).
- **Format:** Optimized PNG or WebP with crisp text rendering.
- **Privacy:** All screenshots display synthetic demo data only (`EMP001`–`EMP200`, `@innovatecorp.com` or `@demo.com`); zero real-world personal information is exposed.
