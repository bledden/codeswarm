#!/usr/bin/env python3
"""
CodeSwarm Full Integration Demo
Showcases all 6 sponsor services working together
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import (
    BrowserUseClient,
    OpenRouterClient,
    Neo4jRAGClient,
    WorkOSAuthClient,
    DaytonaClient
)
from evaluation.galileo_evaluator import GalileoEvaluator
from orchestration import FullCodeSwarmWorkflow


def print_header(text: str, char: str = "="):
    """Print formatted header"""
    print(f"\n{char * 80}")
    print(f"  {text}")
    print(f"{char * 80}\n")


async def main():
    """Run full integration demo

    Usage:
        python3 demo_full_integration.py                    # Text-only mode
        python3 demo_full_integration.py sketch.jpg         # With vision analysis
    """
    print_header("🐝 CODESWARM - FULL INTEGRATION DEMO", "=")
    print("This demo showcases all 6 sponsor services:")
    print("  1. OpenRouter (Anthropic) - Multi-model LLM generation")
    print("  2. Galileo Observe - Real-time quality scoring")
    print("  3. Neo4j Aura - RAG pattern storage & retrieval")
    print("  4. WorkOS - Team authentication")
    print("  5. Daytona - Workspace deployment")
    print("  6. Tavily - Documentation scraping (Browser Use alternative)")
    print()

    # Check for image argument
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    if image_path:
        if Path(image_path).exists():
            print(f"📷 Using sketch image: {image_path}\n")
        else:
            print(f"⚠️  Image not found: {image_path}")
            print(f"    Continuing in text-only mode\n")
            image_path = None
    else:
        print("💡 Tip: Pass image path for vision analysis: python3 demo_full_integration.py sketch.jpg\n")

    # Initialize all services
    print("⚙️  Initializing services...")

    try:
        async with OpenRouterClient() as openrouter:
            print("  ✅ OpenRouter connected")

            try:
                async with Neo4jRAGClient() as neo4j:
                    print("  ✅ Neo4j Aura connected")

                    try:
                        galileo = GalileoEvaluator()
                        print("  ✅ Galileo Observe initialized")

                        try:
                            workos = WorkOSAuthClient()
                            print("  ✅ WorkOS initialized")

                            try:
                                async with DaytonaClient() as daytona:
                                    print("  ✅ Daytona connected")
                                    print()

                                    # Create full workflow
                                    workflow = FullCodeSwarmWorkflow(
                                        openrouter_client=openrouter,
                                        neo4j_client=neo4j,
                                        galileo_evaluator=galileo,
                                        workos_client=workos,
                                        daytona_client=daytona,
                                        quality_threshold=85.0,  # Slightly lower for demo
                                        max_iterations=2
                                    )

                                    # Execute workflow
                                    print_header("EXECUTING FULL WORKFLOW", "-")

                                    result = await workflow.execute(
                                        task="Create a secure REST API for managing user tasks with JWT authentication",
                                        user_id="demo-user-blake",
                                        image_path=image_path,  # Vision analysis if image provided
                                        scrape_docs=True,
                                        deploy=True  # Enabled for demo
                                    )

                                    # Print results
                                    print_header("📊 FINAL RESULTS", "=")

                                    print(f"Task: {result['task']}\n")

                                    print("Quality Scores:")
                                    print(f"  Architecture:    {result['architecture']['galileo_score']:.1f}/100")
                                    print(f"  Implementation:  {result['implementation']['galileo_score']:.1f}/100")
                                    print(f"  Security:        {result['security']['galileo_score']:.1f}/100")
                                    print(f"  Testing:         {result['testing']['galileo_score']:.1f}/100")
                                    print(f"  ────────────────")
                                    print(f"  Average:         {result['avg_score']:.1f}/100")
                                    print()

                                    print(f"Quality Threshold: {result['quality_threshold_met'] and '✅ MET' or '❌ NOT MET'} (85+)")
                                    print(f"RAG Patterns Used: {result['rag_patterns_used']}")
                                    if result['pattern_id']:
                                        print(f"Stored Pattern ID: {result['pattern_id']}")
                                    print()

                                    print("Code Generation:")
                                    print(f"  Architecture:    {len(result['architecture']['code']):,} characters")
                                    print(f"  Implementation:  {len(result['implementation']['code']):,} characters")
                                    print(f"  Security:        {len(result['security']['code']):,} characters")
                                    print(f"  Testing:         {len(result['testing']['code']):,} characters")
                                    total_chars = (
                                        len(result['architecture']['code']) +
                                        len(result['implementation']['code']) +
                                        len(result['security']['code']) +
                                        len(result['testing']['code'])
                                    )
                                    print(f"  ────────────────")
                                    print(f"  Total:           {total_chars:,} characters")
                                    print()

                                    print("Performance:")
                                    print(f"  Architecture:    {result['architecture']['latency_ms']:,}ms")
                                    print(f"  Implementation:  {result['implementation']['latency_ms']:,}ms")
                                    print(f"  Security:        {result['security']['latency_ms']:,}ms")
                                    print(f"  Testing:         {result['testing']['latency_ms']:,}ms")
                                    total_latency = (
                                        result['architecture']['latency_ms'] +
                                        result['implementation']['latency_ms'] +
                                        result['security']['latency_ms'] +
                                        result['testing']['latency_ms']
                                    )
                                    print(f"  ────────────────")
                                    print(f"  Total:           {total_latency:,}ms ({total_latency/1000:.1f}s)")
                                    print()

                                    # Save results
                                    output_dir = Path("demo_output")
                                    output_dir.mkdir(exist_ok=True)

                                    timestamp = result['timestamp'].replace(':', '-').replace('.', '-')
                                    output_file = output_dir / f"full_demo_{timestamp}.json"

                                    import json
                                    with open(output_file, 'w') as f:
                                        json.dump(result, f, indent=2, default=str)

                                    print(f"💾 Results saved to: {output_file}")
                                    print()

                                    print_header("✅ DEMO COMPLETE - ALL 6 SERVICES INTEGRATED!", "=")

                            except Exception as e:
                                print(f"  ⚠️  Daytona error: {e}")
                                print("  Continuing without Daytona...")
                        except Exception as e:
                            print(f"  ⚠️  WorkOS error: {e}")
                            print("  Continuing without WorkOS...")
                    except Exception as e:
                        print(f"  ⚠️  Galileo error: {e}")
                        print("  Continuing without Galileo...")
            except Exception as e:
                print(f"  ❌ Neo4j error: {e}")
                print("  Cannot continue without Neo4j.")
                return 1

    except Exception as e:
        print(f"❌ OpenRouter error: {e}")
        print("Cannot continue without OpenRouter.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
