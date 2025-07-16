"""xAI provider implementation."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, NoReturn, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base import BaseProvider
from ..core.exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from ..core.models import (
    ChatRequest,
    ChatResponse,
    MessageRole,
    ProviderConfig,
    StreamingChunk,
    Usage,
)

logger = structlog.get_logger(__name__)


class XAIProvider(BaseProvider):
    """xAI provider implementation."""

    BASE_URL = "https://api.x.ai/v1"

    # Model configurations with pricing (per 1M tokens)
    SUPPORTED_MODELS = {
        # Grok 4 Series (Latest 2025)
        "grok-4": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 2.00 / 1000000,
                "completion_per_token": 10.00 / 1000000,
            },
        },
        "grok-4-heavy": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        # Grok 3 Series
        "grok-3-beta": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 2.00 / 1000000,
                "completion_per_token": 10.00 / 1000000,
            },
        },
        "grok-3-fast-beta": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 1.00 / 1000000,
                "completion_per_token": 5.00 / 1000000,
            },
        },
        # Grok 2 Series
        "grok-2-1212": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "December 2024",
            "pricing": {
                "prompt_per_token": 2.00 / 1000000,
                "completion_per_token": 10.00 / 1000000,
            },
        },
        "grok-2-vision-1212": {
            "context_length": 32768,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "December 2024",
            "pricing": {
                "prompt_per_token": 2.00 / 1000000,
                "completion_per_token": 10.00 / 1000000,
            },
        },
        # Legacy Beta Models
        "grok-beta": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 5.00 / 1000000,  # Higher legacy pricing
                "completion_per_token": 15.00 / 1000000,
            },
        },
        "grok-vision-beta": {
            "context_length": 8192,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "October 2024",
            "pricing": {
                "prompt_per_token": 5.00 / 1000000,  # Higher legacy pricing
                "completion_per_token": 15.00 / 1000000,
            },
        },
    }

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize xAI provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.base_url = config.base_url or self.BASE_URL
        self._client: httpx.AsyncClient | None = None

        logger.info("xAI provider initialized", base_url=self.base_url)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "xai"

    @property
    def supported_models(self) -> dict[str, dict[str, Any]]:
        """Return supported models and their capabilities."""
        return self.SUPPORTED_MODELS

    async def connect(self) -> None:
        """Initialize HTTP client with connection pooling."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "pyaibridge/0.0.1",
                },
            )
            logger.info("xAI client connected")

    async def disconnect(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("xAI client disconnected")

    async def validate_model(self, model: str) -> bool:
        """Validate if a model is supported.

        Args:
            model: Model name to validate

        Returns:
            True if model is supported, False otherwise
        """
        return model in self.SUPPORTED_MODELS

    def _convert_role(self, role: MessageRole) -> str:
        """Convert pyaibridge role to xAI role.

        Args:
            role: The role to convert

        Returns:
            xAI role string
        """
        role_mapping = {
            MessageRole.USER: "user",
            MessageRole.ASSISTANT: "assistant",
            MessageRole.SYSTEM: "system",
        }
        return role_mapping[role]

    def _prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Prepare messages for xAI API.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages for xAI
        """
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": self._convert_role(MessageRole(msg["role"])),
                "content": msg["content"],
            })
        return formatted_messages

    def calculate_cost(self, usage: dict[str, int], model: str) -> Optional[float]:
        """Calculate the cost for the given usage.

        Args:
            usage: Usage dictionary with token counts
            model: Model name

        Returns:
            Cost in USD

        Raises:
            ValueError: If model is not supported
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model '{model}' is not supported")

        model_info = self.SUPPORTED_MODELS[model]
        pricing: dict[str, float] = model_info["pricing"]  # type: ignore

        prompt_cost = usage.get("prompt_tokens", 0) * pricing["prompt_per_token"]
        completion_cost = usage.get("completion_tokens", 0) * pricing["completion_per_token"]

        return prompt_cost + completion_cost

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
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
        if not self._client:
            await self.connect()
        
        assert self._client is not None

        if not await self.validate_model(request.model):
            raise ValidationError(
                f"Model '{request.model}' is not supported by xAI",
                field="model"
            )

        # Prepare request payload
        payload = {
            "model": request.model,
            "messages": self._prepare_messages([msg.model_dump() for msg in request.messages]),
            "stream": False,
        }

        # Add optional parameters
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            payload["stop"] = request.stop
        if request.user is not None:
            payload["user"] = request.user

        try:
            response = await self._client.post(
                "/chat/completions",
                json=payload,
                timeout=request.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Extract response data
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")

            # Extract usage information
            usage_data = data.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

            return ChatResponse(
                id=data["id"],
                model=data["model"],
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                created=datetime.now(),
                metadata={"provider": "xai"},
            )

        except httpx.HTTPStatusError as e:
            await self._handle_http_error(e)
        except httpx.RequestError as e:
            logger.error("xAI request error", error=str(e))
            raise ProviderError(f"Request failed: {e}", "xai") from e
        except (KeyError, ValueError) as e:
            logger.error("xAI response parsing error", error=str(e))
            raise ProviderError(f"Invalid response format: {e}", "xai") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def stream_chat(  # type: ignore[override]
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
        if not self._client:
            await self.connect()
        
        assert self._client is not None

        if not await self.validate_model(request.model):
            raise ValidationError(
                f"Model '{request.model}' is not supported by xAI",
                field="model"
            )

        # Prepare request payload
        payload = {
            "model": request.model,
            "messages": self._prepare_messages([msg.model_dump() for msg in request.messages]),
            "stream": True,
        }

        # Add optional parameters
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            payload["stop"] = request.stop
        if request.user is not None:
            payload["user"] = request.user

        try:
            async with self._client.stream(
                "POST",
                "/chat/completions",
                json=payload,
                timeout=request.timeout,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            choice = data["choices"][0]

                            if choice.get("delta", {}).get("content"):
                                content = choice["delta"]["content"]
                                finish_reason = choice.get("finish_reason")

                                yield StreamingChunk(
                                    id=data["id"],
                                    model=data["model"],
                                    content=content,
                                    finish_reason=finish_reason,
                                    created=datetime.now(),
                                    metadata={"provider": "xai"},
                                )

                        except json.JSONDecodeError:
                            logger.warning("Failed to parse streaming chunk", line=line)
                            continue

        except httpx.HTTPStatusError as e:
            await self._handle_http_error(e)
        except httpx.RequestError as e:
            logger.error("xAI streaming request error", error=str(e))
            raise ProviderError(f"Streaming request failed: {e}", "xai") from e

    async def _handle_http_error(self, error: httpx.HTTPStatusError) -> NoReturn:
        """Handle HTTP errors from xAI API.

        Args:
            error: The HTTP error to handle

        Raises:
            AuthenticationError: For 401 errors
            RateLimitError: For 429 errors
            ProviderError: For other errors
        """
        status_code = error.response.status_code
        error_detail = "Unknown error"

        try:
            error_data = error.response.json()
            error_detail = error_data.get("error", {}).get("message", str(error))
        except (ValueError, KeyError):
            error_detail = str(error)

        logger.error(
            "xAI API error",
            status_code=status_code,
            error=error_detail,
        )

        if status_code == 401:
            raise AuthenticationError("Invalid xAI API key", "xai")
        elif status_code == 429:
            raise RateLimitError("xAI rate limit exceeded", "xai")
        else:
            raise ProviderError(f"xAI API error ({status_code}): {error_detail}", "xai", status_code)
