#!/usr/bin/env python3
"""
TestPyPI deployment script.
Builds and uploads package to TestPyPI for testing.
"""

import subprocess
import sys
import os
from pathlib import Path

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

def run_command(cmd, description):
    """Run a command and return success status."""
    print_status(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print_status(f"✓ {description} completed", "success")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print_status(f"✗ {description} failed", "error")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_status(f"✗ {description} timed out", "error")
        return False
    except Exception as e:
        print_status(f"✗ {description} error: {e}", "error")
        return False

def check_prerequisites():
    """Check if all prerequisites are met."""
    print_status("Checking prerequisites...", "info")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print_status("pyproject.toml not found. Run from project root.", "error")
        return False
    
    # Check for TestPyPI token
    token = os.getenv("TESTPYPI_TOKEN")
    if not token:
        print_status("TESTPYPI_TOKEN environment variable not set", "warning")
        print_status("You'll need to enter credentials manually", "info")
    
    print_status("Prerequisites check completed", "success")
    return True

def clean_dist():
    """Clean old distribution files."""
    print_status("Cleaning old distribution files...", "info")
    
    dist_path = Path("dist")
    if dist_path.exists():
        import shutil
        shutil.rmtree(dist_path)
        print_status("Old dist/ directory removed", "success")
    
    return True

def build_package():
    """Build the package."""
    print_status("Building package...", "info")
    return run_command("uv build", "Package build")

def upload_to_testpypi():
    """Upload package to TestPyPI."""
    print_status("Uploading to TestPyPI...", "info")
    
    token = os.getenv("TESTPYPI_TOKEN")
    if token:
        cmd = f"uv run twine upload --repository testpypi --username __token__ --password {token} dist/*"
    else:
        cmd = "uv run twine upload --repository testpypi dist/*"
    
    return run_command(cmd, "TestPyPI upload")

def verify_upload():
    """Verify the upload by checking TestPyPI."""
    print_status("Verifying upload...", "info")
    
    # Read version from pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('version ='):
                    version = line.split('=')[1].strip().strip('"')
                    break
        
        testpypi_url = f"https://test.pypi.org/project/pyaibridge/{version}/"
        print_status(f"Check your package at: {testpypi_url}", "info")
        
        # Provide installation instructions
        print_status("To test installation:", "info")
        print(f"  pip install -i https://test.pypi.org/simple/ pyaibridge=={version}")
        
        return True
        
    except Exception as e:
        print_status(f"Could not verify upload: {e}", "warning")
        return False

def main():
    """Main deployment function."""
    print_status("📦 Starting TestPyPI deployment...", "header")
    print_status("=" * 60, "header")
    
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Clean Distribution", clean_dist),
        ("Build Package", build_package),
        ("Upload to TestPyPI", upload_to_testpypi),
        ("Verify Upload", verify_upload)
    ]
    
    for step_name, step_func in steps:
        print_status(f"\n🔍 {step_name}", "header")
        print("-" * 40)
        
        if not step_func():
            print_status(f"❌ {step_name} failed - stopping deployment", "error")
            return 1
    
    print_status("\n" + "=" * 60, "header")
    print_status("🎉 TESTPYPI DEPLOYMENT COMPLETED!", "success")
    print_status("=" * 60, "header")
    
    print_status("\nNext steps:", "info")
    print_status("1. Test installation from TestPyPI", "info")
    print_status("2. Run integration tests", "info")
    print_status("3. If all good, deploy to production PyPI", "info")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())