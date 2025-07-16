# Model Support

PyAIBridge supports the latest models from OpenAI, Google, and Anthropic. This page provides a comprehensive overview of all supported models, their capabilities, and pricing.

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

| Model | Context Length | Streaming | Input Cost* | Output Cost* |
|-------|----------------|-----------|-------------|--------------|
| `gemini-2.5-pro` | 2M tokens | ✅ | $1.25 | $5.00 |
| `gemini-2.5-flash` | 1M tokens | ✅ | $0.075 | $0.30 |
| `gemini-2.5-flash-8b` | 1M tokens | ✅ | $0.0375 | $0.15 |

*Per 1M tokens

**Features:**
- Massive context windows (up to 2M tokens)
- Ultra-fast inference
- Competitive pricing

### Gemini 2.0 Series

| Model | Context Length | Streaming | Input Cost* | Output Cost* |
|-------|----------------|-----------|-------------|--------------|
| `gemini-2.0-flash` | 1M tokens | ✅ | $0.075 | $0.30 |

*Per 1M tokens

### Gemini 1.5 Series (Stable)

| Model | Context Length | Streaming | Input Cost* | Output Cost* |
|-------|----------------|-----------|-------------|--------------|
| `gemini-1.5-pro` | 2M tokens | ✅ | $1.25 | $5.00 |
| `gemini-1.5-flash` | 1M tokens | ✅ | $0.075 | $0.30 |
| `gemini-1.5-flash-8b` | 1M tokens | ✅ | $0.0375 | $0.15 |

*Per 1M tokens

## Anthropic Claude Models

### Claude 4 Series (Latest 2025) ⭐

| Model | Context Length | Streaming | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|------------------|-------------|--------------|
| `claude-4-opus` | 200K tokens | ✅ | April 2024 | $15.00 | $75.00 |
| `claude-4-sonnet` | 200K tokens | ✅ | April 2024 | $3.00 | $15.00 |
| `claude-4-haiku` | 200K tokens | ✅ | April 2024 | $0.25 | $1.25 |

*Per 1M tokens

**Features:**
- Superior reasoning and analysis
- High-quality code generation
- Excellent instruction following

### Claude 3.5 Series (Current Production)

| Model | Context Length | Streaming | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|------------------|-------------|--------------|
| `claude-3-5-sonnet-20241022` | 200K tokens | ✅ | April 2024 | $3.00 | $15.00 |
| `claude-3-5-haiku-20241022` | 200K tokens | ✅ | July 2024 | $1.00 | $5.00 |

*Per 1M tokens

### Claude 3 Series (Legacy but Stable)

| Model | Context Length | Streaming | Knowledge Cutoff | Input Cost* | Output Cost* |
|-------|----------------|-----------|------------------|-------------|--------------|
| `claude-3-opus-20240229` | 200K tokens | ✅ | August 2023 | $15.00 | $75.00 |
| `claude-3-sonnet-20240229` | 200K tokens | ✅ | August 2023 | $3.00 | $15.00 |
| `claude-3-haiku-20240307` | 200K tokens | ✅ | August 2023 | $0.25 | $1.25 |

*Per 1M tokens

## Model Selection Guide

### For General Use
- **High Quality**: `gpt-4.1`, `claude-4-sonnet`, `gemini-2.5-pro`
- **Balanced**: `gpt-4.1-mini`, `claude-4-haiku`, `gemini-2.5-flash`
- **Cost-Effective**: `gpt-4.1-nano`, `gemini-2.5-flash-8b`

### For Specific Use Cases

#### 🧠 Reasoning & Analysis
- **Best**: `o3-pro`, `claude-4-opus`
- **Good**: `o3`, `claude-4-sonnet`
- **Budget**: `o4-mini`, `claude-4-haiku`

#### 💻 Code Generation
- **Best**: `claude-4-sonnet`, `gpt-4.1`
- **Good**: `claude-3-5-sonnet-20241022`, `gpt-4.1-mini`
- **Budget**: `claude-4-haiku`, `gpt-4o-mini`

#### 📄 Long Documents
- **Best**: `gemini-2.5-pro` (2M context), `gpt-4.1` (1M context)
- **Good**: `gemini-1.5-pro`, `claude-4-opus`
- **Budget**: `gemini-2.5-flash`, `gpt-4.1-mini`

#### ⚡ Speed & Performance
- **Fastest**: `gemini-2.5-flash-8b`, `gpt-4.1-nano`
- **Fast**: `gemini-2.5-flash`, `claude-4-haiku`
- **Balanced**: `gpt-4.1-mini`, `claude-3-5-haiku-20241022`

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
    ("google", "gemini-2.5-flash"),
    ("claude", "claude-4-haiku")
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

## See Also

- [OpenAI Provider](OpenAI-Provider) - OpenAI-specific documentation
- [Google Provider](Google-Provider) - Google Gemini documentation  
- [Claude Provider](Claude-Provider) - Anthropic Claude documentation
- [Cost Calculation](Cost-Calculation) - Detailed cost calculation guide