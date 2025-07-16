"""OpenAI provider implementation."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Dict, Optional

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
    ProviderConfig,
    StreamingChunk,
    Usage,
)

logger = structlog.get_logger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    BASE_URL = "https://api.openai.com/v1"

    # Model configurations with pricing (per 1M tokens)
    SUPPORTED_MODELS = {
        # GPT-4.1 Series (Latest 2025)
        "gpt-4.1": {
            "context_length": 1000000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "pricing": {
                "prompt_per_token": 2.00 / 1000000,
                "completion_per_token": 8.00 / 1000000,
                "cached_prompt_per_token": 0.50 / 1000000,
            },
        },
        "gpt-4.1-mini": {
            "context_length": 1000000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "pricing": {
                "prompt_per_token": 0.40 / 1000000,
                "completion_per_token": 1.60 / 1000000,
                "cached_prompt_per_token": 0.10 / 1000000,
            },
        },
        "gpt-4.1-nano": {
            "context_length": 1000000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "pricing": {
                "prompt_per_token": 0.20 / 1000000,
                "completion_per_token": 0.80 / 1000000,
            },
        },
        # O-Series Reasoning Models (Latest 2025)
        "o3": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "model_type": "reasoning",
            "pricing": {
                "prompt_per_token": 10.00 / 1000000,
                "completion_per_token": 40.00 / 1000000,
            },
        },
        "o3-pro": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "model_type": "reasoning",
            "pricing": {
                "prompt_per_token": 15.00 / 1000000,
                "completion_per_token": 60.00 / 1000000,
            },
        },
        "o4-mini": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "June 2024",
            "model_type": "reasoning",
            "pricing": {
                "prompt_per_token": 0.30 / 1000000,
                "completion_per_token": 1.20 / 1000000,
            },
        },
        # Legacy Models (Still Supported)
        "gpt-4o": {
            "context_length": 128000,
            "supports_streaming": True,
            "pricing": {
                "prompt_per_token": 0.005 / 1000000,
                "completion_per_token": 0.015 / 1000000,
            },
        },
        "gpt-4o-mini": {
            "context_length": 128000,
            "supports_streaming": True,
            "pricing": {
                "prompt_per_token": 0.00015 / 1000000,
                "completion_per_token": 0.0006 / 1000000,
            },
        },
        "gpt-4-turbo": {
            "context_length": 128000,
            "supports_streaming": True,
            "pricing": {
                "prompt_per_token": 0.01 / 1000000,
                "completion_per_token": 0.03 / 1000000,
            },
        },
        "gpt-3.5-turbo": {
            "context_length": 4096,
            "supports_streaming": True,
            "pricing": {
                "prompt_per_token": 0.0015 / 1000000,
                "completion_per_token": 0.002 / 1000000,
            },
        },
    }

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize OpenAI provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.base_url = config.base_url or self.BASE_URL
        self._client: Optional[httpx.AsyncClient] = None

        logger.info("OpenAI provider initialized", base_url=self.base_url)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "openai"

    @property
    def supported_models(self) -> Dict[str, Dict[str, Any]]:
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
            logger.info("OpenAI client connected")

    async def disconnect(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("OpenAI client disconnected")

    async def validate_model(self, model: str) -> bool:
        """Validate if a model is supported."""
        return model in self.SUPPORTED_MODELS

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
        """
        if not await self.validate_model(request.model):
            raise ValidationError(f"Model '{request.model}' is not supported", "model")

        if self._client is None:
            await self.connect()

        payload = self._build_payload(request)

        try:
            logger.info(
                "Making OpenAI chat request", model=request.model, stream=request.stream
            )

            response = await self._client.post("/chat/completions", json=payload)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key", "openai")
            elif response.status_code == 429:
                retry_after = response.headers.get("retry-after")
                raise RateLimitError(
                    "Rate limit exceeded",
                    "openai",
                    retry_after=float(retry_after) if retry_after else None,
                )
            elif response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise ProviderError(
                    f"OpenAI API error: {response.status_code}",
                    "openai",
                    response.status_code,
                    error_data,
                )

            data = response.json()
            return self._parse_response(data)

        except httpx.TimeoutException:
            raise ProviderError("Request timeout", "openai")
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "openai")

    async def stream_chat(
        self, request: ChatRequest
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Generate a streaming chat completion."""
        if not await self.validate_model(request.model):
            raise ValidationError(f"Model '{request.model}' is not supported", "model")

        if self._client is None:
            await self.connect()

        payload = self._build_payload(request)
        payload["stream"] = True

        try:
            logger.info("Making OpenAI streaming request", model=request.model)

            async with self._client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key", "openai")
                elif response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    raise RateLimitError(
                        "Rate limit exceeded",
                        "openai",
                        retry_after=float(retry_after) if retry_after else None,
                    )
                elif response.status_code != 200:
                    error_data = await response.aread()
                    raise ProviderError(
                        f"OpenAI API error: {response.status_code}",
                        "openai",
                        response.status_code,
                        {"error": error_data.decode()},
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            chunk = self._parse_streaming_chunk(data)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException:
            raise ProviderError("Request timeout", "openai")
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "openai")

    def _build_payload(self, request: ChatRequest) -> Dict[str, Any]:
        """Build OpenAI API payload from request."""
        payload = {
            "model": request.model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in request.messages
            ],
        }

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

        return payload

    def _parse_response(self, data: Dict[str, Any]) -> ChatResponse:
        """Parse OpenAI API response."""
        choice = data["choices"][0]
        usage_data = data.get("usage", {})

        return ChatResponse(
            id=data["id"],
            model=data["model"],
            content=choice["message"]["content"],
            finish_reason=choice.get("finish_reason"),
            usage=Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            ),
            created=datetime.fromtimestamp(data["created"]),
            metadata={"provider": "openai", "raw_response": data},
        )

    def _parse_streaming_chunk(self, data: Dict[str, Any]) -> Optional[StreamingChunk]:
        """Parse OpenAI streaming chunk."""
        if not data.get("choices"):
            return None

        choice = data["choices"][0]
        delta = choice.get("delta", {})

        content = delta.get("content", "")
        if not content and not choice.get("finish_reason"):
            return None

        return StreamingChunk(
            id=data["id"],
            model=data["model"],
            content=content,
            finish_reason=choice.get("finish_reason"),
            created=datetime.fromtimestamp(data["created"]),
            metadata={"provider": "openai", "raw_chunk": data},
        )
