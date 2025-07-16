"""Streaming example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole


async def main():
    """Demonstrate streaming usage of pyaibridge."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create OpenAI provider
    provider = LLMFactory.create("openai", api_key=api_key)
    
    # Create chat request
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a creative storyteller."),
        Message(role=MessageRole.USER, content="Tell me a short story about a robot learning to paint."),
    ]
    
    request = ChatRequest(
        messages=messages,
        model="gpt-4.1-mini",  # Updated to latest 2025 model
        max_tokens=300,
        temperature=0.8,
        stream=True,  # Enable streaming
    )
    
    try:
        # Use provider as context manager
        async with provider:
            print("Story: ", end="", flush=True)
            
            # Stream response chunks
            async for chunk in provider.stream_chat(request):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                
                # Check if streaming is complete
                if chunk.finish_reason:
                    print(f"\\n\\nStreaming completed. Reason: {chunk.finish_reason}")
                    break
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())