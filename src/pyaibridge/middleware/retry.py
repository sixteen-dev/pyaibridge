"""Retry middleware for handling transient failures."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Type

import structlog
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..core.exceptions import ProviderError, RateLimitError, TimeoutError

logger = structlog.get_logger(__name__)


class RetryMiddleware:
    """Middleware for handling retries with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 60.0,
        multiplier: float = 2.0,
        retry_on: tuple[Type[Exception], ...] = (ProviderError, TimeoutError),
        retry_on_rate_limit: bool = True,
    ) -> None:
        """Initialize retry middleware.

        Args:
            max_retries: Maximum number of retry attempts
            min_wait: Minimum wait time between retries (seconds)
            max_wait: Maximum wait time between retries (seconds)
            multiplier: Multiplier for exponential backoff
            retry_on: Exception types to retry on
            retry_on_rate_limit: Whether to retry on rate limit errors
        """
        self.max_retries = max_retries
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier

        # Build retry condition
        retry_exceptions = list(retry_on)
        if retry_on_rate_limit:
            retry_exceptions.append(RateLimitError)

        self.retry_condition = retry_if_exception_type(tuple(retry_exceptions))

    async def __call__(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.min_wait,
                max=self.max_wait,
            ),
            retry=self.retry_condition,
            reraise=True,
        ):
            with attempt:
                try:
                    result = await func(*args, **kwargs)
                    if attempt.retry_state.attempt_number > 1:
                        logger.info(
                            "Retry successful",
                            attempt=attempt.retry_state.attempt_number,
                            function=func.__name__,
                        )
                    return result
                except RateLimitError as e:
                    logger.warning(
                        "Rate limit exceeded, retrying",
                        attempt=attempt.retry_state.attempt_number,
                        retry_after=e.retry_after,
                        provider=e.provider,
                    )

                    # Respect rate limit retry-after header
                    if e.retry_after:
                        await asyncio.sleep(e.retry_after)

                    raise
                except Exception as e:
                    logger.warning(
                        "Request failed, retrying",
                        attempt=attempt.retry_state.attempt_number,
                        error=str(e),
                        function=func.__name__,
                    )
                    raise
