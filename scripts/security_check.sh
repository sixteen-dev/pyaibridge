#!/bin/bash
# Security checks for PyPI package

set -e

echo "🔒 Running security checks for pyaibridge..."

# Install security tools
echo "📦 Installing security tools..."
uv sync --group security

# 1. Dependency vulnerability scanning
echo "🔍 Checking for known vulnerabilities..."
uv run safety check --json --output safety-report.json || true
uv run pip-audit --format=json --output=pip-audit-report.json || true

# 2. Static code analysis for security issues
echo "🔎 Running static security analysis..."
uv run bandit -r src/ -f json -o bandit-report.json || true

# 3. Check for hardcoded secrets
echo "🔐 Scanning for hardcoded secrets..."
if command -v semgrep &> /dev/null; then
    uv run semgrep --config=auto --json --output=semgrep-report.json src/ || true
fi

# 4. SAST scanning with custom rules
echo "🛡️  Running additional security patterns..."
uv run bandit -r src/ -ll --severity-level medium

# 5. Check package metadata for security
echo "📋 Validating package metadata..."
python -c "
import sys
import json
sys.path.insert(0, 'src')
from pyaibridge import __version__
print(f'Package version: {__version__}')
"

# 6. Verify no sensitive files in package
echo "📁 Checking for sensitive files..."
find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name ".env*" | grep -v .gitignore || echo "✅ No sensitive files found"

echo "✅ Security checks completed!"
echo "📊 Reports generated:"
echo "  - safety-report.json"
echo "  - pip-audit-report.json" 
echo "  - bandit-report.json"
if command -v semgrep &> /dev/null; then
    echo "  - semgrep-report.json"
fi