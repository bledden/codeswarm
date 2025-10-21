"""
Full CodeSwarm Workflow Test

Tests complete end-to-end flow with all agents:
1. Architecture Agent (Claude Sonnet 4.5)
2. Implementation Agent (GPT-5 Pro) + Security Agent (Claude Opus 4.1) - Parallel
3. Testing Agent (Grok-4)
4. Synthesis
"""

import asyncio
import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.openrouter_client import OpenRouterClient
from src.agents import (
    ArchitectureAgent,
    ImplementationAgent,
    SecurityAgent,
    TestingAgent,
    VisionAgent
)
from src.orchestration import CodeSwarmWorkflow
from src.evaluation import GalileoEvaluator
from src.learning.code_learner import CodeSwarmLearner


async def test_full_workflow():
    """Test complete CodeSwarm workflow"""

    print("\n" + "="*80)
    print(" CODESWARM FULL WORKFLOW TEST")
    print("="*80)
    print("\nTask: Create a simple REST API for a todo list application")
    print("Testing: All 4 agents + workflow orchestration + quality improvement")
    print("="*80 + "\n")

    # Initialize components
    print(" Initializing components...")

    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    print("    OpenRouter client")

    evaluator = GalileoEvaluator(project="codeswarm-test")
    print("    Galileo evaluator")

    learner = CodeSwarmLearner(cache_dir="cache/learning", neo4j_client=None)
    print("    Autonomous learner")

    # Initialize agents
    print("\n Initializing agents...")

    architecture_agent = ArchitectureAgent(
        openrouter_client=openrouter,
        evaluator=evaluator
    )

    implementation_agent = ImplementationAgent(
        openrouter_client=openrouter,
        evaluator=evaluator
    )

    security_agent = SecurityAgent(
        openrouter_client=openrouter,
        evaluator=evaluator
    )

    testing_agent = TestingAgent(
        openrouter_client=openrouter,
        evaluator=evaluator
    )

    vision_agent = VisionAgent(
        openrouter_client=openrouter,
        evaluator=None
    )

    print("    All 5 agents ready")

    # Create workflow
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
    print("    Workflow ready\n")

    # Run workflow
    task = "Create a REST API for a todo list with user authentication"

    try:
        result = await workflow.run(
            task=task,
            image_path=None,
            user_id="test-user"
        )

        # Display results
        print("\n" + "="*80)
        print(" RESULTS")
        print("="*80)

        print("\n  ARCHITECTURE OUTPUT:")
        print("-" * 80)
        arch_preview = result["architecture_output"][:400] if result["architecture_output"] else "None"
        print(arch_preview + "...")

        print("\n IMPLEMENTATION OUTPUT:")
        print("-" * 80)
        impl_preview = result["implementation_output"][:400] if result["implementation_output"] else "None"
        print(impl_preview + "...")

        print("\n SECURITY OUTPUT:")
        print("-" * 80)
        sec_preview = result["security_output"][:400] if result["security_output"] else "None"
        print(sec_preview + "...")

        print("\n TESTING OUTPUT:")
        print("-" * 80)
        test_preview = result["testing_output"][:400] if result["testing_output"] else "None"
        print(test_preview + "...")

        # Metrics
        print("\n" + "="*80)
        print(" QUALITY METRICS")
        print("="*80)

        for agent, score in result["galileo_scores"].items():
            status = "" if score >= 90 else ""
            print(f"{status} {agent.upper():20s}: {score:.1f}/100")

        avg_score = sum(result["galileo_scores"].values()) / len(result["galileo_scores"])
        print(f"\n{'AVERAGE':20s}: {avg_score:.1f}/100")
        print(f"{'TOTAL ITERATIONS':20s}: {result['improvement_iterations']}")
        print(f"{'SYNTHESIS':20s}: {' Complete' if result['synthesis_complete'] else ' Failed'}")

        # Save output
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "test_workflow_result.txt"
        with open(output_file, "w") as f:
            f.write(result["final_code"])

        print(f"\n Saved to: {output_file}")

        # Test validation
        print("\n" + "="*80)
        print(" VALIDATION")
        print("="*80)

        checks = [
            ("Architecture generated", bool(result["architecture_output"])),
            ("Implementation generated", bool(result["implementation_output"])),
            ("Security analysis done", bool(result["security_output"])),
            ("Tests generated", bool(result["testing_output"])),
            ("Average score >= 85", avg_score >= 85),
            ("Synthesis complete", result["synthesis_complete"]),
        ]

        for check_name, passed in checks:
            status = "" if passed else ""
            print(f"{status} {check_name}")

        all_passed = all(passed for _, passed in checks)

        print("\n" + "="*80)
        if all_passed:
            print(" ALL CHECKS PASSED - CODESWARM WORKING PERFECTLY!")
        else:
            print("  SOME CHECKS FAILED - Review output above")
        print("="*80 + "\n")

        return all_passed

    except Exception as e:
        print(f"\n WORKFLOW FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await openrouter.close()
        print("\n[CLEANUP]  Session closed")


async def main():
    """Run the full workflow test"""
    success = await test_full_workflow()

    if success:
        print("\n Full workflow test PASSED")
        return 0
    else:
        print("\n Full workflow test FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
