"""
CodeSwarm Main Entry Point

Initialize all components and run the workflow
"""

import os
import sys
import asyncio
from pathlib import Path

# Initialize Weave if available
try:
    import weave
    weave.init(project_name="codeswarm-hackathon")
    print("[WEAVE]  Observability initialized")
except ImportError:
    print("[WEAVE]   Weave not available - running without observability")
except Exception as e:
    print(f"[WEAVE]   Failed to initialize: {e}")

# Import CodeSwarm components
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


async def initialize_codeswarm():
    """Initialize all CodeSwarm components"""
    print("\n Initializing CodeSwarm...")
    print("="*60)

    # 1. OpenRouter client (for all models)
    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    print("[] OpenRouter client ready")

    # 2. Galileo evaluator
    evaluator = GalileoEvaluator(project="codeswarm-hackathon")
    print("[] Galileo evaluator ready")

    # 3. Autonomous learner
    learner = CodeSwarmLearner(cache_dir="cache/learning", neo4j_client=None)
    print("[] Autonomous learner ready")

    # 4. Initialize agents
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
        evaluator=None  # Vision doesn't need Galileo scoring
    )

    print("[] All agents initialized")

    # 5. Create workflow
    workflow = CodeSwarmWorkflow(
        architecture_agent=architecture_agent,
        implementation_agent=implementation_agent,
        security_agent=security_agent,
        testing_agent=testing_agent,
        vision_agent=vision_agent,
        rag_client=None,  # TODO: Neo4j RAG client
        browser_client=None,  # TODO: Browser Use client
        learner=learner
    )

    print("[] Workflow ready")
    print("="*60)
    print(" CodeSwarm initialization complete!\n")

    return workflow, openrouter


async def run_codeswarm(task: str, image_path: str = None):
    """
    Run CodeSwarm on a task

    Args:
        task: User's task description
        image_path: Optional path to sketch/mockup image
    """
    # Initialize
    workflow, openrouter = await initialize_codeswarm()

    try:
        # Run workflow
        result = await workflow.run(
            task=task,
            image_path=image_path,
            user_id="demo-user"
        )

        # Print results
        print("\n" + "="*60)
        print(" RESULTS")
        print("="*60)

        print("\n  ARCHITECTURE:")
        print("-" * 60)
        print(result["architecture_output"][:500] + "...")

        print("\n IMPLEMENTATION:")
        print("-" * 60)
        print(result["implementation_output"][:500] + "...")

        print("\n SECURITY:")
        print("-" * 60)
        print(result["security_output"][:500] + "...")

        print("\n TESTS:")
        print("-" * 60)
        print(result["testing_output"][:500] + "...")

        print("\n" + "="*60)
        print(" METRICS")
        print("="*60)
        for agent, score in result["galileo_scores"].items():
            print(f"{agent.upper()}: {score:.1f}/100")

        avg_score = sum(result["galileo_scores"].values()) / len(result["galileo_scores"])
        print(f"\nAVERAGE: {avg_score:.1f}/100")
        print(f"ITERATIONS: {result['improvement_iterations']}")

        # Save final code
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "generated_code.txt"
        with open(output_file, "w") as f:
            f.write(result["final_code"])

        print(f"\n Saved to: {output_file}")

        return result

    finally:
        # Cleanup
        await openrouter.close()
        print("\n[CLEANUP]  Session closed")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <task> [image_path]")
        print("\nExample:")
        print('  python src/main.py "Create a REST API for a todo app"')
        print('  python src/main.py "Build this website" demo/sketch.jpg')
        sys.exit(1)

    task = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Run
    asyncio.run(run_codeswarm(task, image_path))


if __name__ == "__main__":
    main()
