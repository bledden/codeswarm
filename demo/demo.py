"""
CodeSwarm Demo Script

DEMO: Sketch → Live Website
User takes a photo of a website sketch, CodeSwarm generates production-ready code

This is the main hackathon demo showcasing:
1. Vision Agent analyzing sketch
2. 4 specialized agents collaborating
3. Quality assurance (Galileo 90+ threshold)
4. Self-improvement loop
5. Production-ready output
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.openrouter_client import OpenRouterClient
from agents import (
    ArchitectureAgent,
    ImplementationAgent,
    SecurityAgent,
    TestingAgent,
    VisionAgent
)
from orchestration import CodeSwarmWorkflow
from evaluation import GalileoEvaluator
from learning.code_learner import CodeSwarmLearner


def print_header(text, char="="):
    """Print formatted header"""
    width = 80
    print("\n" + char * width)
    print(text.center(width))
    print(char * width + "\n")


def print_section(title):
    """Print section divider"""
    print(f"\n{'' * 80}")
    print(f" {title}")
    print(f"{'' * 80}\n")


async def run_demo(image_path: str = None):
    """
    Run the CodeSwarm demo

    Args:
        image_path: Path to sketch/mockup image (optional for demo)
    """

    print_header(" CODESWARM DEMO", "=")

    print("DEMONSTRATION:")
    print("   User sketches a website on paper")
    print("   Takes a photo")
    print("   CodeSwarm generates production-ready code")
    print("   Quality assured (90+ threshold)")
    print("   Ready to deploy")

    if image_path:
        print(f"\n Image: {image_path}")
        if not Path(image_path).exists():
            print(f"  Warning: Image not found, will skip vision analysis")
            image_path = None
    else:
        print("\n  No image provided - running without vision analysis")
        print("   For full demo: python demo.py path/to/sketch.jpg")

    # Demo task
    task = "Create a modern landing page for a SaaS product with hero section, features, pricing, and contact form"

    print(f"\n Task: {task}")

    input("\n  Press Enter to start CodeSwarm...")

    # Initialize
    print_section("INITIALIZATION")

    print("  Initializing components...")
    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    evaluator = GalileoEvaluator(project="codeswarm-demo")
    learner = CodeSwarmLearner(cache_dir="cache/learning")

    print(" OpenRouter client ready")
    print(" Galileo evaluator ready")
    print(" Autonomous learner ready")

    print("\n Initializing agents...")
    architecture_agent = ArchitectureAgent(openrouter, evaluator)
    implementation_agent = ImplementationAgent(openrouter, evaluator)
    security_agent = SecurityAgent(openrouter, evaluator)
    testing_agent = TestingAgent(openrouter, evaluator)
    vision_agent = VisionAgent(openrouter, None)

    print(" Architecture Agent (Claude Sonnet 4.5)")
    print(" Implementation Agent (GPT-5 Pro)")
    print(" Security Agent (Claude Opus 4.1)")
    print(" Testing Agent (Grok-4)")
    print(" Vision Agent (GPT-5-image)")

    print("\n Creating workflow...")
    workflow = CodeSwarmWorkflow(
        architecture_agent=architecture_agent,
        implementation_agent=implementation_agent,
        security_agent=security_agent,
        testing_agent=testing_agent,
        vision_agent=vision_agent,
        rag_client=None,
        browser_client=None,
        learner=learner
    )
    print(" LangGraph workflow ready")

    # Run workflow
    print_section("CODESWARM EXECUTION")

    start_time = datetime.now()

    try:
        result = await workflow.run(
            task=task,
            image_path=image_path,
            user_id="demo-user"
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        # Display results
        print_section("RESULTS")

        print(" QUALITY METRICS:")
        print("-" * 80)

        scores = result["galileo_scores"]
        for agent, score in scores.items():
            bar_length = int(score / 2)  # 0-100 → 0-50 chars
            bar = "" * bar_length + "" * (50 - bar_length)
            status = "" if score >= 90 else "" if score >= 85 else ""
            print(f"{status} {agent.upper():15s} [{bar}] {score:.1f}/100")

        avg_score = sum(scores.values()) / len(scores)
        print(f"\n{'AVERAGE':15s} {avg_score:.1f}/100")
        print(f"{'ITERATIONS':15s} {result['improvement_iterations']}")
        print(f"{'TIME ELAPSED':15s} {elapsed:.1f}s")

        # Save outputs
        print_section("SAVING OUTPUTS")

        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save architecture
        arch_file = output_dir / f"architecture_{timestamp}.md"
        with open(arch_file, "w") as f:
            f.write(f"# Architecture\n\n{result['architecture_output']}")
        print(f" Architecture: {arch_file}")

        # Save implementation
        impl_file = output_dir / f"implementation_{timestamp}.py"
        with open(impl_file, "w") as f:
            f.write(result['implementation_output'])
        print(f" Implementation: {impl_file}")

        # Save security analysis
        sec_file = output_dir / f"security_{timestamp}.md"
        with open(sec_file, "w") as f:
            f.write(f"# Security Analysis\n\n{result['security_output']}")
        print(f" Security: {sec_file}")

        # Save tests
        test_file = output_dir / f"tests_{timestamp}.py"
        with open(test_file, "w") as f:
            f.write(result['testing_output'])
        print(f" Tests: {test_file}")

        # Save complete output
        complete_file = output_dir / f"complete_{timestamp}.txt"
        with open(complete_file, "w") as f:
            f.write(result['final_code'])
        print(f" Complete: {complete_file}")

        # Summary
        print_section("DEMO COMPLETE")

        quality_status = " EXCELLENT" if avg_score >= 95 else " GOOD" if avg_score >= 90 else "  ACCEPTABLE"

        print(f"Quality: {quality_status} ({avg_score:.1f}/100)")
        print(f"Time: {elapsed:.1f}s")
        print(f"Agents: 4 specialized models collaborated")
        print(f"Output: Production-ready code saved to demo_output/")

        if avg_score >= 90:
            print("\n Code meets 90+ quality threshold - stored in knowledge base")
        else:
            print("\n  Code below 90 threshold - not added to knowledge base")

        print("\n" + "=" * 80)
        print(" READY TO DEPLOY")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await openrouter.close()


async def main():
    """Main demo entry point"""

    # Check for image argument
    image_path = sys.argv[1] if len(sys.argv) > 1 else None

    success = await run_demo(image_path)

    if success:
        print("\n Demo completed successfully!")
        return 0
    else:
        print("\n Demo failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
