"""
Base Integration Connector Abstract Interface
----------------------------------------------
Contract that every external integration connector must fulfill.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.integrations.base.models import (
    IntegrationStatus,
    ConnectionTestResult,
    IntegrationHealth,
    SyncResult
)
from backend.integrations.base.circuit_breaker import CircuitBreaker

class BaseConnector(ABC):
    """
    Abstract Base Class for all external enterprise connectors.
    Enforces status reporting, health checks, safe connectivity testing, and sync execution.
    """
    def __init__(self, name: str, category: str, display_name: str, description: str):
        self.name = name
        self.category = category
        self.display_name = display_name
        self.description = description
        self.circuit_breaker = CircuitBreaker(name=name)
        self.total_calls = 0
        self.failed_calls = 0
        self.last_success: Optional[str] = None
        self.last_failure: Optional[str] = None
        self.error_message: Optional[str] = None

    @abstractmethod
    def is_enabled(self) -> bool:
        """Returns True if the integration feature flag is active."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if required credentials and configuration parameters are present."""
        pass

    def get_status(self) -> IntegrationStatus:
        """Computes current operational status based on configuration, health, and dependency state."""
        if not self.is_enabled():
            return IntegrationStatus.DISABLED
        if not self.is_configured():
            return IntegrationStatus.NOT_CONFIGURED
        if self.circuit_breaker.state == "OPEN":
            return IntegrationStatus.ERROR
        if self.error_message:
            return IntegrationStatus.ERROR
        return IntegrationStatus.CONNECTED

    def record_success(self):
        """Records a successful integration interaction."""
        self.total_calls += 1
        self.last_success = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.error_message = None

    def record_failure(self, err_msg: str):
        """Records an integration interaction error."""
        self.total_calls += 1
        self.failed_calls += 1
        self.last_failure = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.error_message = err_msg

    def get_health(self) -> IntegrationHealth:
        """Returns normalized health metrics for the connector."""
        return IntegrationHealth(
            name=self.name,
            category=self.category,
            display_name=self.display_name,
            enabled=self.is_enabled(),
            configured=self.is_configured(),
            status=self.get_status(),
            last_success=self.last_success,
            last_failure=self.last_failure,
            error_message=self.error_message,
            total_calls=self.total_calls,
            failed_calls=self.failed_calls,
            circuit_breaker_state=self.circuit_breaker.state
        )

    @abstractmethod
    def test_connection(self) -> ConnectionTestResult:
        """
        Executes a safe connectivity and authentication test.
        Must not modify business records or disrupt production operations.
        """
        pass

    @abstractmethod
    def sync(self, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        """
        Executes outbound or inbound synchronization for this connector.
        """
        pass
