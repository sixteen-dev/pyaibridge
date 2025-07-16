"""Basic usage example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole


async def main():
    """Demonstrate basic usage of pyaibridge."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create OpenAI provider
    provider = LLMFactory.create("openai", api_key=api_key)
    
    # Create chat request
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What is the capital of France?"),
    ]
    
    request = ChatRequest(
        messages=messages,
        model="gpt-4.1-mini",  # Updated to latest 2025 model
        max_tokens=100,
        temperature=0.7,
    )
    
    try:
        # Use provider as context manager for automatic cleanup
        async with provider:
            # Generate response
            response = await provider.chat(request)
            
            print(f"Response: {response.content}")
            print(f"Model: {response.model}")
            print(f"Tokens used: {response.usage.total_tokens}")
            
            # Calculate cost
            cost = provider.calculate_cost(
                {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
                response.model
            )
            
            if cost:
                print(f"Estimated cost: ${cost:.6f}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())