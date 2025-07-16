"""Anthropic Claude provider implementation."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

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


class ClaudeProvider(BaseProvider):
    """Anthropic Claude provider implementation."""

    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    # Model configurations with pricing (per 1M tokens)
    SUPPORTED_MODELS = {
        # Claude 4 Series (Latest 2025)
        "claude-4-opus": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "April 2024",
            "pricing": {
                "prompt_per_token": 15.00 / 1000000,
                "completion_per_token": 75.00 / 1000000,
            },
        },
        "claude-4-sonnet": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "April 2024",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        "claude-4-haiku": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "April 2024",
            "pricing": {
                "prompt_per_token": 0.25 / 1000000,
                "completion_per_token": 1.25 / 1000000,
            },
        },
        # Claude 3.5 Series (Current Production)
        "claude-3-5-sonnet-20241022": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "April 2024",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        "claude-3-5-haiku-20241022": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "July 2024",
            "pricing": {
                "prompt_per_token": 1.00 / 1000000,
                "completion_per_token": 5.00 / 1000000,
            },
        },
        # Claude 3 Series (Legacy but Stable)
        "claude-3-opus-20240229": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "August 2023",
            "pricing": {
                "prompt_per_token": 15.00 / 1000000,
                "completion_per_token": 75.00 / 1000000,
            },
        },
        "claude-3-sonnet-20240229": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "August 2023",
            "pricing": {
                "prompt_per_token": 3.00 / 1000000,
                "completion_per_token": 15.00 / 1000000,
            },
        },
        "claude-3-haiku-20240307": {
            "context_length": 200000,
            "supports_streaming": True,
            "knowledge_cutoff": "August 2023",
            "pricing": {
                "prompt_per_token": 0.25 / 1000000,
                "completion_per_token": 1.25 / 1000000,
            },
        },
    }

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Anthropic Claude provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.base_url = config.base_url or self.BASE_URL
        self._client: httpx.AsyncClient | None = None

        logger.info("Anthropic Claude provider initialized", base_url=self.base_url)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "claude"

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
                    "x-api-key": self.config.api_key,
                    "content-type": "application/json",
                    "anthropic-version": self.API_VERSION,
                    "user-agent": "pyaibridge/0.1.1",
                },
            )
            logger.info("Anthropic Claude client connected")

    async def disconnect(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Anthropic Claude client disconnected")

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

        assert self._client is not None

        payload = self._build_payload(request)

        try:
            logger.info(
                "Making Anthropic Claude chat request",
                model=request.model,
                stream=request.stream,
            )

            response = await self._client.post("/messages", json=payload)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key", "claude")
            elif response.status_code == 429:
                retry_after = response.headers.get("retry-after")
                raise RateLimitError(
                    "Rate limit exceeded",
                    "claude",
                    retry_after=float(retry_after) if retry_after else None,
                )
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(
                    f"Bad request: {error_data.get('error', {}).get('message', 'Unknown error')}",
                    "claude"
                )
            elif response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise ProviderError(
                    f"Anthropic Claude API error: {response.status_code}",
                    "claude",
                    response.status_code,
                    error_data,
                )

            data = response.json()
            return self._parse_response(data, request.model)

        except httpx.TimeoutException as e:
            raise ProviderError("Request timeout", "claude") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "claude") from e

    async def stream_chat(  # type: ignore[override]
        self, request: ChatRequest
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Generate a streaming chat completion."""
        if not await self.validate_model(request.model):
            raise ValidationError(f"Model '{request.model}' is not supported", "model")

        if self._client is None:
            await self.connect()

        assert self._client is not None

        payload = self._build_payload(request)
        payload["stream"] = True

        try:
            logger.info("Making Anthropic Claude streaming request", model=request.model)

            async with self._client.stream("POST", "/messages", json=payload) as response:
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key", "claude")
                elif response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    raise RateLimitError(
                        "Rate limit exceeded",
                        "claude",
                        retry_after=float(retry_after) if retry_after else None,
                    )
                elif response.status_code != 200:
                    error_data = await response.aread()
                    raise ProviderError(
                        f"Anthropic Claude API error: {response.status_code}",
                        "claude",
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
                            chunk = self._parse_streaming_chunk(data, request.model)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException as e:
            raise ProviderError("Request timeout", "claude") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "claude") from e

    def _build_payload(self, request: ChatRequest) -> dict[str, Any]:
        """Build Anthropic Claude API payload from request."""
        # Separate system messages from conversation
        system_messages = []
        conversation_messages = []

        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                system_messages.append(msg.content)
            else:
                conversation_messages.append({
                    "role": self._convert_role(msg.role),
                    "content": msg.content
                })

        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens or 4096,
            "messages": conversation_messages,
        }

        # Add system prompt if any system messages exist
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)

        # Add optional parameters
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop is not None:
            payload["stop_sequences"] = (
                request.stop if isinstance(request.stop, list) else [request.stop]
            )

        return payload

    def _convert_role(self, role: MessageRole) -> str:
        """Convert MessageRole to Claude's role format."""
        if role == MessageRole.USER:
            return "user"
        elif role == MessageRole.ASSISTANT:
            return "assistant"
        else:
            # Claude doesn't support system role in messages, handle separately
            return "user"

    def _parse_response(self, data: dict[str, Any], model: str) -> ChatResponse:
        """Parse Anthropic Claude API response."""
        if "content" not in data or not data["content"]:
            raise ProviderError("No content in response", "claude", details=data)

        # Extract content from Claude's response format
        content = ""
        for content_block in data["content"]:
            if content_block.get("type") == "text":
                content += content_block.get("text", "")

        # Extract usage information
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )

        return ChatResponse(
            id=data.get("id", str(uuid.uuid4())),
            model=data.get("model", model),
            content=content,
            finish_reason=data.get("stop_reason"),
            usage=usage,
            created=datetime.now(),
            metadata={"provider": "claude", "raw_response": data},
        )

    def _parse_streaming_chunk(
        self, data: dict[str, Any], model: str
    ) -> StreamingChunk | None:
        """Parse Anthropic Claude streaming chunk."""
        event_type = data.get("type")

        if event_type == "content_block_delta":
            # Extract text delta from content block
            delta = data.get("delta", {})
            if delta.get("type") == "text_delta":
                content = delta.get("text", "")
                if content:
                    return StreamingChunk(
                        id=str(uuid.uuid4()),
                        model=model,
                        content=content,
                        finish_reason=None,
                        created=datetime.now(),
                        metadata={"provider": "claude", "raw_chunk": data},
                    )

        elif event_type == "message_delta":
            # Check for completion
            delta = data.get("delta", {})
            stop_reason = delta.get("stop_reason")
            if stop_reason:
                return StreamingChunk(
                    id=str(uuid.uuid4()),
                    model=model,
                    content="",
                    finish_reason=stop_reason,
                    created=datetime.now(),
                    metadata={"provider": "claude", "raw_chunk": data},
                )

        return None
