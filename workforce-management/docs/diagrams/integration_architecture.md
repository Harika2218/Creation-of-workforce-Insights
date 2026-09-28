# ENTERPRISE INTEGRATION ARCHITECTURE DIAGRAM

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** `docs/diagrams/integration_architecture.md`  

---

```mermaid
graph LR
    subgraph Core_Platform ["InnovateCorp HRvantage Core (FastAPI :8000)"]
        IntegRouter["/api/v1/integrations"]
        IntegManager["Integration Health & Sync Manager"]
        WebhookHandler["Inbound Webhook Verification (HMAC-SHA256)"]
        SyncTelemetry[("db.integration_sync_history")]
    end

    subgraph Chat_Collaboration ["Team Collaboration Integrations"]
        Slack["Slack Incoming Webhooks
        • Status: CONFIGURED
        • Sends automated shift & leave notifications"]
        
        Teams["Microsoft Teams
        • Status: FOUNDATION_ONLY
        • Adaptive Cards template engine ready"]
    end

    subgraph Identity_Calendar ["Identity & Calendar Ecosystem (Cloud Blocked)"]
        Entra["Microsoft Entra ID (Azure AD)
        • Status: BLOCKED_EXTERNAL_DEPENDENCY
        • Coded for SAML 2.0 / OAuth2 SSO"]
        
        Outlook["Microsoft Outlook & Graph API
        • Status: BLOCKED_EXTERNAL_DEPENDENCY
        • Coded for Calendar Sync & Meeting Bookings"]
        
        GoogleWork["Google Workspace & Calendar
        • Status: BLOCKED_EXTERNAL_DEPENDENCY
        • Coded for Google OAuth2 & Event API"]
    end

    subgraph Hardware_ERP ["Hardware & Enterprise ERP"]
        BioTerminal["Biometric Punch Hardware Terminals
        • Status: FOUNDATION_ONLY
        • TCP/IP Listener & Payload Ingestion Ready"]
        
        SAPERP["SAP / Oracle HRMS
        • Status: FOUNDATION_ONLY
        • Standard CSV/JSON Payroll Export Handshake"]
    end

    IntegRouter --> IntegManager
    IntegManager --> SyncTelemetry
    WebhookHandler --> IntegManager

    IntegManager -->|Outbound Webhooks| Slack
    IntegManager -->|Adaptive Cards| Teams
    IntegManager -.->|OAuth2 Token Exchange| Entra
    IntegManager -.->|Graph REST Calls| Outlook
    IntegManager -.->|Google API Client| GoogleWork

    BioTerminal -.->|Ingest Batch| WebhookHandler
    IntegManager -.->|Batch Export| SAPERP
```
