#!/usr/bin/env python3
"""
Real API testing script.
Tests with actual API keys from environment variables.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyaibridge.providers import OpenAIProvider, GoogleProvider, ClaudeProvider, XAIProvider
from pyaibridge.core.models import ProviderConfig, ChatRequest, Message, MessageRole

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Print colored status message."""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
    else:
        print(f"{Colors.BOLD}{message}{Colors.END}")

async def test_provider(provider_class, api_key_env, provider_name, model):
    """Test a specific provider with real API."""
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        print_status(f"{provider_name}: No API key found in {api_key_env}", "warning")
        return False
    
    try:
        print_status(f"Testing {provider_name}...", "info")
        
        # Initialize provider
        config = ProviderConfig(api_key=api_key)
        provider = provider_class(config)
        
        # Test model validation
        is_valid = await provider.validate_model(model)
        if not is_valid:
            print_status(f"{provider_name}: Model {model} not valid", "error")
            return False
        
        # Create test request
        messages = [
            Message(role=MessageRole.USER, content="Say 'Hello from pyaibridge!'")
        ]
        
        request = ChatRequest(
            messages=messages,
            model=model,
            max_tokens=20,
            temperature=0.1
        )
        
        # Make API call
        response = await provider.chat(request)
        
        # Verify response
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print_status(f"{provider_name}: ✓ Response received: {content[:50]}...", "success")
            
            # Test cost calculation
            if response.usage:
                cost = provider.calculate_cost(response.usage.__dict__, model)
                print_status(f"{provider_name}: ✓ Cost calculated: ${cost:.6f}", "success")
            
            return True
        else:
            print_status(f"{provider_name}: No response received", "error")
            return False
            
    except Exception as e:
        print_status(f"{provider_name}: Error - {str(e)}", "error")
        return False

async def main():
    """Run real API tests."""
    print_status("🔑 Starting real API key testing...", "header")
    print_status("=" * 60, "header")
    
    print_status("\nRequired environment variables:", "info")
    print_status("  OPENAI_API_KEY - OpenAI API key", "info")
    print_status("  GOOGLE_API_KEY - Google AI API key", "info") 
    print_status("  CLAUDE_API_KEY - Anthropic API key", "info")
    print_status("  XAI_API_KEY - xAI API key", "info")
    print_status("\nSet any you want to test, others will be skipped.\n", "info")
    
    # Test configurations
    tests = [
        (OpenAIProvider, "OPENAI_API_KEY", "OpenAI", "gpt-4o-mini"),
        (GoogleProvider, "GOOGLE_API_KEY", "Google", "gemini-1.5-flash"),
        (ClaudeProvider, "CLAUDE_API_KEY", "Claude", "claude-3-haiku-20240307"),
        (XAIProvider, "XAI_API_KEY", "xAI", "grok-beta")
    ]
    
    results = []
    
    for provider_class, env_var, name, model in tests:
        print_status(f"\n🔍 Testing {name}", "header")
        print("-" * 40)
        
        result = await test_provider(provider_class, env_var, name, model)
        results.append((name, result))
    
    # Summary
    print_status("\n" + "=" * 60, "header")
    print_status("📊 REAL API TEST SUMMARY", "header")
    print_status("=" * 60, "header")
    
    passed = 0
    tested = 0
    
    for name, result in results:
        if result is not False:  # Was tested (had API key)
            tested += 1
            if result:
                passed += 1
                print_status(f"✅ {name}: PASSED")
            else:
                print_status(f"❌ {name}: FAILED")
        else:
            print_status(f"⏭️  {name}: SKIPPED (no API key)")
    
    if tested == 0:
        print_status("\n⚠️  No API keys provided - all tests skipped", "warning")
        print_status("Set environment variables to test with real APIs", "info")
        return 0
    elif passed == tested:
        print_status(f"\n🎉 ALL {tested} TESTED PROVIDERS PASSED!", "success")
        return 0
    else:
        print_status(f"\n⚠️  {tested - passed}/{tested} providers failed", "error")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))