"""Tests for LLMFactory."""

import pytest

from pyaibridge import LLMFactory, ValidationError
from pyaibridge.providers.google import GoogleProvider
from pyaibridge.providers.openai import OpenAIProvider


class TestLLMFactory:
    """Test cases for LLMFactory."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = LLMFactory.create("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.config.api_key == "test-key"

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        with pytest.raises(ValidationError, match="Provider 'unsupported' is not supported"):
            LLMFactory.create("unsupported", api_key="test-key")

    def test_create_google_provider(self):
        """Test creating Google provider."""
        provider = LLMFactory.create("google", api_key="test-key")
        assert isinstance(provider, GoogleProvider)
        assert provider.config.api_key == "test-key"

    def test_list_providers(self):
        """Test listing available providers."""
        providers = LLMFactory.list_providers()
        assert "openai" in providers
        assert "google" in providers
        assert providers["openai"] == OpenAIProvider
        assert providers["google"] == GoogleProvider

    def test_create_with_config_parameters(self):
        """Test creating provider with various config parameters."""
        provider = LLMFactory.create(
            "openai",
            api_key="test-key",
            base_url="https://custom.openai.com",
            max_retries=5,
            timeout=60.0,
            rate_limit=100,
        )

        assert provider.config.api_key == "test-key"
        assert provider.config.base_url == "https://custom.openai.com"
        assert provider.config.max_retries == 5
        assert provider.config.timeout == 60.0
        assert provider.config.rate_limit == 100
