"""
SMTP Email Provider Implementation
----------------------------------
Delivers email via standard SMTP server with TLS encryption and timeouts.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from backend.config import settings
from backend.integrations.email.provider import BaseEmailProvider
from backend.integrations.base.exceptions import (
    IntegrationAuthenticationError,
    IntegrationConnectionError,
    IntegrationTimeoutError
)

class SMTPProvider(BaseEmailProvider):
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        timeout: int = 8
    ):
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USERNAME
        self.password = password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.EMAIL_FROM
        self.timeout = timeout

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        sender = from_email or self.from_email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient_email

        msg.attach(MIMEText(text_body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.sendmail(sender, recipient_email, msg.as_string())
            return True
        except smtplib.SMTPAuthenticationError as e:
            raise IntegrationAuthenticationError(f"SMTP authentication failed: {e}", provider="smtp")
        except (smtplib.SMTPConnectError, ConnectionRefusedError, OSError) as e:
            raise IntegrationConnectionError(f"SMTP connection failed to {self.host}:{self.port}: {e}", provider="smtp")
        except TimeoutError as e:
            raise IntegrationTimeoutError(f"SMTP connection timed out: {e}", provider="smtp")
        except Exception as e:
            raise IntegrationConnectionError(f"SMTP delivery error: {e}", provider="smtp")

    def test_connection(self) -> Dict[str, Any]:
        """Verifies SMTP host reachability and TLS handshake."""
        try:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as server:
                server.ehlo()
                has_tls = server.has_extn("STARTTLS")
                if has_tls:
                    server.starttls()
                    server.ehlo()
                if self.username and self.password:
                    server.login(self.username, self.password)
            return {
                "ok": True,
                "host": self.host,
                "port": self.port,
                "tls_supported": has_tls,
                "authenticated": bool(self.username and self.password)
            }
        except smtplib.SMTPAuthenticationError as e:
            raise IntegrationAuthenticationError(f"Invalid SMTP credentials: {e}", provider="smtp")
        except Exception as e:
            raise IntegrationConnectionError(f"Cannot connect to SMTP server: {e}", provider="smtp")
