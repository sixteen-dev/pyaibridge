"""Tests for OpenAI provider."""


import httpx
import pytest
import respx

from pyaibridge.core.exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
)
from pyaibridge.core.models import ChatRequest, Message, MessageRole, ProviderConfig
from pyaibridge.providers.openai import OpenAIProvider


class TestOpenAIProvider:
    """Test cases for OpenAI provider."""

    @pytest.fixture
    def provider(self):
        """Create OpenAI provider instance."""
        config = ProviderConfig(api_key="test-key", base_url="https://api.openai.com/v1")
        provider = OpenAIProvider(config)
        # Override the HTTP client creation to use httpx for testing (to work with respx mocks)
        async def mock_connect():
            from pyaibridge.http_client import HybridHttpClient
            provider._client = HybridHttpClient(timeout=provider.config.timeout, use_rust=False)
            await provider._client.connect()
        provider.connect = mock_connect
        return provider

    @pytest.fixture
    def chat_request(self):
        """Create basic chat request."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        return ChatRequest(messages=messages, model="gpt-4.1-mini")

    def test_provider_name(self, provider):
        """Test provider name."""
        assert provider.provider_name == "openai"

    def test_supported_models(self, provider):
        """Test supported models."""
        models = provider.supported_models
        # Latest GPT-4.1 series
        assert "gpt-4.1" in models
        assert "gpt-4.1-mini" in models
        assert "gpt-4.1-nano" in models
        # O-series reasoning models
        assert "o3" in models
        assert "o3-pro" in models
        assert "o4-mini" in models
        # Legacy models
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models
        assert "gpt-4-turbo" in models
        assert "gpt-3.5-turbo" in models

        # Check model has required fields
        gpt41_mini = models["gpt-4.1-mini"]
        assert "context_length" in gpt41_mini
        assert "supports_streaming" in gpt41_mini
        assert "pricing" in gpt41_mini
        assert "knowledge_cutoff" in gpt41_mini

        # Check reasoning model
        o4_mini = models["o4-mini"]
        assert "model_type" in o4_mini
        assert o4_mini["model_type"] == "reasoning"

    async def test_validate_model(self, provider):
        """Test model validation."""
        assert await provider.validate_model("gpt-4.1-mini") is True
        assert await provider.validate_model("o4-mini") is True
        assert await provider.validate_model("gpt-4o-mini") is True
        assert await provider.validate_model("invalid-model") is False

    def test_get_model_info(self, provider):
        """Test getting model info."""
        # Test new GPT-4.1 model
        info = provider.get_model_info("gpt-4.1-mini")
        assert info["context_length"] == 1000000
        assert info["supports_streaming"] is True
        assert info["knowledge_cutoff"] == "June 2024"

        # Test reasoning model
        o4_info = provider.get_model_info("o4-mini")
        assert o4_info["context_length"] == 200000
        assert o4_info["model_type"] == "reasoning"

        # Test legacy model
        legacy_info = provider.get_model_info("gpt-4o-mini")
        assert legacy_info["context_length"] == 128000
        assert legacy_info["supports_streaming"] is True

        with pytest.raises(ValueError):
            provider.get_model_info("invalid-model")

    def test_estimate_tokens(self, provider):
        """Test token estimation."""
        text = "Hello, world!"
        tokens = provider.estimate_tokens(text)
        assert tokens == len(text) // 4

    def test_calculate_cost(self, provider):
        """Test cost calculation."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20}

        # Test new GPT-4.1-mini pricing
        cost = provider.calculate_cost(usage, "gpt-4.1-mini")
        expected_cost = (10 * 0.40 / 1000000) + (20 * 1.60 / 1000000)
        assert abs(cost - expected_cost) < 1e-10

        # Test reasoning model pricing
        o4_cost = provider.calculate_cost(usage, "o4-mini")
        expected_o4_cost = (10 * 0.30 / 1000000) + (20 * 1.20 / 1000000)
        assert abs(o4_cost - expected_o4_cost) < 1e-10

        # Test legacy model pricing
        legacy_cost = provider.calculate_cost(usage, "gpt-4o-mini")
        expected_legacy_cost = (10 * 0.00015 / 1000000) + (20 * 0.0006 / 1000000)
        assert abs(legacy_cost - expected_legacy_cost) < 1e-10

    @pytest.mark.asyncio
    async def test_chat_success(self, provider, chat_request):
        """Test successful chat completion."""
        mock_response = {
            "id": "chatcmpl-123",
            "model": "gpt-4.1-mini",
            "created": 1677649420,
            "choices": [
                {
                    "message": {"content": "Hello there!"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(200, json=mock_response)
            )

            response = await provider.chat(chat_request)

            assert response.id == "chatcmpl-123"
            assert response.model == "gpt-4.1-mini"
            assert response.content == "Hello there!"
            assert response.finish_reason == "stop"
            assert response.usage.prompt_tokens == 10
            assert response.usage.completion_tokens == 20
            assert response.usage.total_tokens == 30

    @pytest.mark.asyncio
    async def test_chat_authentication_error(self, provider, chat_request):
        """Test authentication error handling."""
        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
            )

            with pytest.raises(AuthenticationError):
                await provider.chat(chat_request)

    @pytest.mark.asyncio
    async def test_chat_rate_limit_error(self, provider, chat_request):
        """Test rate limit error handling."""
        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(
                    429,
                    headers={"retry-after": "60"},
                    json={"error": {"message": "Rate limit exceeded"}}
                )
            )

            with pytest.raises(RateLimitError) as exc_info:
                await provider.chat(chat_request)

            assert exc_info.value.retry_after == 60.0

    @pytest.mark.asyncio
    async def test_chat_provider_error(self, provider, chat_request):
        """Test provider error handling."""
        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(500, json={"error": {"message": "Internal server error"}})
            )

            with pytest.raises(ProviderError) as exc_info:
                await provider.chat(chat_request)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_stream_chat_success(self, provider, chat_request):
        """Test successful streaming chat completion."""
        stream_data = [
            'data: {"id":"chatcmpl-123","model":"gpt-4.1-mini","created":1677649420,"choices":[{"delta":{"content":"Hello"}}]}',
            'data: {"id":"chatcmpl-123","model":"gpt-4.1-mini","created":1677649420,"choices":[{"delta":{"content":" there"}}]}',
            'data: {"id":"chatcmpl-123","model":"gpt-4.1-mini","created":1677649420,"choices":[{"delta":{},"finish_reason":"stop"}]}',
            'data: [DONE]'
        ]

        with respx.mock:
            respx.post("https://api.openai.com/v1/chat/completions").mock(
                return_value=httpx.Response(200, content="\n".join(stream_data))
            )

            chunks = []
            async for chunk in provider.stream_chat(chat_request):
                chunks.append(chunk)

            assert len(chunks) == 3  # Three chunks including finish chunk
            assert chunks[0].content == "Hello"
            assert chunks[1].content == " there"
            assert chunks[2].finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_context_manager(self, provider):
        """Test provider as async context manager."""
        async with provider:
            assert provider._client is not None

        assert provider._client is None
