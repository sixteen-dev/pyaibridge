"""Tests for Google provider."""

import json
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import respx

from pyaibridge.core.exceptions import AuthenticationError, ProviderError, RateLimitError
from pyaibridge.core.models import ChatRequest, Message, MessageRole, ProviderConfig
from pyaibridge.providers.google import GoogleProvider


class TestGoogleProvider:
    """Test cases for Google provider."""
    
    @pytest.fixture
    def provider(self):
        """Create Google provider instance."""
        config = ProviderConfig(api_key="test-key", base_url="https://generativelanguage.googleapis.com/v1beta")
        return GoogleProvider(config)
    
    @pytest.fixture
    def chat_request(self):
        """Create basic chat request."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        return ChatRequest(messages=messages, model="gemini-2.5-flash")
    
    def test_provider_name(self, provider):
        """Test provider name."""
        assert provider.provider_name == "google"
    
    def test_supported_models(self, provider):
        """Test supported models."""
        models = provider.supported_models
        assert "gemini-2.5-flash" in models
        assert "gemini-2.5-flash-8b" in models
        assert "gemini-2.5-pro" in models
        assert "gemini-2.0-flash" in models
        assert "gemini-1.5-pro" in models
        assert "gemini-1.5-flash" in models
        assert "gemini-1.5-flash-8b" in models
        
        # Check model has required fields
        flash_model = models["gemini-2.5-flash"]
        assert "context_length" in flash_model
        assert "supports_streaming" in flash_model
        assert "pricing" in flash_model
    
    async def test_validate_model(self, provider):
        """Test model validation."""
        assert await provider.validate_model("gemini-2.5-flash") is True
        assert await provider.validate_model("invalid-model") is False
    
    def test_get_model_info(self, provider):
        """Test getting model info."""
        info = provider.get_model_info("gemini-2.5-flash")
        assert info["context_length"] == 1000000
        assert info["supports_streaming"] is True
        
        with pytest.raises(ValueError):
            provider.get_model_info("invalid-model")
    
    def test_calculate_cost(self, provider):
        """Test cost calculation."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20}
        cost = provider.calculate_cost(usage, "gemini-2.5-flash")
        
        # gemini-2.5-flash pricing: $0.075 per 1M input tokens, $0.30 per 1M output tokens
        expected_cost = (10 * 0.075 / 1000000) + (20 * 0.30 / 1000000)
        assert abs(cost - expected_cost) < 1e-10
    
    def test_convert_role(self, provider):
        """Test role conversion."""
        assert provider._convert_role(MessageRole.USER) == "user"
        assert provider._convert_role(MessageRole.ASSISTANT) == "model"
        assert provider._convert_role(MessageRole.SYSTEM) == "user"  # Google treats system as user
    
    @pytest.mark.asyncio
    async def test_chat_success(self, provider, chat_request):
        """Test successful chat completion."""
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Hello there!"}
                        ]
                    },
                    "finishReason": "STOP"
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
                "totalTokenCount": 30
            }
        }
        
        with respx.mock:
            respx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            ).mock(return_value=httpx.Response(200, json=mock_response))
            
            response = await provider.chat(chat_request)
            
            assert response.model == "gemini-2.5-flash"
            assert response.content == "Hello there!"
            assert response.finish_reason == "STOP"
            assert response.usage.prompt_tokens == 10
            assert response.usage.completion_tokens == 20
            assert response.usage.total_tokens == 30
    
    @pytest.mark.asyncio
    async def test_chat_authentication_error(self, provider, chat_request):
        """Test authentication error handling."""
        with respx.mock:
            respx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            ).mock(return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}}))
            
            with pytest.raises(AuthenticationError):
                await provider.chat(chat_request)
    
    @pytest.mark.asyncio
    async def test_chat_rate_limit_error(self, provider, chat_request):
        """Test rate limit error handling."""
        with respx.mock:
            respx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            ).mock(return_value=httpx.Response(429, json={"error": {"message": "Rate limit exceeded"}}))
            
            with pytest.raises(RateLimitError):
                await provider.chat(chat_request)
    
    @pytest.mark.asyncio
    async def test_chat_provider_error(self, provider, chat_request):
        """Test provider error handling."""
        with respx.mock:
            respx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            ).mock(return_value=httpx.Response(500, json={"error": {"message": "Internal server error"}}))
            
            with pytest.raises(ProviderError) as exc_info:
                await provider.chat(chat_request)
            
            assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_stream_chat_success(self, provider, chat_request):
        """Test successful streaming chat completion."""
        stream_responses = [
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "Hello"}]
                        }
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": " there"}]
                        }
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "!"}]
                        },
                        "finishReason": "STOP"
                    }
                ]
            }
        ]
        
        stream_body = "\n".join(json.dumps(resp) for resp in stream_responses)
        
        with respx.mock:
            respx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent"
            ).mock(return_value=httpx.Response(200, content=stream_body))
            
            chunks = []
            async for chunk in provider.stream_chat(chat_request):
                chunks.append(chunk)
            
            assert len(chunks) == 3
            assert chunks[0].content == "Hello"
            assert chunks[1].content == " there"
            assert chunks[2].content == "!"
            assert chunks[2].finish_reason == "STOP"
    
    @pytest.mark.asyncio
    async def test_build_payload(self, provider, chat_request):
        """Test payload building."""
        payload = provider._build_payload(chat_request)
        
        assert "contents" in payload
        assert len(payload["contents"]) == 1
        assert payload["contents"][0]["role"] == "user"
        assert payload["contents"][0]["parts"][0]["text"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_build_payload_with_parameters(self, provider):
        """Test payload building with parameters."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        request = ChatRequest(
            messages=messages,
            model="gemini-2.5-flash",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            stop=["END"]
        )
        
        payload = provider._build_payload(request)
        
        assert "generationConfig" in payload
        config = payload["generationConfig"]
        assert config["maxOutputTokens"] == 100
        assert config["temperature"] == 0.7
        assert config["topP"] == 0.9
        assert config["stopSequences"] == ["END"]
    
    @pytest.mark.asyncio
    async def test_system_message_handling(self, provider):
        """Test system message handling."""
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful"),
            Message(role=MessageRole.USER, content="Hello")
        ]
        request = ChatRequest(messages=messages, model="gemini-2.5-flash")
        
        payload = provider._build_payload(request)
        
        # System messages should be converted to user messages
        assert len(payload["contents"]) == 2
        assert payload["contents"][0]["role"] == "user"
        assert payload["contents"][0]["parts"][0]["text"] == "You are helpful"
        assert payload["contents"][1]["role"] == "user"
        assert payload["contents"][1]["parts"][0]["text"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, provider):
        """Test provider as async context manager."""
        async with provider:
            assert provider._client is not None
        
        assert provider._client is None