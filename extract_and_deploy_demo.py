#!/usr/bin/env python3.11
"""
Extract files from demo output and deploy to Daytona
"""

import asyncio
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integrations import DaytonaClient


def extract_files_from_code(code: str) -> dict:
    """Extract files from code with # File: markers"""
    files = {}
    current_file = None
    current_content = []

    for line in code.split('\n'):
        # Check for file marker
        if line.startswith('# File: '):
            # Save previous file
            if current_file:
                files[current_file] = '\n'.join(current_content)

            # Start new file
            current_file = line.replace('# File: ', '').strip()
            current_content = []
        elif current_file:
            current_content.append(line)

    # Save last file
    if current_file:
        files[current_file] = '\n'.join(current_content)

    return files


async def deploy_to_daytona(files: dict, project_name: str):
    """Deploy extracted files to Daytona"""

    print("=" * 80)
    print(f"DEPLOYING {project_name.upper()} TO DAYTONA")
    print("=" * 80)
    print()

    # Initialize client
    print("[1/4] 🔌 Connecting to Daytona...")
    daytona = DaytonaClient()
    print(f"      ✅ Connected")
    print()

    # Create workspace
    print("[2/4] 🏗️  Creating workspace...")
    workspace = await daytona.create_workspace(
        name=f"{project_name}",
        repository_url=None,
        branch="main"
    )
    workspace_id = workspace.get('id')
    print(f"      ✅ Workspace created: {workspace_id}")
    print()

    # Deploy files
    print(f"[3/4] 🚀 Deploying {len(files)} files...")

    # Determine run command based on package.json
    run_command = None
    if 'package.json' in files:
        # It's a Node project - install and run dev server
        run_command = "cd /home/daytona && npm install && nohup npm run dev > /tmp/server.log 2>&1 &"
    else:
        # Static files - just serve them
        run_command = "cd /home/daytona && nohup python3 -m http.server 3000 > /tmp/server.log 2>&1 &"

    deployment = await daytona.deploy_code(
        workspace_id=workspace_id,
        files=files,
        run_command=run_command
    )
    print(f"      ✅ Deployed!")
    print()

    # Get preview URL
    print("[4/4] 🌐 Getting preview URL...")

    # For Vite projects, port is usually 5173
    port = 5173 if 'vite.config' in str(files.keys()) else 3000
    preview_url = await daytona.get_preview_url(workspace_id, port=port)

    print(f"      ✅ Preview URL obtained")
    print()

    print("=" * 80)
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("=" * 80)
    print()
    print(f"📁 Project: {project_name}")
    print(f"📦 Files deployed: {len(files)}")
    print(f"🔗 Preview URL: {preview_url}")
    print()
    print("✨ Open the URL in your browser (requires Daytona login)")
    print()

    await daytona.close()


async def main():
    """Main function"""

    # Read the generated code
    demo_dir = Path("output/demo_20251019_013627")
    code_file = demo_dir / "implementation" / "implementation.js"

    if not code_file.exists():
        print(f"❌ Code file not found: {code_file}")
        return

    print("📖 Reading generated code...")
    code = code_file.read_text()
    print(f"   Size: {len(code)} bytes")
    print()

    # Extract files
    print("📦 Extracting files...")
    files = extract_files_from_code(code)
    print(f"   Found {len(files)} files:")
    for filename in files.keys():
        size = len(files[filename])
        print(f"     - {filename} ({size} bytes)")
    print()

    if not files:
        print("❌ No files extracted! Code format may not use # File: markers")
        return

    # Deploy to Daytona
    await deploy_to_daytona(files, "todo-app-demo")


if __name__ == "__main__":
    asyncio.run(main())
