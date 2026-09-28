"""
AI-Powered Workforce Management Automation System
Backend Configuration Settings
--------------------------------------------------
Loads application settings, security tokens, and environment parameters.
"""

import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

class Settings:
    PROJECT_NAME: str = "AI Workforce Management Automation System"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "hr_automation")

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secure-jwt-secret-key-for-hr-automation-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")) # 8 hours

    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # Geofencing
    DEFAULT_GEOFENCE_RADIUS_METERS: float = float(os.getenv("DEFAULT_GEOFENCE_RADIUS_METERS", "500.0"))

    # Phase 6: AI HR Chatbot & RAG
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "local")  # "local" (deterministic grounded reasoning) or "openai"
    LLM_API_KEY: str = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local_tfidf")  # "local_tfidf", "openai"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHATBOT_TEMPERATURE: float = float(os.getenv("CHATBOT_TEMPERATURE", "0.2"))
    CHATBOT_MAX_TOKENS: int = int(os.getenv("CHATBOT_MAX_TOKENS", "800"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.08"))

    # Phase 7: Real-Time Notifications & Workflow Automation
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() in ("true", "1", "yes")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "notifications@innovatecorp.demo")
    SCHEDULER_INTERVAL_SECONDS: int = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "60"))
    SHIFT_REMINDER_MINUTES: int = int(os.getenv("SHIFT_REMINDER_MINUTES", "60"))

    # Phase 10: External Integrations & Enterprise Connectivity
    # Email Provider Abstraction
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "smtp")  # "smtp", "sendgrid", "ses", "mock"
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SES_AWS_REGION: str = os.getenv("SES_AWS_REGION", "us-east-1")
    SES_AWS_ACCESS_KEY_ID: str = os.getenv("SES_AWS_ACCESS_KEY_ID", "")
    SES_AWS_SECRET_ACCESS_KEY: str = os.getenv("SES_AWS_SECRET_ACCESS_KEY", "")

    # Microsoft Ecosystem (Teams, Outlook/Graph, Entra ID)
    MICROSOFT_ENABLED: bool = os.getenv("MICROSOFT_ENABLED", "false").lower() in ("true", "1", "yes")
    MICROSOFT_TENANT_ID: str = os.getenv("MICROSOFT_TENANT_ID", "")
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_CALENDAR_ENABLED: bool = os.getenv("MICROSOFT_CALENDAR_ENABLED", "false").lower() in ("true", "1", "yes")
    TEAMS_ENABLED: bool = os.getenv("TEAMS_ENABLED", "false").lower() in ("true", "1", "yes")
    TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")

    # Slack Ecosystem
    SLACK_ENABLED: bool = os.getenv("SLACK_ENABLED", "false").lower() in ("true", "1", "yes")
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_DEFAULT_CHANNEL: str = os.getenv("SLACK_DEFAULT_CHANNEL", "#hr-notifications")

    # Google Workspace
    GOOGLE_ENABLED: bool = os.getenv("GOOGLE_ENABLED", "false").lower() in ("true", "1", "yes")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_CALENDAR_ENABLED: bool = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() in ("true", "1", "yes")

    # Identity & Access (Active Directory / Entra ID)
    ENTRA_ID_ENABLED: bool = os.getenv("ENTRA_ID_ENABLED", "false").lower() in ("true", "1", "yes")
    LDAP_AD_ENABLED: bool = os.getenv("LDAP_AD_ENABLED", "false").lower() in ("true", "1", "yes")
    LDAP_SERVER_URI: str = os.getenv("LDAP_SERVER_URI", "")
    LDAP_BIND_DN: str = os.getenv("LDAP_BIND_DN", "")
    LDAP_BIND_PASSWORD: str = os.getenv("LDAP_BIND_PASSWORD", "")
    LDAP_BASE_DN: str = os.getenv("LDAP_BASE_DN", "")

    # Payroll Software Gateway
    PAYROLL_INTEGRATION_ENABLED: bool = os.getenv("PAYROLL_INTEGRATION_ENABLED", "false").lower() in ("true", "1", "yes")
    PAYROLL_PROVIDER: str = os.getenv("PAYROLL_PROVIDER", "generic_api")  # "generic_api", "quickbooks", "adp"
    PAYROLL_API_BASE_URL: str = os.getenv("PAYROLL_API_BASE_URL", "")
    PAYROLL_API_KEY: str = os.getenv("PAYROLL_API_KEY", "")

    # ERP & HRMS (SAP & Oracle)
    SAP_ENABLED: bool = os.getenv("SAP_ENABLED", "false").lower() in ("true", "1", "yes")
    SAP_BASE_URL: str = os.getenv("SAP_BASE_URL", "")
    SAP_CLIENT_ID: str = os.getenv("SAP_CLIENT_ID", "")
    SAP_CLIENT_SECRET: str = os.getenv("SAP_CLIENT_SECRET", "")
    ORACLE_HRMS_ENABLED: bool = os.getenv("ORACLE_HRMS_ENABLED", "false").lower() in ("true", "1", "yes")
    ORACLE_HRMS_BASE_URL: str = os.getenv("ORACLE_HRMS_BASE_URL", "")
    ORACLE_HRMS_CLIENT_ID: str = os.getenv("ORACLE_HRMS_CLIENT_ID", "")
    ORACLE_HRMS_CLIENT_SECRET: str = os.getenv("ORACLE_HRMS_CLIENT_SECRET", "")

    # Biometric Devices
    BIOMETRIC_ENABLED: bool = os.getenv("BIOMETRIC_ENABLED", "false").lower() in ("true", "1", "yes")
    BIOMETRIC_PROVIDER: str = os.getenv("BIOMETRIC_PROVIDER", "zkteco_push")  # "zkteco_push", "generic_ip"
    BIOMETRIC_BASE_URL: str = os.getenv("BIOMETRIC_BASE_URL", "")
    BIOMETRIC_API_KEY: str = os.getenv("BIOMETRIC_API_KEY", "")

    # Webhook Security & Resilience
    WEBHOOK_SIGNING_SECRET: str = os.getenv("WEBHOOK_SIGNING_SECRET", "super-secure-webhook-signing-secret-2026")
    INTEGRATION_TIMEOUT_SECONDS: int = int(os.getenv("INTEGRATION_TIMEOUT_SECONDS", "10"))
    INTEGRATION_MAX_RETRIES: int = int(os.getenv("INTEGRATION_MAX_RETRIES", "3"))

    # Phase 12: Production Infrastructure, Reliability & Observability
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json" if os.getenv("ENVIRONMENT") == "production" else "text")

    # MongoDB Connection Pool & Resilience
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "50"))
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
    MONGODB_CONNECT_TIMEOUT_MS: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "5000"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "10"))
    RATE_LIMIT_AI_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AI_PER_MINUTE", "30"))
    RATE_LIMIT_GENERAL_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_GENERAL_PER_MINUTE", "120"))

    # Security & Hosts
    ALLOWED_HOSTS: list = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]

    # Observability & Monitoring
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() in ("true", "1", "yes")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

settings = Settings()

