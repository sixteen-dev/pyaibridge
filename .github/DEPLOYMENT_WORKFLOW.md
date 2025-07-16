# Deployment Workflow

This document describes the branching strategy and CI/CD workflow for safe package deployments.

## Branching Strategy

```
main branch (production)
├── test-pypi branch (staging)
```

## Workflow Overview

### 1. Development → Test PyPI
- Push changes to `test-pypi` branch
- CI automatically runs tests and deploys to Test PyPI
- Manual testing can be performed using Test PyPI packages

### 2. Test PyPI → Production PyPI
- Create PR from `test-pypi` → `main`
- After PR merge, CI automatically deploys to production PyPI
- GitHub release is created automatically

## Detailed Process

### Stage 1: Deploy to Test PyPI
1. **Push to test-pypi branch**
   ```bash
   git checkout -b test-pypi
   # Make your changes
   git push origin test-pypi
   ```

2. **Automated CI Process**
   - Tests run across Python 3.9-3.12
   - Security checks with bandit
   - Code quality checks with ruff and mypy
   - Package is built and deployed to Test PyPI
   - Integration tests run (if API keys available)

3. **Manual Testing**
   ```bash
   # Install from Test PyPI
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyaibridge
   
   # Test your package
   python -c "import pyaibridge; print(pyaibridge.__version__)"
   ```

### Stage 2: Deploy to Production PyPI
1. **Create Pull Request**
   - Create PR from `test-pypi` → `main`
   - Review changes and ensure Test PyPI testing was successful
   - Merge PR

2. **Automated Production Deployment**
   - Tests run again on main branch
   - Package is built and deployed to production PyPI
   - Git tag is created automatically (v{version})
   - GitHub release is created with release notes

## Workflows

### `.github/workflows/test-pypi-deploy.yml`
- **Trigger**: Push to `test-pypi` branch
- **Purpose**: Deploy to Test PyPI for staging
- **Includes**: Tests, security checks, Test PyPI deployment, integration tests

### `.github/workflows/production-deploy.yml`
- **Trigger**: Push to `main` branch
- **Purpose**: Deploy to production PyPI
- **Includes**: Tests, security checks, PyPI deployment, release creation

### `.github/workflows/test-and-deploy.yml`
- **Trigger**: Push/PR to `main` or `test-pypi` branches
- **Purpose**: Continuous integration (tests only)
- **Includes**: Tests, security checks, code quality checks

## Environment Configuration

Ensure these GitHub environments are configured:

### `test-pypi` Environment
- **URL**: https://test.pypi.org/project/pyaibridge/
- **Required**: PyPI trusted publishing for Test PyPI

### `pypi` Environment
- **URL**: https://pypi.org/project/pyaibridge/
- **Required**: PyPI trusted publishing for production
- **Protection**: Require manual approval for production deployments

### `api-testing` Environment
- **Secrets**: API keys for integration testing
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY`
  - `CLAUDE_API_KEY`
  - `XAI_API_KEY`

## Version Management

- Version is managed in `src/pyaibridge/__init__.py`
- Update version before pushing to `test-pypi`
- Version should follow semantic versioning (e.g., 0.1.3, 1.0.0)

## Safety Features

1. **Staging Environment**: Test PyPI acts as staging
2. **Manual Review**: PR process allows code review
3. **Automated Testing**: Comprehensive test suite runs on both stages
4. **Security Scanning**: Bandit and other security tools
5. **Environment Protection**: Production requires approval
6. **Rollback Capability**: Git tags allow easy rollback

## Quick Commands

```bash
# Start new feature/fix
git checkout -b test-pypi

# Update version (edit src/pyaibridge/__init__.py)
# Make your changes

# Deploy to Test PyPI
git push origin test-pypi

# After testing, create PR to main
gh pr create --title "Deploy v{version}" --body "Deploy version {version} to production"

# After PR merge, production deployment happens automatically
```