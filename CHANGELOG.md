# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-20

### Added

**Rust HTTP Integration:**
- Hybrid HTTP client with automatic Rust/httpx detection
- Rust-accelerated HTTP requests for 1.22x performance improvement
- PyO3-based Rust extension with streaming support
- Automatic fallback to httpx when Rust unavailable
- Cross-platform wheel building for zero-setup deployment

**Performance Enhancements:**
- 1.22x faster overall HTTP performance with Rust
- 1.49x faster performance for medium workloads
- Connection pooling optimization in Rust client
- Release-optimized builds with stripped debug symbols

**Developer Experience:**
- Comprehensive HTTP benchmarking tools
- Enhanced version management for mixed Python/Rust projects
- CI/CD pipeline updates for cross-platform Rust builds
- Updated documentation with performance metrics

**Code Quality:**
- Complete ruff linting compliance (fixed 35+ errors)
- Full mypy type safety with proper Rust module handling
- Enhanced error handling with proper exception chaining
- Improved import organization and type annotations

### Changed
- All HTTP providers now use HybridHttpClient for performance
- Updated CI/CD pipeline for maturin-based Rust builds
- Enhanced bump_version script to handle Cargo.toml versioning
- Updated README and wiki with performance information

### Technical Details
- Integrated Rust HTTP client into OpenAI, Claude, Google, and XAI providers
- Added streaming support with proper async generator handling
- Implemented type-safe fallback mechanisms
- Zero breaking changes - fully backward compatible

## [0.1.1] - 2025-01-15

### Added

**Latest OpenAI Models (2025):**
- GPT-4.1 series: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- O-series reasoning models: `o3`, `o3-pro`, `o4-mini`
- 1M token context window for GPT-4.1 series
- 200K token context window for O-series models
- Updated pricing for all new models based on 2025 rates
- Knowledge cutoff information (June 2024) for new models
- Model type classification (reasoning vs general purpose)

**Enhanced Features:**
- Cost calculation for cached prompts (GPT-4.1 series)
- Model-specific metadata (knowledge cutoff, model type)
- Comprehensive test coverage for all new models

**Updated Examples:**
- `openai_latest_models.py` - Compare all 2025 OpenAI models
- Updated all examples to use `gpt-4.1-mini` as default
- Reasoning model examples with complex problem solving

**Documentation:**
- Updated README with latest model information
- Updated pricing information throughout documentation
- Added model comparison examples

## [0.1.0] - 2025-01-15

### Added

**Google Gemini Provider:**
- Full Google Gemini API support with async/await
- Support for all Gemini models:
  - Gemini 2.5 Flash, Gemini 2.5 Flash-8B, Gemini 2.5 Pro
  - Gemini 2.0 Flash  
  - Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 1.5 Flash-8B
- Google-specific streaming support
- Accurate pricing calculations for all Gemini models
- Comprehensive test coverage for Google provider
- Google-specific examples and documentation

**Enhanced Factory:**
- Added Google provider to LLMFactory
- Multi-provider support in factory pattern
- Updated provider registration system

**Examples:**
- `google_usage.py` - Basic Google Gemini usage
- `google_streaming.py` - Google streaming examples
- `google_models_comparison.py` - Compare different Gemini models
- `multi_provider_comparison.py` - Compare OpenAI vs Google responses

**Testing:**
- Complete test suite for Google provider
- Updated factory tests for multi-provider support
- Mocked Google API responses for reliable testing

### Changed
- Updated version to 0.1.0
- Enhanced README with Google provider documentation
- Updated supported providers list

## [0.0.1] - 2025-01-15

### Added

**Initial Release:**
- Core architecture with `BaseProvider` interface
- Type-safe Pydantic models for requests/responses
- Comprehensive exception hierarchy
- Async/await support throughout

**OpenAI Provider:**
- Full OpenAI API support with GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- Connection pooling for high performance
- Streaming support for real-time responses
- Smart retry logic with exponential backoff
- Rate limit handling with respect for retry-after headers

**Core Features:**
- LLMFactory for provider creation
- Built-in metrics collection and cost tracking
- Comprehensive error handling
- Type hints and validation with Pydantic
- Modern Python best practices (Python 3.9+)

**Development:**
- Full test coverage with pytest
- Code quality tools: Black, Ruff, mypy
- Development dependencies and tooling
- Examples and documentation

**Examples:**
- `basic_usage.py` - Basic chat completion
- `streaming_example.py` - Streaming responses  
- `metrics_example.py` - Metrics collection

**Documentation:**
- Comprehensive README with usage examples
- API documentation and configuration guides
- Development setup instructions