"""
Quick CodeSwarm Demo (2 agents only for fast testing)

Shows Architecture + Implementation working together
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, 'src')

from integrations.openrouter_client import OpenRouterClient
from agents import ArchitectureAgent, ImplementationAgent
from evaluation import GalileoEvaluator


async def quick_demo():
    """Run quick 2-agent demo"""

    print("\n" + "="*80)
    print(" CODESWARM QUICK DEMO (2 Agents)")
    print("="*80)
    print("\nTask: Create a REST API for a todo list")
    print("Agents: Architecture (Claude Sonnet 4.5) + Implementation (GPT-5 Pro)")
    print("="*80 + "\n")

    # Initialize
    print("  Initializing...")
    openrouter = OpenRouterClient()
    await openrouter.create_session_if_needed()
    evaluator = GalileoEvaluator()

    arch_agent = ArchitectureAgent(openrouter, evaluator)
    impl_agent = ImplementationAgent(openrouter, evaluator)
    print(" Ready\n")

    task = "Create a REST API for a todo list with CRUD operations"

    # Stage 1: Architecture
    print("" * 80)
    print("STAGE 1: Architecture Design")
    print("" * 80)

    arch_output = await arch_agent.execute(
        task=task,
        context={},
        quality_threshold=85,
        max_iterations=1
    )

    print(f"\n Architecture Complete")
    print(f"   Score: {arch_output.galileo_score:.1f}/100")
    print(f"   Length: {len(arch_output.code)} chars")
    print(f"\n   Preview:")
    print(f"   {arch_output.code[:300]}...\n")

    # Stage 2: Implementation
    print("" * 80)
    print("STAGE 2: Implementation")
    print("" * 80)

    impl_output = await impl_agent.execute(
        task=task,
        context={"architecture_output": arch_output.code},
        quality_threshold=85,
        max_iterations=1
    )

    print(f"\n Implementation Complete")
    print(f"   Score: {impl_output.galileo_score:.1f}/100")
    print(f"   Length: {len(impl_output.code)} chars")
    print(f"\n   Preview:")
    print(f"   {impl_output.code[:300]}...\n")

    # Results
    avg_score = (arch_output.galileo_score + impl_output.galileo_score) / 2

    print("="*80)
    print(" RESULTS")
    print("="*80)
    print(f"Architecture: {arch_output.galileo_score:.1f}/100")
    print(f"Implementation: {impl_output.galileo_score:.1f}/100")
    print(f"\nAverage Score: {avg_score:.1f}/100")

    if avg_score >= 90:
        print(" Exceeds 90+ quality threshold!")
    elif avg_score >= 85:
        print(" Meets 85+ quality threshold!")

    # Save output
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"quick_demo_{timestamp}.txt"

    with open(output_file, "w") as f:
        f.write(f"# CodeSwarm Quick Demo\n\n")
        f.write(f"Task: {task}\n\n")
        f.write(f"## Architecture\n\n{arch_output.code}\n\n")
        f.write(f"## Implementation\n\n{impl_output.code}\n\n")

    print(f"\n Saved to: {output_file}")
    print("="*80)

    await openrouter.close()

    print("\n Demo complete!\n")


if __name__ == "__main__":
    asyncio.run(quick_demo())
