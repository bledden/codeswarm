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
from datetime import datetime
import time

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

    parser.add_argument(
        '--rag-limit',
        type=int,
        default=None,
        help='Number of similar patterns to retrieve from Neo4j (default: 5, recommended by RAG best practices)'
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

    # Track session start time
    session_start_time = time.time()
    start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Session started: {start_timestamp}")
    print()

    # Initialize services
    init_start = time.time()
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

    init_duration = time.time() - init_start
    print(f"⏱️  Initialization took {init_duration:.2f}s")
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
    workflow_start = time.time()
    workflow_start_timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"⏰ Workflow started: {workflow_start_timestamp}")
    print()

    result = await workflow.execute(
        task=task,
        user_id="demo-user",
        image_path=image_path,
        scrape_docs=True,
        deploy=True,  # Auto-deploy by default
        rag_pattern_limit=args.rag_limit  # User-configurable RAG pattern limit
    )

    # Display results
    workflow_duration = time.time() - workflow_start
    print()
    print("=" * 80)
    print("  ✅ CODE GENERATION COMPLETE!")
    print("=" * 80)
    completion_timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"⏰ Completed: {completion_timestamp}")
    print(f"⏱️  Workflow took {workflow_duration:.2f}s ({workflow_duration/60:.1f} minutes)")
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

    # PHASE 4: User Feedback Loop
    if neo4j and result.get('pattern_id'):
        print("=" * 80)
        print("  💬 FEEDBACK (helps improve future generations)")
        print("=" * 80)
        print()

        try:
            # Generate session ID
            import uuid
            session_id = str(uuid.uuid4())[:8]

            # Ask for feedback
            code_quality = None
            context_quality = None

            try:
                code_input = input("Rate code quality (1-5, or press Enter to skip): ").strip()
                if code_input and code_input.isdigit():
                    code_quality = min(max(int(code_input), 1), 5)

                context_input = input("Rate documentation relevance (1-5, or press Enter to skip): ").strip()
                if context_input and context_input.isdigit():
                    context_quality = min(max(int(context_input), 1), 5)
            except (EOFError, KeyboardInterrupt):
                print("\n  Skipping feedback")
                code_quality = None
                context_quality = None

            # Store feedback if provided
            if code_quality is not None and context_quality is not None:
                import asyncio
                await neo4j.store_user_feedback(
                    session_id=session_id,
                    pattern_id=result['pattern_id'],
                    task=task,
                    code_quality=code_quality,
                    context_quality=context_quality,
                    would_retry=False
                )
                print(f"  ✅ Feedback saved! Thank you.\n")

                # If context quality is low, offer to identify unhelpful docs
                if context_quality < 3 and result.get('documentation_urls'):
                    print("  Which docs seemed irrelevant? (comma-separated numbers, or press Enter to skip)")
                    for i, url in enumerate(result['documentation_urls'], 1):
                        # Show domain only for cleaner output
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        print(f"    {i}. {domain}")

                    try:
                        unhelpful_input = input("  Unhelpful docs: ").strip()
                        if unhelpful_input:
                            indices = [int(x.strip()) - 1 for x in unhelpful_input.split(',') if x.strip().isdigit()]
                            for idx in indices:
                                if 0 <= idx < len(result['documentation_urls']):
                                    url = result['documentation_urls'][idx]
                                    await neo4j.mark_doc_unhelpful(
                                        url=url,
                                        session_id=session_id,
                                        reason="User marked as irrelevant"
                                    )
                            print(f"  ✅ Marked {len(indices)} docs as unhelpful\n")
                    except (ValueError, EOFError, KeyboardInterrupt):
                        print("  Skipping doc feedback\n")
            else:
                print("  Skipping feedback\n")

            # ITERATIVE REFINEMENT: Offer to refine the generated code
            try:
                refine_input = input("\n🔄 Would you like to refine this code? (y/n): ").strip().lower()

                if refine_input == 'y':
                    refinement_request = input("What changes would you like to make? ").strip()

                    if refinement_request:
                        print("\n" + "=" * 80)
                        print("  🔄 ITERATIVE REFINEMENT")
                        print("=" * 80)
                        print(f"\n📝 Refinement Request: {refinement_request}\n")

                        # Construct refinement task
                        refinement_task = f"{refinement_request}\n\nBased on this existing code:\n{result.get('code', '')[:2000]}..."

                        # Re-run workflow with previous code as context
                        print("🔄 Running full sequential workflow with refinement...")
                        refinement_result = await workflow.execute(
                            task=refinement_task,
                            user_id="demo-user",
                            image_path=image_path,  # Reuse original image if present
                            scrape_docs=True,
                            deploy=True,
                            rag_pattern_limit=args.rag_limit
                        )

                        # Update result for next iteration
                        result = refinement_result

                        print("\n✅ Refinement complete!")
                        if refinement_result.get('deployment_url'):
                            print(f"🚀 New deployment: {refinement_result['deployment_url']}")

                        # Loop back to feedback (recursive refinement)
                        continue_refining = True
                        while continue_refining:
                            try:
                                another_refinement = input("\n🔄 Refine again? (y/n): ").strip().lower()
                                if another_refinement != 'y':
                                    continue_refining = False
                                    break

                                next_refinement = input("What else would you like to change? ").strip()
                                if next_refinement:
                                    print("\n" + "=" * 80)
                                    print("  🔄 ADDITIONAL REFINEMENT")
                                    print("=" * 80)
                                    print(f"\n📝 Request: {next_refinement}\n")

                                    next_task = f"{next_refinement}\n\nBased on this existing code:\n{result.get('code', '')[:2000]}..."

                                    result = await workflow.execute(
                                        task=next_task,
                                        user_id="demo-user",
                                        image_path=image_path,
                                        scrape_docs=True,
                                        deploy=True,
                                        rag_pattern_limit=args.rag_limit
                                    )

                                    print("\n✅ Refinement complete!")
                                    if result.get('deployment_url'):
                                        print(f"🚀 New deployment: {result['deployment_url']}")
                                else:
                                    continue_refining = False
                            except (EOFError, KeyboardInterrupt):
                                print("\n  Ending refinement loop")
                                continue_refining = False

            except (EOFError, KeyboardInterrupt):
                print("\n  Skipping refinement")

            # PHASE 5: GitHub Integration
            try:
                from src.integrations.github_client import GitHubClient

                github = GitHubClient()

                # Check authentication, prompt if needed
                authenticated = github.is_authenticated()
                just_authenticated = False  # Track if user just authenticated

                if not authenticated:
                    # Offer to authenticate
                    push_prompt = input("\n📦 Push code to GitHub? (requires authentication) (y/n): ").strip().lower()
                    if push_prompt == 'y':
                        authenticated = github.prompt_authentication()
                        just_authenticated = authenticated  # Mark that we just authenticated

                # If authenticated (or just authenticated), proceed with push
                if authenticated:
                    # Only ask if they didn't just authenticate (they already said yes)
                    if not just_authenticated:
                        push_to_github = input("\n📦 Push code to GitHub? (y/n): ").strip().lower()
                    else:
                        # They just authenticated, so we know they want to push
                        push_to_github = 'y'

                    if push_to_github == 'y':
                        repo_name = input("  Repository name: ").strip()

                        if repo_name:
                            make_private = input("  Make repository private? (y/n, default: n): ").strip().lower()
                            private = make_private == 'y'

                            print(f"\n  🚀 Creating GitHub repository...")

                            # Get files from implementation output
                            output_files = {}
                            if 'implementation' in result and 'parsed_files' in result['implementation']:
                                output_files = result['implementation']['parsed_files']
                                print(f"  📄 Found {len(output_files)} files to commit")
                            else:
                                print(f"  ⚠️  No parsed_files found in result!")
                                print(f"  Result keys: {list(result.keys())}")

                            github_result = await github.create_and_push_repository(
                                repo_name=repo_name,
                                files=output_files,
                                description=f"CodeSwarm generated: {task[:100]}",
                                private=private,
                                task=task
                            )

                            if github_result['success']:
                                print(f"  ✅ Repository created: {github_result['url']}\n")

                                # Store GitHub URL in Neo4j
                                if neo4j and result.get('pattern_id'):
                                    await neo4j.link_github_url_to_pattern(
                                        pattern_id=result['pattern_id'],
                                        github_url=github_result['url']
                                    )
                                    print(f"  ✅ GitHub URL linked to pattern\n")
                            else:
                                print(f"  ❌ Failed to create repository: {github_result['error']}\n")

            except (EOFError, KeyboardInterrupt):
                print("\n  Skipping GitHub push")
            except Exception as e:
                print(f"  ⚠️  GitHub integration error: {e}\n")

        except Exception as e:
            print(f"  ⚠️  Feedback error: {e}\n")

    # Cleanup: Close all aiohttp sessions
    try:
        if openrouter and hasattr(openrouter, 'close'):
            await openrouter.close()
        if daytona and hasattr(daytona, 'close'):
            await daytona.close()
        if tavily and hasattr(tavily, 'close'):
            await tavily.close()
    except Exception:
        pass  # Silent cleanup - don't show errors to user

    # Session summary
    total_duration = time.time() - session_start_time
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 80)
    print("  SESSION SUMMARY")
    print("=" * 80)
    print(f"⏰ Started:  {start_timestamp}")
    print(f"⏰ Finished: {end_timestamp}")
    print(f"⏱️  Total time: {total_duration:.2f}s ({total_duration/60:.1f} minutes)")
    print("=" * 80)
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
