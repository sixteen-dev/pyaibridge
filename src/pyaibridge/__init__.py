"""
pyaibridge - High-performance unified API for all LLM providers
"""

__version__ = "0.2.2"
__author__ = "Sujeeth Shetty"
__email__ = "sujeeth.data@gmail.com"

from .core.base import BaseProvider
from .core.exceptions import (
    AuthenticationError,
    ProviderError,
    PyAIBridgeError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .core.models import (
    ChatRequest,
    ChatResponse,
    Message,
    MessageRole,
    ProviderConfig,
    StreamingChunk,
    Usage,
)
from .factory import LLMFactory
from .providers import ClaudeProvider, GoogleProvider, OpenAIProvider, XAIProvider
from .utils.metrics import MetricsCollector, metrics

__all__ = [
    # Core classes
    "BaseProvider",
    "LLMFactory",
    # Models
    "ChatRequest",
    "ChatResponse",
    "Message",
    "MessageRole",
    "ProviderConfig",
    "StreamingChunk",
    "Usage",
    # Providers
    "ClaudeProvider",
    "GoogleProvider",
    "OpenAIProvider",
    "XAIProvider",
    # Exceptions
    "PyAIBridgeError",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    # Utilities
    "MetricsCollector",
    "metrics",
]
