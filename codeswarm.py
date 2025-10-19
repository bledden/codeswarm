#!/usr/bin/env python3.11
"""
CodeSwarm - AI Code Generation
Command-line interface for AI-powered code generation

Usage:
  python codeswarm.py --task "create a landing page"
  python codeswarm.py --task "make a website that looks like this image /path/to/image.jpg"
  python codeswarm.py  # Interactive mode
"""
import asyncio
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import weave

# Load environment
load_dotenv()

# Initialize Weave tracing
weave.init(project_name="codeswarm")

sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import OpenRouterClient, Neo4jRAGClient, WorkOSAuthClient, DaytonaClient, TavilyClient
from evaluation.galileo_evaluator import GalileoEvaluator
from orchestration.full_workflow import FullCodeSwarmWorkflow


def print_banner():
    """Print welcome banner"""
    print()
    print("=" * 80)
    print("  CodeSwarm - AI Code Generation")
    print("=" * 80)
    print()


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="CodeSwarm - AI-powered code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python codeswarm.py --task "create a landing page for a coffee shop"
  python codeswarm.py --task "make a website that looks like this image /path/to/image.jpg"
  python codeswarm.py  # Interactive mode (prompts for task)
        """
    )

    parser.add_argument(
        '--task',
        type=str,
        help='Task description (can include image path in the text)'
    )

    parser.add_argument(
        '--image',
        type=str,
        help='Path to image file for vision-based generation (optional, overrides path in task)'
    )

    return parser.parse_args()


async def main():
    """Run code generation (interactive or from command-line args)"""
    args = parse_args()

    print_banner()

    # Get task from args or prompt interactively
    if args.task:
        user_input = args.task
        print(f"📝 Task: {user_input}\n")
    else:
        # Interactive mode - prompt user
        print("What kind of code do you need today?")
        print()
        print("Examples:")
        print("  • Create a REST API for user management")
        print("  • Build a responsive website (include image: /path/to/sketch.jpg)")
        print("  • Make a chat application with WebSocket support")
        print()

        user_input = input("Your request: ").strip()

    if not user_input:
        print()
        print("No request provided. Exiting.")
        return

    # Parse input for image path
    image_path = None
    task = user_input

    # Use --image arg if provided
    if args.image:
        expanded_path = Path(args.image).expanduser()
        if expanded_path.exists():
            image_path = str(expanded_path)
            print(f"✅ Using image from --image arg: {image_path}\n")
        else:
            print(f"⚠️  WARNING: Image file not found: {args.image}")
            print(f"   Continuing without image...\n")
    else:
        # Check if user included image path in their request
        # Look for file paths (starts with / or ~/ or ./)
        import re
        path_match = re.search(r'(?:image:|sketch:|mockup:)?\s*([~/.]?[^\s]+\.(jpg|jpeg|png|gif|webp))', user_input, re.IGNORECASE)

        if path_match:
            potential_path = path_match.group(1)
            expanded_path = Path(potential_path).expanduser()

            if expanded_path.exists():
                image_path = str(expanded_path)
                # Remove the path from the task description
                task = user_input.replace(path_match.group(0), '').strip()
                task = re.sub(r'\s+', ' ', task)  # Clean up extra spaces
                print()
                print(f"✅ Found image in task: {image_path}")

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
        print("  ✅ OpenRouter")
    except Exception as e:
        print(f"  ❌ OpenRouter failed: {e}")
        return

    # Neo4j (optional)
    neo4j = None
    try:
        neo4j = Neo4jRAGClient()
        services_initialized.append("Neo4j")
        print("  ✅ Neo4j")
    except Exception as e:
        print(f"  ⚠️  Neo4j unavailable")

    # Galileo (optional)
    galileo = None
    try:
        galileo = GalileoEvaluator()
        services_initialized.append("Galileo")
        print("  ✅ Galileo")
    except Exception as e:
        print(f"  ⚠️  Galileo unavailable")

    # WorkOS (optional)
    workos = None
    try:
        workos = WorkOSAuthClient()
        services_initialized.append("WorkOS")
        print("  ✅ WorkOS")
    except Exception as e:
        print(f"  ⚠️  WorkOS unavailable")

    # Daytona (optional)
    daytona = None
    try:
        async with DaytonaClient() as daytona_client:
            daytona = daytona_client
            services_initialized.append("Daytona")
            print("  ✅ Daytona")
    except Exception as e:
        print(f"  ⚠️  Daytona unavailable")

    # Tavily AI Search (optional - primary documentation source)
    tavily = None
    try:
        tavily = TavilyClient()
        services_initialized.append("Tavily")
        print("  ✅ Tavily")
    except Exception as e:
        print(f"  ⚠️  Tavily unavailable")

    print(f"\n🎯 {len(services_initialized)}/6 services active")
    print()

    # Create workflow
    workflow = FullCodeSwarmWorkflow(
        openrouter_client=openrouter,
        neo4j_client=neo4j,
        galileo_evaluator=galileo,
        workos_client=workos,
        daytona_client=daytona,
        tavily_client=tavily,
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
        deploy=True  # Auto-deploy by default
    )

    # Display results
    print()
    print("=" * 80)
    print("  ✅ CODE GENERATION COMPLETE!")
    print("=" * 80)
    print()

    if result.get('quality_score'):
        print(f"📊 Quality Score: {result['quality_score']}/100")
    if result.get('iterations'):
        print(f"🔄 Iterations: {result['iterations']}")

    print()

    if result.get('code'):
        print("📝 Generated Code Preview:")
        print("-" * 80)
        code = result['code']
        # Show first 40 lines
        lines = code.split('\n')
        preview_lines = lines[:40]
        print('\n'.join(preview_lines))
        if len(lines) > 40:
            print(f"\n... ({len(lines) - 40} more lines)")
        print("-" * 80)
        print()

    if result.get('deployment_url'):
        print(f"🚀 Deployed to: {result['deployment_url']}")
        print()

    print("✨ Thank you for using CodeSwarm!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
