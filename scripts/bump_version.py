#!/usr/bin/env python3
"""
Version bumping script for pyaibridge.
Automatically updates version in __init__.py and pyproject.toml
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple

def get_current_version() -> str:
    """Get current version from __init__.py"""
    init_file = Path("src/pyaibridge/__init__.py")
    if not init_file.exists():
        raise FileNotFoundError("src/pyaibridge/__init__.py not found")
    
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Version not found in __init__.py")
    
    return match.group(1)

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string"""
    try:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format X.Y.Z")
        return tuple(int(part) for part in parts)
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version}") from e

def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("bump_type must be 'major', 'minor', or 'patch'")

def update_init_file(new_version: str) -> None:
    """Update version in __init__.py"""
    init_file = Path("src/pyaibridge/__init__.py")
    content = init_file.read_text()
    
    new_content = re.sub(
        r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
        f'\\g<1>{new_version}\\g<2>',
        content
    )
    
    if content == new_content:
        raise ValueError("Failed to update version in __init__.py")
    
    init_file.write_text(new_content)
    print(f"✅ Updated src/pyaibridge/__init__.py: {new_version}")

def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("⚠️  pyproject.toml not found, skipping")
        return
    
    content = pyproject_file.read_text()
    
    # Only update the version in the [project] section, not tool configurations
    # Look for the pattern after [project] section and before any other section
    new_content = re.sub(
        r'(\[project\][\s\S]*?^version\s*=\s*["\'])[^"\']+(["\'])',
        f'\\g<1>{new_version}\\g<2>',
        content,
        flags=re.MULTILINE
    )
    
    if content != new_content:
        pyproject_file.write_text(new_content)
        print(f"✅ Updated pyproject.toml: {new_version}")
    else:
        print("⚠️  No version found in pyproject.toml or using dynamic versioning")

def main():
    parser = argparse.ArgumentParser(description="Bump version for pyaibridge")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--version",
        help="Set specific version instead of bumping"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        print(f"📋 Current version: {current_version}")
        
        if args.version:
            new_version = args.version
            # Validate the version format
            parse_version(new_version)
        else:
            new_version = bump_version(current_version, args.bump_type)
        
        print(f"🎯 New version: {new_version}")
        
        if args.dry_run:
            print("🔍 Dry run - no files will be modified")
            return
        
        # Update files
        update_init_file(new_version)
        update_pyproject_toml(new_version)
        
        print(f"🎉 Version successfully bumped to {new_version}")
        print("\n📝 Next steps:")
        print(f"   git add .")
        print(f"   git commit -m 'chore: bump version to {new_version}'")
        print(f"   git tag v{new_version}")
        print(f"   git push origin main --tags")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()