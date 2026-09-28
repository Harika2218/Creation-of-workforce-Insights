"""
ERP Connector Base Abstraction
------------------------------
Standardized contract for Enterprise Resource Planning integrations.
"""

from abc import abstractmethod
from typing import Dict, Any, List
from backend.integrations.base.connector import BaseConnector

class BaseERPConnector(BaseConnector):
    @abstractmethod
    def sync_cost_centers(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def sync_departments(self) -> List[Dict[str, Any]]:
        pass
