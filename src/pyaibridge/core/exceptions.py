"""Exception classes for pyaibridge."""

from typing import Any, Optional


class PyAIBridgeError(Exception):
    """Base exception for all pyaibridge errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderError(PyAIBridgeError):
    """Exception raised when a provider operation fails."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.provider = provider
        self.status_code = status_code


class RateLimitError(ProviderError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        provider: str,
        retry_after: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, provider, 429, details)
        self.retry_after = retry_after


class AuthenticationError(ProviderError):
    """Exception raised when authentication fails."""

    def __init__(
        self, message: str, provider: str, details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message, provider, 401, details)


class ValidationError(PyAIBridgeError):
    """Exception raised when input validation fails."""

    def __init__(
        self, message: str, field: str, details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)
        self.field = field


class TimeoutError(PyAIBridgeError):
    """Exception raised when operation times out."""

    def __init__(
        self, message: str, timeout: float, details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)
        self.timeout = timeout
