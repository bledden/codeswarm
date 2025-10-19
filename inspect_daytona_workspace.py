#!/usr/bin/env python3
"""
Script to inspect files in a Daytona workspace
Usage: python inspect_daytona_workspace.py <workspace_id>
"""

import sys
import os
from daytona_sdk import Daytona

def inspect_workspace(workspace_id: str):
    """Inspect files in a Daytona workspace"""

    # Initialize SDK (reads from environment variables)
    daytona = Daytona()

    print(f"🔍 Inspecting workspace: {workspace_id}")
    print(f"=" * 60)

    try:
        # Get the workspace/sandbox
        sandbox = daytona.get(workspace_id)
        print(f"✅ Connected to workspace\n")

        # List files in root directory
        print("📁 Files in root directory (/):")
        try:
            root_files = sandbox.fs.list_dir('/')
            if root_files:
                for file in root_files:
                    print(f"  - {file}")
            else:
                print("  (empty)")
        except Exception as e:
            print(f"  Error listing root: {e}")

        # Try common directories
        common_dirs = ['/workspace', '/home', '/app', '/project']
        for dir_path in common_dirs:
            print(f"\n📁 Files in {dir_path}:")
            try:
                files = sandbox.fs.list_dir(dir_path)
                if files:
                    for file in files:
                        print(f"  - {file}")
                else:
                    print(f"  (empty or doesn't exist)")
            except Exception as e:
                print(f"  Directory doesn't exist or error: {e}")

        # Try to read a common file
        common_files = [
            '/workspace/index.html',
            '/workspace/App.tsx',
            '/workspace/package.json',
            '/index.html',
            '/App.tsx',
            '/package.json'
        ]

        print(f"\n📄 Checking for common files:")
        for file_path in common_files:
            try:
                content = sandbox.fs.read_file(file_path)
                print(f"  ✅ Found: {file_path}")
                print(f"     Preview: {content[:100]}...")
                break  # Found one, stop checking
            except Exception as e:
                print(f"  ❌ Not found: {file_path}")

    except Exception as e:
        print(f"❌ Error accessing workspace: {e}")
        print(f"\nMake sure:")
        print(f"  1. DAYTONA_API_KEY is set in environment")
        print(f"  2. DAYTONA_API_URL is set correctly")
        print(f"  3. Workspace ID is valid: {workspace_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_daytona_workspace.py <workspace_id>")
        print("\nTo find your workspace ID:")
        print("  - Check the output from test_daytona_deployment.py")
        print("  - Look for 'Created workspace: <id>' in the logs")
        sys.exit(1)

    workspace_id = sys.argv[1]
    inspect_workspace(workspace_id)
