"""xAI provider implementation."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Optional

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
from ..http_client import HybridHttpClient

logger = structlog.get_logger(__name__)


class XAIProvider(BaseProvider):
    """xAI provider implementation."""

    BASE_URL = "https://api.x.ai/v1"

    # Model configurations with pricing (per 1M tokens) - Updated from xAI docs
    SUPPORTED_MODELS = {
        # Grok 4 Series (Latest reasoning model)
        "grok-4-0709": {
            "context_length": 256000,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "November 2024",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        # Grok 3 Series (Current stable models)
        "grok-3": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "November 2024",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        "grok-3-mini": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "November 2024",
            "pricing": {
                "prompt_per_token": 0.30 / 1000000,
                "completion_per_token": 0.50 / 1000000,
            },
        },
        "grok-3-fast": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "November 2024",
            "pricing": {
                "prompt_per_token": 5.00 / 1000000,
                "completion_per_token": 25.00 / 1000000,
            },
        },
        "grok-3-mini-fast": {
            "context_length": 131072,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_tool_use": True,
            "supports_search": True,
            "knowledge_cutoff": "November 2024",
            "pricing": {
                "prompt_per_token": 0.60 / 1000000,
                "completion_per_token": 4.00 / 1000000,
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
        self._client: HybridHttpClient | None = None

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
            self._client = HybridHttpClient(
                timeout=self.config.timeout,
            )
            await self._client.connect()
            logger.info("xAI client connected")

    async def disconnect(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.disconnect()
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
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "pyaibridge/0.2.3",
            }

            response = await self._client.post(
                url=url,
                json_data=payload,
                headers=headers,
                timeout=int(request.timeout or 30),
                stream=False
            )
            assert isinstance(response, dict), "Expected dict response for non-streaming request"

            if response["status_code"] == 401:
                raise AuthenticationError("Invalid xAI API key", "xai")
            elif response["status_code"] == 429:
                retry_after = response["headers"].get("retry-after")
                raise RateLimitError(
                    "xAI rate limit exceeded",
                    "xai",
                    retry_after=float(retry_after) if retry_after else None,
                )
            elif response["status_code"] != 200:
                error_data = response["json"] if response["json"] else {}
                raise ProviderError(
                    f"xAI API error ({response['status_code']}): {error_data.get('error', {}).get('message', 'Unknown error')}",
                    "xai",
                    response["status_code"],
                    error_data,
                )

            data = response["json"]

            # Extract response data
            choice = data["choices"][0]
            content = choice["message"]["content"] or ""
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
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "pyaibridge/0.2.3",
            }

            response = await self._client.post(
                url=url,
                json_data=payload,
                headers=headers,
                timeout=int(request.timeout or 30),
                stream=True
            )

            # For streaming, response is an AsyncGenerator
            assert hasattr(response, "__aiter__"), "Expected async generator for streaming request"

            async for line in response:
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

        except Exception as e:
            logger.error("xAI streaming request error", error=str(e))
            raise ProviderError(f"Streaming request failed: {e}", "xai") from e

