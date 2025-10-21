#!/usr/bin/env python3.11
"""
Test Galileo Logging

This script tests that Galileo Observe is properly logging workflows
and you can see them in the web UI.
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.evaluation import GalileoEvaluator


async def test_galileo_logging():
    """Test complete Galileo logging flow"""
    print("="*80)
    print("GALILEO LOGGING TEST".center(80))
    print("="*80)
    print()

    # Step 1: Initialize Galileo
    print("[1/3] 🔌 Initializing Galileo Evaluator...")
    try:
        evaluator = GalileoEvaluator()
        print(f"      ✅ Initialized")
        print(f"      📊 Project: {evaluator.project}")
        print(f"      🌐 Console: {evaluator.console_url}")
        print()
    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return

    # Step 2: Create a test evaluation
    print("[2/3] 📝 Creating test evaluation...")
    try:
        test_task = "Create a simple function to add two numbers"
        test_code = """def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    \"\"\"
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")

    return a + b


# Example usage
if __name__ == "__main__":
    result = add_numbers(5, 3)
    print(f"5 + 3 = {result}")
"""

        score = await evaluator.evaluate(
            task=test_task,
            output=test_code,
            agent="implementation",
            model="gpt-5-pro",
            input_tokens=50,
            output_tokens=150,
            latency_ms=1234
        )

        print(f"      ✅ Evaluation complete")
        print(f"      📊 Score: {score:.1f}/100")
        print()

    except Exception as e:
        print(f"      ❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Verify in Galileo UI
    print("[3/3] 🌐 Verifying in Galileo UI...")
    print()
    print(f"{'='*80}")
    print("CHECK GALILEO WEB UI".center(80))
    print(f"{'='*80}\n")
    print(f"1. Go to: {evaluator.console_url}")
    print(f"2. Navigate to project: {evaluator.project}")
    print(f"3. Look for workflow: CodeSwarm-implementation")
    print()
    print("You should see:")
    print("  • Workflow name: CodeSwarm-implementation")
    print("  • Model: gpt-5-pro")
    print("  • Input tokens: 50")
    print("  • Output tokens: 150")
    print("  • Latency: 1234ms")
    print("  • Agent metadata: implementation")
    print()
    print(f"{'='*80}")
    print("✅ TEST COMPLETE".center(80))
    print(f"{'='*80}\n")
    print("If you see the workflow in Galileo UI, logging is working!")
    print("If not, check:")
    print("  1. GALILEO_API_KEY is correct in .env")
    print("  2. GALILEO_PROJECT matches your Galileo project name")
    print("  3. Network connectivity to Galileo API")
    print()


if __name__ == "__main__":
    asyncio.run(test_galileo_logging())
