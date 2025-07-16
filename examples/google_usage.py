"""Google Gemini usage example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole


async def main():
    """Demonstrate Google Gemini usage with pyaibridge."""
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return
    
    # Create Google provider
    provider = LLMFactory.create("google", api_key=api_key)
    
    # Create chat request
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful AI assistant specialized in explaining complex topics simply."),
        Message(role=MessageRole.USER, content="Explain quantum computing in simple terms."),
    ]
    
    request = ChatRequest(
        messages=messages,
        model="gemini-2.5-flash",
        max_tokens=200,
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