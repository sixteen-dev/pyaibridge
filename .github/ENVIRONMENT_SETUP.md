# GitHub Environment Setup Guide

This guide explains how to set up GitHub repository environments and secrets for automated deployments.

## Required Environments

Create these environments in your GitHub repository (Settings > Environments):

### 1. `test-pypi` Environment

**Purpose**: Deploy to TestPyPI for testing
**Protection rules**: 
- Required reviewers: None (auto-deploy on develop branch)
- Wait timer: 0 minutes

**Secrets**: None required (uses OIDC)

### 2. `pypi` Environment

**Purpose**: Deploy to production PyPI
**Protection rules**:
- Required reviewers: Repository admins
- Wait timer: 5 minutes
- Restrict to tags matching `v*`

**Secrets**: None required (uses OIDC)

### 3. `api-testing` Environment

**Purpose**: Run integration tests with real API keys
**Protection rules**:
- Required reviewers: None
- Wait timer: 0 minutes

**Secrets** (optional - only set what you want to test):
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google AI API key  
- `CLAUDE_API_KEY`: Anthropic API key
- `XAI_API_KEY`: xAI API key

## Setting Up Environments

### Step 1: Create Environments

1. Go to your repository on GitHub
2. Click **Settings** > **Environments**
3. Click **New environment**
4. Create each environment with the names above

### Step 2: Configure Protection Rules

For each environment:

1. Click on the environment name
2. Add protection rules as specified above
3. Save the environment

### Step 3: Add Secrets

For each environment:

1. Click on the environment name
2. Click **Add secret** in the Environment secrets section
3. Add the required secrets

## Setting Up OIDC (Trusted Publishing)

Since you have OIDC configured, no API tokens are needed! The workflow uses OpenID Connect for secure authentication.

### PyPI Trusted Publishing Setup

1. Sign up at https://pypi.org/ and https://test.pypi.org/
2. Configure trusted publishing for your repositories:
   - Go to your project settings on PyPI
   - Add trusted publisher with your GitHub repository details
   - Environment names: `pypi` and `testpypi`

### Provider API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Google AI**: https://console.cloud.google.com/apis/credentials
- **Anthropic**: https://console.anthropic.com/
- **xAI**: https://console.x.ai/

## Deployment Workflows

### Automatic TestPyPI Deployment

- **Trigger**: Push to `develop` branch
- **Process**:
  1. Run all tests
  2. Build package  
  3. Deploy to TestPyPI
  4. Test installation
  5. Run API integration tests

### Automatic PyPI Deployment

- **Trigger**: Create GitHub release
- **Process**:
  1. Run all tests
  2. Verify version matches release tag
  3. Build package
  4. Deploy to PyPI (with approval)
  5. Test installation

### Manual Workflow Triggers

You can also trigger workflows manually:

1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**
4. Choose branch and run

## Branch Strategy

```
main branch (production)
├── develop branch (testing)
└── feature/* branches
```

**Recommended flow**:
1. Develop in feature branches
2. Merge to `develop` → triggers TestPyPI deployment
3. Test the TestPyPI package
4. Merge to `main` and create release → triggers PyPI deployment

## Release Process

### 1. Prepare Release

```bash
# Update version
scripts/bump_version.py 0.1.3

# Update CHANGELOG.md
# Commit changes
git add .
git commit -m "Prepare release v0.1.3"
git push origin main
```

### 2. Create GitHub Release

1. Go to **Releases** > **Create a new release**
2. Tag: `v0.1.3`
3. Title: `Release v0.1.3`
4. Description: Copy from CHANGELOG.md
5. Click **Publish release**

### 3. Monitor Deployment

1. Go to **Actions** tab
2. Watch the deployment workflow
3. Approve PyPI deployment when prompted
4. Verify package is available on PyPI

## Troubleshooting

### Common Issues

1. **Token authentication failed**
   - Check token is correctly set in environment secrets
   - Ensure token has correct permissions

2. **Version already exists**
   - Increment version number
   - Cannot overwrite existing versions on PyPI

3. **Tests failing**
   - Check test logs in Actions tab
   - Fix issues before merging

4. **Environment protection rules**
   - Ensure you have required permissions
   - Check approval requirements

### Security Best Practices

- OIDC provides keyless authentication (more secure than API tokens)
- Never commit API keys to code
- Use environment secrets for sensitive data
- Limit API key permissions to minimum required
- Monitor usage and costs
- Enable branch protection rules