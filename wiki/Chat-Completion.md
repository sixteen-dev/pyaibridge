# Chat Completion

Chat completion is the core functionality of PyAIBridge. It allows you to send messages to LLM providers and receive responses in a unified format.

## Basic Usage

```python
import asyncio
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole

async def basic_chat():
    # Create provider
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    # Create messages
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What is the capital of France?"),
    ]
    
    # Create request
    request = ChatRequest(
        messages=messages,
        model="gpt-4.1-mini",
        max_tokens=100,
        temperature=0.7
    )
    
    # Send request
    async with provider:
        response = await provider.chat(request)
        print(f"Response: {response.content}")
        print(f"Tokens: {response.usage.total_tokens}")

asyncio.run(basic_chat())
```

## Message Types

PyAIBridge supports three message roles:

### System Messages
Set the behavior and context for the assistant.

```python
system_msg = Message(
    role=MessageRole.SYSTEM,
    content="You are an expert Python developer. Provide concise, practical answers."
)
```

### User Messages
Messages from the human user.

```python
user_msg = Message(
    role=MessageRole.USER,
    content="How do I create a list comprehension?"
)
```

### Assistant Messages
Previous responses from the AI (for conversation history).

```python
assistant_msg = Message(
    role=MessageRole.ASSISTANT,
    content="A list comprehension is created using: [expression for item in iterable]"
)
```

## ChatRequest Parameters

The `ChatRequest` class supports extensive configuration:

```python
request = ChatRequest(
    messages=messages,                    # Required: List of messages
    model="gpt-4.1-mini",                # Required: Model name
    max_tokens=1000,                     # Optional: Max tokens to generate
    temperature=0.7,                     # Optional: 0.0-2.0, creativity level
    top_p=0.9,                          # Optional: 0.0-1.0, nucleus sampling
    frequency_penalty=0.0,               # Optional: -2.0 to 2.0, reduce repetition
    presence_penalty=0.0,                # Optional: -2.0 to 2.0, encourage new topics
    stop=["\\n\\n", "END"],              # Optional: Stop sequences
    stream=False,                        # Optional: Enable streaming
    user="user-123",                     # Optional: User identifier
    timeout=30.0                         # Optional: Request timeout
)
```

### Parameter Details

#### `temperature`
Controls randomness in output:
- `0.0`: Deterministic, focused responses
- `0.7`: Balanced creativity (recommended)
- `1.0`: More creative and varied
- `2.0`: Very creative, less focused

#### `top_p`
Nucleus sampling parameter:
- `0.1`: Very focused on likely tokens
- `0.9`: Good balance (recommended)
- `1.0`: Consider all possible tokens

#### `frequency_penalty`
Reduces repetition of tokens:
- `0.0`: No penalty (default)
- `0.5`: Moderate reduction
- `1.0`: Strong reduction
- `2.0`: Maximum reduction

#### `presence_penalty`
Encourages discussing new topics:
- `0.0`: No penalty (default)
- `0.5`: Moderate encouragement
- `1.0`: Strong encouragement
- `2.0`: Maximum encouragement

#### `stop`
Sequences where generation should stop:
```python
# Single stop sequence
stop="\\n\\n"

# Multiple stop sequences
stop=["\\n\\n", "END", "STOP"]
```

## ChatResponse

The response contains comprehensive information:

```python
response = await provider.chat(request)

# Basic response data
print(f"Content: {response.content}")
print(f"Model: {response.model}")
print(f"ID: {response.id}")
print(f"Finish reason: {response.finish_reason}")
print(f"Created: {response.created}")

# Token usage
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")

# Metadata
print(f"Provider: {response.metadata['provider']}")
```

### Finish Reasons

The `finish_reason` indicates why generation stopped:

- `"stop"`: Natural completion
- `"length"`: Hit max_tokens limit
- `"content_filter"`: Content was filtered
- `"tool_calls"`: Function calling (future feature)
- `None`: Still generating (streaming only)

## Multi-turn Conversations

Build conversations by maintaining message history:

```python
async def conversation():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    # Start conversation
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful math tutor."),
        Message(role=MessageRole.USER, content="What is 2 + 2?")
    ]
    
    async with provider:
        # First exchange
        request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        response = await provider.chat(request)
        
        # Add assistant response to history
        messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=response.content
        ))
        
        # Continue conversation
        messages.append(Message(
            role=MessageRole.USER,
            content="Now what is 2 + 2 + 3?"
        ))
        
        # Second exchange
        request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        response = await provider.chat(request)
        
        print(f"Final response: {response.content}")
```

## Provider-Specific Features

### OpenAI Features

```python
# Using latest GPT-4.1 models
request = ChatRequest(
    messages=messages,
    model="gpt-4.1-mini",  # or "gpt-4.1", "gpt-4.1-nano"
    user="user-123",       # For tracking
    frequency_penalty=0.5,
    presence_penalty=0.2
)

# O-series reasoning models
request = ChatRequest(
    messages=messages,
    model="o3",  # or "o3-pro", "o4-mini"
    max_tokens=2000,
    temperature=0.1  # Lower for reasoning tasks
)
```

### Google Gemini Features

```python
# Large context models
request = ChatRequest(
    messages=messages,
    model="gemini-2.5-pro",  # 2M token context
    max_tokens=8000,
    temperature=0.7
)

# Fast models
request = ChatRequest(
    messages=messages,
    model="gemini-2.5-flash-8b",  # Ultra-fast
    max_tokens=1000,
    temperature=0.8
)
```

### Claude Features

```python
# Latest Claude 4 models
request = ChatRequest(
    messages=messages,
    model="claude-4-sonnet",  # or "claude-4-opus", "claude-4-haiku"
    max_tokens=4000,
    temperature=0.7
)

# System messages handled specially by Claude
system_message = Message(
    role=MessageRole.SYSTEM,
    content="You are Claude, an AI assistant created by Anthropic."
)
```

## Error Handling

Handle various error scenarios:

```python
from pyaibridge import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ProviderError,
    TimeoutError
)

async def robust_chat():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Hello!")],
        model="gpt-4.1-mini"
    )
    
    try:
        async with provider:
            response = await provider.chat(request)
            return response.content
            
    except AuthenticationError:
        print("Invalid API key")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}")
    except ValidationError as e:
        print(f"Invalid request: {e}")
    except TimeoutError:
        print("Request timed out")
    except ProviderError as e:
        print(f"Provider error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom Headers and Metadata

```python
# Add custom metadata
request = ChatRequest(
    messages=messages,
    model="gpt-4.1-mini",
    metadata={
        "session_id": "sess_123",
        "user_tier": "premium"
    }
)
```

### Context Window Management

```python
def trim_messages(messages: list, max_tokens: int = 8000):
    """Keep conversation within context limits."""
    # Estimate tokens (rough: 1 token ≈ 4 chars)
    total_chars = sum(len(msg.content) for msg in messages)
    estimated_tokens = total_chars // 4
    
    if estimated_tokens <= max_tokens:
        return messages
    
    # Keep system message and recent messages
    system_msgs = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
    other_msgs = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
    
    # Take most recent messages that fit
    trimmed = system_msgs
    for msg in reversed(other_msgs):
        if len(''.join(m.content for m in trimmed + [msg])) // 4 < max_tokens:
            trimmed.append(msg)
        else:
            break
    
    return trimmed
```

### Batch Processing

```python
async def batch_chat(requests: list[ChatRequest]):
    """Process multiple requests efficiently."""
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    async with provider:
        tasks = [provider.chat(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append({"error": str(response)})
            else:
                results.append({"content": response.content})
        
        return results
```

### Model Comparison

```python
async def compare_responses(prompt: str, models: list[str]):
    """Compare responses across different models."""
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    message = Message(role=MessageRole.USER, content=prompt)
    results = {}
    
    async with provider:
        for model in models:
            request = ChatRequest(messages=[message], model=model)
            try:
                response = await provider.chat(request)
                results[model] = {
                    "content": response.content,
                    "tokens": response.usage.total_tokens,
                    "cost": provider.calculate_cost(response.usage, model)
                }
            except Exception as e:
                results[model] = {"error": str(e)}
    
    return results
```

## Best Practices

### 1. Use Context Managers
Always use providers with context managers for proper cleanup:

```python
async with provider:
    response = await provider.chat(request)
```

### 2. Handle Rate Limits
Implement exponential backoff for rate limits:

```python
import asyncio
from random import uniform

async def chat_with_retry(provider, request, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await provider.chat(request)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = (2 ** attempt) + uniform(0, 1)
            await asyncio.sleep(wait_time)
```

### 3. Monitor Token Usage
Track costs and usage:

```python
from pyaibridge.utils.metrics import metrics

async def monitored_chat(provider, request):
    metrics.start_timer("chat", provider.provider_name)
    
    try:
        response = await provider.chat(request)
        
        # Record metrics
        metrics.record_tokens(
            provider.provider_name,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        cost = provider.calculate_cost(response.usage, response.model)
        if cost:
            metrics.record_cost(provider.provider_name, cost)
        
        return response
        
    finally:
        metrics.end_timer("chat", provider.provider_name)
```

### 4. Validate Models
Check model support before making requests:

```python
async def safe_chat(provider, request):
    if not await provider.validate_model(request.model):
        raise ValidationError(f"Model {request.model} not supported")
    
    return await provider.chat(request)
```

## See Also

- [Streaming](Streaming) - Real-time response streaming
- [Model Support](Model-Support) - All supported models
- [Error Handling](Error-Handling) - Comprehensive error handling
- [Metrics and Monitoring](Metrics-and-Monitoring) - Usage tracking