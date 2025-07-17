# Model Support

PyAIBridge supports the latest models from OpenAI, Google, Anthropic, and xAI. This page provides a comprehensive overview of all supported models, their capabilities, and pricing.

## OpenAI Models

### GPT-4.1 Series (Latest 2025) ⭐

| Model | Context Length | Streaming | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|------------------|-------------|--------------|
| `gpt-4.1` | 1M tokens | ✅ | June 2024 | $2.00 | $8.00 |
| `gpt-4.1-mini` | 1M tokens | ✅ | June 2024 | $0.40 | $1.60 |
| `gpt-4.1-nano` | 1M tokens | ✅ | June 2024 | $0.20 | $0.80 |

*Per 1M tokens

**Features:**
- Ultra-large context windows (1M tokens)
- Latest knowledge cutoff
- Cached prompt pricing available for `gpt-4.1` and `gpt-4.1-mini`

### O-Series Reasoning Models (Latest 2025) 🧠

| Model | Context Length | Streaming | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|------------------|-------------|--------------|
| `o3` | 200K tokens | ✅ | June 2024 | $10.00 | $40.00 |
| `o3-pro` | 200K tokens | ✅ | June 2024 | $15.00 | $60.00 |
| `o4-mini` | 200K tokens | ✅ | June 2024 | $0.30 | $1.20 |

*Per 1M tokens

**Features:**
- Advanced reasoning capabilities
- Optimized for complex problem-solving
- Higher quality outputs for analytical tasks

### Legacy Models (Still Supported)

| Model | Context Length | Streaming | Input Cost* | Output Cost* |
|-------|----------------|-----------|-------------|--------------|
| `gpt-4o` | 128K tokens | ✅ | $0.005 | $0.015 |
| `gpt-4o-mini` | 128K tokens | ✅ | $0.00015 | $0.0006 |
| `gpt-4-turbo` | 128K tokens | ✅ | $0.01 | $0.03 |
| `gpt-3.5-turbo` | 4K tokens | ✅ | $0.0015 | $0.002 |

*Per 1M tokens

## Google Gemini Models

### Gemini 2.5 Series (Latest 2025) ⭐

| Model | Context Length | Max Output | Multimodal | Thinking | Function Calling | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|------------|----------|------------------|------------------|-------------|--------------|
| `gemini-2.5-pro` | 1M tokens | 64K tokens | ✅ (Audio, Video, PDF) | ✅ | ✅ | January 2025 | $1.25 | $5.00 |
| `gemini-2.5-flash` | 1M tokens | 64K tokens | ✅ (Audio, Video) | ✅ | ✅ | January 2025 | $0.075 | $0.30 |
| `gemini-2.5-flash-lite-preview-06-17` | 1M tokens | 64K tokens | ✅ (Audio, Video) | ✅ | ✅ | January 2025 | $0.0375 | $0.15 |

*Per 1M tokens

**Features:**
- State-of-the-art thinking and reasoning capabilities
- Enhanced multimodal understanding (audio, video, PDF support)
- Massive context windows with large output tokens
- Advanced coding and function calling
- Most cost-efficient option available (`flash-lite-preview`)

### Gemini 2.0 Series

| Model | Context Length | Max Output | Multimodal | Special Features | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|------------|------------------|------------------|-------------|--------------|
| `gemini-2.0-flash` | 1M tokens | 8K tokens | ✅ (Audio, Video) | Live API, Real-time streaming | August 2024 | $0.075 | $0.30 |
| `gemini-2.0-flash-lite` | 1M tokens | 8K tokens | ✅ (Audio, Video) | Cost-efficient, Low latency | August 2024 | $0.0375 | $0.15 |
| `gemini-2.0-flash-preview-image-generation` | 32K tokens | 8K tokens | ✅ (Audio, Video) | Image generation & editing | August 2024 | $0.075 | $0.30 |

*Per 1M tokens

**Features:**
- Next-generation features with superior speed
- Native tool use and real-time streaming capabilities
- Conversational image generation and editing
- Live API support for interactive applications

### Gemini 1.5 Series (Legacy but Stable)

| Model | Context Length | Max Output | Multimodal | Function Calling | Deprecation Date | Input Cost* | Output Cost* |
|-------|----------------|------------|------------|------------------|------------------|-------------|--------------|
| `gemini-1.5-pro` | 2M tokens | 8K tokens | ✅ (Audio, Video) | ✅ | September 2025 | $1.25 | $5.00 |
| `gemini-1.5-flash` | 1M tokens | 8K tokens | ✅ (Audio, Video) | ✅ | September 2025 | $0.075 | $0.30 |
| `gemini-1.5-flash-8b` | 1M tokens | 8K tokens | ✅ (Audio, Video) | ✅ | September 2025 | $0.0375 | $0.15 |

*Per 1M tokens

**Features:**
- Largest context window (2M tokens for Pro)
- Proven stability and reliability
- Full multimodal support with video processing
- Being phased out in favor of Gemini 2.5 series

## Anthropic Claude Models

### Claude 4 Series (Latest 2025) ⭐

| Model | Context Length | Max Output | Streaming | Vision | Extended Thinking | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|-----------|--------|------------------|------------------|-------------|--------------|
| `claude-opus-4-20250514` | 200K tokens | 32K tokens | ✅ | ✅ | ✅ | March 2025 | $15.00 | $75.00 |
| `claude-sonnet-4-20250514` | 200K tokens | 64K tokens | ✅ | ✅ | ✅ | March 2025 | $3.00 | $15.00 |

*Per 1M tokens

**Features:**
- Latest generation with extended thinking capabilities
- Superior reasoning and analysis
- High-quality code generation
- Vision input support (text + images)
- Largest output tokens in Claude family

### Claude 3.7 Series (Extended Thinking) 🧠

| Model | Context Length | Max Output | Streaming | Vision | Extended Thinking | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|-----------|--------|------------------|------------------|-------------|--------------|
| `claude-3-7-sonnet-20250219` | 200K tokens | 64K tokens | ✅ | ✅ | ✅ | November 2024 | $3.00 | $15.00 |

*Per 1M tokens

**Features:**
- Extended thinking capabilities for complex reasoning
- Enhanced performance over Claude 3.5
- Vision input support

### Claude 3.5 Series (Current Production)

| Model | Context Length | Max Output | Streaming | Vision | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|-----------|--------|------------------|-------------|--------------|
| `claude-3-5-sonnet-20241022` | 200K tokens | 8K tokens | ✅ | ✅ | April 2024 | $3.00 | $15.00 |
| `claude-3-5-sonnet-20240620` | 200K tokens | 8K tokens | ✅ | ✅ | April 2024 | $3.00 | $15.00 |
| `claude-3-5-haiku-20241022` | 200K tokens | 8K tokens | ✅ | ✅ | July 2024 | $0.80 | $4.00 |

*Per 1M tokens

### Claude 3 Series (Legacy but Stable)

| Model | Context Length | Max Output | Streaming | Vision | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|------------|-----------|--------|------------------|-------------|--------------|
| `claude-3-opus-20240229` | 200K tokens | 4K tokens | ✅ | ✅ | August 2023 | $15.00 | $75.00 |
| `claude-3-sonnet-20240229` | 200K tokens | 4K tokens | ✅ | ✅ | August 2023 | $3.00 | $15.00 |
| `claude-3-haiku-20240307` | 200K tokens | 4K tokens | ✅ | ✅ | August 2023 | $0.25 | $1.25 |

*Per 1M tokens

## xAI Grok Models

### Grok 4 Series (Latest Reasoning Models) ⭐

| Model | Context Length | Streaming | Tool Use | Search | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|----------|--------|------------------|-------------|--------------|
| `grok-4-0709` | 256K tokens | ✅ | ✅ | ✅ | November 2024 | $3.00 | $15.00 |

*Per 1M tokens

**Features:**
- Advanced reasoning capabilities (no non-reasoning mode)
- Largest context window in Grok series (256K tokens)
- Built-in web search capabilities
- Function calling and tool use support
- Note: `presencePenalty`, `frequencyPenalty`, and `stop` parameters not supported

### Grok 3 Series (Current Stable Models) ⭐

| Model | Context Length | Streaming | Tool Use | Search | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|----------|--------|------------------|-------------|--------------|
| `grok-3` | 131K tokens | ✅ | ✅ | ✅ | November 2024 | $3.00 | $15.00 |
| `grok-3-mini` | 131K tokens | ✅ | ✅ | ✅ | November 2024 | $0.30 | $0.50 |
| `grok-3-fast` | 131K tokens | ✅ | ✅ | ✅ | November 2024 | $5.00 | $25.00 |
| `grok-3-mini-fast` | 131K tokens | ✅ | ✅ | ✅ | November 2024 | $0.60 | $4.00 |

*Per 1M tokens

**Features:**
- Main production-ready models from xAI
- Cost-effective options available (`grok-3-mini`)
- Fast processing variants available
- Full feature support including search and tools

### Grok 2 Series (Vision & Image Generation)

| Model | Context Length | Streaming | Vision | Image Gen | Search | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|--------|-----------|--------|------------------|-------------|--------------|
| `grok-2-vision-1212` | 32K tokens | ✅ | ✅ | ❌ | ✅ | November 2024 | $2.00 | $10.00 |
| `grok-2-image-1212` | 32K tokens | ❌ | ❌ | ✅ | ❌ | November 2024 | - | $0.07/image |

*Per 1M tokens

**Features:**
- `grok-2-vision-1212`: Multimodal input (text + images)
- `grok-2-image-1212`: Text-to-image generation
- Maximum image size: 20MiB
- Supported formats: JPG, JPEG, PNG

### Live Search Pricing

xAI models support real-time web search with additional costs:
- **Live Search**: $25 per 1,000 sources used ($0.025 per source)
- Sources used available in `response.usage.num_sources_used`

*Per 1M tokens

## Model Selection Guide

### For General Use
- **High Quality**: `gpt-4.1`, `claude-opus-4-20250514`, `gemini-2.5-pro`, `grok-4-0709`
- **Balanced**: `gpt-4.1-mini`, `claude-sonnet-4-20250514`, `gemini-2.5-flash`, `grok-3`
- **Cost-Effective**: `gpt-4.1-nano`, `gemini-2.5-flash-lite-preview-06-17`, `grok-3-mini`, `claude-3-haiku-20240307`

### For Specific Use Cases

#### 🧠 Reasoning & Analysis
- **Best**: `o3-pro`, `claude-opus-4-20250514`, `grok-4-0709`, `claude-3-7-sonnet-20250219`
- **Good**: `o3`, `claude-sonnet-4-20250514`, `grok-3`
- **Budget**: `o4-mini`, `claude-3-5-haiku-20241022`, `grok-3-mini`

#### 💻 Code Generation
- **Best**: `claude-sonnet-4-20250514`, `gpt-4.1`, `grok-4-0709`
- **Good**: `claude-3-5-sonnet-20241022`, `gpt-4.1-mini`, `grok-3`
- **Budget**: `claude-3-5-haiku-20241022`, `gpt-4o-mini`, `grok-3-mini`

#### 📄 Long Documents
- **Best**: `gemini-1.5-pro` (2M context), `gemini-2.5-pro` (1M context), `gpt-4.1` (1M context)
- **Good**: `gemini-2.5-flash` (1M context), `claude-opus-4-20250514` (200K context), `grok-4-0709` (256K context)
- **Budget**: `gemini-2.5-flash-lite-preview-06-17`, `gpt-4.1-mini`, `grok-3-mini`

#### ⚡ Speed & Performance
- **Fastest**: `gemini-2.5-flash-lite-preview-06-17`, `gemini-2.0-flash-lite`, `gpt-4.1-nano`, `grok-3-fast`
- **Fast**: `gemini-2.5-flash`, `gemini-2.0-flash`, `claude-3-5-haiku-20241022`, `grok-3-mini`
- **Balanced**: `gpt-4.1-mini`, `claude-sonnet-4-20250514`, `grok-3`

## Usage Examples

### Checking Model Support

```python
from pyaibridge import LLMFactory

# Create provider
provider = LLMFactory.create("openai", api_key="sk-...")

# Check if model is supported
is_supported = await provider.validate_model("gpt-4.1-mini")
print(f"Model supported: {is_supported}")

# Get all supported models
models = provider.supported_models
for model_name, info in models.items():
    print(f"{model_name}: {info['context_length']} tokens")
```

### Getting Model Information

```python
# Get detailed model information
model_info = provider.get_model_info("gpt-4.1-mini")
print(f"Context length: {model_info['context_length']}")
print(f"Supports streaming: {model_info['supports_streaming']}")
print(f"Pricing: {model_info['pricing']}")
```

### Cost Calculation

```python
from pyaibridge import ChatRequest, Message, MessageRole

request = ChatRequest(
    messages=[Message(role=MessageRole.USER, content="Hello!")],
    model="gpt-4.1-mini"
)

async with provider:
    response = await provider.chat(request)
    
    # Calculate cost
    cost = provider.calculate_cost(response.usage, response.model)
    print(f"Cost: ${cost:.6f}")
```

## Model Comparison Tool

Use this comparison to choose the right model:

```python
from pyaibridge.utils.cost import CostCalculator

def compare_models(text: str, providers: list):
    """Compare cost and capabilities across models."""
    
    results = []
    for provider_name, model in providers:
        provider = LLMFactory.create(provider_name, api_key="...")
        calculator = CostCalculator(provider)
        
        # Estimate cost
        cost = calculator.calculate_text_cost(text, model, is_prompt=True)
        
        # Get model info
        info = provider.get_model_info(model)
        
        results.append({
            "provider": provider_name,
            "model": model,
            "context_length": info["context_length"],
            "estimated_cost": cost,
            "supports_streaming": info["supports_streaming"]
        })
    
    return results

# Compare models for a specific task
models_to_compare = [
    ("openai", "gpt-4.1-mini"),
    ("google", "gemini-2.5-flash-lite-preview-06-17"),
    ("claude", "claude-3-5-haiku-20241022"),
    ("xai", "grok-3-mini")
]

results = compare_models("Your prompt here", models_to_compare)
for result in results:
    print(f"{result['model']}: ${result['estimated_cost']:.6f}")
```

## Notes

- Pricing is subject to change by providers
- Context lengths are maximum supported
- All models support async operations
- Streaming support varies by provider implementation
- Knowledge cutoffs are approximate and provider-specific

#### 🔍 Web Search & Real-time Data
- **Best**: `grok-4-0709`, `grok-3`, `grok-3-fast` (built-in Live Search)
- **Good**: `grok-3-mini`, `grok-3-mini-fast` (cost-effective with search)
- **Note**: Other providers require external search integration

#### 🎨 Multimodal & Image Generation
- **Vision**: `gemini-2.5-pro` (Audio, Video, PDF), `grok-2-vision-1212`, `claude-opus-4-20250514`
- **Video Processing**: `gemini-2.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`
- **Image Generation**: `gemini-2.0-flash-preview-image-generation`, `grok-2-image-1212` ($0.07/image)
- **Budget Multimodal**: `gemini-2.5-flash-lite-preview-06-17` (most cost-effective)

## See Also

- [OpenAI Provider](OpenAI-Provider) - OpenAI-specific documentation
- [Google Provider](Google-Provider) - Google Gemini documentation  
- [Claude Provider](Claude-Provider) - Anthropic Claude documentation
- [xAI Provider](XAI-Provider) - xAI Grok models documentation
- [Cost Calculation](Cost-Calculation) - Detailed cost calculation guide