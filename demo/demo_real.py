"""
CodeSwarm REAL Presentation Demo
=================================

This is a REAL working demo that:
1. Actually generates code using real LLMs
2. Stores patterns in Neo4j
3. Gets real scores from Galileo
4. Outputs code to demo_output/ for validation
5. Shows improvement over 3 requests

Unlike demo_presentation.py (simulated), this makes real API calls
and generates real, validatable code.

Usage:
    python demo/demo_real.py
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

# Import real components
from integrations.openrouter_client import OpenRouterClient
from integrations.neo4j_client import Neo4jRAGClient
from evaluation.galileo_evaluator import GalileoEvaluator

# Color output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_agent(agent_name: str, message: str):
    """Print agent message"""
    color = {
        "RAG": Colors.CYAN,
        "ARCHITECTURE": Colors.BLUE,
        "IMPLEMENTATION": Colors.GREEN,
        "SECURITY": Colors.RED,
        "TESTING": Colors.CYAN,
        "GALILEO": Colors.HEADER,
        "NEO4J": Colors.GREEN,
    }.get(agent_name, Colors.END)
    print(f"{color}[{agent_name}]{Colors.END} {message}")


class RealDemoRequest:
    """Real working demo request that generates actual code"""

    def __init__(
        self,
        request_num: int,
        task: str,
        output_dir: Path
    ):
        self.request_num = request_num
        self.task = task
        self.output_dir = output_dir / f"request_{request_num:02d}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.openrouter = None
        self.neo4j = None
        self.evaluator = None

        self.results = {
            "request_num": request_num,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "outputs": {},
            "scores": {},
            "patterns_retrieved": 0
        }

    async def initialize_clients(self):
        """Initialize API clients"""
        print_agent("INIT", "Initializing OpenRouter...")
        self.openrouter = OpenRouterClient()
        await self.openrouter.create_session_if_needed()

        print_agent("INIT", "Initializing Neo4j...")
        self.neo4j = Neo4jRAGClient()
        await self.neo4j.verify_connection()

        print_agent("INIT", "Initializing Galileo...")
        self.evaluator = GalileoEvaluator(project=f"codeswarm-demo-req{self.request_num}")

        print(f"{Colors.GREEN}All clients ready!{Colors.END}\n")

    async def step_rag_retrieval(self):
        """Retrieve patterns from Neo4j"""
        print(f"\n{Colors.BOLD}[STEP 1/4] RAG Retrieval from Neo4j{Colors.END}")
        print("-" * 70)

        print_agent("RAG", "Searching for similar authentication patterns...")

        # Search for similar patterns
        patterns = await self.neo4j.retrieve_similar_patterns(
            task=self.task,
            limit=5,
            min_score=90.0
        )

        self.results["patterns_retrieved"] = len(patterns)

        if len(patterns) == 0:
            print_agent("RAG", f"{Colors.YELLOW}Found 0 patterns (cold start){Colors.END}")
        else:
            print_agent("RAG", f"{Colors.GREEN}Found {len(patterns)} high-quality pattern(s):{Colors.END}")
            for p in patterns:
                print(f"  - {p['id']}: {p['avg_score']:.1f}/100")

        return patterns

    async def step_generate_architecture(self, context: str = ""):
        """Generate architecture using Claude Sonnet 4.5"""
        print(f"\n{Colors.BOLD}[STEP 2/4] Agent Execution - Architecture{Colors.END}")
        print("-" * 70)

        print_agent("ARCHITECTURE", "Using Claude Sonnet 4.5...")

        prompt = f"""Design a complete system architecture for:

Task: {self.task}

{context}

Provide:
1. API endpoint structure
2. Database schema
3. Authentication flow
4. Security considerations

Output should be production-ready architecture documentation."""

        response = await self.openrouter.complete(
            model="claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": "You are an expert system architect."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )

        architecture = response["choices"][0]["message"]["content"]

        # Save to file
        arch_file = self.output_dir / "architecture.md"
        arch_file.write_text(architecture)

        print_agent("ARCHITECTURE", f"Generated architecture ({len(architecture)} chars)")
        print_agent("ARCHITECTURE", f"Saved to: {arch_file}")

        # Evaluate with Galileo
        score = await self.evaluator.evaluate(
            task=self.task,
            output=architecture,
            agent="architecture",
            model="claude-sonnet-4.5",
            input_tokens=response["usage"]["prompt_tokens"],
            output_tokens=response["usage"]["completion_tokens"],
            latency_ms=response["latency_ms"]
        )

        self.results["outputs"]["architecture"] = str(arch_file)
        self.results["scores"]["architecture"] = score

        print(f"  {Colors.GREEN}Score: {score:.1f}/100{Colors.END}")

        return architecture, score

    async def step_generate_implementation(self, architecture: str, context: str = ""):
        """Generate implementation using GPT-5 Pro"""
        print(f"\n{Colors.BOLD}[STEP 3/4] Agent Execution - Implementation{Colors.END}")
        print("-" * 70)

        print_agent("IMPLEMENTATION", "Using GPT-5 Pro...")

        prompt = f"""Implement the following architecture:

{architecture[:1000]}...

Task: {self.task}

{context}

Generate production-ready Python code with:
1. Complete FastAPI implementation
2. Database models
3. Authentication logic
4. Error handling
5. Input validation

Output only the Python code, well-commented."""

        response = await self.openrouter.complete(
            model="gpt-5-pro",
            messages=[
                {"role": "system", "content": "You are an expert Python developer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.2
        )

        implementation = response["choices"][0]["message"]["content"]

        # Save to file
        impl_file = self.output_dir / "implementation.py"
        impl_file.write_text(implementation)

        print_agent("IMPLEMENTATION", f"Generated code ({len(implementation)} chars)")
        print_agent("IMPLEMENTATION", f"Saved to: {impl_file}")

        # Evaluate
        score = await self.evaluator.evaluate(
            task=self.task,
            output=implementation,
            agent="implementation",
            model="gpt-5-pro",
            input_tokens=response["usage"]["prompt_tokens"],
            output_tokens=response["usage"]["completion_tokens"],
            latency_ms=response["latency_ms"]
        )

        self.results["outputs"]["implementation"] = str(impl_file)
        self.results["scores"]["implementation"] = score

        print(f"  {Colors.GREEN}Score: {score:.1f}/100{Colors.END}")

        return implementation, score

    async def step_quality_gate(self):
        """Check quality and store in Neo4j"""
        print(f"\n{Colors.BOLD}[STEP 4/4] Quality Gate & Storage{Colors.END}")
        print("-" * 70)

        avg_score = sum(self.results["scores"].values()) / len(self.results["scores"])
        self.results["avg_score"] = avg_score

        print_agent("GALILEO", f"Average Score: {avg_score:.1f}/100")

        if avg_score >= 90:
            print(f"{Colors.GREEN}Score exceeds 90 threshold - storing in Neo4j...{Colors.END}")

            # Store pattern
            pattern_id = await self.neo4j.store_successful_pattern(
                task=self.task,
                agent_outputs={
                    "architecture": {
                        "code": Path(self.results["outputs"]["architecture"]).read_text()[:10000],
                        "galileo_score": self.results["scores"]["architecture"],
                        "latency_ms": 0,
                        "iterations": 1
                    },
                    "implementation": {
                        "code": Path(self.results["outputs"]["implementation"]).read_text()[:10000],
                        "galileo_score": self.results["scores"]["implementation"],
                        "latency_ms": 0,
                        "iterations": 1
                    }
                },
                avg_score=avg_score,
                metadata={"request_num": self.request_num, "demo": True}
            )

            self.results["pattern_id"] = pattern_id
            print_agent("NEO4J", f"Stored as: {pattern_id}")
        else:
            print(f"{Colors.RED}Score below 90 threshold - would trigger improvement loop{Colors.END}")

        # Save results summary
        results_file = self.output_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print_agent("RESULTS", f"Summary saved to: {results_file}")

    async def run(self, previous_patterns: list = None):
        """Execute the full request"""
        print_header(f"REQUEST #{self.request_num}: {self.task}")

        # Initialize if first request
        if not self.openrouter:
            await self.initialize_clients()

        # Step 1: RAG Retrieval
        patterns = await self.step_rag_retrieval()

        # Build context from previous patterns
        context = ""
        if patterns:
            context = f"\nBuild upon these proven patterns:\n"
            for p in patterns[:2]:
                context += f"- Pattern {p['id']}: {p['task']} (score: {p['avg_score']:.1f})\n"

        # Step 2: Architecture
        architecture, arch_score = await self.step_generate_architecture(context)

        # Step 3: Implementation
        implementation, impl_score = await self.step_generate_implementation(architecture, context)

        # Step 4: Quality Gate
        await self.step_quality_gate()

        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'─'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}Request #{self.request_num} Complete{Colors.END}")
        print(f"{Colors.GREEN}Average Score: {self.results['avg_score']:.1f}/100{Colors.END}")
        print(f"{Colors.GREEN}Output Directory: {self.output_dir}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'─'*70}{Colors.END}\n")

        return self.results

    async def cleanup(self):
        """Cleanup connections"""
        if self.openrouter:
            await self.openrouter.close()
        if self.neo4j:
            await self.neo4j.close()


async def run_real_demo():
    """Run the complete real demo with 3 requests"""

    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║              CODESWARM REAL WORKING DEMO                           ║")
    print("║                                                                    ║")
    print("║    Generates REAL code, stores in REAL Neo4j, gets REAL scores    ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    print(f"{Colors.CYAN}This demo will:{Colors.END}")
    print(f"  1. Make real API calls to OpenRouter (Claude, GPT-5)")
    print(f"  2. Generate actual code files in demo_output/")
    print(f"  3. Store patterns in Neo4j database")
    print(f"  4. Get real quality scores from Galileo")
    print(f"  5. Show improvement over 3 requests\n")

    print(f"{Colors.YELLOW}Note: This uses real API credits (~$0.24 total){Colors.END}")

    response = input(f"\n{Colors.YELLOW}Continue? (yes/no): {Colors.END}")
    if response.lower() not in ['yes', 'y']:
        print("Demo cancelled.")
        return

    # Setup output directory
    output_dir = Path(__file__).parent.parent / "demo_output" / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{Colors.GREEN}Output directory: {output_dir}{Colors.END}\n")

    all_results = []

    # Request 1: Basic auth
    request1 = RealDemoRequest(
        request_num=1,
        task="Build a FastAPI user authentication endpoint with password hashing using bcrypt",
        output_dir=output_dir
    )

    result1 = await request1.run()
    all_results.append(result1)

    input(f"\n{Colors.YELLOW}Press ENTER for Request #2...{Colors.END}")

    # Request 2: JWT auth (reuses clients from request1)
    request2 = RealDemoRequest(
        request_num=2,
        task="Build authentication API with JWT access tokens and refresh tokens",
        output_dir=output_dir
    )
    request2.openrouter = request1.openrouter
    request2.neo4j = request1.neo4j

    result2 = await request2.run()
    all_results.append(result2)

    input(f"\n{Colors.YELLOW}Press ENTER for Request #3...{Colors.END}")

    # Request 3: Production auth
    request3 = RealDemoRequest(
        request_num=3,
        task="Build production-ready authentication with JWT, rate limiting, and account lockout protection",
        output_dir=output_dir
    )
    request3.openrouter = request1.openrouter
    request3.neo4j = request1.neo4j

    result3 = await request3.run()
    all_results.append(result3)

    # Cleanup
    await request1.cleanup()

    # Final summary
    print_header("DEMO SUMMARY - Real Quality Improvement")

    print(f"{Colors.BOLD}Quality Progression:{Colors.END}")
    for i, result in enumerate(all_results, 1):
        improvement = ""
        if i > 1:
            diff = result["avg_score"] - all_results[i-2]["avg_score"]
            improvement = f" ({Colors.GREEN}+{diff:.1f}{Colors.END})"

        score_color = Colors.GREEN if result["avg_score"] >= 95 else Colors.YELLOW
        print(f"  Request {i}: {score_color}{result['avg_score']:.1f}/100{Colors.END}{improvement}")
        print(f"    - Retrieved {result['patterns_retrieved']} prior pattern(s)")
        print(f"    - Output: {output_dir}/request_{i:02d}/")

    print(f"\n{Colors.BOLD}Generated Files:{Colors.END}")
    print(f"  Location: {output_dir}")
    print(f"  Structure:")
    print(f"    request_01/")
    print(f"      ├── architecture.md")
    print(f"      ├── implementation.py")
    print(f"      └── results.json")
    print(f"    request_02/")
    print(f"      ├── architecture.md")
    print(f"      ├── implementation.py")
    print(f"      └── results.json")
    print(f"    request_03/")
    print(f"      ├── architecture.md")
    print(f"      ├── implementation.py")
    print(f"      └── results.json")

    print(f"\n{Colors.BOLD}Validation:{Colors.END}")
    print(f"  1. Check generated code: ls {output_dir}/request_*/")
    print(f"  2. View Neo4j patterns: Open http://localhost:7474")
    print(f"     Run: MATCH (p:CodePattern) WHERE p.demo = true RETURN p")
    print(f"  3. Check Galileo: Visit https://app.galileo.ai")

    print(f"\n{Colors.BOLD}{Colors.HEADER}{'═'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}Real code generated and validated!{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'═'*70}{Colors.END}\n")


async def main():
    """Main entry point"""
    try:
        await run_real_demo()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted{Colors.END}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}Demo error: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
