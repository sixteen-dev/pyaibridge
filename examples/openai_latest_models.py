"""OpenAI latest models example for pyaibridge."""

import asyncio
import os
from pyaibridge import LLMFactory, ChatRequest, Message, MessageRole


async def compare_openai_models():
    """Compare different OpenAI models including the latest 2025 releases."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create provider
    provider = LLMFactory.create("openai", api_key=api_key)
    
    # Test prompt
    messages = [
        Message(role=MessageRole.USER, content="Explain quantum computing in simple terms with a practical example."),
    ]
    
    # Models to test (latest 2025 models)
    models = [
        "gpt-4.1",           # Latest flagship model
        "gpt-4.1-mini",      # Balanced speed and intelligence
        "gpt-4.1-nano",      # Fastest and cheapest
        "o4-mini",           # Reasoning model - cost-efficient
        "o3",                # Advanced reasoning model
        "gpt-4o-mini",       # Legacy but still excellent
    ]
    
    try:
        async with provider:
            for model in models:
                print(f"🤖 Testing {model}:")
                print("=" * 70)
                
                request = ChatRequest(
                    messages=messages,
                    model=model,
                    max_tokens=200,
                    temperature=0.7,
                )
                
                try:
                    response = await provider.chat(request)
                    
                    print(f"Response: {response.content[:300]}...")
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
                    
                    if 'knowledge_cutoff' in model_info:
                        print(f"Knowledge Cutoff: {model_info['knowledge_cutoff']}")
                    
                    if 'model_type' in model_info:
                        print(f"Model Type: {model_info['model_type']}")
                    
                except Exception as e:
                    print(f"Error with {model}: {e}")
                
                print("\\n")
                
    except Exception as e:
        print(f"Error: {e}")


async def test_reasoning_models():
    """Test reasoning models with a complex problem."""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create provider
    provider = LLMFactory.create("openai", api_key=api_key)
    
    # Complex reasoning task
    messages = [
        Message(role=MessageRole.USER, content="""
        A company has 100 employees. 60% work in engineering, 25% in sales, and 15% in marketing.
        If the company grows by 50% and maintains the same department ratios, but engineering 
        productivity increases by 20% per person, what's the effective engineering capacity 
        compared to the original 100-person company?
        """),
    ]
    
    # Reasoning models
    reasoning_models = ["o4-mini", "o3"]
    
    try:
        async with provider:
            for model in reasoning_models:
                print(f"🧠 Testing reasoning model {model}:")
                print("=" * 60)
                
                request = ChatRequest(
                    messages=messages,
                    model=model,
                    max_tokens=300,
                    temperature=0.3,  # Lower temperature for reasoning
                )
                
                try:
                    response = await provider.chat(request)
                    
                    print(f"Response: {response.content}")
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
                    
                except Exception as e:
                    print(f"Error with {model}: {e}")
                
                print("\\n")
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("🚀 OpenAI Latest Models Comparison")
    print("=" * 70)
    asyncio.run(compare_openai_models())
    
    print("\\n" + "🧠 Reasoning Models Test")
    print("=" * 70)
    asyncio.run(test_reasoning_models())