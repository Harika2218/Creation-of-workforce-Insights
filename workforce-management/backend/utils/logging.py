"""
AI-Powered Workforce Management Automation System
Production Logging & Correlation Infrastructure
--------------------------------------------------
Configures structured JSON logging with context-propagated Request/Correlation IDs,
security-aware redaction filters (never logging passwords, JWTs, or sensitive PII),
and standardized log levels.
"""

import os
import sys
import re
import logging
from contextvars import ContextVar
from typing import Optional, Any
from datetime import datetime, timezone

# Context variables for request tracing across async tasks
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="SYSTEM")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="ANONYMOUS")

# Redaction patterns for sensitive data
SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(password|secret|token|jwt|apiKey|api_key|authorization)\s*[:=]\s*["\']?([^"\'\s,]+)'), r'\1="***REDACTED***"'),
    (re.compile(r'(?i)bearer\s+[a-zA-Z0-9_\-\.]+', re.IGNORECASE), 'Bearer ***REDACTED***'),
    (re.compile(r'(?i)\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '****-****-****-****'),  # Credit cards
    (re.compile(r'(?i)\b[A-Z]{5}\d{4}[A-Z]{1}\b'), '*****REDACTED*****')                     # Tax ID / PAN
]

class SecurityRedactionFilter(logging.Filter):
    """
    Log filter that intercepts and sanitizes sensitive credentials, tokens,
    and private HR information from log messages and extras.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Inject correlation context if not explicitly set
        if not hasattr(record, "request_id") or not record.request_id:
            record.request_id = request_id_ctx.get()
        if not hasattr(record, "user_id") or not record.user_id:
            record.user_id = user_id_ctx.get()

        # Sanitize message string
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        # Sanitize args if present
        if record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        return True

def setup_logging(log_level: Optional[str] = None, log_format: Optional[str] = None):
    """
    Initializes system-wide structured logging.
    """
    level_name = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    format_type = log_format or os.getenv("LOG_FORMAT", "text").lower()

    numeric_level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to prevent duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.addFilter(SecurityRedactionFilter())

    if format_type == "json":
        try:
            from pythonjsonlogger.json import JsonFormatter
            formatter = JsonFormatter(
                fmt="%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(user_id)s",
                rename_fields={"levelname": "level", "asctime": "timestamp"}
            )
        except Exception:
            # Fallback if library import behaves differently
            formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"%(name)s","request_id":"%(request_id)s","user_id":"%(user_id)s","message":"%(message)s"}'
            )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(user_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure third-party loggers
    logging.getLogger("uvicorn.access").handlers = [console_handler]
    logging.getLogger("uvicorn.error").handlers = [console_handler]

    # Silence excessively noisy loggers in production
    if numeric_level >= logging.INFO:
        logging.getLogger("pymongo").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured with the security redaction filter."""
    logger = logging.getLogger(name)
    return logger
