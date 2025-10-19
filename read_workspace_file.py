#!/usr/bin/env python3
"""
Read a specific file from Daytona workspace
Usage: python read_workspace_file.py <workspace_id> <file_path>
"""

import sys
from daytona_sdk import Daytona

if len(sys.argv) < 3:
    print("Usage: python read_workspace_file.py <workspace_id> <file_path>")
    print("\nExample:")
    print("  python read_workspace_file.py abc123 /workspace/index.html")
    sys.exit(1)

workspace_id = sys.argv[1]
file_path = sys.argv[2]

# Initialize SDK
daytona = Daytona()

try:
    # Get workspace
    sandbox = daytona.get(workspace_id)

    # Read file
    content = sandbox.fs.read_file(file_path)

    print(f"📄 Contents of {file_path}:")
    print("=" * 60)
    print(content)

except Exception as e:
    print(f"❌ Error reading file: {e}")
    print(f"\nTry running inspect_daytona_workspace.py first to see available files")
