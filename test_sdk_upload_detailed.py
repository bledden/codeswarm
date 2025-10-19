#!/usr/bin/env python3.11
"""
Detailed test of Daytona SDK file upload
Tests exactly what the SDK is doing
"""

import os
from dotenv import load_dotenv
from daytona_sdk import Daytona

load_dotenv()

# The workspace ID from our recent test
workspace_id = "46a6d18b-de61-494c-8158-7b748c836166"

print("=" * 80)
print("DAYTONA SDK UPLOAD DEBUG TEST")
print("=" * 80)
print()

# Initialize SDK
print("[1] Initializing Daytona SDK...")
daytona = Daytona()
print("✅ SDK initialized")
print()

# Get the workspace
print(f"[2] Connecting to workspace: {workspace_id}")
sandbox = daytona.get(workspace_id)
print(f"✅ Connected to sandbox")
print()

# Check current working directory
print("[3] Checking workspace working directory...")
try:
    # Try to get the current directory
    result = sandbox.process.exec("pwd")
    print(f"Working directory: {result.stdout if hasattr(result, 'stdout') else result}")
except Exception as e:
    print(f"Could not get working directory: {e}")
print()

# List files in various locations
print("[4] Listing files in various locations...")
locations_to_check = [
    "/",
    "/workspace",
    "/home",
    "/root",
    "/tmp",
    ".",  # Current directory
]

for location in locations_to_check:
    try:
        files = sandbox.fs.list_dir(location)
        print(f"✅ {location}: {len(files)} files")
        if files:
            for f in files[:5]:
                print(f"   - {f}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more")
    except Exception as e:
        print(f"❌ {location}: {e}")
print()

# Now try uploading a test file with VERY verbose output
print("[5] Uploading test file...")
test_content = b"Hello from CodeSwarm test!"
test_paths = [
    "test.txt",  # Relative path
    "/test.txt",  # Absolute root
    "/workspace/test.txt",  # Absolute workspace
    "./test.txt",  # Explicit current directory
]

for test_path in test_paths:
    try:
        print(f"\nTrying to upload to: {test_path}")
        sandbox.fs.upload_file(test_content, test_path)
        print(f"   ✅ Upload returned successfully")

        # Try to read it back
        try:
            read_content = sandbox.fs.read_file(test_path)
            if read_content == test_content.decode('utf-8'):
                print(f"   ✅ File verified! Content matches!")
                print(f"   📂 SUCCESS: Files should be uploaded to '{test_path}'")
                break
            else:
                print(f"   ⚠️  File content doesn't match")
        except Exception as e:
            print(f"   ❌ Could not read back: {e}")
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")

print()
print("[6] Final check - list all locations again...")
for location in locations_to_check:
    try:
        files = sandbox.fs.list_dir(location)
        if "test.txt" in [f.split('/')[-1] for f in files]:
            print(f"✅ Found test.txt in {location}!")
    except:
        pass

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
