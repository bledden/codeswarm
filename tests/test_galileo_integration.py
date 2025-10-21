#!/usr/bin/env python3.11
"""
Test Galileo Integration with Agents

This tests whether agents are actually calling Galileo during execution.
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.integrations import OpenRouterClient
from src.evaluation import GalileoEvaluator
from src.agents import ImplementationAgent


async def test_agent_with_galileo():
    """Test that agents actually use Galileo evaluator"""
    print("="*80)
    print("AGENT + GALILEO INTEGRATION TEST".center(80))
    print("="*80)
    print()

    # Initialize services
    print("[1/3] 🔌 Initializing services...")
    try:
        openrouter = OpenRouterClient()
        galileo = GalileoEvaluator()
        print(f"      ✅ OpenRouter connected")
        print(f"      ✅ Galileo initialized (project: {galileo.project})")
        print()
    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return

    # Create agent WITH Galileo evaluator
    print("[2/3] 🤖 Creating agent with Galileo evaluator...")
    agent = ImplementationAgent(
        openrouter_client=openrouter,
        evaluator=galileo  # THIS IS THE KEY!
    )
    print(f"      ✅ Agent created with evaluator: {agent.evaluator is not None}")
    print()

    # Execute a simple task
    print("[3/3] 💻 Executing task (this should log to Galileo)...")
    task = "Write a Python function to calculate fibonacci numbers"

    try:
        result = await agent.execute(
            task=task,
            context={"architecture_output": "Simple recursive implementation"},
            quality_threshold=70.0,
            max_iterations=1
        )

        print(f"      ✅ Execution complete!")
        print(f"      📊 Score: {result.galileo_score or 'N/A'}")
        print(f"      📝 Code length: {len(result.code)} chars")
        print()

        # Check if evaluation happened
        if result.galileo_score:
            print(f"{'='*80}")
            print("✅ GALILEO EVALUATION SUCCESSFUL!".center(80))
            print(f"{'='*80}\n")
            print(f"Score: {result.galileo_score}/100")
            print(f"Agent: implementation")
            print(f"Project: {galileo.project}")
            print()
            print("🌐 Check Galileo UI:")
            print(f"   URL: {galileo.console_url}")
            print(f"   Project: {galileo.project}")
            print(f"   Workflow: CodeSwarm-implementation")
            print()
        else:
            print(f"{'='*80}")
            print("⚠️  NO GALILEO SCORE FOUND".center(80))
            print(f"{'='*80}\n")
            print("The agent executed but didn't get a Galileo score.")
            print("This means the evaluator might not be being called.")
            print()

    except Exception as e:
        print(f"      ❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()

    # Close connections
    await openrouter.close()

    print("="*80)
    print("TEST COMPLETE".center(80))
    print("="*80)
    print()


if __name__ == "__main__":
    asyncio.run(test_agent_with_galileo())
