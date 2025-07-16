# Examples

This page contains comprehensive examples demonstrating various PyAIBridge features and use cases.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Multi-Provider Examples](#multi-provider-examples)
- [Streaming Examples](#streaming-examples)
- [Cost Management](#cost-management)
- [Error Handling](#error-handling)
- [Production Applications](#production-applications)
- [Advanced Patterns](#advanced-patterns)

## Basic Usage

### Simple Chat Completion

```python
import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole

async def simple_chat():
    """Basic chat completion example."""
    
    # Create provider
    provider = LLMFactory.create(
        "openai", 
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create request
    request = ChatRequest(
        messages=[
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.USER, content="What is Python?")
        ],
        model="gpt-4.1-mini",
        max_tokens=150,
        temperature=0.7
    )
    
    # Get response
    async with provider:
        response = await provider.chat(request)
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.usage.total_tokens}")

asyncio.run(simple_chat())
```

### Interactive Conversation

```python
async def interactive_conversation():
    """Interactive chat with conversation history."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    conversation = [
        Message(role=MessageRole.SYSTEM, content="You are a knowledgeable tutor.")
    ]
    
    async with provider:
        while True:
            # Get user input
            user_input = input("\\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            # Add user message
            conversation.append(
                Message(role=MessageRole.USER, content=user_input)
            )
            
            # Get response
            request = ChatRequest(
                messages=conversation,
                model="gpt-4.1-mini",
                max_tokens=300
            )
            
            try:
                response = await provider.chat(request)
                print(f"Assistant: {response.content}")
                
                # Add assistant response to conversation
                conversation.append(
                    Message(role=MessageRole.ASSISTANT, content=response.content)
                )
                
            except Exception as e:
                print(f"Error: {e}")

asyncio.run(interactive_conversation())
```

## Multi-Provider Examples

### Provider Comparison

```python
async def compare_providers():
    """Compare responses across different providers."""
    
    providers = {
        "openai": LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY")),
        "google": LLMFactory.create("google", api_key=os.getenv("GOOGLE_API_KEY")),
        "claude": LLMFactory.create("claude", api_key=os.getenv("CLAUDE_API_KEY"))
    }
    
    models = {
        "openai": "gpt-4.1-mini",
        "google": "gemini-2.5-flash",
        "claude": "claude-4-haiku"
    }
    
    prompt = "Explain quantum computing in simple terms."
    message = Message(role=MessageRole.USER, content=prompt)
    
    results = {}
    
    for name, provider in providers.items():
        if provider is None:  # Skip if API key not available
            continue
            
        request = ChatRequest(
            messages=[message],
            model=models[name],
            max_tokens=200,
            temperature=0.7
        )
        
        try:
            async with provider:
                response = await provider.chat(request)
                
                results[name] = {
                    "content": response.content,
                    "tokens": response.usage.total_tokens,
                    "model": response.model
                }
                
        except Exception as e:
            results[name] = {"error": str(e)}
    
    # Display results
    for provider, result in results.items():
        print(f"\\n{'='*50}")
        print(f"Provider: {provider.upper()}")
        print(f"{'='*50}")
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Model: {result['model']}")
            print(f"Tokens: {result['tokens']}")
            print(f"Response: {result['content']}")

asyncio.run(compare_providers())
```

### Fallback Provider Pattern

```python
async def fallback_providers():
    """Use multiple providers as fallbacks."""
    
    # Priority order of providers
    provider_configs = [
        ("openai", "gpt-4.1-mini", os.getenv("OPENAI_API_KEY")),
        ("google", "gemini-2.5-flash", os.getenv("GOOGLE_API_KEY")),
        ("claude", "claude-4-haiku", os.getenv("CLAUDE_API_KEY"))
    ]
    
    message = Message(role=MessageRole.USER, content="Write a haiku about coding.")
    
    for provider_name, model, api_key in provider_configs:
        if not api_key:
            continue
            
        try:
            provider = LLMFactory.create(provider_name, api_key=api_key)
            request = ChatRequest(messages=[message], model=model)
            
            async with provider:
                response = await provider.chat(request)
                print(f"Success with {provider_name}: {response.content}")
                return response
                
        except Exception as e:
            print(f"Failed with {provider_name}: {e}")
            continue
    
    print("All providers failed!")

asyncio.run(fallback_providers())
```

## Streaming Examples

### Real-time Chat Interface

```python
import sys

async def streaming_chat():
    """Real-time streaming chat interface."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    conversation = [
        Message(role=MessageRole.SYSTEM, content="You are a creative writing assistant.")
    ]
    
    async with provider:
        while True:
            user_input = input("\\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            conversation.append(Message(role=MessageRole.USER, content=user_input))
            
            request = ChatRequest(
                messages=conversation,
                model="gpt-4.1-mini",
                stream=True,
                max_tokens=500
            )
            
            print("Assistant: ", end='', flush=True)
            response_content = ""
            
            try:
                async for chunk in provider.stream_chat(request):
                    if chunk.content:
                        print(chunk.content, end='', flush=True)
                        response_content += chunk.content
                    
                    if chunk.finish_reason:
                        print()  # New line
                        break
                
                # Add response to conversation
                conversation.append(
                    Message(role=MessageRole.ASSISTANT, content=response_content)
                )
                
            except Exception as e:
                print(f"\\nError: {e}")

asyncio.run(streaming_chat())
```

### Streaming with Progress

```python
import time

async def streaming_with_progress():
    """Streaming with progress indicators."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    request = ChatRequest(
        messages=[
            Message(role=MessageRole.USER, content="Write a detailed story about space exploration.")
        ],
        model="gpt-4.1-mini",
        max_tokens=1000,
        stream=True
    )
    
    start_time = time.time()
    chunk_count = 0
    word_count = 0
    
    print("Story Generation Starting...\\n")
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            if chunk.content:
                print(chunk.content, end='', flush=True)
                chunk_count += 1
                word_count += len(chunk.content.split())
                
                # Show progress every 100 chunks
                if chunk_count % 100 == 0:
                    elapsed = time.time() - start_time
                    wps = word_count / elapsed if elapsed > 0 else 0
                    print(f"\\n[Progress: {chunk_count} chunks, {word_count} words, {wps:.1f} words/sec]\\n", end='')
            
            if chunk.finish_reason:
                elapsed = time.time() - start_time
                print(f"\\n\\n[Completed in {elapsed:.1f}s - {chunk_count} chunks, {word_count} words]")
                break

asyncio.run(streaming_with_progress())
```

## Cost Management

### Cost Tracking

```python
from pyaibridge.utils.metrics import metrics

async def cost_tracking_example():
    """Track costs across multiple requests."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    prompts = [
        "Explain machine learning",
        "Write a Python function",
        "Describe quantum physics",
        "Create a marketing plan"
    ]
    
    total_cost = 0.0
    
    async with provider:
        for i, prompt in enumerate(prompts, 1):
            request = ChatRequest(
                messages=[Message(role=MessageRole.USER, content=prompt)],
                model="gpt-4.1-mini",
                max_tokens=200
            )
            
            # Start timing
            metrics.start_timer("chat", "openai")
            
            try:
                response = await provider.chat(request)
                
                # Calculate cost
                cost = provider.calculate_cost(response.usage, response.model)
                total_cost += cost
                
                # Record metrics
                metrics.record_tokens(
                    "openai",
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                metrics.record_cost("openai", cost)
                
                print(f"Request {i}:")
                print(f"  Tokens: {response.usage.total_tokens}")
                print(f"  Cost: ${cost:.6f}")
                print(f"  Running total: ${total_cost:.6f}")
                print()
                
            finally:
                metrics.end_timer("chat", "openai")
    
    # Get final metrics
    final_metrics = metrics.get_summary()
    print("Final Statistics:")
    print(f"Total requests: {len(prompts)}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Average cost per request: ${total_cost/len(prompts):.6f}")
    print(f"Total tokens: {final_metrics['openai']['total_tokens']}")

asyncio.run(cost_tracking_example())
```

### Budget Management

```python
async def budget_management():
    """Manage API usage within budget constraints."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    max_budget = 0.10  # $0.10 budget
    current_spend = 0.0
    
    prompts = [
        "Explain Python",
        "Write JavaScript code",
        "Describe databases",
        "Create API documentation",
        "Design system architecture"
    ]
    
    async with provider:
        for prompt in prompts:
            # Check budget before request
            if current_spend >= max_budget:
                print(f"Budget limit reached: ${current_spend:.6f}")
                break
            
            request = ChatRequest(
                messages=[Message(role=MessageRole.USER, content=prompt)],
                model="gpt-4o-mini",  # Cheaper model
                max_tokens=100
            )
            
            try:
                response = await provider.chat(request)
                cost = provider.calculate_cost(response.usage, response.model)
                current_spend += cost
                
                print(f"Prompt: {prompt[:30]}...")
                print(f"Cost: ${cost:.6f} (Total: ${current_spend:.6f})")
                print(f"Response: {response.content[:100]}...")
                print(f"Remaining budget: ${max_budget - current_spend:.6f}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error with prompt '{prompt}': {e}")

asyncio.run(budget_management())
```

## Error Handling

### Comprehensive Error Handling

```python
from pyaibridge import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ProviderError,
    TimeoutError
)
import asyncio
from random import uniform

async def robust_chat_with_retry():
    """Robust chat with comprehensive error handling and retries."""
    
    async def chat_with_exponential_backoff(provider, request, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await provider.chat(request)
                
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                
                # Use retry_after if provided, otherwise exponential backoff
                wait_time = e.retry_after if e.retry_after else (2 ** attempt) + uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(wait_time)
                
            except TimeoutError:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) + uniform(0, 1)
                print(f"Timeout. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    request = ChatRequest(
        messages=[Message(role=MessageRole.USER, content="Hello!")],
        model="gpt-4.1-mini"
    )
    
    try:
        async with provider:
            response = await chat_with_exponential_backoff(provider, request)
            print(f"Success: {response.content}")
            
    except AuthenticationError:
        print("Authentication failed. Check your API key.")
    except ValidationError as e:
        print(f"Request validation failed: {e}")
    except ProviderError as e:
        print(f"Provider error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(robust_chat_with_retry())
```

## Production Applications

### Document Processing Pipeline

```python
import json
from typing import List, Dict

async def document_processing_pipeline():
    """Process documents using different providers for different tasks."""
    
    # Initialize providers
    openai_provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    claude_provider = LLMFactory.create("claude", api_key=os.getenv("CLAUDE_API_KEY"))
    
    # Sample documents
    documents = [
        "Machine learning is a subset of artificial intelligence...",
        "Quantum computing represents a paradigm shift...",
        "Blockchain technology enables decentralized systems..."
    ]
    
    results = []
    
    async with openai_provider, claude_provider:
        for i, doc in enumerate(documents):
            print(f"Processing document {i+1}/{len(documents)}")
            
            # Step 1: Summarize with Claude (good at analysis)
            summary_request = ChatRequest(
                messages=[
                    Message(role=MessageRole.SYSTEM, content="Summarize the following text in 2-3 sentences."),
                    Message(role=MessageRole.USER, content=doc)
                ],
                model="claude-4-haiku",
                max_tokens=150
            )
            
            # Step 2: Extract keywords with OpenAI (good at structured output)
            keywords_request = ChatRequest(
                messages=[
                    Message(role=MessageRole.SYSTEM, content="Extract 5 key terms from this text. Return as JSON array."),
                    Message(role=MessageRole.USER, content=doc)
                ],
                model="gpt-4.1-mini",
                max_tokens=100
            )
            
            try:
                # Process in parallel
                summary_task = claude_provider.chat(summary_request)
                keywords_task = openai_provider.chat(keywords_request)
                
                summary_response, keywords_response = await asyncio.gather(
                    summary_task, keywords_task
                )
                
                # Parse keywords JSON
                try:
                    keywords = json.loads(keywords_response.content)
                except json.JSONDecodeError:
                    keywords = keywords_response.content.split(', ')
                
                result = {
                    "document_id": i + 1,
                    "original_length": len(doc),
                    "summary": summary_response.content,
                    "keywords": keywords,
                    "processing_costs": {
                        "summary": claude_provider.calculate_cost(summary_response.usage, summary_response.model),
                        "keywords": openai_provider.calculate_cost(keywords_response.usage, keywords_response.model)
                    }
                }
                
                results.append(result)
                print(f"  Summary: {result['summary'][:50]}...")
                print(f"  Keywords: {result['keywords']}")
                
            except Exception as e:
                print(f"  Error processing document {i+1}: {e}")
    
    # Final report
    total_cost = sum(
        r["processing_costs"]["summary"] + r["processing_costs"]["keywords"] 
        for r in results
    )
    
    print(f"\\nProcessing complete:")
    print(f"Documents processed: {len(results)}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Average cost per document: ${total_cost/len(results):.6f}")

asyncio.run(document_processing_pipeline())
```

### Multi-Model Content Generation

```python
async def content_generation_workflow():
    """Generate content using multiple models for different strengths."""
    
    providers = {
        "openai": LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY")),
        "claude": LLMFactory.create("claude", api_key=os.getenv("CLAUDE_API_KEY")),
        "google": LLMFactory.create("google", api_key=os.getenv("GOOGLE_API_KEY"))
    }
    
    topic = "The future of renewable energy"
    
    tasks = {
        "outline": {
            "provider": "claude",
            "model": "claude-4-sonnet",
            "prompt": f"Create a detailed outline for an article about '{topic}'. Include main sections and key points.",
            "max_tokens": 300
        },
        "introduction": {
            "provider": "openai", 
            "model": "gpt-4.1-mini",
            "prompt": f"Write an engaging introduction for an article about '{topic}'. Make it compelling and informative.",
            "max_tokens": 200
        },
        "technical_section": {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "prompt": f"Write a technical section about current innovations in '{topic}'. Include specific examples and data.",
            "max_tokens": 400
        }
    }
    
    results = {}
    
    # Process all tasks in parallel
    async def process_task(task_name, task_config):
        provider = providers[task_config["provider"]]
        
        request = ChatRequest(
            messages=[Message(role=MessageRole.USER, content=task_config["prompt"])],
            model=task_config["model"],
            max_tokens=task_config["max_tokens"]
        )
        
        async with provider:
            response = await provider.chat(request)
            return task_name, response
    
    try:
        # Run all tasks concurrently
        task_coroutines = [
            process_task(name, config) 
            for name, config in tasks.items()
        ]
        
        completed_tasks = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        for result in completed_tasks:
            if isinstance(result, Exception):
                print(f"Task failed: {result}")
                continue
                
            task_name, response = result
            results[task_name] = {
                "content": response.content,
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "provider": tasks[task_name]["provider"]
            }
        
        # Display results
        print(f"Content Generation Results for: {topic}")
        print("=" * 60)
        
        for task_name, result in results.items():
            print(f"\\n{task_name.upper()} ({result['provider']} - {result['model']}):")
            print(f"Tokens: {result['tokens']}")
            print(f"Content: {result['content'][:200]}...")
            
    except Exception as e:
        print(f"Workflow error: {e}")

asyncio.run(content_generation_workflow())
```

## Advanced Patterns

### Request Batching

```python
import asyncio
from typing import List

async def batch_processing():
    """Process multiple requests efficiently in batches."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    # Generate many requests
    prompts = [
        f"Write a short poem about {topic}"
        for topic in ["ocean", "mountains", "stars", "forest", "desert", "river", "clouds", "sunset"]
    ]
    
    async def process_batch(prompts_batch: List[str], batch_size: int = 3):
        """Process prompts in batches to avoid overwhelming the API."""
        
        results = []
        
        for i in range(0, len(prompts_batch), batch_size):
            batch = prompts_batch[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} requests")
            
            # Create requests for this batch
            requests = [
                ChatRequest(
                    messages=[Message(role=MessageRole.USER, content=prompt)],
                    model="gpt-4o-mini",  # Faster model for batch processing
                    max_tokens=100
                )
                for prompt in batch
            ]
            
            # Process batch concurrently
            async with provider:
                batch_tasks = [provider.chat(request) for request in requests]
                batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Collect results
                for j, response in enumerate(batch_responses):
                    if isinstance(response, Exception):
                        results.append({"error": str(response), "prompt": batch[j]})
                    else:
                        results.append({
                            "prompt": batch[j],
                            "response": response.content,
                            "tokens": response.usage.total_tokens
                        })
            
            # Brief pause between batches
            await asyncio.sleep(1)
        
        return results
    
    # Process all prompts
    results = await process_batch(prompts)
    
    # Display results
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    print(f"\\nBatch Processing Complete:")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total tokens: {sum(r['tokens'] for r in successful)}")
    
    # Show sample results
    for i, result in enumerate(successful[:3]):
        print(f"\\nSample {i+1}:")
        print(f"Prompt: {result['prompt']}")
        print(f"Response: {result['response']}")

asyncio.run(batch_processing())
```

### Dynamic Model Selection

```python
async def dynamic_model_selection():
    """Dynamically select the best model based on request characteristics."""
    
    provider = LLMFactory.create("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    def select_model(prompt: str, max_tokens: int) -> str:
        """Select the most appropriate model based on request characteristics."""
        
        # For long responses, use models with larger context
        if max_tokens > 1000:
            return "gpt-4.1"
        
        # For code-related prompts, use reasoning models
        code_keywords = ["python", "javascript", "function", "class", "algorithm", "code"]
        if any(keyword in prompt.lower() for keyword in code_keywords):
            return "o4-mini"  # Reasoning model for code
        
        # For creative tasks, use balanced model
        creative_keywords = ["story", "poem", "creative", "imagine", "artistic"]
        if any(keyword in prompt.lower() for keyword in creative_keywords):
            return "gpt-4.1-mini"
        
        # Default to cost-effective model
        return "gpt-4o-mini"
    
    test_prompts = [
        ("Write a Python function to sort a list", 200),
        ("Tell me a creative story about dragons", 500),
        ("Explain quantum mechanics in detail", 1200),
        ("What is the capital of France?", 50)
    ]
    
    async with provider:
        for prompt, max_tokens in test_prompts:
            # Dynamic model selection
            selected_model = select_model(prompt, max_tokens)
            
            request = ChatRequest(
                messages=[Message(role=MessageRole.USER, content=prompt)],
                model=selected_model,
                max_tokens=max_tokens
            )
            
            try:
                response = await provider.chat(request)
                cost = provider.calculate_cost(response.usage, response.model)
                
                print(f"Prompt: {prompt}")
                print(f"Selected model: {selected_model}")
                print(f"Tokens used: {response.usage.total_tokens}")
                print(f"Cost: ${cost:.6f}")
                print(f"Response: {response.content[:100]}...")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error with prompt '{prompt}': {e}")

asyncio.run(dynamic_model_selection())
```

These examples demonstrate the versatility and power of PyAIBridge for various use cases, from simple chat completion to complex production workflows. Each example includes error handling, cost management, and performance considerations that are essential for real-world applications.

## See Also

- [API Reference](API-Reference) - Complete API documentation
- [Best Practices](Best-Practices) - Production deployment guidelines
- [Contributing](Contributing) - How to contribute examples