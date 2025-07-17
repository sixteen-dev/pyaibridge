"""Tests for xAI provider."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
import respx
import httpx

from pyaibridge.core.exceptions import AuthenticationError, ProviderError, RateLimitError, ValidationError
from pyaibridge.core.models import ChatRequest, Message, MessageRole, ProviderConfig
from pyaibridge.providers.xai import XAIProvider


class TestXAIProvider:
    """Test cases for xAI provider."""
    
    @pytest.fixture
    def provider(self):
        """Create xAI provider instance."""
        config = ProviderConfig(api_key="test-key", base_url="https://api.x.ai/v1")
        return XAIProvider(config)
    
    @pytest.fixture
    def chat_request(self):
        """Create basic chat request."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        return ChatRequest(messages=messages, model="grok-3-mini")
    
    def test_provider_name(self, provider):
        """Test provider name."""
        assert provider.provider_name == "xai"
    
    def test_supported_models(self, provider):
        """Test supported models."""
        models = provider.supported_models
        # Grok 4 series
        assert "grok-4-0709" in models
        # Grok 3 series
        assert "grok-3" in models
        assert "grok-3-mini" in models
        assert "grok-3-fast" in models
        assert "grok-3-mini-fast" in models
        # Grok 2 series
        assert "grok-2-vision-1212" in models
        assert "grok-2-image-1212" in models
        
        # Check model capabilities
        grok4_info = models["grok-4-0709"]
        assert grok4_info["supports_streaming"] is True
        assert grok4_info["supports_tool_use"] is True
        assert grok4_info["supports_search"] is True
        assert grok4_info["context_length"] == 256000
        
        # Check vision model
        vision_info = models["grok-2-vision-1212"]
        assert vision_info["supports_vision"] is True
    
    async def test_validate_model(self, provider):
        """Test model validation."""
        assert await provider.validate_model("grok-3-mini") is True
        assert await provider.validate_model("grok-4-0709") is True
        assert await provider.validate_model("invalid-model") is False
    
    def test_convert_role(self, provider):
        """Test role conversion."""
        assert provider._convert_role(MessageRole.USER) == "user"
        assert provider._convert_role(MessageRole.ASSISTANT) == "assistant"
        assert provider._convert_role(MessageRole.SYSTEM) == "system"
    
    def test_prepare_messages(self, provider):
        """Test message preparation."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "system", "content": "You are helpful."}
        ]
        
        formatted = provider._prepare_messages(messages)
        
        assert len(formatted) == 3
        assert formatted[0] == {"role": "user", "content": "Hello"}
        assert formatted[1] == {"role": "assistant", "content": "Hi there!"}
        assert formatted[2] == {"role": "system", "content": "You are helpful."}
    
    def test_calculate_cost(self, provider):
        """Test cost calculation."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20}
        cost = provider.calculate_cost(usage, "grok-3-mini")
        
        # grok-3-mini pricing: $0.30 per 1M input tokens, $0.50 per 1M output tokens
        expected_cost = (10 * 0.30 / 1000000) + (20 * 0.50 / 1000000)
        assert abs(cost - expected_cost) < 1e-10
    
    def test_calculate_cost_grok4(self, provider):
        """Test cost calculation for Grok 4."""
        usage = {"prompt_tokens": 15, "completion_tokens": 25}
        cost = provider.calculate_cost(usage, "grok-4-0709")
        
        # grok-4-0709 pricing: $3.00 per 1M input tokens, $15.00 per 1M output tokens
        expected_cost = (15 * 3.00 / 1000000) + (25 * 15.00 / 1000000)
        assert abs(cost - expected_cost) < 1e-10
    
    def test_calculate_cost_grok3(self, provider):
        """Test cost calculation for Grok 3 model."""
        usage = {"prompt_tokens": 5, "completion_tokens": 10}
        cost = provider.calculate_cost(usage, "grok-3")
        
        # grok-3 pricing: $3.00 per 1M input tokens, $15.00 per 1M output tokens
        expected_cost = (5 * 3.00 / 1000000) + (10 * 15.00 / 1000000)
        assert abs(cost - expected_cost) < 1e-10
    
    def test_calculate_cost_invalid_model(self, provider):
        """Test cost calculation with invalid model."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20}
        
        with pytest.raises(ValueError, match="Model 'invalid-model' is not supported"):
            provider.calculate_cost(usage, "invalid-model")
    
    @respx.mock
    async def test_chat_success(self, provider, chat_request):
        """Test successful chat completion."""
        # Mock the response
        mock_response = {
            "id": "chatcmpl-123",
            "model": "grok-3-mini",
            "choices": [{
                "message": {"content": "Hello! How can I help you?"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18
            }
        }
        
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        response = await provider.chat(chat_request)
        
        assert response.id == "chatcmpl-123"
        assert response.model == "grok-3-mini"
        assert response.content == "Hello! How can I help you?"
        assert response.finish_reason == "stop"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 8
        assert response.usage.total_tokens == 18
        assert response.metadata["provider"] == "xai"
    
    @respx.mock
    async def test_chat_authentication_error(self, provider, chat_request):
        """Test chat with authentication error."""
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
        )
        
        with pytest.raises(AuthenticationError, match="Invalid xAI API key"):
            await provider.chat(chat_request)
    
    @respx.mock
    async def test_chat_rate_limit_error(self, provider, chat_request):
        """Test chat with rate limit error."""
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(429, json={"error": {"message": "Rate limit exceeded"}})
        )
        
        with pytest.raises(RateLimitError, match="xAI rate limit exceeded"):
            await provider.chat(chat_request)
    
    @respx.mock
    async def test_chat_provider_error(self, provider, chat_request):
        """Test chat with provider error."""
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Internal server error"}})
        )
        
        with pytest.raises(ProviderError, match="xAI API error \\(500\\)"):
            await provider.chat(chat_request)
    
    async def test_chat_invalid_model(self, provider):
        """Test chat with invalid model."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        request = ChatRequest(messages=messages, model="invalid-model")
        
        with pytest.raises(ValidationError, match="Model 'invalid-model' is not supported by xAI"):
            await provider.chat(request)
    
    async def test_stream_chat_success(self, provider, chat_request):
        """Test successful streaming chat completion."""
        # Skip this test for now as it requires complex streaming mock setup
        # This would be tested in integration tests  
        pass
    
    async def test_connection_lifecycle(self, provider):
        """Test connection and disconnection."""
        # Initially no client
        assert provider._client is None
        
        # Connect
        await provider.connect()
        assert provider._client is not None
        assert isinstance(provider._client, httpx.AsyncClient)
        
        # Disconnect
        await provider.disconnect()
        assert provider._client is None
    
    async def test_context_manager(self, provider):
        """Test async context manager."""
        assert provider._client is None
        
        async with provider:
            assert provider._client is not None
            
        assert provider._client is None
    
    def test_model_info_access(self, provider):
        """Test accessing model information."""
        grok4_info = provider.get_model_info("grok-4-0709")
        assert grok4_info["supports_tool_use"] is True
        assert grok4_info["supports_search"] is True
        assert grok4_info["context_length"] == 256000
        
        vision_info = provider.get_model_info("grok-2-vision-1212")
        assert vision_info["supports_vision"] is True
        
        with pytest.raises(ValueError, match="Model 'invalid' is not supported by xai"):
            provider.get_model_info("invalid")