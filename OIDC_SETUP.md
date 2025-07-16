# OIDC (Trusted Publishing) Setup Guide

Since you have OIDC configured, your deployment is much more secure! No API tokens needed.

## What is OIDC Trusted Publishing?

OpenID Connect (OIDC) allows GitHub Actions to authenticate directly with PyPI without storing API tokens. This is:
- ✅ **More secure** - No long-lived tokens
- ✅ **Easier to manage** - No token rotation needed
- ✅ **More reliable** - No token expiration issues

## Your Current Setup

Since you mentioned you have OIDC and environments already configured, your workflow should work immediately with these components:

### GitHub Workflow Features

```yaml
permissions:
  id-token: write  # Required for OIDC

- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    verbose: true  # No password/token needed!
```

### Environment Configuration

Your GitHub environments should be configured as:

- **`test-pypi`** environment - for TestPyPI deployments
- **`pypi`** environment - for production PyPI deployments

## Deployment Flow

### TestPyPI (Develop Branch)
```bash
git push origin develop
```
→ Triggers automatic deployment to TestPyPI

### PyPI (Production Release)
```bash
# Create release on GitHub
gh release create v0.1.3 --title "Release v0.1.3"
```
→ Triggers production deployment to PyPI (with approval)

## Verification

### Check OIDC Configuration

1. **PyPI Project Settings**:
   - Go to https://pypi.org/manage/project/pyaibridge/
   - Check "Publishing" tab for trusted publishers

2. **GitHub Environment Settings**:
   - Repository → Settings → Environments
   - Verify `pypi` and `testpypi` environments exist

### Test Deployment

The simplest way to test is:

```bash
# Push to develop branch
git checkout develop
git push origin develop

# Watch GitHub Actions
# Should deploy to TestPyPI automatically
```

## Benefits of Your Setup

✅ **No secrets to manage** - OIDC handles authentication
✅ **Environment protection** - Manual approval for production
✅ **Audit trail** - All deployments tracked in GitHub
✅ **Version verification** - Ensures tags match package versions
✅ **Automatic testing** - Multi-Python version testing

## Troubleshooting OIDC

### Common Issues

1. **"OIDC token not found"**
   - Check `permissions: id-token: write` in workflow
   - Verify environment names match PyPI configuration

2. **"Trusted publisher not configured"**
   - Add trusted publisher on PyPI project settings
   - Match repository name, environment name exactly

3. **"Environment not found"**
   - Create environments in GitHub repository settings
   - Use exact names: `pypi`, `test-pypi`

### Debug Steps

1. Check workflow logs in GitHub Actions
2. Verify PyPI trusted publisher configuration
3. Ensure environment names match exactly
4. Check repository permissions

## Your Next Steps

Since you have OIDC configured, you can immediately:

1. **Test deployment**:
   ```bash
   git checkout develop
   echo "# Test change" >> README.md
   git add . && git commit -m "test: trigger deployment"
   git push origin develop
   ```

2. **Monitor in GitHub Actions**:
   - Go to Actions tab
   - Watch the workflow run
   - Should deploy to TestPyPI automatically

3. **Create production release**:
   ```bash
   # When ready for production
   gh release create v0.1.3 --title "Release v0.1.3"
   ```

Your setup is already more secure and easier to maintain than traditional API token-based deployments!