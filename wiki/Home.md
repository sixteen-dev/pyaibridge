# PyAIBridge Wiki

Welcome to the PyAIBridge documentation! PyAIBridge is a high-performance unified API for all major LLM providers.

## 🚀 Quick Start

```python
import asyncio
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole

async def main():
    # Create provider
    provider = LLMFactory.create("openai", api_key="your-api-key")
    
    # Create request
    request = ChatRequest(
        messages=[
            Message(role=MessageRole.USER, content="Hello!")
        ],
        model="gpt-4.1-mini"
    )
    
    # Get response
    async with provider:
        response = await provider.chat(request)
        print(response.content)

asyncio.run(main())
```

## 📚 Documentation

### Core Features
- **[Factory Pattern](Factory-Pattern)** - Create providers using the factory
- **[Chat Completion](Chat-Completion)** - Generate text responses
- **[Streaming](Streaming)** - Real-time response streaming
- **[Performance](Performance)** - Rust acceleration and benchmarks
- **[Error Handling](Error-Handling)** - Robust error management
- **[Metrics & Monitoring](Metrics-and-Monitoring)** - Track usage and performance
- **[Cost Calculation](Cost-Calculation)** - Calculate API costs

### Providers
- **[OpenAI Provider](OpenAI-Provider)** - GPT-4.1, O-series, and legacy models
- **[Google Provider](Google-Provider)** - Gemini 2.5 and 1.5 series
- **[Claude Provider](Claude-Provider)** - Claude 4, 3.5, and 3 series

### Advanced Features
- **[Rate Limiting](Rate-Limiting)** - Control request rates
- **[Retry Logic](Retry-Logic)** - Automatic retry mechanisms
- **[Middleware](Middleware)** - Extend functionality
- **[Custom Providers](Custom-Providers)** - Add new providers

### Reference
- **[API Reference](API-Reference)** - Complete API documentation
- **[Model Support](Model-Support)** - All supported models and pricing
- **[Configuration](Configuration)** - Provider configuration options
- **[Examples](Examples)** - Code examples and use cases

## 🏗️ Architecture

PyAIBridge follows a clean architecture with:

- **Factory Pattern** for provider creation
- **Base Provider** interface for consistency
- **Hybrid HTTP Client** with Rust acceleration and Python fallback
- **Pydantic Models** for type safety
- **Structured Logging** for observability
- **Async/Await** for performance

## 🎯 Key Benefits

- **Unified Interface** - Same API for all providers
- **Type Safety** - Full TypeScript-like type hints
- **Rust-Accelerated Performance** - 1.22x faster HTTP with automatic fallback
- **Monitoring** - Built-in metrics and cost tracking
- **Extensibility** - Easy to add new providers
- **Production Ready** - Error handling, logging, testing
- **Zero Setup** - No Rust toolchain required for installation

## 🔧 Installation

```bash
pip install pyaibridge
```

## 🤝 Contributing

See our [Contributing Guide](Contributing) for how to contribute to PyAIBridge.

## 📄 License

PyAIBridge is licensed under the MIT License. See [LICENSE](https://github.com/sixteen-dev/pyaibridge/blob/main/LICENSE) for details.