# Testing Guide

This guide covers how to test pyaibridge with real API keys and deploy to TestPyPI.

## Testing with Real API Keys

### 1. Set up environment variables

Create a `.env` file or set environment variables for the providers you want to test:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Google AI
export GOOGLE_API_KEY="AIza..."

# Anthropic (Claude)
export CLAUDE_API_KEY="sk-ant-..."

# xAI (Grok)
export XAI_API_KEY="xai-..."
```

### 2. Run real API tests

```bash
# From the project root
uv run python scripts/test_real_api.py
```

This will:
- Test each provider that has an API key set
- Skip providers without API keys
- Make actual API calls to verify functionality
- Test model validation, chat completion, and cost calculation

### 3. Example output

```
🔑 Starting real API key testing...
============================================================

Required environment variables:
  OPENAI_API_KEY - OpenAI API key
  GOOGLE_API_KEY - Google AI API key
  CLAUDE_API_KEY - Anthropic API key
  XAI_API_KEY - xAI API key

🔍 Testing OpenAI
----------------------------------------
ℹ️  Testing OpenAI...
✅ OpenAI: ✓ Response received: Hello from pyaibridge! How can I assist you today?
✅ OpenAI: ✓ Cost calculated: $0.000150

📊 REAL API TEST SUMMARY
============================================================
✅ OpenAI: PASSED
⏭️  Google: SKIPPED (no API key)
⏭️  Claude: SKIPPED (no API key)
⏭️  xAI: SKIPPED (no API key)

🎉 ALL 1 TESTED PROVIDERS PASSED!
```

## Deploying to TestPyPI

### 1. Get TestPyPI account and token

1. Create account at https://test.pypi.org/
2. Go to Account Settings > API tokens
3. Create a new token with scope "Entire account"
4. Set environment variable:

```bash
export TESTPYPI_TOKEN="pypi-..."
```

### 2. Deploy to TestPyPI

```bash
# From the project root
uv run python scripts/deploy_testpypi.py
```

This will:
- Clean old distribution files
- Build the package
- Upload to TestPyPI
- Provide verification links

### 3. Test installation from TestPyPI

After successful deployment:

```bash
# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ pyaibridge==0.1.2

# Test the installation
python -c "import pyaibridge; print('✅ Package imported successfully')"
```

### 4. Manual deployment steps

If you prefer manual deployment:

```bash
# Build package
uv build

# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*
```

## Production Deployment

After testing on TestPyPI:

### 1. Get PyPI token

1. Create account at https://pypi.org/
2. Create API token
3. Set environment variable:

```bash
export PYPI_TOKEN="pypi-..."
```

### 2. Deploy to production PyPI

```bash
# Upload to production PyPI
uv run twine upload dist/*
```

## Troubleshooting

### Common issues

1. **API key not found**: Make sure environment variables are set correctly
2. **Upload conflicts**: Version already exists on TestPyPI - increment version number
3. **Authentication failed**: Check your TestPyPI/PyPI token

### Version management

To update version for new releases:

```bash
# Update version in pyproject.toml
version = "0.1.3"

# Also update in src/pyaibridge/__init__.py
__version__ = "0.1.3"
```

### Testing checklist

Before deploying:

- [ ] All unit tests pass: `uv run pytest`
- [ ] Package tests pass: `uv run python scripts/test_package.py`
- [ ] Real API tests pass: `uv run python scripts/test_real_api.py`
- [ ] Version number updated
- [ ] CHANGELOG updated
- [ ] Documentation updated