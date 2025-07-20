"""Google Gemini streaming example for pyaibridge."""

import asyncio
import os

from pyaibridge import ChatRequest, LLMFactory, Message, MessageRole


async def main():
    """Demonstrate Google Gemini streaming with pyaibridge."""

    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return

    # Create Google provider
    provider = LLMFactory.create("google", api_key=api_key)

    # Create chat request
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a creative writer who tells engaging stories."),
        Message(role=MessageRole.USER, content="Write a short story about an AI discovering emotions for the first time."),
    ]

    request = ChatRequest(
        messages=messages,
        model="gemini-2.5-flash",
        max_tokens=400,
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
