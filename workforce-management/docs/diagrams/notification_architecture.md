# NOTIFICATION & WORKFLOW AUTOMATION ARCHITECTURE DIAGRAM

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** `docs/diagrams/notification_architecture.md`  

---

```mermaid
graph TD
    subgraph Event_Emitters ["1. Enterprise Event Triggers"]
        PunchEvent["Attendance Punch (Late arrival, Missing punch)"]
        LeaveEvent["Leave Request (Filed, Approved, Rejected)"]
        ShiftEvent["Shift Swap Proposed / Authorized"]
        PayrollEvent["Monthly Payroll Finalized & Payslip Ready"]
        CronEvent["Daily Scheduler (Birthdays, Work Anniversaries, Compliance Scan)"]
        AIEvent["AI Alert (Critical Anomaly Flag, Severe Attrition Surge)"]
    end

    subgraph Dispatcher_Core ["2. Notification Engine (backend/services/notification_service.py)"]
        EventBus["Internal Event Dispatcher"]
        PrefFilter["Preference Checker (db.notification_preferences)
        • Honors user channel toggles (Email / In-App / Shift Alerts)"]
        Deduplicator["Deduplication Engine (prevents duplicate spam)"]
    end

    subgraph Multi_Channel_Delivery ["3. Multi-Channel Delivery Channels"]
        subgraph Channel_InApp ["Channel 1: Real-Time In-App Drawer"]
            DBNotify[("db.notifications")]
            BadgeCount["Unread Counter Badge"]
            ClientPoll["FastAPI Polling / SSE Client"]
        end

        subgraph Channel_Email ["Channel 2: Email Gateway Abstraction"]
            EmailQueue["Async Delivery Queue"]
            SMTPDriver["SMTP / SendGrid Production Driver"]
            EmailLog[("db.email_delivery_logs")]
        end

        subgraph Channel_Chat ["Channel 3: External Chat Connectors"]
            SlackHook["Slack Webhook Formatter"]
            TeamsHook["Microsoft Teams Adaptive Card Dispatcher"]
        end
    end

    PunchEvent & LeaveEvent & ShiftEvent & PayrollEvent & CronEvent & AIEvent --> EventBus
    EventBus --> PrefFilter --> Deduplicator

    Deduplicator -->|Store In-App| DBNotify --> BadgeCount --> ClientPoll
    Deduplicator -->|Dispatch Email| EmailQueue --> SMTPDriver --> EmailLog
    Deduplicator -->|External Alert| SlackHook & TeamsHook
```
