"""Google Gemini provider implementation."""

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


class GoogleProvider(BaseProvider):
    """Google Gemini provider implementation."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    # Model configurations with pricing and capabilities - Updated from Google docs
    SUPPORTED_MODELS = {
        # Gemini 2.5 Series (Latest 2025)
        "gemini-2.5-pro": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 65536,  # 64K tokens
            "supports_streaming": True,
            "supports_thinking": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "supports_search_grounding": True,
            "knowledge_cutoff": "January 2025",
            "pricing": {
                "prompt_per_token": 1.25 / 1000000,
                "completion_per_token": 5.0 / 1000000,
            },
        },
        "gemini-2.5-flash": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 65536,  # 64K tokens
            "supports_streaming": True,
            "supports_thinking": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "supports_search_grounding": True,
            "knowledge_cutoff": "January 2025",
            "pricing": {
                "prompt_per_token": 0.075 / 1000000,
                "completion_per_token": 0.30 / 1000000,
            },
        },
        "gemini-2.5-flash-lite-preview-06-17": {
            "context_length": 1000000,  # 1M tokens
            "max_output": 64000,  # 64K tokens
            "supports_streaming": True,
            "supports_thinking": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "knowledge_cutoff": "January 2025",
            "pricing": {
                "prompt_per_token": 0.0375 / 1000000,  # Most cost-efficient
                "completion_per_token": 0.15 / 1000000,
            },
        },
        # Gemini 2.0 Series
        "gemini-2.0-flash": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 8192,  # 8K tokens
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "supports_search": True,
            "supports_live_api": True,
            "knowledge_cutoff": "August 2024",
            "pricing": {
                "prompt_per_token": 0.075 / 1000000,
                "completion_per_token": 0.30 / 1000000,
            },
        },
        "gemini-2.0-flash-lite": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 8192,  # 8K tokens
            "supports_streaming": True,
            "supports_function_calling": True,
            "knowledge_cutoff": "August 2024",
            "pricing": {
                "prompt_per_token": 0.0375 / 1000000,  # Cost-efficient
                "completion_per_token": 0.15 / 1000000,
            },
        },
        # Gemini 1.5 Series (Legacy but Stable)
        "gemini-1.5-pro": {
            "context_length": 2097152,  # 2M tokens
            "max_output": 8192,  # 8K tokens
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "deprecation_date": "September 2025",
            "pricing": {
                "prompt_per_token": 1.25 / 1000000,
                "completion_per_token": 5.0 / 1000000,
            },
        },
        "gemini-1.5-flash": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 8192,  # 8K tokens
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "deprecation_date": "September 2025",
            "pricing": {
                "prompt_per_token": 0.075 / 1000000,
                "completion_per_token": 0.30 / 1000000,
            },
        },
        "gemini-1.5-flash-8b": {
            "context_length": 1048576,  # 1M tokens
            "max_output": 8192,  # 8K tokens
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_code_execution": True,
            "deprecation_date": "September 2025",
            "pricing": {
                "prompt_per_token": 0.0375 / 1000000,
                "completion_per_token": 0.15 / 1000000,
            },
        },
    }

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Google Gemini provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.base_url = config.base_url or self.BASE_URL
        self._client: httpx.AsyncClient | None = None

        logger.info("Google Gemini provider initialized", base_url=self.base_url)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "google"

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
                    "x-goog-api-key": self.config.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "pyaibridge/0.0.1",
                },
            )
            logger.info("Google Gemini client connected")

    async def disconnect(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Google Gemini client disconnected")

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
        endpoint = f"/models/{request.model}:generateContent"

        try:
            logger.info(
                "Making Google Gemini chat request",
                model=request.model,
                stream=request.stream,
            )

            response = await self._client.post(endpoint, json=payload)

            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_str = str(error_data)
                if "API_KEY" in error_str or "api_key" in error_str.lower():
                    raise AuthenticationError("Invalid API key", "google")
                else:
                    raise ProviderError(
                        f"Bad request: {error_data}", "google", 400, error_data
                    )
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key", "google")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", "google")
            elif response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise ProviderError(
                    f"Google Gemini API error: {response.status_code}",
                    "google",
                    response.status_code,
                    error_data,
                )

            data = response.json()
            return self._parse_response(data, request.model)

        except httpx.TimeoutException as e:
            raise ProviderError("Request timeout", "google") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "google") from e

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
        endpoint = f"/models/{request.model}:streamGenerateContent"

        try:
            logger.info("Making Google Gemini streaming request", model=request.model)

            async with self._client.stream("POST", endpoint, json=payload) as response:
                if response.status_code == 400:
                    error_data = await response.aread()
                    error_str = error_data.decode().lower()
                    if (
                        b"API_KEY" in error_data
                        or b"api_key" in error_data
                        or "api_key" in error_str
                    ):
                        raise AuthenticationError("Invalid API key", "google")
                    else:
                        raise ProviderError(
                            f"Bad request: {error_data.decode()}", "google", 400
                        )
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key", "google")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded", "google")
                elif response.status_code != 200:
                    error_data = await response.aread()
                    raise ProviderError(
                        f"Google Gemini API error: {response.status_code}",
                        "google",
                        response.status_code,
                        {"error": error_data.decode()},
                    )

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            chunk = self._parse_streaming_chunk(data, request.model)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException as e:
            raise ProviderError("Request timeout", "google") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Request failed: {e}", "google") from e

    def _build_payload(self, request: ChatRequest) -> dict[str, Any]:
        """Build Google Gemini API payload from request."""
        # Convert messages to Google's format
        contents = []
        for msg in request.messages:
            role = self._convert_role(msg.role)
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload: dict[str, Any] = {
            "contents": contents,
        }

        # Add generation config if parameters are provided
        generation_config: dict[str, Any] = {}
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.top_p is not None:
            generation_config["topP"] = request.top_p
        if request.stop is not None:
            generation_config["stopSequences"] = (
                request.stop if isinstance(request.stop, list) else [request.stop]
            )

        if generation_config:
            payload["generationConfig"] = generation_config

        return payload

    def _convert_role(self, role: MessageRole) -> str:
        """Convert MessageRole to Google's role format."""
        if role == MessageRole.USER:
            return "user"
        elif role == MessageRole.ASSISTANT:
            return "model"
        elif role == MessageRole.SYSTEM:
            # Google doesn't have a system role, so we'll treat it as user
            return "user"
        else:
            return "user"

    def _parse_response(self, data: dict[str, Any], model: str) -> ChatResponse:
        """Parse Google Gemini API response."""
        if "candidates" not in data or not data["candidates"]:
            raise ProviderError("No candidates in response", "google", details=data)

        candidate = data["candidates"][0]

        if "content" not in candidate or "parts" not in candidate["content"]:
            raise ProviderError("Invalid response format", "google", details=data)

        content = ""
        for part in candidate["content"]["parts"]:
            if "text" in part:
                content += part["text"]

        # Extract usage information if available
        usage_data = data.get("usageMetadata", {})
        usage = Usage(
            prompt_tokens=usage_data.get("promptTokenCount", 0),
            completion_tokens=usage_data.get("candidatesTokenCount", 0),
            total_tokens=usage_data.get("totalTokenCount", 0),
        )

        return ChatResponse(
            id=str(uuid.uuid4()),  # Google doesn't provide IDs, so we generate one
            model=model,
            content=content,
            finish_reason=candidate.get("finishReason"),
            usage=usage,
            created=datetime.now(),
            metadata={"provider": "google", "raw_response": data},
        )

    def _parse_streaming_chunk(
        self, data: dict[str, Any], model: str
    ) -> StreamingChunk | None:
        """Parse Google Gemini streaming chunk."""
        if "candidates" not in data or not data["candidates"]:
            return None

        candidate = data["candidates"][0]

        if "content" not in candidate or "parts" not in candidate["content"]:
            return None

        content = ""
        for part in candidate["content"]["parts"]:
            if "text" in part:
                content += part["text"]

        if not content and not candidate.get("finishReason"):
            return None

        return StreamingChunk(
            id=str(uuid.uuid4()),  # Google doesn't provide IDs, so we generate one
            model=model,
            content=content,
            finish_reason=candidate.get("finishReason"),
            created=datetime.now(),
            metadata={"provider": "google", "raw_chunk": data},
        )
