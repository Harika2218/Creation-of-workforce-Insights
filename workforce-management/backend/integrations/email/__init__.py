"""
Email Integration Package
"""
from backend.integrations.email.provider import BaseEmailProvider
from backend.integrations.email.smtp_provider import SMTPProvider
from backend.integrations.email.sendgrid_provider import SendGridProvider
from backend.integrations.email.mock_provider import MockEmailProvider
from backend.integrations.email.email_connector import EmailConnector

__all__ = [
    "BaseEmailProvider",
    "SMTPProvider",
    "SendGridProvider",
    "MockEmailProvider",
    "EmailConnector",
]
