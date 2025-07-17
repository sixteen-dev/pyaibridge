"""Factory for creating LLM providers."""

from __future__ import annotations

from typing import Any

from .core.base import BaseProvider
from .core.exceptions import ValidationError
from .core.models import ProviderConfig
from .providers.claude import ClaudeProvider
from .providers.google import GoogleProvider
from .providers.openai import OpenAIProvider
from .providers.xai import XAIProvider


class LLMFactory:
    """Factory for creating LLM providers."""

    _providers: dict[str, type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "google": GoogleProvider,
        "claude": ClaudeProvider,
        "xai": XAIProvider,
    }

    @classmethod
    def create(cls, provider: str, **kwargs: Any) -> BaseProvider:
        """Create a provider instance.

        Args:
            provider: Provider name (e.g., "openai")
            **kwargs: Configuration parameters

        Returns:
            Provider instance

        Raises:
            ValidationError: If provider is not supported
        """
        if provider not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValidationError(
                f"Provider '{provider}' is not supported. Available providers: {available}",
                "provider",
            )

        provider_class = cls._providers[provider]
        config = ProviderConfig(**kwargs)

        return provider_class(config)

    @classmethod
    def list_providers(cls) -> dict[str, type[BaseProvider]]:
        """List available providers.

        Returns:
            Dictionary of provider names to classes
        """
        return cls._providers.copy()

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseProvider]) -> None:
        """Register a new provider.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        if not issubclass(provider_class, BaseProvider):
            raise ValidationError(
                "Provider class must inherit from BaseProvider", "provider_class"
            )

        cls._providers[name] = provider_class
