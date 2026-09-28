"""
Email Provider Abstraction Layer
--------------------------------
Standard interface for pluggable email delivery providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseEmailProvider(ABC):
    """Abstract interface for all email delivery provider implementations."""
    @abstractmethod
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Tests provider connectivity and authentication."""
        pass
