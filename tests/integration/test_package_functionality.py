"""
Integration tests to verify all package functionalities work correctly.
These tests verify the package can be imported and all providers work as expected.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestPackageImports:
    """Test that all package components can be imported correctly."""
    
    def test_main_package_import(self):
        """Test main package can be imported."""
        import pyaibridge
        assert hasattr(pyaibridge, '__version__')
        assert pyaibridge.__version__ == "0.1.2"
    
    def test_provider_imports(self):
        """Test all providers can be imported."""
        from pyaibridge.providers import OpenAIProvider, GoogleProvider, ClaudeProvider, XAIProvider
        
        # Verify providers are classes
        assert isinstance(OpenAIProvider, type)
        assert isinstance(GoogleProvider, type) 
        assert isinstance(ClaudeProvider, type)
        assert isinstance(XAIProvider, type)
    
    def test_core_models_import(self):
        """Test core models can be imported."""
        from pyaibridge.core.models import (
            ChatRequest, ChatResponse, Message, MessageRole, 
            ProviderConfig, Usage, StreamingChunk
        )
        
        # Verify they are classes/enums
        assert isinstance(ChatRequest, type)
        assert isinstance(ChatResponse, type)
        assert isinstance(Message, type)
        assert isinstance(ProviderConfig, type)
        assert isinstance(Usage, type)
        assert isinstance(StreamingChunk, type)
    
    def test_exceptions_import(self):
        """Test exception classes can be imported."""
        from pyaibridge.core.exceptions import (
            PyAIBridgeError, ProviderError, AuthenticationError,
            RateLimitError, ValidationError, TimeoutError
        )
        
        # Verify they are exception classes
        assert issubclass(PyAIBridgeError, Exception)
        assert issubclass(ProviderError, PyAIBridgeError)
        assert issubclass(AuthenticationError, ProviderError)
        assert issubclass(RateLimitError, ProviderError)
        assert issubclass(ValidationError, PyAIBridgeError)
        assert issubclass(TimeoutError, PyAIBridgeError)


class TestProviderInitialization:
    """Test that all providers can be initialized correctly."""
    
    def test_openai_provider_init(self):
        """Test OpenAI provider initialization."""
        from pyaibridge.providers import OpenAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = OpenAIProvider(config)
        
        assert provider.provider_name == "openai"
        assert provider.config.api_key == "test-key-123"
        assert len(provider.supported_models) > 0
        assert "gpt-4.1" in provider.supported_models
    
    def test_google_provider_init(self):
        """Test Google provider initialization."""
        from pyaibridge.providers import GoogleProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = GoogleProvider(config)
        
        assert provider.provider_name == "google"
        assert provider.config.api_key == "test-key-123"
        assert len(provider.supported_models) > 0
        assert "gemini-2.5-flash" in provider.supported_models
    
    def test_claude_provider_init(self):
        """Test Claude provider initialization."""
        from pyaibridge.providers import ClaudeProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = ClaudeProvider(config)
        
        assert provider.provider_name == "claude"
        assert provider.config.api_key == "test-key-123"
        assert len(provider.supported_models) > 0
        assert "claude-4-opus" in provider.supported_models
    
    def test_xai_provider_init(self):
        """Test xAI provider initialization.""" 
        from pyaibridge.providers import XAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = XAIProvider(config)
        
        assert provider.provider_name == "xai"
        assert provider.config.api_key == "test-key-123"
        assert len(provider.supported_models) > 0
        assert "grok-4" in provider.supported_models


class TestModelValidation:
    """Test model validation across all providers."""
    
    async def test_all_providers_model_validation(self):
        """Test model validation for all providers."""
        from pyaibridge.providers import OpenAIProvider, GoogleProvider, ClaudeProvider, XAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        providers = [
            OpenAIProvider(config),
            GoogleProvider(config), 
            ClaudeProvider(config),
            XAIProvider(config)
        ]
        
        for provider in providers:
            # Test valid models
            for model in list(provider.supported_models.keys())[:3]:  # Test first 3 models
                result = await provider.validate_model(model)
                assert result, f"{provider.provider_name} should support {model}"
            
            # Test invalid model
            result = await provider.validate_model("invalid-model-xyz")
            assert not result, f"{provider.provider_name} should not support invalid model"


class TestMessageCreation:
    """Test message and request creation."""
    
    def test_message_creation(self):
        """Test creating messages."""
        from pyaibridge.core.models import Message, MessageRole
        
        # Test user message
        user_msg = Message(role=MessageRole.USER, content="Hello, world!")
        assert user_msg.role == MessageRole.USER
        assert user_msg.content == "Hello, world!"
        
        # Test assistant message
        assistant_msg = Message(role=MessageRole.ASSISTANT, content="Hi there!")
        assert assistant_msg.role == MessageRole.ASSISTANT
        assert assistant_msg.content == "Hi there!"
        
        # Test system message
        system_msg = Message(role=MessageRole.SYSTEM, content="You are helpful.")
        assert system_msg.role == MessageRole.SYSTEM
        assert system_msg.content == "You are helpful."
    
    def test_chat_request_creation(self):
        """Test creating chat requests."""
        from pyaibridge.core.models import ChatRequest, Message, MessageRole
        
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful."),
            Message(role=MessageRole.USER, content="Hello!")
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1",
            max_tokens=100,
            temperature=0.7
        )
        
        assert len(request.messages) == 2
        assert request.model == "gpt-4.1"
        assert request.max_tokens == 100
        assert request.temperature == 0.7


class TestCostCalculation:
    """Test cost calculation functionality."""
    
    def test_cost_calculation_all_providers(self):
        """Test cost calculation for all providers."""
        from pyaibridge.providers import OpenAIProvider, GoogleProvider, ClaudeProvider, XAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        
        test_usage = {"prompt_tokens": 100, "completion_tokens": 50}
        
        # Test OpenAI
        openai_provider = OpenAIProvider(config)
        cost = openai_provider.calculate_cost(test_usage, "gpt-4.1")
        assert cost > 0, "OpenAI cost should be positive"
        
        # Test Google
        google_provider = GoogleProvider(config)
        cost = google_provider.calculate_cost(test_usage, "gemini-2.5-flash")
        assert cost > 0, "Google cost should be positive"
        
        # Test Claude
        claude_provider = ClaudeProvider(config)
        cost = claude_provider.calculate_cost(test_usage, "claude-4-sonnet")
        assert cost > 0, "Claude cost should be positive"
        
        # Test xAI
        xai_provider = XAIProvider(config)
        cost = xai_provider.calculate_cost(test_usage, "grok-4")
        assert cost > 0, "xAI cost should be positive"


class TestProviderConfiguration:
    """Test provider configuration handling."""
    
    def test_provider_config_validation(self):
        """Test provider configuration validation."""
        from pyaibridge.core.models import ProviderConfig
        
        # Test valid config
        config = ProviderConfig(
            api_key="test-key-at-least-32-chars-long",
            timeout=30.0,
            max_retries=3
        )
        assert config.api_key == "test-key-at-least-32-chars-long"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        
        # Test config with optional parameters
        config_with_options = ProviderConfig(
            api_key="test-key-at-least-32-chars-long",
            base_url="https://custom.api.com",
            rate_limit=100
        )
        assert config_with_options.base_url == "https://custom.api.com"
        assert config_with_options.rate_limit == 100
    
    def test_invalid_config(self):
        """Test invalid configuration handling."""
        from pyaibridge.core.models import ProviderConfig
        from pydantic import ValidationError
        
        # Test negative timeout
        with pytest.raises(ValidationError):
            ProviderConfig(api_key="test-key", timeout=-1)
        
        # Test negative max_retries
        with pytest.raises(ValidationError):
            ProviderConfig(api_key="test-key", max_retries=-1)


class TestModelInfo:
    """Test model information retrieval."""
    
    def test_model_info_retrieval(self):
        """Test getting model information."""
        from pyaibridge.providers import OpenAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = OpenAIProvider(config)
        
        # Test valid model
        model_info = provider.get_model_info("gpt-4.1")
        assert "context_length" in model_info
        assert "supports_streaming" in model_info
        assert "pricing" in model_info
        
        # Test invalid model
        with pytest.raises(ValueError):
            provider.get_model_info("invalid-model")


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_token_estimation(self):
        """Test token estimation functionality."""
        from pyaibridge.providers import OpenAIProvider
        from pyaibridge.core.models import ProviderConfig
        
        config = ProviderConfig(api_key="test-key-123")
        provider = OpenAIProvider(config)
        
        # Test token estimation
        text = "Hello, world! This is a test message."
        estimated_tokens = provider.estimate_tokens(text)
        assert isinstance(estimated_tokens, int)
        assert estimated_tokens > 0
    
    def test_role_conversion(self):
        """Test role conversion in providers."""
        from pyaibridge.providers import XAIProvider
        from pyaibridge.core.models import ProviderConfig, MessageRole
        
        config = ProviderConfig(api_key="test-key-123")
        provider = XAIProvider(config)
        
        # Test role conversions
        assert provider._convert_role(MessageRole.USER) == "user"
        assert provider._convert_role(MessageRole.ASSISTANT) == "assistant"
        assert provider._convert_role(MessageRole.SYSTEM) == "system"