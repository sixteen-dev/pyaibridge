"""Rate limiting middleware."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Optional

import structlog

logger = structlog.get_logger(__name__)


class RateLimitMiddleware:
    """Middleware for rate limiting requests."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
    ) -> None:
        """Initialize rate limit middleware.

        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.interval = 60.0 / requests_per_minute

        # Token bucket algorithm
        self.tokens = float(self.burst_size)
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def __call__(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function with rate limiting.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        await self._acquire_token()
        return await func(*args, **kwargs)

    async def _acquire_token(self) -> None:
        """Acquire a token from the bucket."""
        async with self._lock:
            now = time.time()

            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
            self.last_refill = now

            # If no tokens available, wait
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.requests_per_minute / 60.0)
                logger.info("Rate limit reached, waiting", wait_time=wait_time)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
