"""
Integration Exception Hierarchy
-------------------------------
Custom exceptions for integration errors, timeouts, and circuit breakers.
"""

class IntegrationException(Exception):
    """Base exception for all integration operations."""
    def __init__(self, message: str, provider: str = "generic"):
        self.message = message
        self.provider = provider
        super().__init__(f"[{provider.upper()}] {message}")

class IntegrationNotConfiguredError(IntegrationException):
    """Raised when an operation is requested on an unconfigured or disabled integration."""
    pass

class IntegrationAuthenticationError(IntegrationException):
    """Raised when authentication credentials (API key, token, secret) are rejected by external system."""
    pass

class IntegrationConnectionError(IntegrationException):
    """Raised when the remote service is unreachable or network connectivity fails."""
    pass

class IntegrationTimeoutError(IntegrationException):
    """Raised when an external request exceeds the configured timeout threshold."""
    pass

class CircuitBreakerOpenError(IntegrationException):
    """Raised when calls are short-circuited due to an open circuit breaker."""
    pass
