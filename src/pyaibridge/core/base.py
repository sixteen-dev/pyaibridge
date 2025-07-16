"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Optional

from .models import ChatRequest, ChatResponse, ProviderConfig, StreamingChunk


class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider with configuration.

        Args:
            config: Provider configuration
        """
        self.config = config
        self._client: Optional[Any] = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> dict[str, dict[str, Any]]:
        """Return supported models and their capabilities."""
        pass

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat completion.

        Args:
            request: Chat completion request

        Returns:
            Chat completion response

        Raises:
            ProviderError: If the request fails
            ValidationError: If the request is invalid
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def stream_chat(
        self, request: ChatRequest
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Generate a streaming chat completion.

        Args:
            request: Chat completion request (with stream=True)

        Yields:
            Streaming chunks of the response

        Raises:
            ProviderError: If the request fails
            ValidationError: If the request is invalid
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def validate_model(self, model: str) -> bool:
        """Validate if a model is supported.

        Args:
            model: Model name to validate

        Returns:
            True if model is supported, False otherwise
        """
        pass

    async def __aenter__(self) -> BaseProvider:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()

    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection to the provider."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up connection to the provider."""
        pass

    def get_model_info(self, model: str) -> dict[str, Any]:
        """Get information about a specific model.

        Args:
            model: Model name

        Returns:
            Model information dictionary

        Raises:
            ValueError: If model is not supported
        """
        if model not in self.supported_models:
            raise ValueError(
                f"Model '{model}' is not supported by {self.provider_name}"
            )
        return self.supported_models[model]

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def calculate_cost(self, usage: dict[str, int], model: str) -> Optional[float]:
        """Calculate cost for token usage.

        Args:
            usage: Token usage dictionary
            model: Model name

        Returns:
            Estimated cost in USD, or None if pricing not available
        """
        model_info = self.get_model_info(model)
        pricing = model_info.get("pricing")
        if not pricing:
            return None

        prompt_cost = usage.get("prompt_tokens", 0) * pricing.get("prompt_per_token", 0)
        completion_cost = usage.get("completion_tokens", 0) * pricing.get(
            "completion_per_token", 0
        )

        return prompt_cost + completion_cost
