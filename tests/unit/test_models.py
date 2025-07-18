"""Tests for data models."""

import pytest
from datetime import datetime

from pyaibridge.core.models import (
    ChatRequest,
    ChatResponse,
    Message,
    MessageRole,
    ProviderConfig,
    StreamingChunk,
    Usage,
)


class TestMessage:
    """Test cases for Message model."""
    
    def test_valid_message(self):
        """Test creating a valid message."""
        message = Message(role=MessageRole.USER, content="Hello, world!")
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.name is None
        assert message.metadata == {}
    
    def test_message_with_metadata(self):
        """Test message with metadata."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Hi there!",
            name="assistant",
            metadata={"confidence": 0.95}
        )
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Hi there!"
        assert message.name == "assistant"
        assert message.metadata == {"confidence": 0.95}
    
    def test_empty_content_fails(self):
        """Test that empty content fails validation."""
        with pytest.raises(ValueError):
            Message(role=MessageRole.USER, content="")


class TestChatRequest:
    """Test cases for ChatRequest model."""
    
    def test_basic_request(self):
        """Test creating a basic chat request."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        request = ChatRequest(messages=messages, model="gpt-4o-mini")
        
        assert len(request.messages) == 1
        assert request.model == "gpt-4o-mini"
        assert request.stream is False
        assert request.timeout == 30.0
    
    def test_request_with_parameters(self):
        """Test chat request with various parameters."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        request = ChatRequest(
            messages=messages,
            model="gpt-4o",
            max_tokens=100,
            temperature=0.8,
            top_p=0.9,
            stop=["\\n", "END"],
            stream=True,
            user="test-user",
            timeout=60.0,
        )
        
        assert request.max_tokens == 100
        assert request.temperature == 0.8
        assert request.top_p == 0.9
        assert request.stop == ["\\n", "END"]
        assert request.stream is True
        assert request.user == "test-user"
        assert request.timeout == 60.0
    
    def test_empty_messages_fails(self):
        """Test that empty messages list fails validation."""
        with pytest.raises(ValueError):
            ChatRequest(messages=[], model="gpt-4o-mini")
    
    def test_too_many_stop_sequences_fails(self):
        """Test that too many stop sequences fails validation."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        with pytest.raises(ValueError):
            ChatRequest(
                messages=messages,
                model="gpt-4o-mini",
                stop=["1", "2", "3", "4", "5"]  # More than 4
            )
    
    def test_invalid_temperature_fails(self):
        """Test that invalid temperature fails validation."""
        messages = [Message(role=MessageRole.USER, content="Hello")]
        with pytest.raises(ValueError):
            ChatRequest(messages=messages, model="gpt-4o-mini", temperature=3.0)


class TestChatResponse:
    """Test cases for ChatResponse model."""
    
    def test_basic_response(self):
        """Test creating a basic chat response."""
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        response = ChatResponse(
            id="test-123",
            model="gpt-4o-mini",
            content="Hello there!",
            usage=usage,
        )
        
        assert response.id == "test-123"
        assert response.model == "gpt-4o-mini"
        assert response.content == "Hello there!"
        assert response.usage.total_tokens == 30
        assert isinstance(response.created, datetime)
        assert response.metadata == {}
    
    def test_response_with_finish_reason(self):
        """Test response with finish reason."""
        response = ChatResponse(
            id="test-123",
            model="gpt-4o-mini",
            content="Hello!",
            finish_reason="stop",
        )
        
        assert response.finish_reason == "stop"


class TestUsage:
    """Test cases for Usage model."""
    
    def test_valid_usage(self):
        """Test creating valid usage."""
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
    
    def test_negative_tokens_fails(self):
        """Test that negative tokens fail validation."""
        with pytest.raises(ValueError):
            Usage(prompt_tokens=-1, completion_tokens=20, total_tokens=19)


class TestProviderConfig:
    """Test cases for ProviderConfig model."""
    
    def test_basic_config(self):
        """Test creating basic provider config."""
        config = ProviderConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.base_url is None
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.rate_limit is None
        assert config.metadata == {}
    
    def test_config_with_all_parameters(self):
        """Test config with all parameters."""
        config = ProviderConfig(
            api_key="test-key",
            base_url="https://api.example.com",
            max_retries=5,
            timeout=60.0,
            rate_limit=100,
            metadata={"custom": "value"},
        )
        
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.example.com"
        assert config.max_retries == 5
        assert config.timeout == 60.0
        assert config.rate_limit == 100
        assert config.metadata == {"custom": "value"}
    
    def test_invalid_max_retries_fails(self):
        """Test that invalid max_retries fails validation."""
        with pytest.raises(ValueError):
            ProviderConfig(api_key="test-key", max_retries=-1)
    
    def test_invalid_timeout_fails(self):
        """Test that invalid timeout fails validation."""
        with pytest.raises(ValueError):
            ProviderConfig(api_key="test-key", timeout=0.0)