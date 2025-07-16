# 🚀 PyPI Deployment Guide

This guide explains how to set up automated deployment to PyPI for the pyaibridge package.

## 🔐 Step 1: Configure PyPI Trusted Publishing (Recommended)

**Trusted publishing** is the most secure way to deploy to PyPI without API tokens.

### 1.1 Create PyPI Account & Project
1. Go to [PyPI](https://pypi.org/) and create an account
2. Go to [Test PyPI](https://test.pypi.org/) and create an account (for testing)
3. Reserve your package name by uploading an initial version manually:
   ```bash
   uv build
   uv run twine upload dist/* --repository testpypi
   uv run twine upload dist/*  # For production PyPI
   ```

### 1.2 Configure Trusted Publishing on PyPI
1. Go to your project on PyPI: `https://pypi.org/manage/project/pyaibridge/`
2. Navigate to **"Publishing"** tab
3. Click **"Add a new publisher"**
4. Fill in the details:
   - **PyPI Project Name**: `pyaibridge`
   - **Owner**: `your-github-username` 
   - **Repository name**: `pyaibridge` (or your repo name)
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

5. Repeat for Test PyPI with environment name: `test-pypi`

### 1.3 Set up GitHub Environments
1. Go to your GitHub repository → Settings → Environments
2. Create two environments:
   - **`pypi`** (for production)
   - **`test-pypi`** (for testing)
3. Configure protection rules (optional but recommended):
   - Require review from maintainers
   - Restrict to main branch only

## 🔧 Step 2: Alternative - API Token Method

If you can't use trusted publishing, use API tokens:

### 2.1 Generate PyPI API Tokens
1. Go to PyPI → Account Settings → API Tokens
2. Create a token scoped to your project
3. Copy the token (starts with `pypi-`)

### 2.2 Add Secrets to GitHub
1. Go to your repo → Settings → Secrets and Variables → Actions
2. Add these secrets:
   - `PYPI_API_TOKEN`: Your PyPI token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI token

### 2.3 Update Workflow (if using tokens)
Modify `.github/workflows/release.yml` to use tokens instead of OIDC:
```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## 🚀 Step 3: Deployment Methods

### Method 1: Automatic Release (Recommended)
Use the automated workflow with version bumping:

```bash
# Go to GitHub Actions → "Auto Release" → Run workflow
# Select: patch/minor/major or enter custom version
```

This will:
1. ✅ Run all security checks
2. 🔢 Bump version automatically
3. 📝 Generate changelog
4. 🏷️ Create Git tag
5. 📦 Deploy to Test PyPI → Production PyPI
6. 📋 Create GitHub Release

### Method 2: Manual Tag Release
Create and push a version tag manually:

```bash
# Bump version manually
python scripts/bump_version.py patch  # or minor/major

# Commit and tag
git add .
git commit -m "chore: bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags
```

The workflow will automatically trigger and deploy.

### Method 3: Manual Workflow Dispatch
1. Go to GitHub Actions → "Release to PyPI"
2. Click "Run workflow"
3. Enter the version to release

## 📊 Step 4: Monitoring Deployments

### Check Deployment Status
- **GitHub Actions**: Monitor workflow progress
- **PyPI**: Check package page for new version
- **Test PyPI**: Verify test deployment first

### Verify Installation
```bash
# Test from Test PyPI
pip install --index-url https://test.pypi.org/simple/ pyaibridge

# Test from Production PyPI  
pip install pyaibridge
```

## 🔒 Security Features

Our deployment pipeline includes:

✅ **Security Scanning**: Bandit, Safety, pip-audit  
✅ **Code Quality**: Ruff, MyPy, Tests  
✅ **Version Verification**: Ensures tag matches package version  
✅ **Test Deployment**: Always test on Test PyPI first  
✅ **Trusted Publishing**: No API tokens needed  
✅ **Signed Releases**: GitHub-signed release artifacts  

## 🛠️ Troubleshooting

### Common Issues

**"Package already exists"**
- Version already published. Bump to a new version.

**"Invalid OIDC token"**  
- Check trusted publishing configuration on PyPI
- Verify environment names match exactly

**"Permission denied"**
- Check GitHub environment protection rules
- Ensure proper permissions in workflow

**"Security check failed"**
- Review security reports in workflow logs
- Fix any high-severity issues before release

### Manual Recovery
If automation fails, you can always deploy manually:

```bash
uv build
uv run twine check dist/*
uv run twine upload dist/*
```

## 📋 Deployment Checklist

Before each release:

- [ ] All tests passing
- [ ] Security scans clean  
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped correctly
- [ ] Test PyPI deployment works
- [ ] Production deployment successful
- [ ] GitHub release created
- [ ] Installation verification complete

## 🎯 Quick Commands

```bash
# Check current version
python -c "import sys; sys.path.insert(0, 'src'); from pyaibridge import __version__; print(__version__)"

# Dry run version bump
python scripts/bump_version.py patch --dry-run

# Manual build and check
uv build && uv run twine check dist/*

# Run security checks
./scripts/security_check.sh
```