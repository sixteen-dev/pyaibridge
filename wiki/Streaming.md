# Streaming

Streaming allows you to receive responses in real-time as they're generated, providing a better user experience for chat applications and long responses.

## Basic Streaming

```python
import asyncio
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole

async def basic_streaming():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[
            Message(role=MessageRole.USER, content="Write a story about a robot")
        ],
        model="gpt-4.1-mini",
        max_tokens=500,
        stream=True  # Enable streaming
    )
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            print(chunk.content, end='', flush=True)
        print()  # New line at end

asyncio.run(basic_streaming())
```

## StreamingChunk Object

Each streaming chunk contains:

```python
async for chunk in provider.stream_chat(request):
    print(f"ID: {chunk.id}")
    print(f"Model: {chunk.model}")
    print(f"Content: {chunk.content}")
    print(f"Finish reason: {chunk.finish_reason}")
    print(f"Created: {chunk.created}")
    print(f"Metadata: {chunk.metadata}")
```

### Chunk Properties

- `id`: Unique identifier for the response stream
- `model`: Model used for generation
- `content`: Text content of this chunk (empty for final chunk)
- `finish_reason`: Why generation ended (only in final chunk)
- `created`: Timestamp when chunk was created
- `metadata`: Provider-specific metadata

## Building Complete Responses

Accumulate chunks to build the full response:

```python
async def stream_and_collect():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Explain quantum computing")],
        model="gpt-4.1-mini",
        stream=True
    )
    
    complete_response = ""
    finish_reason = None
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            complete_response += chunk.content
            
            # Print chunk in real-time
            print(chunk.content, end='', flush=True)
            
            # Check for completion
            if chunk.finish_reason:
                finish_reason = chunk.finish_reason
                break
    
    print(f"\n\nComplete response: {complete_response}")
    print(f"Finished because: {finish_reason}")
```

## Provider-Specific Streaming

### OpenAI Streaming

```python
async def openai_streaming():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Write Python code")],
        model="gpt-4.1-mini",
        stream=True
    )
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            # OpenAI provides incremental content
            if chunk.content:
                print(chunk.content, end='', flush=True)
            
            # Check completion
            if chunk.finish_reason == "stop":
                print("\n[Completed normally]")
            elif chunk.finish_reason == "length":
                print("\n[Hit max tokens]")
```

### Google Gemini Streaming

```python
async def gemini_streaming():
    provider = LLMFactory.create("google", api_key="AIza...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Explain machine learning")],
        model="gemini-2.5-flash",
        stream=True
    )
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            # Gemini may provide larger chunks
            if chunk.content:
                print(chunk.content, end='', flush=True)
```

### Claude Streaming

```python
async def claude_streaming():
    provider = LLMFactory.create("claude", api_key="sk-ant-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Analyze this data")],
        model="claude-4-sonnet",
        stream=True
    )
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            # Claude provides word-by-word streaming
            if chunk.content:
                print(chunk.content, end='', flush=True)
            
            # Claude-specific finish reasons
            if chunk.finish_reason == "end_turn":
                print("\n[Turn completed]")
```

## Advanced Streaming Patterns

### Streaming with Progress Indicators

```python
import time

async def streaming_with_progress():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Write a detailed essay")],
        model="gpt-4.1-mini",
        max_tokens=1000,
        stream=True
    )
    
    start_time = time.time()
    chunk_count = 0
    total_chars = 0
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            chunk_count += 1
            total_chars += len(chunk.content)
            
            print(chunk.content, end='', flush=True)
            
            # Show progress every 50 chunks
            if chunk_count % 50 == 0:
                elapsed = time.time() - start_time
                speed = total_chars / elapsed if elapsed > 0 else 0
                print(f"\n[Progress: {chunk_count} chunks, {speed:.1f} chars/sec]\n", end='')
            
            if chunk.finish_reason:
                elapsed = time.time() - start_time
                print(f"\n\nCompleted in {elapsed:.1f}s with {chunk_count} chunks")
                break
```

### Streaming with Stop Conditions

```python
async def streaming_with_stop():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Tell me about Python")],
        model="gpt-4.1-mini",
        stream=True
    )
    
    collected_text = ""
    stop_phrases = ["In conclusion", "To summarize"]
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            collected_text += chunk.content
            print(chunk.content, end='', flush=True)
            
            # Check for stop phrases
            if any(phrase.lower() in collected_text.lower() for phrase in stop_phrases):
                print("\n[Stopping early - found conclusion]")
                break
            
            if chunk.finish_reason:
                print(f"\n[Finished: {chunk.finish_reason}]")
                break
```

### Streaming with Buffering

```python
import asyncio

async def buffered_streaming():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Explain neural networks")],
        model="gpt-4.1-mini",
        stream=True
    )
    
    buffer = ""
    buffer_size = 50  # Characters to buffer
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            buffer += chunk.content
            
            # Flush buffer when it reaches target size
            if len(buffer) >= buffer_size:
                print(buffer, end='', flush=True)
                buffer = ""
                await asyncio.sleep(0.1)  # Small delay for readability
            
            if chunk.finish_reason:
                # Flush remaining buffer
                if buffer:
                    print(buffer, end='', flush=True)
                print(f"\n[Finished: {chunk.finish_reason}]")
                break
```

## Streaming Error Handling

```python
from pyaibridge import (
    AuthenticationError,
    RateLimitError,
    ProviderError,
    TimeoutError
)

async def robust_streaming():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Hello!")],
        model="gpt-4.1-mini",
        stream=True
    )
    
    try:
        async with provider:
            async for chunk in provider.stream_chat(request):
                print(chunk.content, end='', flush=True)
                
                if chunk.finish_reason:
                    print(f"\n[Completed: {chunk.finish_reason}]")
                    break
                    
    except AuthenticationError:
        print("\n[Error: Invalid API key]")
    except RateLimitError as e:
        print(f"\n[Error: Rate limited. Retry after {e.retry_after}s]")
    except TimeoutError:
        print("\n[Error: Request timed out]")
    except ProviderError as e:
        print(f"\n[Error: Provider error - {e}]")
    except Exception as e:
        print(f"\n[Error: Unexpected - {e}]")
```

## Chat Application Example

A complete streaming chat application:

```python
import asyncio
from typing import List

class StreamingChat:
    def __init__(self, provider_name: str, api_key: str, model: str):
        self.provider = LLMFactory.create(provider_name, api_key=api_key)
        self.model = model
        self.conversation: List[Message] = []
    
    async def add_system_message(self, content: str):
        """Add system message to conversation."""
        self.conversation.append(
            Message(role=MessageRole.SYSTEM, content=content)
        )
    
    async def chat_stream(self, user_input: str) -> str:
        """Send user input and stream response."""
        # Add user message
        self.conversation.append(
            Message(role=MessageRole.USER, content=user_input)
        )
        
        request = ChatRequest(
            messages=self.conversation,
            model=self.model,
            stream=True
        )
        
        print("Assistant: ", end='', flush=True)
        response_content = ""
        
        async with self.provider:
            async for chunk in self.provider.stream_chat(request):
                if chunk.content:
                    print(chunk.content, end='', flush=True)
                    response_content += chunk.content
                
                if chunk.finish_reason:
                    print()  # New line
                    break
        
        # Add assistant response to conversation
        self.conversation.append(
            Message(role=MessageRole.ASSISTANT, content=response_content)
        )
        
        return response_content
    
    async def run(self):
        """Run interactive chat loop."""
        await self.add_system_message("You are a helpful assistant.")
        
        print("Streaming Chat Started! Type 'quit' to exit.")
        
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['quit', 'exit']:
                break
            
            try:
                await self.chat_stream(user_input)
            except Exception as e:
                print(f"Error: {e}")

# Usage
async def main():
    chat = StreamingChat("openai", "sk-...", "gpt-4.1-mini")
    await chat.run()

# Run the chat
if __name__ == "__main__":
    asyncio.run(main())
```

## Performance Considerations

### Streaming vs Non-Streaming Performance

```python
import time

async def compare_streaming_performance():
    provider = LLMFactory.create("openai", api_key="sk-...")
    
    messages = [Message(role=MessageRole.USER, content="Write a long story")]
    
    # Non-streaming
    start_time = time.time()
    request = ChatRequest(messages=messages, model="gpt-4.1-mini", stream=False)
    
    async with provider:
        response = await provider.chat(request)
        non_streaming_time = time.time() - start_time
        print(f"Non-streaming: {non_streaming_time:.2f}s total")
    
    # Streaming
    start_time = time.time()
    first_chunk_time = None
    request = ChatRequest(messages=messages, model="gpt-4.1-mini", stream=True)
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            if first_chunk_time is None:
                first_chunk_time = time.time() - start_time
            
            if chunk.finish_reason:
                total_time = time.time() - start_time
                print(f"Streaming: {first_chunk_time:.2f}s to first chunk, {total_time:.2f}s total")
                break
```

## Best Practices

### 1. Handle Empty Chunks
Some providers may send empty chunks:

```python
async for chunk in provider.stream_chat(request):
    if chunk.content:  # Only process non-empty content
        print(chunk.content, end='', flush=True)
```

### 2. Implement Timeouts
Add timeouts for streaming operations:

```python
import asyncio

async def streaming_with_timeout():
    provider = LLMFactory.create("openai", api_key="sk-...")
    request = ChatRequest(messages=[...], model="gpt-4.1-mini", stream=True)
    
    try:
        async with provider:
            async with asyncio.timeout(60):  # 60 second timeout
                async for chunk in provider.stream_chat(request):
                    print(chunk.content, end='', flush=True)
                    if chunk.finish_reason:
                        break
    except asyncio.TimeoutError:
        print("\n[Timeout: Response took too long]")
```

### 3. Monitor Stream Health
Track streaming metrics:

```python
async def monitored_streaming():
    provider = LLMFactory.create("openai", api_key="sk-...")
    request = ChatRequest(messages=[...], model="gpt-4.1-mini", stream=True)
    
    chunk_count = 0
    start_time = time.time()
    last_chunk_time = start_time
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            current_time = time.time()
            chunk_interval = current_time - last_chunk_time
            
            # Alert if chunks are coming too slowly
            if chunk_interval > 5.0:
                print(f"\n[Warning: Slow chunk - {chunk_interval:.1f}s delay]\n")
            
            chunk_count += 1
            last_chunk_time = current_time
            
            print(chunk.content, end='', flush=True)
            
            if chunk.finish_reason:
                total_time = current_time - start_time
                avg_chunk_time = total_time / chunk_count
                print(f"\n[Stats: {chunk_count} chunks, {avg_chunk_time:.3f}s/chunk avg]")
                break
```

## See Also

- [Chat Completion](Chat-Completion) - Non-streaming chat completion
- [Error Handling](Error-Handling) - Handling streaming errors
- [Metrics and Monitoring](Metrics-and-Monitoring) - Tracking streaming performance