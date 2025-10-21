#!/usr/bin/env python3
"""
Diagnose why Daytona workspace shows blank page
Usage: python diagnose_blank_page.py <workspace_id>
"""

import sys
from daytona_sdk import Daytona

def diagnose(workspace_id: str):
    """Diagnose deployment issues"""

    daytona = Daytona()

    print(f"🔍 Diagnosing workspace: {workspace_id}")
    print(f"=" * 60)

    try:
        sandbox = daytona.get(workspace_id)
        print(f"✅ Connected to workspace\n")

        # Check 1: Where are the files?
        print("📋 CHECK 1: Finding uploaded files")
        print("-" * 60)

        possible_locations = [
            '/',
            '/workspace',
            '/home',
            '/app',
            '/project'
        ]

        found_locations = []
        for location in possible_locations:
            try:
                file_infos = sandbox.fs.list_files(location)
                if file_infos and len(file_infos) > 0:
                    found_locations.append(location)
                    print(f"✅ Found {len(file_infos)} files in {location}:")
                    for f in file_infos[:10]:  # Show first 10
                        # f is a FileInfo object with .name, .path, .size, etc
                        name = f.name if hasattr(f, 'name') else str(f)
                        size = f.size if hasattr(f, 'size') else '?'
                        print(f"   - {name} ({size} bytes)")
                    if len(file_infos) > 10:
                        print(f"   ... and {len(file_infos) - 10} more")
            except Exception as e:
                pass  # Directory doesn't exist or no access

        if not found_locations:
            print("❌ No files found! Files may not have uploaded successfully.")
            return

        # Check 2: Look for index.html
        print(f"\n📋 CHECK 2: Looking for index.html")
        print("-" * 60)

        index_found = False
        for location in found_locations:
            try:
                content_bytes = sandbox.fs.download_file(f"{location}/index.html")
                content = content_bytes.decode('utf-8') if isinstance(content_bytes, bytes) else content_bytes
                print(f"✅ Found index.html in {location}")
                print(f"   Size: {len(content)} bytes")
                print(f"   Preview:\n{content[:200]}...")
                index_found = True
                break
            except:
                pass

        if not index_found:
            print("❌ No index.html found!")
            print("   Possible reasons:")
            print("   - Files uploaded with wrong paths")
            print("   - React app needs to be built first")

        # Check 3: Look for package.json
        print(f"\n📋 CHECK 3: Looking for package.json")
        print("-" * 60)

        package_found = False
        for location in found_locations:
            try:
                content_bytes = sandbox.fs.download_file(f"{location}/package.json")
                content = content_bytes.decode('utf-8') if isinstance(content_bytes, bytes) else content_bytes
                print(f"✅ Found package.json in {location}")
                import json
                pkg = json.loads(content)
                print(f"   Name: {pkg.get('name', 'unknown')}")
                if 'scripts' in pkg:
                    print(f"   Scripts:")
                    for script_name in pkg['scripts']:
                        print(f"     - {script_name}: {pkg['scripts'][script_name]}")
                package_found = True
                break
            except Exception as e:
                pass

        if not package_found:
            print("ℹ️  No package.json found (might be a static HTML project)")

        # Check 4: Suggest fixes
        print(f"\n💡 SUGGESTIONS:")
        print("-" * 60)

        if not index_found:
            print("1. Files may be in wrong location")
            print("   → Check test_daytona_deployment.py to see upload paths")
            print("   → Files should be in /workspace or root /")

        if package_found and not index_found:
            print("2. React app needs to be built")
            print("   → Run: npm install")
            print("   → Run: npm run build")
            print("   → Serve from build/ or dist/ directory")

        print("\n3. Check Daytona preview URL port")
        print(f"   → URL should match app port (usually 3000 for React dev)")
        print(f"   → Or use build folder for static serving")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_blank_page.py <workspace_id>")
        sys.exit(1)

    workspace_id = sys.argv[1]
    diagnose(workspace_id)
