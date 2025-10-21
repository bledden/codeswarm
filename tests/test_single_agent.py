"""Quick test of a single agent to debug response parsing"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, 'src')

from src.integrations.openrouter_client import OpenRouterClient
from src.agents import TestingAgent
from src.evaluation import GalileoEvaluator


async def test_testing_agent():
    """Test just the testing agent to see raw output"""

    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    evaluator = GalileoEvaluator()

    agent = TestingAgent(openrouter, evaluator)

    task = "Create tests for a simple add function"
    context = {
        "implementation_output": """
def add(a, b):
    '''Add two numbers'''
    return a + b
"""
    }

    print("Testing Testing Agent...\n")

    output = await agent.execute(task, context, quality_threshold=85, max_iterations=1)

    print(f"\n{'='*70}")
    print("RAW OUTPUT:")
    print(f"{'='*70}")
    print(f"Code length: {len(output.code)}")
    print(f"Score: {output.galileo_score}")
    print(f"\nFirst 500 chars of code:")
    print(output.code[:500])
    print(f"\n{'='*70}")
    print("REASONING:")
    print(f"{'='*70}")
    print(output.reasoning[:500] if output.reasoning else "No reasoning")

    await openrouter.close()


if __name__ == "__main__":
    asyncio.run(test_testing_agent())
