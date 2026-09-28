"""
Integration Circuit Breaker Implementation
------------------------------------------
Prevents cascading failures by isolating broken external integrations.
Transitions between CLOSED, OPEN, and HALF_OPEN states based on consecutive errors.
"""

import time
from typing import Callable, Any
from backend.integrations.base.exceptions import CircuitBreakerOpenError

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # "CLOSED", "OPEN", "HALF_OPEN"
        self.last_failure_time: float = 0.0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executes func wrapped in circuit breaker safety checks."""
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN for integration '{self.name}'. Request short-circuited.",
                    provider=self.name
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def reset(self):
        """Manually reset the circuit breaker to CLOSED."""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0
