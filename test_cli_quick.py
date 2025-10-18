#!/usr/bin/env python3
"""
Quick CLI test - verifies the CLI workflow works without full generation
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import OpenRouterClient, Neo4jRAGClient
from evaluation import GalileoEvaluator
from orchestration import FullCodeSwarmWorkflow


async def test_cli_workflow():
    """Test CLI workflow with minimal configuration"""

    print("\n🐝 CODESWARM CLI - QUICK TEST")
    print("="*60)

    task = "Create a Python function that adds two numbers"

    print(f"\n📝 Task: {task}\n")
    print("⚙️  Initializing services...")

    try:
        async with OpenRouterClient() as openrouter:
            print("  ✅ OpenRouter connected")

            async with Neo4jRAGClient() as neo4j:
                print("  ✅ Neo4j connected")

                galileo = GalileoEvaluator()
                print("  ✅ Galileo initialized")

                print("\n🎯 Creating workflow...")

                workflow = FullCodeSwarmWorkflow(
                    openrouter_client=openrouter,
                    neo4j_client=neo4j,
                    galileo_evaluator=galileo,
                    quality_threshold=90.0,
                    max_iterations=1  # Just 1 iteration for quick test
                )

                print("✅ Workflow created successfully")
                print("\n📊 Ready for code generation!")
                print("\nSkipping actual generation to keep test quick.")
                print("CLI workflow initialization: ✅ PASSED")

                return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_cli_workflow())
    sys.exit(0 if result else 1)
