# Factory Pattern

The `LLMFactory` is the main entry point for creating provider instances in PyAIBridge. It provides a unified way to instantiate any supported LLM provider.

## Basic Usage

```python
from pyaibridge import LLMFactory

# Create providers
openai_provider = LLMFactory.create("openai", api_key="sk-...")
google_provider = LLMFactory.create("google", api_key="AIza...")
claude_provider = LLMFactory.create("claude", api_key="sk-ant...")
```

## Available Providers

| Provider | Name | Description |
|----------|------|-------------|
| OpenAI | `"openai"` | GPT-4.1, O-series, and legacy models |
| Google | `"google"` | Gemini 2.5 and 1.5 series |
| Claude | `"claude"` | Claude 4, 3.5, and 3 series |

## Configuration Parameters

All providers accept these common configuration parameters:

```python
provider = LLMFactory.create(
    "openai",
    api_key="your-api-key",           # Required: API key
    base_url="https://custom.api",    # Optional: Custom base URL
    max_retries=3,                    # Optional: Max retry attempts
    timeout=30.0,                     # Optional: Request timeout (seconds)
    rate_limit=60,                    # Optional: Requests per minute
    metadata={"team": "ai-team"}      # Optional: Custom metadata
)
```

## Factory Methods

### `create(provider: str, **kwargs) -> BaseProvider`

Creates a provider instance.

**Parameters:**
- `provider` (str): Provider name ("openai", "google", "claude")
- `**kwargs`: Configuration parameters

**Returns:**
- `BaseProvider`: Provider instance

**Raises:**
- `ValidationError`: If provider is not supported

```python
# Valid providers
provider = LLMFactory.create("openai", api_key="sk-...")

# Invalid provider raises ValidationError
try:
    provider = LLMFactory.create("invalid", api_key="...")
except ValidationError as e:
    print(f"Error: {e}")
```

### `list_providers() -> Dict[str, Type[BaseProvider]]`

Lists all available providers.

```python
providers = LLMFactory.list_providers()
print(providers.keys())  # ['openai', 'google', 'claude']
```

### `register_provider(name: str, provider_class: Type[BaseProvider]) -> None`

Registers a custom provider.

```python
from pyaibridge.core.base import BaseProvider

class CustomProvider(BaseProvider):
    # Implementation here
    pass

# Register custom provider
LLMFactory.register_provider("custom", CustomProvider)

# Now you can use it
provider = LLMFactory.create("custom", api_key="...")
```

## Provider-Specific Configuration

### OpenAI Provider

```python
openai_provider = LLMFactory.create(
    "openai",
    api_key="sk-proj-...",
    base_url="https://api.openai.com/v1",  # Default
    timeout=30.0,
    max_retries=3
)
```

### Google Provider

```python
google_provider = LLMFactory.create(
    "google",
    api_key="AIza...",
    base_url="https://generativelanguage.googleapis.com/v1beta",  # Default
    timeout=30.0,
    max_retries=3
)
```

### Claude Provider

```python
claude_provider = LLMFactory.create(
    "claude",
    api_key="sk-ant-...",
    base_url="https://api.anthropic.com/v1",  # Default
    timeout=30.0,
    max_retries=3
)
```

## Error Handling

```python
from pyaibridge import LLMFactory, ValidationError

try:
    provider = LLMFactory.create("openai", api_key="invalid-key")
    # Provider created successfully, but will fail on first request
    
except ValidationError as e:
    print(f"Configuration error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Use Environment Variables

```python
import os
from pyaibridge import LLMFactory

provider = LLMFactory.create(
    "openai",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 2. Provider Context Manager

```python
async def example():
    provider = LLMFactory.create("openai", api_key="...")
    
    async with provider:
        # Provider is connected and ready
        response = await provider.chat(request)
        # Provider is automatically disconnected
```

### 3. Configuration from Dict

```python
config = {
    "api_key": "sk-...",
    "timeout": 60.0,
    "max_retries": 5
}

provider = LLMFactory.create("openai", **config)
```

### 4. Multiple Providers

```python
providers = {}

for name in ["openai", "google", "claude"]:
    api_key = os.getenv(f"{name.upper()}_API_KEY")
    if api_key:
        providers[name] = LLMFactory.create(name, api_key=api_key)

# Use providers dict for load balancing or fallback
```

## Advanced Usage

### Custom Base URL for OpenAI-Compatible APIs

```python
# For services like Ollama, LM Studio, etc.
provider = LLMFactory.create(
    "openai",
    api_key="not-needed",  # Some local services don't need keys
    base_url="http://localhost:11434/v1"
)
```

### Provider with Custom Headers

```python
provider = LLMFactory.create(
    "openai",
    api_key="sk-...",
    metadata={
        "custom_headers": {
            "X-Custom-Header": "value"
        }
    }
)
```

## See Also

- [Chat Completion](Chat-Completion) - Using providers for chat
- [Configuration](Configuration) - Advanced configuration options
- [Custom Providers](Custom-Providers) - Creating custom providers