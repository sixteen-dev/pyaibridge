"""Multi-provider comparison example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole


async def compare_providers():
    """Compare responses from different providers."""
    
    # Get API keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not openai_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    if not google_key:
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return
    
    # Create providers
    openai_provider = LLMFactory.create("openai", api_key=openai_key)
    google_provider = LLMFactory.create("google", api_key=google_key)
    
    # Create test request
    messages = [
        Message(role=MessageRole.USER, content="Explain the concept of recursion in programming with a simple example."),
    ]
    
    openai_request = ChatRequest(
        messages=messages,
        model="gpt-4.1-mini",  # Updated to latest 2025 model
        max_tokens=150,
        temperature=0.7,
    )
    
    google_request = ChatRequest(
        messages=messages,
        model="gemini-2.5-flash",
        max_tokens=150,
        temperature=0.7,
    )
    
    try:
        # Test OpenAI
        print("🔵 OpenAI GPT-4.1-mini:")
        print("=" * 50)
        
        async with openai_provider:
            openai_response = await openai_provider.chat(openai_request)
            print(f"Response: {openai_response.content}")
            print(f"Tokens: {openai_response.usage.total_tokens}")
            
            openai_cost = openai_provider.calculate_cost(
                {
                    "prompt_tokens": openai_response.usage.prompt_tokens,
                    "completion_tokens": openai_response.usage.completion_tokens,
                },
                openai_response.model
            )
            if openai_cost:
                print(f"Cost: ${openai_cost:.6f}")
        
        print("\\n")
        
        # Test Google
        print("🔴 Google Gemini 2.5 Flash:")
        print("=" * 50)
        
        async with google_provider:
            google_response = await google_provider.chat(google_request)
            print(f"Response: {google_response.content}")
            print(f"Tokens: {google_response.usage.total_tokens}")
            
            google_cost = google_provider.calculate_cost(
                {
                    "prompt_tokens": google_response.usage.prompt_tokens,
                    "completion_tokens": google_response.usage.completion_tokens,
                },
                google_response.model
            )
            if google_cost:
                print(f"Cost: ${google_cost:.6f}")
        
        print("\\n")
        
        # Compare costs
        if openai_cost and google_cost:
            print("💰 Cost Comparison:")
            print("=" * 50)
            print(f"OpenAI: ${openai_cost:.6f}")
            print(f"Google: ${google_cost:.6f}")
            
            cheaper = "OpenAI" if openai_cost < google_cost else "Google"
            savings = abs(openai_cost - google_cost)
            print(f"{cheaper} is cheaper by ${savings:.6f}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(compare_providers())