"""Google Gemini models comparison example for pyaibridge."""

import asyncio
import os

from pyaibridge import ChatRequest, LLMFactory, Message, MessageRole


async def compare_google_models():
    """Compare different Google Gemini models."""

    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return

    # Create provider
    provider = LLMFactory.create("google", api_key=api_key)

    # Test prompt
    messages = [
        Message(role=MessageRole.USER, content="Write a Python function to calculate the factorial of a number using recursion."),
    ]

    # Models to test
    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-8b",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]

    try:
        async with provider:
            for model in models:
                print(f"🔍 Testing {model}:")
                print("=" * 60)

                request = ChatRequest(
                    messages=messages,
                    model=model,
                    max_tokens=200,
                    temperature=0.3,
                )

                try:
                    response = await provider.chat(request)

                    print(f"Response: {response.content[:200]}...")
                    print(f"Tokens: {response.usage.total_tokens}")

                    # Calculate cost
                    cost = provider.calculate_cost(
                        {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                        },
                        response.model
                    )

                    if cost:
                        print(f"Cost: ${cost:.6f}")

                    # Model info
                    model_info = provider.get_model_info(model)
                    print(f"Context Length: {model_info['context_length']:,} tokens")
                    print(f"Supports Streaming: {model_info['supports_streaming']}")

                except Exception as e:
                    print(f"Error with {model}: {e}")

                print("\\n")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(compare_google_models())
