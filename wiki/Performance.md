# Performance & Rust Acceleration

PyAIBridge features a **Rust-accelerated HTTP client** that provides significant performance improvements over pure Python implementations.

## ⚡ Performance Overview

### Key Metrics
- **1.22x faster** HTTP requests compared to httpx
- **58ms average time saved** per request
- **22% performance improvement** across all operations
- **Automatic fallback** to Python if Rust unavailable

### Benchmark Results
```
Test Scenario: 170 HTTP requests to test endpoints

Rust HTTP Client:    269ms average response time
Python httpx:        327ms average response time
Performance Gain:    1.22x faster
Time Saved:          58ms per request
Success Rate:        100% for both clients
```

## 🏗️ Architecture

### Hybrid HTTP Client
PyAIBridge uses a **hybrid HTTP client** that automatically chooses the best available implementation:

1. **Primary**: Rust-based HTTP client (if available)
2. **Fallback**: Python httpx client (always available)

### Automatic Detection
```python
from pyaibridge.http_client import HybridHttpClient

# Automatically detects and uses Rust client
client = HybridHttpClient()
await client.connect()
# Output: "Using Rust HTTP client for enhanced performance"
```

### Manual Control
```python
# Force Rust client (fails if not available)
client = HybridHttpClient(use_rust=True)

# Force Python client
client = HybridHttpClient(use_rust=False)

# Auto-detect (default)
client = HybridHttpClient(use_rust=None)
```

## 🚀 Rust Implementation Details

### Features
- **Connection pooling** with configurable limits
- **Async/await support** using tokio runtime
- **Timeout handling** with per-request overrides
- **Error mapping** to Python exceptions
- **JSON serialization** using serde_json
- **Streaming support** for real-time responses

### Dependencies
The Rust HTTP client uses these high-performance crates:
- `reqwest` - HTTP client with connection pooling
- `tokio` - Async runtime
- `serde_json` - Fast JSON handling
- `pyo3` - Python bindings

### Binary Optimization
- **Release builds** with full optimization
- **Stripped symbols** for minimal size
- **4MB final binary** (15x smaller than debug)
- **Cross-platform wheels** for all major platforms

## 📊 Performance Testing

### Benchmarking Tools
PyAIBridge includes comprehensive benchmarking:

```bash
# Run HTTP client benchmarks
uv run python dev/http_benchmark.py

# Run end-to-end provider benchmarks  
uv run python dev/benchmark_test.py
```

### Test Scenarios
1. **Small Payload** - Basic requests (20 iterations)
2. **Medium Load** - High frequency requests (50 iterations) 
3. **Connection Reuse** - Connection pooling efficiency (100 iterations)

### Results by Scenario
| Scenario | Rust Client | httpx Client | Improvement |
|----------|-------------|--------------|-------------|
| Small Payload | 286ms | 291ms | 1.02x faster |
| Medium Load | 210ms | 312ms | **1.49x faster** |
| Connection Reuse | 295ms | 342ms | 1.16x faster |
| **Overall** | **269ms** | **327ms** | **1.22x faster** |

## 🎯 Performance Benefits

### Provider Operations
All PyAIBridge providers automatically benefit:
- **OpenAI** - GPT-4.1, O-series models
- **Google** - Gemini 2.5 series 
- **Claude** - Claude 4, 3.5 series
- **xAI** - Grok models

### Real-World Impact
```python
# Before: 327ms average per request
# After:  269ms average per request
# Saved:  58ms × 1000 requests = 58 seconds per 1000 requests

import time
start = time.time()

# 100 chat completions with Rust acceleration
for i in range(100):
    response = await provider.chat(request)
    
elapsed = time.time() - start
# ~5.8 seconds faster than pure Python
```

## 🔧 Installation & Setup

### For Users (No Setup Required)
```bash
pip install pyaibridge
# Rust acceleration works immediately!
```

### For Developers
```bash
# Install Rust toolchain (one-time)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build development version
uv run maturin develop

# Build optimized release
uv run maturin develop --release
```

## 🛡️ Reliability

### Graceful Fallback
The hybrid approach ensures reliability:
- **Rust available**: Uses optimized Rust client
- **Rust unavailable**: Automatically falls back to httpx
- **Rust fails**: Switches to Python for the request
- **Same interface**: No code changes required

### Error Handling
```python
try:
    response = await provider.chat(request)
    # Works regardless of underlying HTTP client
except ProviderError as e:
    # Same error handling for both implementations
    print(f"Request failed: {e}")
```

## 🚢 Distribution

### Cross-Platform Wheels
PyAIBridge publishes optimized wheels for:
- **Linux**: x86_64, aarch64
- **Windows**: x64  
- **macOS**: x86_64, ARM64 (Apple Silicon)

### CI/CD Pipeline
- **Automated builds** for all platforms
- **Release optimization** with stripped symbols
- **Cross-compilation** using GitHub Actions
- **Quality testing** before publication

## 🔬 Future Optimizations

### Planned Improvements
- **HTTP/2 support** for multiplexed connections
- **Connection warming** for reduced latency
- **Request batching** for bulk operations
- **Memory pool optimization** for zero-copy operations

### Benchmarking Goals
- **Target**: 2x performance improvement over httpx
- **Metric**: Sub-200ms average response times
- **Reliability**: 99.9% fallback success rate

The Rust acceleration makes PyAIBridge one of the fastest LLM client libraries available, while maintaining the simplicity and reliability Python developers expect.