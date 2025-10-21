"""
Quick test of CodeSwarm components
"""

import asyncio
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.openrouter_client import OpenRouterClient
from src.agents import ArchitectureAgent
from src.evaluation import GalileoEvaluator


async def test_openrouter():
    """Test OpenRouter client connection"""
    print("\n" + "="*60)
    print("TEST 1: OpenRouter Client")
    print("="*60)

    try:
        async with OpenRouterClient() as client:
            response = await client.complete(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'CodeSwarm is working!' and nothing else."}
                ],
                max_tokens=50
            )

            message = response["choices"][0]["message"]["content"]
            print(f" OpenRouter working!")
            print(f"   Response: {message}")
            print(f"   Latency: {response['latency_ms']}ms")
            return True
    except Exception as e:
        print(f" OpenRouter failed: {e}")
        return False


async def test_architecture_agent():
    """Test Architecture Agent"""
    print("\n" + "="*60)
    print("TEST 2: Architecture Agent")
    print("="*60)

    try:
        client = OpenRouterClient()
        await client.create_session_if_needed()

        evaluator = GalileoEvaluator()
        agent = ArchitectureAgent(
            openrouter_client=client,
            evaluator=evaluator
        )

        # Simple test task
        output = await agent.execute(
            task="Design a simple REST API for a todo list",
            context={},
            quality_threshold=85.0,  # Lower threshold for test
            max_iterations=1  # Just 1 iteration for test
        )

        print(f" Architecture Agent working!")
        print(f"   Model: {output.model_used}")
        print(f"   Score: {output.galileo_score:.1f}/100")
        print(f"   Code length: {len(output.code)} chars")
        print(f"   Latency: {output.latency_ms}ms")
        print(f"\n   Preview:")
        print(f"   {output.code[:200]}...")

        await client.close()
        return True

    except Exception as e:
        print(f" Architecture Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n CodeSwarm Component Tests")
    print("="*60)

    results = []

    # Test 1: OpenRouter
    results.append(await test_openrouter())

    # Test 2: Architecture Agent
    results.append(await test_architecture_agent())

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print(" All tests passed!")
    else:
        print(f"  {total - passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
