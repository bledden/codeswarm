#!/usr/bin/env python3.11
"""
CodeSwarm Interactive Demo
Simple prompt-based interface for sketch-to-website generation
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import OpenRouterClient, Neo4jRAGClient, GalileoEvaluator, WorkOSAuthClient, DaytonaClient, BrowserUseClient
from orchestration.full_workflow import FullCodeSwarmWorkflow


def print_banner():
    """Print welcome banner"""
    print("=" * 80)
    print("  CodeSwarm - Sketch to Website Generator")
    print("  Turn your drawings into working websites!")
    print("=" * 80)
    print()


async def main():
    """Run interactive demo"""
    print_banner()

    # Get user input
    print("📝 What website would you like to build?")
    print("   (Example: A responsive landing page with email signup)")
    task = input("\n   Your request: ").strip()

    if not task:
        print("❌ No task provided. Exiting.")
        return

    print()
    print("🖼️  Do you have a sketch or mockup image? (optional)")
    print("   (Enter full path to image, or press Enter to skip)")
    image_path = input("\n   Image path: ").strip()

    if image_path and not Path(image_path).exists():
        print(f"⚠️  Image not found: {image_path}")
        print("   Continuing without image...")
        image_path = None
    elif image_path:
        print(f"✅ Using image: {image_path}")

    print()
    print("🚀 Deploy to Daytona workspace when done?")
    deploy_choice = input("   (y/n, default: y): ").strip().lower()
    deploy = deploy_choice != 'n'

    print()
    print("=" * 80)
    print("  Starting Code Generation")
    print("=" * 80)
    print()

    # Initialize services
    print("🔧 Initializing services...")
    services_initialized = []

    try:
        openrouter = OpenRouterClient()
        services_initialized.append("OpenRouter")
        print("  ✅ OpenRouter connected")
    except Exception as e:
        print(f"  ❌ OpenRouter failed: {e}")
        return

    # Neo4j (optional)
    neo4j = None
    try:
        neo4j = Neo4jRAGClient()
        services_initialized.append("Neo4j")
        print("  ✅ Neo4j connected")
    except Exception as e:
        print(f"  ⚠️  Neo4j unavailable: {e}")

    # Galileo (optional)
    galileo = None
    try:
        galileo = GalileoEvaluator()
        services_initialized.append("Galileo")
        print("  ✅ Galileo initialized")
    except Exception as e:
        print(f"  ⚠️  Galileo unavailable: {e}")

    # WorkOS (optional)
    workos = None
    try:
        workos = WorkOSAuthClient()
        services_initialized.append("WorkOS")
        print("  ✅ WorkOS initialized")
    except Exception as e:
        print(f"  ⚠️  WorkOS unavailable: {e}")

    # Daytona (optional)
    daytona = None
    try:
        async with DaytonaClient() as daytona_client:
            daytona = daytona_client
            services_initialized.append("Daytona")
            print("  ✅ Daytona connected")
    except Exception as e:
        print(f"  ⚠️  Daytona unavailable: {e}")

    # Browser Use (optional)
    browser_use = None
    try:
        browser_use = BrowserUseClient()
        services_initialized.append("Browser Use")
        print("  ✅ Browser Use connected")
    except Exception as e:
        print(f"  ⚠️  Browser Use unavailable: {e}")

    print(f"\n🎯 {len(services_initialized)}/6 services active")
    print()

    # Create workflow
    workflow = FullCodeSwarmWorkflow(
        openrouter_client=openrouter,
        neo4j_client=neo4j,
        galileo_evaluator=galileo,
        workos_client=workos,
        daytona_client=daytona,
        browser_use_client=browser_use,
        quality_threshold=90.0,
        max_iterations=3
    )

    # Execute workflow
    print("=" * 80)
    print("  GENERATING CODE")
    print("=" * 80)
    print()

    result = await workflow.execute(
        task=task,
        user_id="demo-user",
        image_path=image_path,
        scrape_docs=True,
        deploy=deploy
    )

    # Display results
    print()
    print("=" * 80)
    print("  ✅ CODE GENERATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"📊 Quality Score: {result.get('quality_score', 'N/A')}")
    print(f"🔄 Iterations: {result.get('iterations', 'N/A')}")
    print()

    if result.get('code'):
        print("📝 Generated Code:")
        print("-" * 80)
        code = result['code']
        # Show first 50 lines
        lines = code.split('\n')
        preview_lines = lines[:50]
        print('\n'.join(preview_lines))
        if len(lines) > 50:
            print(f"\n... ({len(lines) - 50} more lines)")
        print("-" * 80)
        print()

    if result.get('deployment_url'):
        print(f"🚀 Deployed to: {result['deployment_url']}")
        print()

    print("Thank you for using CodeSwarm! 🎉")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
