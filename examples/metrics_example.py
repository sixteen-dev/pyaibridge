"""Metrics collection example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole, metrics


async def main():
    """Demonstrate metrics collection with pyaibridge."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create OpenAI provider
    provider = LLMFactory.create("openai", api_key=api_key)
    
    # Create multiple chat requests
    requests = [
        ChatRequest(
            messages=[Message(role=MessageRole.USER, content="What is 2+2?")],
            model="gpt-4.1-mini",  # Updated to latest 2025 model
        ),
        ChatRequest(
            messages=[Message(role=MessageRole.USER, content="Explain quantum computing in simple terms.")],
            model="gpt-4.1-mini",  # Updated to latest 2025 model
            max_tokens=150,
        ),
        ChatRequest(
            messages=[Message(role=MessageRole.USER, content="Write a haiku about programming.")],
            model="gpt-4.1-mini",  # Updated to latest 2025 model
        ),
    ]
    
    try:
        async with provider:
            # Process multiple requests
            for i, request in enumerate(requests, 1):
                print(f"Processing request {i}...")
                
                # Start timing
                metrics.start_timer("chat_completion", "openai")
                
                # Generate response
                response = await provider.chat(request)
                
                # End timing
                duration = metrics.end_timer("chat_completion", "openai")
                
                # Record metrics
                metrics.record_tokens(
                    "openai",
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                )
                
                # Record cost
                cost = provider.calculate_cost(
                    {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                    },
                    response.model
                )
                
                if cost:
                    metrics.record_cost("openai", cost)
                
                metrics.increment("requests_completed", "openai")
                
                print(f"Response: {response.content[:100]}...")
                print(f"Duration: {duration:.2f}s")
                print()
            
            # Print metrics summary
            print("=== Metrics Summary ===")
            summary = metrics.get_summary()
            
            for provider_name, provider_metrics in summary.items():
                print(f"\\nProvider: {provider_name}")
                print(f"  Requests completed: {provider_metrics.get('requests_completed', 0)}")
                print(f"  Total tokens: {provider_metrics.get('total_tokens', 0)}")
                print(f"  Prompt tokens: {provider_metrics.get('prompt_tokens', 0)}")
                print(f"  Completion tokens: {provider_metrics.get('completion_tokens', 0)}")
                
                if 'total_cost' in provider_metrics:
                    print(f"  Total cost: ${provider_metrics['total_cost']:.6f}")
                
                # Timing stats
                if 'timing' in provider_metrics:
                    for operation, timing in provider_metrics['timing'].items():
                        print(f"  {operation}:")
                        print(f"    Count: {timing['count']}")
                        print(f"    Avg duration: {timing['avg_duration']:.2f}s")
                        print(f"    Total duration: {timing['total_duration']:.2f}s")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())