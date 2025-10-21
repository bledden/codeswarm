"""
Quick CodeSwarm Workflow Test

Tests workflow with faster execution:
- Lower quality threshold (85 instead of 90)
- Max 1 iteration per agent
- Simple task
"""

import asyncio
import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.openrouter_client import OpenRouterClient
from src.agents import ArchitectureAgent, ImplementationAgent, SecurityAgent, TestingAgent
from src.evaluation import GalileoEvaluator


async def test_parallel_agents():
    """Test that Implementation + Security can run in parallel"""

    print("\n" + "="*80)
    print(" TEST: Parallel Agent Execution")
    print("="*80)

    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    evaluator = GalileoEvaluator()

    # Create agents
    impl_agent = ImplementationAgent(openrouter, evaluator)
    sec_agent = SecurityAgent(openrouter, evaluator)

    # Shared context (architecture already defined)
    task = "Create a simple user authentication API"
    context = {
        "architecture_output": """
        Simple REST API with 2 endpoints:
        - POST /register: Create new user
        - POST /login: Authenticate user

        Database: SQLite with users table
        Auth: JWT tokens
        """
    }

    print("\n Running Implementation + Security in parallel...")
    import time
    start = time.time()

    # Run in parallel
    impl_task = impl_agent.execute(task, context, quality_threshold=85, max_iterations=1)
    sec_task = sec_agent.execute(task, context, quality_threshold=85, max_iterations=1)

    impl_output, sec_output = await asyncio.gather(impl_task, sec_task)

    elapsed = time.time() - start

    print(f"\n Parallel execution complete in {elapsed:.1f}s")
    print(f"   Implementation: {len(impl_output.code)} chars, score: {impl_output.galileo_score:.1f}")
    print(f"   Security: {len(sec_output.code)} chars, score: {sec_output.galileo_score:.1f}")

    await openrouter.close()

    return True


async def test_sequential_workflow():
    """Test sequential workflow: Architecture → Implementation → Testing"""

    print("\n" + "="*80)
    print(" TEST: Sequential Workflow")
    print("="*80)

    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    evaluator = GalileoEvaluator()

    task = "Create a simple todo list API"

    # Stage 1: Architecture
    print("\n[1/3]   Architecture Agent...")
    arch_agent = ArchitectureAgent(openrouter, evaluator)
    arch_output = await arch_agent.execute(task, {}, quality_threshold=85, max_iterations=1)
    print(f"    Score: {arch_output.galileo_score:.1f}, Length: {len(arch_output.code)} chars")

    # Stage 2: Implementation (uses architecture)
    print("\n[2/3]  Implementation Agent...")
    impl_agent = ImplementationAgent(openrouter, evaluator)
    context = {"architecture_output": arch_output.code}
    impl_output = await impl_agent.execute(task, context, quality_threshold=85, max_iterations=1)
    print(f"    Score: {impl_output.galileo_score:.1f}, Length: {len(impl_output.code)} chars")

    # Stage 3: Testing (uses implementation)
    print("\n[3/3]  Testing Agent...")
    test_agent = TestingAgent(openrouter, evaluator)
    context = {
        "architecture_output": arch_output.code,
        "implementation_output": impl_output.code
    }
    test_output = await test_agent.execute(task, context, quality_threshold=85, max_iterations=1)
    print(f"    Score: {test_output.galileo_score:.1f}, Length: {len(test_output.code)} chars")

    # Summary
    avg_score = (arch_output.galileo_score + impl_output.galileo_score + test_output.galileo_score) / 3
    print(f"\n Average Score: {avg_score:.1f}/100")

    await openrouter.close()

    return avg_score >= 85


async def main():
    """Run quick tests"""

    print("\n CodeSwarm Quick Workflow Tests")
    print("="*80)

    results = []

    # Test 1: Parallel execution
    try:
        result = await test_parallel_agents()
        results.append(("Parallel Agents", result))
    except Exception as e:
        print(f" Parallel test failed: {e}")
        results.append(("Parallel Agents", False))

    # Test 2: Sequential workflow
    try:
        result = await test_sequential_workflow()
        results.append(("Sequential Workflow", result))
    except Exception as e:
        print(f" Sequential test failed: {e}")
        results.append(("Sequential Workflow", False))

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    for test_name, passed in results:
        status = "" if passed else ""
        print(f"{status} {test_name}")

    all_passed = all(passed for _, passed in results)

    print("\n" + "="*80)
    if all_passed:
        print(" ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED")
    print("="*80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
