# PyAIBridge Documentation

## Overview

PyAIBridge is a high-performance unified API library that provides a consistent interface for interacting with multiple Large Language Model (LLM) providers. It abstracts away the complexity of different provider APIs while offering advanced features like automatic retry logic, cost tracking, metrics collection, and streaming support.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Provider Configuration](#provider-configuration)
5. [Basic Usage](#basic-usage)
6. [Advanced Features](#advanced-features)
7. [Real-World Scenarios](#real-world-scenarios)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [API Reference](#api-reference)

## Installation

```bash
pip install pyaibridge
```

## Quick Start

```python
from pyaibridge import LLMFactory, Message, MessageRole, ChatRequest, ProviderConfig

# Setup OpenAI provider
config = ProviderConfig(api_key="your-openai-api-key")
provider = LLMFactory.create_provider("openai", config)

# Create a chat request
messages = [
    Message(role=MessageRole.USER, content="What are the benefits of renewable energy?")
]
request = ChatRequest(messages=messages, model="gpt-4.1-mini")

# Generate response
async with provider:
    response = await provider.chat(request)
    print(response.content)
```

## Core Concepts

### Providers
PyAIBridge supports multiple LLM providers:
- **OpenAI**: GPT-4.1, GPT-4o, GPT-3.5, O-series reasoning models
- **Google**: Gemini 2.5, Gemini 2.0, Gemini 1.5 series
- **Extensible**: Easy to add new providers

### Messages
Messages represent conversation turns with roles:
- `USER`: Human input
- `ASSISTANT`: AI responses
- `SYSTEM`: System instructions

### Requests and Responses
- `ChatRequest`: Encapsulates all request parameters
- `ChatResponse`: Structured response with metadata
- `StreamingChunk`: Individual chunks for streaming responses

## Provider Configuration

### Basic Configuration
```python
from pyaibridge import ProviderConfig

config = ProviderConfig(
    api_key="your-api-key",
    timeout=30.0,
    max_retries=3
)
```

### Advanced Configuration
```python
config = ProviderConfig(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",  # Custom endpoint
    timeout=60.0,
    max_retries=5,
    rate_limit=100,  # Requests per minute
    metadata={"environment": "production"}
)
```

## Basic Usage

### Simple Chat Completion
```python
import asyncio
from pyaibridge import LLMFactory, Message, MessageRole, ChatRequest, ProviderConfig

async def simple_chat():
    # Setup provider
    config = ProviderConfig(api_key="your-api-key")
    provider = LLMFactory.create_provider("openai", config)
    
    # Create request
    messages = [
        Message(role=MessageRole.USER, content="Explain quantum computing in simple terms")
    ]
    request = ChatRequest(messages=messages, model="gpt-4.1-mini")
    
    # Get response
    async with provider:
        response = await provider.chat(request)
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        print(f"Cost: ${provider.calculate_cost(response.usage.dict(), request.model):.6f}")

asyncio.run(simple_chat())
```

### Multi-turn Conversation
```python
async def conversation():
    config = ProviderConfig(api_key="your-api-key")
    provider = LLMFactory.create_provider("openai", config)
    
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful coding assistant."),
        Message(role=MessageRole.USER, content="How do I implement a binary search?")
    ]
    
    async with provider:
        # First exchange
        request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        response = await provider.chat(request)
        
        # Add assistant response to conversation
        messages.append(Message(role=MessageRole.ASSISTANT, content=response.content))
        
        # Follow-up question
        messages.append(Message(role=MessageRole.USER, content="Can you show me the iterative version?"))
        
        request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        response = await provider.chat(request)
        print(response.content)
```

### Streaming Responses
```python
async def streaming_example():
    config = ProviderConfig(api_key="your-api-key")
    provider = LLMFactory.create_provider("openai", config)
    
    messages = [
        Message(role=MessageRole.USER, content="Write a short story about space exploration")
    ]
    request = ChatRequest(messages=messages, model="gpt-4.1-mini", max_tokens=500)
    
    async with provider:
        async for chunk in provider.stream_chat(request):
            print(chunk.content, end="", flush=True)
            if chunk.finish_reason:
                print(f"\\n[Finished: {chunk.finish_reason}]")
```

## Advanced Features

### Cost Tracking
```python
from pyaibridge.utils.metrics import metrics

async def track_costs():
    config = ProviderConfig(api_key="your-api-key")
    provider = LLMFactory.create_provider("openai", config)
    
    async with provider:
        # Make several requests
        for i in range(5):
            request = ChatRequest(
                messages=[Message(role=MessageRole.USER, content=f"Question {i+1}: What is AI?")],
                model="gpt-4.1-mini"
            )
            response = await provider.chat(request)
            
            # Cost is automatically tracked
            cost = provider.calculate_cost(response.usage.dict(), request.model)
            print(f"Request {i+1} cost: ${cost:.6f}")
        
        # Get overall metrics
        summary = metrics.get_summary()
        print(f"Total requests: {summary['openai']['request_count']}")
        print(f"Total cost: ${summary['openai']['total_cost']:.6f}")
```

### Multiple Provider Support
```python
async def multi_provider_example():
    # Setup multiple providers
    openai_config = ProviderConfig(api_key="openai-key")
    google_config = ProviderConfig(api_key="google-key")
    
    openai_provider = LLMFactory.create_provider("openai", openai_config)
    google_provider = LLMFactory.create_provider("google", google_config)
    
    question = "What are the advantages of renewable energy?"
    messages = [Message(role=MessageRole.USER, content=question)]
    
    # Compare responses from different providers
    async with openai_provider, google_provider:
        # OpenAI response
        openai_request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        openai_response = await openai_provider.chat(openai_request)
        
        # Google response
        google_request = ChatRequest(messages=messages, model="gemini-2.5-flash")
        google_response = await google_provider.chat(google_request)
        
        print("OpenAI Response:", openai_response.content[:100] + "...")
        print("Google Response:", google_response.content[:100] + "...")
```

## Real-World Scenarios

### 1. Content Generation Platform

```python
import asyncio
from typing import List, Dict, Any
from pyaibridge import LLMFactory, Message, MessageRole, ChatRequest, ProviderConfig

class ContentGenerator:
    def __init__(self, api_key: str, provider_type: str = "openai"):
        self.config = ProviderConfig(api_key=api_key, timeout=60.0)
        self.provider = LLMFactory.create_provider(provider_type, self.config)
        
    async def generate_blog_post(self, topic: str, target_audience: str, word_count: int = 800) -> Dict[str, Any]:
        """Generate a complete blog post with title, content, and SEO metadata."""
        
        # Generate title
        title_prompt = f"""Create an engaging, SEO-friendly blog post title for:
        Topic: {topic}
        Target Audience: {target_audience}
        Style: Professional yet accessible
        
        Return only the title, no quotes or extra text."""
        
        title_messages = [Message(role=MessageRole.USER, content=title_prompt)]
        title_request = ChatRequest(messages=title_messages, model="gpt-4.1-mini", max_tokens=50)
        
        # Generate content
        content_prompt = f"""Write a comprehensive blog post about: {topic}
        
        Requirements:
        - Target audience: {target_audience}
        - Word count: approximately {word_count} words
        - Include introduction, main points, and conclusion
        - Use headers and subheaders
        - Professional tone with practical examples
        - SEO-optimized content
        
        Format as markdown."""
        
        content_messages = [
            Message(role=MessageRole.SYSTEM, content="You are an expert content writer specializing in engaging, SEO-optimized blog posts."),
            Message(role=MessageRole.USER, content=content_prompt)
        ]
        content_request = ChatRequest(
            messages=content_messages, 
            model="gpt-4.1-mini", 
            max_tokens=1500,
            temperature=0.7
        )
        
        # Generate meta description
        meta_prompt = f"""Create a compelling meta description for a blog post about: {topic}
        
        Requirements:
        - Maximum 155 characters
        - Include primary keyword
        - Compelling and click-worthy
        - Target audience: {target_audience}
        
        Return only the meta description."""
        
        meta_messages = [Message(role=MessageRole.USER, content=meta_prompt)]
        meta_request = ChatRequest(messages=meta_messages, model="gpt-4.1-mini", max_tokens=50)
        
        async with self.provider:
            # Execute all requests
            title_response = await self.provider.chat(title_request)
            content_response = await self.provider.chat(content_request)
            meta_response = await self.provider.chat(meta_request)
            
            # Calculate total cost
            total_cost = (
                self.provider.calculate_cost(title_response.usage.dict(), "gpt-4.1-mini") +
                self.provider.calculate_cost(content_response.usage.dict(), "gpt-4.1-mini") +
                self.provider.calculate_cost(meta_response.usage.dict(), "gpt-4.1-mini")
            )
            
            return {
                "title": title_response.content.strip(),
                "content": content_response.content.strip(),
                "meta_description": meta_response.content.strip(),
                "word_count": len(content_response.content.split()),
                "total_tokens": (title_response.usage.total_tokens + 
                               content_response.usage.total_tokens + 
                               meta_response.usage.total_tokens),
                "total_cost": total_cost,
                "generated_at": title_response.created
            }

# Usage example
async def demo_content_generation():
    generator = ContentGenerator(api_key="your-api-key")
    
    result = await generator.generate_blog_post(
        topic="Sustainable Web Development Practices",
        target_audience="Frontend developers and web designers",
        word_count=1000
    )
    
    print(f"Title: {result['title']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Cost: ${result['total_cost']:.6f}")
    print(f"Meta Description: {result['meta_description']}")
    print("\\n" + "="*50 + "\\n")
    print(result['content'])
```

### 2. Financial Discussion Summarizer

```python
from dataclasses import dataclass
from typing import List, Optional
import asyncio

@dataclass
class RedditPost:
    headline: str
    subreddit: str
    score: int
    comments: List[Dict[str, Any]]
    url: str
    created_utc: float

class FinancialDiscussionSummarizer:
    def __init__(self, api_key: str):
        self.config = ProviderConfig(api_key=api_key)
        self.provider = LLMFactory.create_provider("openai", self.config)
    
    async def generate_market_sentiment_summary(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Generate comprehensive market sentiment analysis from Reddit discussions."""
        
        if not posts:
            return {"summary": "", "sentiment": "neutral", "confidence": 0.0}
        
        # Prepare structured content
        content_parts = []
        for post in posts[:15]:  # Analyze top 15 posts
            post_content = f"""
            Subreddit: r/{post.subreddit}
            Score: {post.score}
            Title: {post.headline}
            """
            
            # Include high-quality comments
            if post.comments:
                top_comments = sorted(post.comments, key=lambda c: c.get("score", 0), reverse=True)[:3]
                for i, comment in enumerate(top_comments):
                    if comment.get("score", 0) > 10:  # Only well-upvoted comments
                        comment_text = comment.get("body", "")[:300]
                        post_content += f"Top Comment {i+1}: {comment_text}\\n"
            
            content_parts.append(post_content)
        
        analysis_prompt = f"""
        Analyze these financial discussions from Reddit and provide:
        
        1. Overall market sentiment (bullish/bearish/neutral)
        2. Key themes or events driving sentiment
        3. Confidence level (0-100%)
        4. Notable stocks/sectors mentioned
        5. Risk factors or concerns highlighted
        
        Content to analyze:
        {chr(10).join(content_parts)}
        
        Format your response as:
        SENTIMENT: [bullish/bearish/neutral]
        CONFIDENCE: [0-100]%
        SUMMARY: [2-3 sentences about key themes]
        KEY_MENTIONS: [stocks/sectors mentioned]
        RISK_FACTORS: [main concerns if any]
        """
        
        messages = [
            Message(
                role=MessageRole.SYSTEM, 
                content="You are a financial analyst specialized in social media sentiment analysis. Provide objective, data-driven insights."
            ),
            Message(role=MessageRole.USER, content=analysis_prompt)
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.2,  # Low temperature for consistent analysis
            max_tokens=400
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            # Parse structured response
            content = response.content.strip()
            lines = content.split('\\n')
            
            result = {
                "raw_response": content,
                "total_posts_analyzed": len(posts),
                "analysis_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini"),
                "generated_at": response.created
            }
            
            # Extract structured data
            for line in lines:
                if line.startswith("SENTIMENT:"):
                    result["sentiment"] = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    conf_text = line.split(":", 1)[1].strip().replace("%", "")
                    result["confidence"] = float(conf_text) / 100
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.split(":", 1)[1].strip()
                elif line.startswith("KEY_MENTIONS:"):
                    result["key_mentions"] = line.split(":", 1)[1].strip()
                elif line.startswith("RISK_FACTORS:"):
                    result["risk_factors"] = line.split(":", 1)[1].strip()
            
            return result

# Usage example
async def demo_financial_analysis():
    # Sample Reddit posts (in real app, you'd fetch from Reddit API)
    sample_posts = [
        RedditPost(
            headline="Tesla earnings beat expectations, stock up 12% in after-hours",
            subreddit="stocks",
            score=2847,
            comments=[
                {"body": "Finally some good news for TSLA holders. The delivery numbers were solid.", "score": 234},
                {"body": "Still overvalued IMO. P/E ratio is insane compared to other automakers.", "score": 156}
            ],
            url="https://reddit.com/r/stocks/post1",
            created_utc=1640995200
        ),
        # Add more sample posts...
    ]
    
    summarizer = FinancialDiscussionSummarizer(api_key="your-api-key")
    analysis = await summarizer.generate_market_sentiment_summary(sample_posts)
    
    print(f"Market Sentiment: {analysis.get('sentiment', 'unknown')}")
    print(f"Confidence: {analysis.get('confidence', 0)*100:.1f}%")
    print(f"Summary: {analysis.get('summary', 'No summary available')}")
    print(f"Analysis Cost: ${analysis.get('analysis_cost', 0):.6f}")
```

### 3. Multi-Language Customer Support Bot

```python
from enum import Enum
from typing import Dict, List, Optional
import asyncio

class SupportCategory(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"

class CustomerSupportBot:
    def __init__(self, api_key: str):
        self.config = ProviderConfig(api_key=api_key, timeout=45.0)
        self.provider = LLMFactory.create_provider("openai", self.config)
        self.conversation_history: Dict[str, List[Message]] = {}
    
    async def detect_language_and_intent(self, user_message: str) -> Dict[str, Any]:
        """Detect user's language and categorize their support request."""
        
        detection_prompt = f"""
        Analyze this customer support message and provide:
        
        1. Language detected (ISO code like 'en', 'es', 'fr', 'de', 'ja', etc.)
        2. Support category (technical, billing, account, general)
        3. Urgency level (low, medium, high, critical)
        4. Sentiment (positive, neutral, negative, frustrated)
        
        Customer message: "{user_message}"
        
        Respond in this exact format:
        LANGUAGE: [language_code]
        CATEGORY: [category]
        URGENCY: [urgency_level]
        SENTIMENT: [sentiment]
        """
        
        messages = [Message(role=MessageRole.USER, content=detection_prompt)]
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.1,
            max_tokens=100
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            # Parse response
            result = {}
            for line in response.content.strip().split('\\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip().lower()] = value.strip()
            
            return {
                "language": result.get("language", "en"),
                "category": result.get("category", "general"),
                "urgency": result.get("urgency", "medium"),
                "sentiment": result.get("sentiment", "neutral"),
                "analysis_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini")
            }
    
    async def generate_support_response(self, 
                                      user_id: str,
                                      user_message: str,
                                      language: str = "en",
                                      category: str = "general") -> Dict[str, Any]:
        """Generate contextual support response in user's language."""
        
        # Initialize conversation history if new user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message to history
        self.conversation_history[user_id].append(
            Message(role=MessageRole.USER, content=user_message)
        )
        
        # Create system prompt based on category and language
        system_prompts = {
            "technical": f"You are a technical support specialist. Provide clear, step-by-step solutions. Always respond in {language}.",
            "billing": f"You are a billing support agent. Be empathetic and provide clear explanations about charges and refunds. Always respond in {language}.",
            "account": f"You are an account support representative. Help with account settings, security, and access issues. Always respond in {language}.",
            "general": f"You are a helpful customer service representative. Provide friendly, professional assistance. Always respond in {language}."
        }
        
        # Prepare conversation context
        conversation_messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompts.get(category, system_prompts["general"]))
        ]
        
        # Add conversation history (last 6 messages for context)
        conversation_messages.extend(self.conversation_history[user_id][-6:])
        
        request = ChatRequest(
            messages=conversation_messages,
            model="gpt-4.1-mini",
            temperature=0.4,
            max_tokens=500
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            # Add assistant response to history
            self.conversation_history[user_id].append(
                Message(role=MessageRole.ASSISTANT, content=response.content)
            )
            
            # Generate follow-up suggestions
            followup_prompt = f"""
            Based on this support interaction, suggest 3 brief follow-up questions the customer might have.
            
            Support response: "{response.content}"
            
            Format as:
            1. [Question 1]
            2. [Question 2]
            3. [Question 3]
            
            Keep suggestions in {language} and relevant to {category} support.
            """
            
            followup_messages = [Message(role=MessageRole.USER, content=followup_prompt)]
            followup_request = ChatRequest(
                messages=followup_messages,
                model="gpt-4.1-mini",
                temperature=0.3,
                max_tokens=200
            )
            
            followup_response = await self.provider.chat(followup_request)
            
            total_cost = (
                self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini") +
                self.provider.calculate_cost(followup_response.usage.dict(), "gpt-4.1-mini")
            )
            
            return {
                "response": response.content,
                "follow_up_suggestions": followup_response.content,
                "language": language,
                "category": category,
                "conversation_length": len(self.conversation_history[user_id]),
                "total_cost": total_cost,
                "response_time": response.created
            }
    
    async def escalate_to_human(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Generate handoff summary for human agents."""
        
        if user_id not in self.conversation_history:
            return {"error": "No conversation history found"}
        
        # Generate conversation summary
        conversation_text = "\\n".join([
            f"{msg.role.value}: {msg.content}" 
            for msg in self.conversation_history[user_id]
        ])
        
        summary_prompt = f"""
        Create a brief handoff summary for a human support agent:
        
        Conversation history:
        {conversation_text}
        
        Escalation reason: {reason}
        
        Provide:
        1. Issue summary (2-3 sentences)
        2. Customer's main concern
        3. Steps already taken
        4. Recommended next actions
        
        Format as a professional handoff note.
        """
        
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are creating a handoff summary for human support agents."),
            Message(role=MessageRole.USER, content=summary_prompt)
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.2,
            max_tokens=300
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            return {
                "handoff_summary": response.content,
                "escalation_reason": reason,
                "conversation_length": len(self.conversation_history[user_id]),
                "summary_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini")
            }

# Usage example
async def demo_customer_support():
    bot = CustomerSupportBot(api_key="your-api-key")
    
    # Simulate customer interaction
    user_id = "customer_123"
    user_message = "Hola, tengo problemas con mi cuenta. No puedo iniciar sesión."
    
    # Detect language and intent
    analysis = await bot.detect_language_and_intent(user_message)
    print(f"Detected: {analysis['language']} language, {analysis['category']} category")
    
    # Generate response
    support_response = await bot.generate_support_response(
        user_id=user_id,
        user_message=user_message,
        language=analysis['language'],
        category=analysis['category']
    )
    
    print(f"Bot Response: {support_response['response']}")
    print(f"Follow-up Suggestions: {support_response['follow_up_suggestions']}")
    print(f"Total Cost: ${support_response['total_cost']:.6f}")
```

### 4. Code Review and Documentation Assistant

```python
import ast
from typing import Dict, List, Any
from pathlib import Path

class CodeReviewAssistant:
    def __init__(self, api_key: str):
        self.config = ProviderConfig(api_key=api_key)
        self.provider = LLMFactory.create_provider("openai", self.config)
    
    async def analyze_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Comprehensive code quality analysis."""
        
        analysis_prompt = f"""
        Analyze this {language} code for:
        
        1. Code quality and best practices
        2. Performance concerns
        3. Security vulnerabilities
        4. Maintainability issues
        5. Bug risks
        6. Suggested improvements
        
        Code to analyze:
        ```{language}
        {code}
        ```
        
        Provide structured feedback with:
        - QUALITY_SCORE: [1-10]
        - ISSUES: [List of specific issues found]
        - SUGGESTIONS: [Concrete improvement recommendations]
        - SECURITY_CONCERNS: [Any security issues]
        - PERFORMANCE_NOTES: [Performance optimization opportunities]
        """
        
        messages = [
            Message(
                role=MessageRole.SYSTEM, 
                content=f"You are a senior software engineer conducting a thorough code review. Focus on {language} best practices, security, and maintainability."
            ),
            Message(role=MessageRole.USER, content=analysis_prompt)
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.3,
            max_tokens=800
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            # Parse structured response
            content = response.content.strip()
            result = {
                "raw_analysis": content,
                "analysis_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini"),
                "language": language,
                "code_length": len(code.split('\\n'))
            }
            
            # Extract structured data
            for line in content.split('\\n'):
                if line.startswith("QUALITY_SCORE:"):
                    try:
                        score_text = line.split(":", 1)[1].strip()
                        result["quality_score"] = int(score_text.split()[0])
                    except:
                        result["quality_score"] = 5
                elif line.startswith("ISSUES:"):
                    result["issues"] = line.split(":", 1)[1].strip()
                elif line.startswith("SUGGESTIONS:"):
                    result["suggestions"] = line.split(":", 1)[1].strip()
                elif line.startswith("SECURITY_CONCERNS:"):
                    result["security_concerns"] = line.split(":", 1)[1].strip()
                elif line.startswith("PERFORMANCE_NOTES:"):
                    result["performance_notes"] = line.split(":", 1)[1].strip()
            
            return result
    
    async def generate_documentation(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate comprehensive documentation for code."""
        
        doc_prompt = f"""
        Generate comprehensive documentation for this {language} code:
        
        ```{language}
        {code}
        ```
        
        Include:
        1. Overview and purpose
        2. Function/class descriptions
        3. Parameter explanations
        4. Return value descriptions
        5. Usage examples
        6. Error handling notes
        
        Format as markdown documentation.
        """
        
        messages = [
            Message(
                role=MessageRole.SYSTEM, 
                content="You are a technical writer creating clear, comprehensive code documentation."
            ),
            Message(role=MessageRole.USER, content=doc_prompt)
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.4,
            max_tokens=1000
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            return {
                "documentation": response.content,
                "language": language,
                "documentation_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini"),
                "generated_at": response.created
            }
    
    async def suggest_unit_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate unit test suggestions."""
        
        test_prompt = f"""
        Analyze this {language} code and suggest comprehensive unit tests:
        
        ```{language}
        {code}
        ```
        
        Generate:
        1. Test cases for happy path scenarios
        2. Edge case tests
        3. Error condition tests
        4. Mock requirements
        5. Test data examples
        
        Provide actual test code using appropriate testing framework.
        """
        
        framework_map = {
            "python": "pytest",
            "javascript": "Jest",
            "java": "JUnit",
            "go": "Go testing package"
        }
        
        messages = [
            Message(
                role=MessageRole.SYSTEM, 
                content=f"You are a test engineer creating comprehensive unit tests using {framework_map.get(language, 'standard testing practices')}."
            ),
            Message(role=MessageRole.USER, content=test_prompt)
        ]
        
        request = ChatRequest(
            messages=messages,
            model="gpt-4.1-mini",
            temperature=0.3,
            max_tokens=1200
        )
        
        async with self.provider:
            response = await self.provider.chat(request)
            
            return {
                "test_code": response.content,
                "language": language,
                "testing_framework": framework_map.get(language, "generic"),
                "test_generation_cost": self.provider.calculate_cost(response.usage.dict(), "gpt-4.1-mini")
            }
    
    async def perform_full_code_review(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Perform comprehensive code review with all analyses."""
        
        # Run all analyses in parallel
        quality_task = self.analyze_code_quality(code, language)
        documentation_task = self.generate_documentation(code, language)
        testing_task = self.suggest_unit_tests(code, language)
        
        quality_result = await quality_task
        documentation_result = await documentation_task
        testing_result = await testing_task
        
        total_cost = (
            quality_result["analysis_cost"] +
            documentation_result["documentation_cost"] +
            testing_result["test_generation_cost"]
        )
        
        return {
            "code_quality": quality_result,
            "documentation": documentation_result,
            "unit_tests": testing_result,
            "total_cost": total_cost,
            "review_summary": {
                "quality_score": quality_result.get("quality_score", 5),
                "total_analyses": 3,
                "language": language,
                "code_lines": len(code.split('\\n'))
            }
        }

# Usage example
async def demo_code_review():
    reviewer = CodeReviewAssistant(api_key="your-api-key")
    
    # Sample code to review
    sample_code = '''
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_user_data(data):
    # Unsafe: no input validation
    result = eval(data["expression"])
    return result
    '''
    
    # Perform full code review
    review_result = await reviewer.perform_full_code_review(sample_code, "python")
    
    print(f"Quality Score: {review_result['review_summary']['quality_score']}/10")
    print(f"Total Cost: ${review_result['total_cost']:.6f}")
    print("\\nIssues Found:")
    print(review_result['code_quality']['issues'])
    print("\\nSuggestions:")
    print(review_result['code_quality']['suggestions'])
```

## Error Handling

### Built-in Exception Types
```python
from pyaibridge.core.exceptions import (
    PyAIBridgeError,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    TimeoutError
)

async def error_handling_example():
    config = ProviderConfig(api_key="invalid-key")
    provider = LLMFactory.create_provider("openai", config)
    
    try:
        messages = [Message(role=MessageRole.USER, content="Hello")]
        request = ChatRequest(messages=messages, model="gpt-4.1-mini")
        
        async with provider:
            response = await provider.chat(request)
            
    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        
    except RateLimitError as e:
        print(f"Rate limit exceeded. Retry after: {e.retry_after} seconds")
        
    except ValidationError as e:
        print(f"Invalid request: {e.message}")
        
    except TimeoutError as e:
        print(f"Request timed out: {e.message}")
        
    except ProviderError as e:
        print(f"Provider error: {e.message}, Status: {e.status_code}")
        
    except PyAIBridgeError as e:
        print(f"General error: {e.message}")
```

### Custom Error Handling
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustLLMClient:
    def __init__(self, api_key: str):
        self.config = ProviderConfig(api_key=api_key, max_retries=3)
        self.provider = LLMFactory.create_provider("openai", self.config)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def robust_chat(self, messages: List[Message], model: str = "gpt-4.1-mini") -> str:
        """Chat with automatic retries and error recovery."""
        
        try:
            request = ChatRequest(messages=messages, model=model)
            
            async with self.provider:
                response = await self.provider.chat(request)
                return response.content
                
        except RateLimitError as e:
            print(f"Rate limited, waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after or 60)
            raise  # Re-raise for retry
            
        except AuthenticationError:
            print("Authentication failed - check API key")
            raise  # Don't retry authentication errors
            
        except (TimeoutError, ProviderError) as e:
            print(f"Transient error: {e.message}, retrying...")
            raise  # Re-raise for retry
```

## Performance Optimization

### Connection Pooling
```python
from pyaibridge.utils.metrics import metrics

class OptimizedLLMService:
    def __init__(self, api_key: str):
        self.config = ProviderConfig(
            api_key=api_key,
            timeout=30.0,
            max_retries=3
        )
        self.provider = LLMFactory.create_provider("openai", self.config)
    
    async def __aenter__(self):
        await self.provider.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.disconnect()
    
    async def batch_process(self, requests: List[ChatRequest]) -> List[ChatResponse]:
        """Process multiple requests efficiently."""
        
        async def process_single(request):
            try:
                return await self.provider.chat(request)
            except Exception as e:
                print(f"Error processing request: {e}")
                return None
        
        # Process requests concurrently
        tasks = [process_single(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed requests
        successful_responses = [r for r in responses if r is not None]
        
        return successful_responses

# Usage
async def batch_processing_demo():
    requests = [
        ChatRequest(
            messages=[Message(role=MessageRole.USER, content=f"Question {i}: What is AI?")],
            model="gpt-4.1-mini"
        ) for i in range(10)
    ]
    
    async with OptimizedLLMService(api_key="your-api-key") as service:
        responses = await service.batch_process(requests)
        
        print(f"Processed {len(responses)} requests")
        
        # Check metrics
        summary = metrics.get_summary()
        print(f"Total cost: ${summary['openai']['total_cost']:.6f}")
```

### Streaming for Long Responses
```python
async def efficient_streaming():
    config = ProviderConfig(api_key="your-api-key")
    provider = LLMFactory.create_provider("openai", config)
    
    request = ChatRequest(
        messages=[
            Message(role=MessageRole.USER, content="Write a detailed essay about climate change")
        ],
        model="gpt-4.1-mini",
        max_tokens=1500
    )
    
    full_response = ""
    async with provider:
        async for chunk in provider.stream_chat(request):
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            
            # Process chunk immediately if needed
            if len(full_response) > 1000:
                # Could save to database, update UI, etc.
                pass
    
    print(f"\\nFull response length: {len(full_response)} characters")
```

## API Reference

### Core Classes

#### LLMFactory
```python
class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str, config: ProviderConfig) -> BaseProvider:
        """Create a provider instance."""
        
    @staticmethod
    def list_providers() -> List[str]:
        """List available providers."""
```

#### ProviderConfig
```python
class ProviderConfig(BaseModel):
    api_key: str
    base_url: Optional[str] = None
    max_retries: int = 3
    timeout: float = 30.0
    rate_limit: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### Message
```python
class Message(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### ChatRequest
```python
class ChatRequest(BaseModel):
    messages: List[Message]
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = False
    user: Optional[str] = None
    timeout: Optional[float] = 30.0
```

#### ChatResponse
```python
class ChatResponse(BaseModel):
    id: str
    model: str
    content: str
    finish_reason: Optional[str] = None
    usage: Optional[Usage] = None
    created: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Provider Methods

#### BaseProvider
```python
class BaseProvider(ABC):
    async def connect(self) -> None:
        """Initialize connection to the provider."""
        
    async def disconnect(self) -> None:
        """Clean up connection to the provider."""
        
    async def validate_model(self, model: str) -> bool:
        """Validate if a model is supported."""
        
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat completion."""
        
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[StreamingChunk, None]:
        """Generate a streaming chat completion."""
        
    def calculate_cost(self, usage: Dict[str, int], model: str) -> Optional[float]:
        """Calculate cost for token usage."""
        
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
```

### Utility Functions

#### Metrics
```python
from pyaibridge.utils.metrics import metrics

# Track metrics
metrics.increment("requests", "openai")
metrics.record_timing("chat_completion", "openai", 1.5)
metrics.record_cost("openai", 0.001)

# Get metrics
summary = metrics.get_summary()
provider_metrics = metrics.get_metrics("openai")
timing_stats = metrics.get_timing_stats("chat_completion", "openai")

# Reset metrics
metrics.reset()
```

## Best Practices

### 1. Resource Management
```python
# Always use async context managers
async with provider:
    response = await provider.chat(request)

# Or manual connection management
await provider.connect()
try:
    response = await provider.chat(request)
finally:
    await provider.disconnect()
```

### 2. Error Handling
```python
# Implement proper error handling
try:
    response = await provider.chat(request)
except RateLimitError as e:
    await asyncio.sleep(e.retry_after or 60)
    # Retry logic
except AuthenticationError:
    # Update API key
    pass
```

### 3. Cost Management
```python
# Monitor costs
response = await provider.chat(request)
cost = provider.calculate_cost(response.usage.dict(), request.model)
print(f"Request cost: ${cost:.6f}")

# Use appropriate models
cheap_request = ChatRequest(messages=messages, model="gpt-4.1-mini")  # Cheaper
expensive_request = ChatRequest(messages=messages, model="gpt-4.1")   # More expensive
```

### 4. Performance Optimization
```python
# Use streaming for long responses
async for chunk in provider.stream_chat(request):
    process_chunk(chunk)

# Batch similar requests
responses = await asyncio.gather(*[
    provider.chat(request) for request in requests
])
```

This comprehensive documentation covers the major use cases and features of PyAIBridge. The library provides a robust, unified interface for working with multiple LLM providers while offering advanced features like cost tracking, metrics collection, and automatic error handling.