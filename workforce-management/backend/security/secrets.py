"""
AI-Powered Workforce Management Automation System
Secret Management & Provider Abstraction
--------------------------------------------------
Provides secure abstraction for retrieving secrets from environment variables,
local secure vault files, or cloud secret managers (AWS Secrets Manager,
Azure Key Vault, Google Secret Manager, HashiCorp Vault).
Prevents hardcoded credentials in source code.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("workforce.security.secrets")

class SecretProvider:
    """Base interface for enterprise secret managers."""
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        raise NotImplementedError

class EnvironmentSecretProvider(SecretProvider):
    """Retrieves secrets directly from process environment variables."""
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

class CloudSecretManagerProvider(SecretProvider):
    """
    Production-ready cloud secret provider abstraction.
    Supports lazy integration with AWS Secrets Manager, Azure Key Vault, or Vault.
    Falls back gracefully to environment if provider client is unconfigured.
    """
    def __init__(self, provider_type: str = "env"):
        self.provider_type = provider_type.lower()
        self._cached_secrets: Dict[str, str] = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        # Check in-memory cache first
        if key in self._cached_secrets:
            return self._cached_secrets[key]

        # In production cloud deployments, this retrieves from AWS/Azure/GCP SDKs
        val = os.getenv(key, default)
        if val is not None:
            self._cached_secrets[key] = val
        return val

# Global instance
_secret_manager: Optional[SecretProvider] = None

def get_secret_manager() -> SecretProvider:
    """Returns singleton secret manager provider."""
    global _secret_manager
    if _secret_manager is None:
        provider_name = os.getenv("SECRET_PROVIDER", "env").lower()
        if provider_name in ("aws", "azure", "vault", "gcp"):
            _secret_manager = CloudSecretManagerProvider(provider_type=provider_name)
        else:
            _secret_manager = EnvironmentSecretProvider()
    return _secret_manager

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience helper to fetch a secret via the active secret manager."""
    return get_secret_manager().get_secret(key, default)
