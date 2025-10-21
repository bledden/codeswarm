#!/usr/bin/env python3.11
"""
Test Daytona Deployment

This script tests the complete Daytona deployment flow:
1. Connect to Daytona API
2. Create a workspace
3. Deploy a simple web app
4. Get the deployment URL
5. Display the URL to view the website
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.integrations import DaytonaClient


async def test_daytona_deployment():
    """Test complete Daytona deployment flow"""
    print("="*80)
    print("DAYTONA DEPLOYMENT TEST".center(80))
    print("="*80)
    print()

    # Step 1: Initialize Daytona client
    print("[1/5] 🔌 Connecting to Daytona API...")
    try:
        daytona = DaytonaClient()
        print(f"      ✅ Connected to {daytona.api_url}")
        print(f"      🔑 API Key: {daytona.api_key[:20]}...")
        print()
    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return

    # Step 2: List existing workspaces
    print("[2/5] 📋 Listing existing workspaces...")
    try:
        workspaces = await daytona.list_workspaces()
        print(f"      ✅ Found {len(workspaces)} existing workspace(s)")
        for ws in workspaces[:3]:  # Show first 3
            print(f"         • {ws.get('name')} (id: {ws.get('id')[:20]}...)")
        print()
    except Exception as e:
        print(f"      ⚠️  Could not list workspaces: {e}")
        print()

    # Step 3: Create a new workspace
    print("[3/5] 🏗️  Creating new workspace...")
    try:
        from datetime import datetime
        workspace_name = f"test-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        workspace = await daytona.create_workspace(
            name=workspace_name,
            repository_url=None,
            branch="main"
        )

        print(f"      ✅ Workspace created!")
        print(f"         • Name: {workspace.get('name')}")
        print(f"         • ID: {workspace.get('id')}")
        print(f"         • Status: {workspace.get('status')}")
        if workspace.get('url'):
            print(f"         • URL: {workspace.get('url')}")
        print()

        workspace_id = workspace.get('id')

    except Exception as e:
        print(f"      ❌ Failed: {e}")
        print(f"         Error details: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Deploy a simple web app
    print("[4/5] 🚀 Deploying simple web app...")
    try:
        # Simple HTML/JS web app
        files = {
            "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeSwarm Test Deployment</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        h1 { font-size: 3em; margin-bottom: 20px; }
        p { font-size: 1.2em; }
        .status {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <h1>🎉 CodeSwarm Deployment Success!</h1>
    <p>This website was automatically generated and deployed to Daytona.</p>
    <div class="status">
        <p><strong>Status:</strong> ✅ Live and Running</p>
        <p><strong>Deployed at:</strong> <span id="time"></span></p>
    </div>
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
    </script>
</body>
</html>""",
            "package.json": """{
  "name": "codeswarm-test",
  "version": "1.0.0",
  "scripts": {
    "start": "python3 -m http.server 3000"
  }
}"""
        }

        deployment = await daytona.deploy_code(
            workspace_id=workspace_id,
            files=files,
            run_command="cd /home/daytona && nohup python3 -m http.server 3000 > /tmp/server.log 2>&1 &"
        )

        print(f"      ✅ Deployment successful!")
        print(f"         • Status: {deployment.get('status')}")
        if deployment.get('url'):
            print(f"         • URL: {deployment.get('url')}")
        if deployment.get('output'):
            print(f"         • Output: {deployment.get('output')[:100]}...")
        print()

    except Exception as e:
        print(f"      ❌ Deployment failed: {e}")
        print(f"         Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print()

    # Step 5: Get preview URL for the workspace
    print("[5/5] 🌐 Getting deployment URL...")
    try:
        # Get workspace status
        status = await daytona.get_workspace_status(workspace_id)
        print(f"      ✅ Workspace status: {status.get('status')}")

        # Get preview URL for port 3000
        preview_url = await daytona.get_preview_url(workspace_id, port=3000)

        if preview_url:
            print(f"      ✅ Preview URL obtained!")
            print(f"         • URL: {preview_url}")
            print()
            print("="*80)
            print("🎉 DEPLOYMENT SUCCESSFUL!".center(80))
            print("="*80)
            print()
            print(f"🌐 View your deployed website at:")
            print(f"   {preview_url}")
            print()
            print("✨ The website shows a simple success page proving deployment works!")
            print()
        else:
            print("      ⚠️  Could not get preview URL")
            print("      💡  The workspace is running but preview URL not available yet")
            print(f"      📋 Workspace ID: {workspace_id}")
            print()

    except Exception as e:
        print(f"      ❌ Could not get preview URL: {e}")
        import traceback
        traceback.print_exc()

    # Close the client
    await daytona.close()

    print("="*80)
    print("TEST COMPLETE".center(80))
    print("="*80)
    print()


if __name__ == "__main__":
    asyncio.run(test_daytona_deployment())
