"""
Retry and Timeout Utilities for External Integrations
-----------------------------------------------------
Provides controlled exponential backoff retries and execution timeouts.
"""

import time
import functools
from typing import Callable, Any, Tuple, Type
from backend.integrations.base.exceptions import IntegrationTimeoutError

def with_retry(
    max_retries: int = 3,
    base_delay: float = 0.2,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying operations on transient failure with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_err = None
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_err = e
                    if attempt == max_retries:
                        break
                    time.sleep(delay)
                    delay *= backoff_factor
            raise last_err
        return wrapper
    return decorator
