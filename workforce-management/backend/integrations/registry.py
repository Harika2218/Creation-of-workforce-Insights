"""
Central Integration Registry
----------------------------
Singleton registry managing the lifecycle, discovery, health introspection,
connection testing, and synchronization of all enterprise connectors.
"""

from typing import Dict, List, Optional, Any
from backend.integrations.base.connector import BaseConnector
from backend.integrations.base.models import IntegrationHealth, ConnectionTestResult, SyncResult
from backend.integrations.email.email_connector import EmailConnector
from backend.integrations.messaging.teams import TeamsConnector
from backend.integrations.messaging.slack import SlackConnector
from backend.integrations.calendar.outlook import OutlookCalendarConnector
from backend.integrations.calendar.google_calendar import GoogleCalendarConnector
from backend.integrations.identity.entra_id import EntraIdConnector
from backend.integrations.identity.ldap_ad import LdapAdConnector
from backend.integrations.payroll.payroll_connector import PayrollGatewayConnector
from backend.integrations.erp.sap_connector import SapConnector
from backend.integrations.hrms.oracle_hrms import OracleHrmsConnector
from backend.integrations.biometric.biometric_connector import BiometricDeviceConnector
from backend.integrations.sync import SyncManager

class IntegrationRegistry:
    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._register_default_connectors()

    def _register_default_connectors(self):
        """Registers all supported enterprise connectors."""
        connectors = [
            EmailConnector(),
            TeamsConnector(),
            SlackConnector(),
            OutlookCalendarConnector(),
            GoogleCalendarConnector(),
            EntraIdConnector(),
            LdapAdConnector(),
            PayrollGatewayConnector(),
            SapConnector(),
            OracleHrmsConnector(),
            BiometricDeviceConnector(),
        ]
        for c in connectors:
            self._connectors[c.name] = c

    def register(self, connector: BaseConnector):
        """Allows registering custom or mock connectors for testing."""
        self._connectors[connector.name] = connector

    def unregister(self, name: str):
        if name in self._connectors:
            del self._connectors[name]

    def get_connector(self, name: str) -> Optional[BaseConnector]:
        return self._connectors.get(name)

    def list_connectors(self) -> List[BaseConnector]:
        return list(self._connectors.values())

    def get_all_health(self) -> List[IntegrationHealth]:
        return [c.get_health() for c in self._connectors.values()]

    def test_connection(self, name: str) -> ConnectionTestResult:
        connector = self.get_connector(name)
        if not connector:
            from datetime import datetime, timezone
            from backend.integrations.base.models import IntegrationStatus
            return ConnectionTestResult(
                success=False,
                status=IntegrationStatus.NOT_CONFIGURED,
                message=f"Integration '{name}' is not recognized in system registry.",
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            )
        return connector.test_connection()

    def sync(self, name: str, options: Optional[Dict[str, Any]] = None) -> SyncResult:
        connector = self.get_connector(name)
        if not connector:
            from datetime import datetime, timezone
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            return SyncResult(
                sync_id=f"SYNC_UNKNOWN_{int(time.time())}",
                integration=name,
                status="FAILED",
                error_summary=f"Integration '{name}' not found.",
                started_at=now_str,
                completed_at=now_str
            )
        return SyncManager.execute_sync(connector, options)

# Global Singleton Registry Instance
registry = IntegrationRegistry()
