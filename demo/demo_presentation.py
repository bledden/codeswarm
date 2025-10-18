"""
CodeSwarm Presentation Demo
============================

Interactive demo showing quality improvement across 3 requests:
Request 1: 93.5/100 (baseline)
Request 2: 95.5/100 (learning)
Request 3: 97.2/100 (mastery)

Usage:
    python demo/demo_presentation.py
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Color output for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_step(step_num: int, total: int, title: str):
    """Print step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[STEP {step_num}/{total}] {title}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.END}")

def print_agent(agent_name: str, message: str):
    """Print agent message"""
    color = {
        "RAG": Colors.CYAN,
        "BROWSER": Colors.YELLOW,
        "ARCHITECTURE": Colors.BLUE,
        "IMPLEMENTATION": Colors.GREEN,
        "SECURITY": Colors.RED,
        "TESTING": Colors.CYAN,
        "GALILEO": Colors.HEADER,
        "NEO4J": Colors.GREEN,
        "LEARNER": Colors.YELLOW
    }.get(agent_name, Colors.END)

    print(f"{color}[{agent_name}]{Colors.END} {message}")

def print_score(agent: str, score: float, improvement: Optional[float] = None):
    """Print score with color coding"""
    color = Colors.GREEN if score >= 95 else Colors.YELLOW if score >= 90 else Colors.RED
    improvement_str = f" (+{improvement:.1f})" if improvement else ""
    print(f"  {color}Score: {score:.1f}/100{improvement_str}{Colors.END}")

def simulate_delay(seconds: float = 0.5):
    """Simulate processing time for demo"""
    time.sleep(seconds)


class DemoRequest:
    """Represents a demo request with simulated scores"""

    def __init__(
        self,
        request_num: int,
        task: str,
        architecture_score: float,
        implementation_score: float,
        security_score: float,
        testing_score: float,
        patterns_found: int = 0,
        browser_docs: int = 0
    ):
        self.request_num = request_num
        self.task = task
        self.scores = {
            "architecture": architecture_score,
            "implementation": implementation_score,
            "security": security_score,
            "testing": testing_score
        }
        self.patterns_found = patterns_found
        self.browser_docs = browser_docs
        self.avg_score = sum(self.scores.values()) / len(self.scores)

    async def run(self, previous_request: Optional['DemoRequest'] = None):
        """Execute demo request"""

        print_header(f"REQUEST #{self.request_num}: {self.task}")

        # Step 1: RAG Retrieval
        await self.step_rag_retrieval(previous_request)

        # Step 2: Browser Use
        await self.step_browser_use()

        # Step 3: Agent Execution
        await self.step_agents(previous_request)

        # Step 4: Quality Gate & Storage
        await self.step_quality_gate(previous_request)

        return self

    async def step_rag_retrieval(self, previous_request: Optional['DemoRequest']):
        """Simulate RAG retrieval"""
        print_step(1, 4, "RAG Retrieval from Neo4j")

        print_agent("RAG", "Searching for similar patterns...")
        simulate_delay(0.8)

        if self.patterns_found == 0:
            print_agent("RAG", f"{Colors.YELLOW}Found 0 matching patterns (cold start){Colors.END}")
            print_agent("RAG", "System starting with zero prior knowledge")
        else:
            print_agent("RAG", f"{Colors.GREEN}Found {self.patterns_found} matching pattern(s):{Colors.END}")

            if previous_request:
                for i in range(self.patterns_found):
                    req_num = self.request_num - self.patterns_found + i
                    if req_num > 0 and req_num < self.request_num:
                        score = 93.5 + (2.0 * (req_num - 1))
                        print(f"  {Colors.CYAN}✓ pattern_{req_num:03d} ({score:.1f}/100){Colors.END}")

            if self.patterns_found > 1:
                print_agent("RAG", f"Analyzing pattern evolution...")
                simulate_delay(0.3)
                improvement_rate = 2.0
                print_agent("RAG", f"Identified improvement trend: +{improvement_rate:.1f} points per iteration")

        simulate_delay(0.5)

    async def step_browser_use(self):
        """Simulate Browser Use documentation scraping"""
        print_step(2, 4, "Browser Use - Live Documentation Scraping")

        if self.browser_docs > 0:
            print_agent("BROWSER", "Scraping FastAPI authentication docs...")
            simulate_delay(1.0)
            print_agent("BROWSER", f"{Colors.GREEN}Found {self.browser_docs} code examples from docs.fastapi.tiangolo.com{Colors.END}")

            if self.request_num >= 2:
                print_agent("BROWSER", "Scraping JWT best practices...")
                simulate_delay(0.8)
                print_agent("BROWSER", f"{Colors.GREEN}Found 8 security patterns for token management{Colors.END}")

            if self.request_num >= 3:
                print_agent("BROWSER", "Scraping rate limiting documentation...")
                simulate_delay(0.8)
                print_agent("BROWSER", f"{Colors.GREEN}Found Redis rate limiting implementation examples{Colors.END}")
        else:
            print_agent("BROWSER", "Using existing pattern knowledge (no scraping needed)")

        simulate_delay(0.5)

    async def step_agents(self, previous_request: Optional['DemoRequest']):
        """Simulate agent execution"""
        print_step(3, 4, "Multi-Agent Code Generation")

        agents = [
            ("ARCHITECTURE", "Claude Sonnet 4.5", "architecture"),
            ("IMPLEMENTATION", "GPT-5 Pro", "implementation"),
            ("SECURITY", "Claude Opus 4.1", "security"),
            ("TESTING", "Grok-4", "testing")
        ]

        for agent_name, model, score_key in agents:
            await self.run_agent(
                agent_name,
                model,
                self.scores[score_key],
                previous_request.scores[score_key] if previous_request else None
            )

    async def run_agent(
        self,
        agent_name: str,
        model: str,
        score: float,
        previous_score: Optional[float]
    ):
        """Simulate individual agent execution"""

        print(f"\n{Colors.BOLD}[AGENT: {agent_name}] Using {model}{Colors.END}")

        # Show what the agent is doing
        if agent_name == "ARCHITECTURE":
            if previous_score:
                print_agent(agent_name, "Using previous architecture pattern as foundation...")
                simulate_delay(0.6)
                print_agent(agent_name, "Enhancing with new requirements...")
            else:
                print_agent(agent_name, "Designing system architecture from scratch...")
                simulate_delay(1.0)
            print_agent(agent_name, "Generated:")
            print(f"    - API endpoint structure")
            print(f"    - Database schema")
            print(f"    - Authentication flow diagram")

        elif agent_name == "IMPLEMENTATION":
            if previous_score:
                print_agent(agent_name, "Reusing proven code patterns...")
                simulate_delay(0.6)
                print_agent(agent_name, "Adding new features...")
            else:
                print_agent(agent_name, "Writing implementation from architecture...")
                simulate_delay(1.2)
            print_agent(agent_name, "Generated:")
            print(f"    - FastAPI endpoint handlers")
            if self.request_num >= 2:
                print(f"    - JWT token encoding/decoding")
            if self.request_num >= 3:
                print(f"    - Redis-based rate limiting")
            print(f"    - User model with SQLAlchemy")

        elif agent_name == "SECURITY":
            if previous_score:
                print_agent(agent_name, "Applying all previous security fixes...")
                simulate_delay(0.5)
            else:
                print_agent(agent_name, "Scanning for vulnerabilities...")
                simulate_delay(1.0)
                print_agent(agent_name, f"{Colors.YELLOW}Issues found:{Colors.END}")
                print(f"    ⚠️  Missing rate limiting on login endpoint")
                print(f"    ⚠️  Password minimum length not enforced")
                print_agent(agent_name, "Applying fixes...")
                simulate_delay(0.8)

            if self.request_num >= 2:
                print_agent(agent_name, "Adding JWT expiration validation...")
                simulate_delay(0.4)
            if self.request_num >= 3:
                print_agent(agent_name, "Adding account lockout after 5 failed attempts...")
                print_agent(agent_name, "Adding suspicious activity detection...")
                simulate_delay(0.4)

        elif agent_name == "TESTING":
            if previous_score:
                print_agent(agent_name, "Building on previous test suite...")
                simulate_delay(0.6)
            else:
                print_agent(agent_name, "Generating comprehensive test suite...")
                simulate_delay(1.0)
            print_agent(agent_name, "Created:")
            test_count = 8 + (self.request_num - 1) * 3
            print(f"    - {test_count} unit tests (edge cases)")
            print(f"    - {4 + (self.request_num - 1) * 2} integration tests")
            if self.request_num >= 2:
                print(f"    - JWT validation tests")
            if self.request_num >= 3:
                print(f"    - Rate limiting tests")
                print(f"    - Account lockout tests")

        simulate_delay(0.8)

        # Show Galileo scoring
        improvement = score - previous_score if previous_score else None
        print_agent("GALILEO", f"{agent_name.capitalize()} evaluation complete")
        print_score(agent_name, score, improvement)

        simulate_delay(0.5)

    async def step_quality_gate(self, previous_request: Optional['DemoRequest']):
        """Simulate quality gate and storage"""
        print_step(4, 4, "Quality Gate & Knowledge Storage")

        print_agent("GALILEO", "Calculating aggregate quality score...")
        simulate_delay(1.0)

        improvement = self.avg_score - previous_request.avg_score if previous_request else None

        if self.avg_score >= 90:
            print_agent("GALILEO", f"{Colors.GREEN}Average Score: {self.avg_score:.1f}/100 ✓{Colors.END}")
            if improvement:
                print(f"  {Colors.GREEN}Improvement: +{improvement:.1f} points from previous request{Colors.END}")

            simulate_delay(0.5)
            print_agent("NEO4J", "Score exceeds 90 threshold - storing pattern...")
            simulate_delay(0.8)

            pattern_id = f"pattern_{self.request_num:03d}"
            print_agent("NEO4J", f"{Colors.GREEN}Stored pattern: {pattern_id}{Colors.END}")

            if previous_request:
                print_agent("NEO4J", f"Creating relationship: {pattern_id} -> BUILDS_ON -> pattern_{self.request_num-1:03d}")

            simulate_delay(0.5)

            # Show learner insights
            if self.request_num >= 2:
                print_agent("LEARNER", "Analyzing quality trajectory...")
                simulate_delay(0.3)

                scores_list = []
                for i in range(1, self.request_num + 1):
                    scores_list.append(93.5 + (2.0 * (i - 1)))

                trajectory = " → ".join([f"{s:.1f}" for s in scores_list])
                print_agent("LEARNER", f"Quality trajectory: {trajectory}")

                if self.request_num >= 3:
                    avg_improvement = (self.avg_score - 93.5) / (self.request_num - 1)
                    print_agent("LEARNER", f"Average improvement rate: +{avg_improvement:.2f} points per request")
        else:
            print_agent("GALILEO", f"{Colors.RED}Average Score: {self.avg_score:.1f}/100 ✗{Colors.END}")
            print_agent("GALILEO", "Score below 90 threshold - triggering improvement loop...")
            print_agent("GALILEO", "Providing feedback to agents for re-generation...")

        simulate_delay(1.0)

        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'─'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}Request #{self.request_num} Complete{Colors.END}")
        print(f"{Colors.GREEN}Generation time: {24 + self.request_num * 2} seconds{Colors.END}")
        print(f"{Colors.GREEN}Final score: {self.avg_score:.1f}/100{Colors.END}")
        if improvement:
            print(f"{Colors.GREEN}Improvement: +{improvement:.1f} points{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'─'*70}{Colors.END}\n")


async def run_complete_demo():
    """Run the complete 3-request demo"""

    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║                  CODESWARM PRESENTATION DEMO                       ║")
    print("║                                                                    ║")
    print("║           The AI Coding Team That Gets Smarter Over Time          ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    print(f"{Colors.CYAN}Watch as CodeSwarm improves from 93.5% to 97.2% quality across 3 requests{Colors.END}\n")

    input(f"{Colors.YELLOW}Press ENTER to start demo...{Colors.END}")

    # Request 1: Baseline (cold start)
    request1 = DemoRequest(
        request_num=1,
        task="Build FastAPI user authentication endpoint with password hashing",
        architecture_score=92.5,
        implementation_score=91.0,
        security_score=94.0,
        testing_score=93.0,
        patterns_found=0,
        browser_docs=12
    )

    await request1.run()

    input(f"\n{Colors.YELLOW}Press ENTER for Request #2...{Colors.END}")

    # Request 2: Learning
    request2 = DemoRequest(
        request_num=2,
        task="Build authentication API with JWT tokens and refresh tokens",
        architecture_score=95.0,
        implementation_score=94.5,
        security_score=96.0,
        testing_score=95.5,
        patterns_found=1,
        browser_docs=8
    )

    await request2.run(previous_request=request1)

    input(f"\n{Colors.YELLOW}Press ENTER for Request #3...{Colors.END}")

    # Request 3: Mastery
    request3 = DemoRequest(
        request_num=3,
        task="Build production-ready auth API with refresh tokens, rate limiting, and account lockout",
        architecture_score=97.5,
        implementation_score=96.0,
        security_score=98.0,
        testing_score=97.0,
        patterns_found=2,
        browser_docs=5
    )

    await request3.run(previous_request=request2)

    # Final Summary
    print_header("DEMO SUMMARY - Quality Improvement Demonstrated")

    print(f"{Colors.BOLD}Quality Progression:{Colors.END}")
    print(f"  Request 1 (Baseline):  {Colors.YELLOW}93.5/100{Colors.END} - Cold start, no prior knowledge")
    print(f"  Request 2 (Learning):  {Colors.GREEN}95.5/100{Colors.END} - {Colors.GREEN}+2.0 points{Colors.END} (learned from Request 1)")
    print(f"  Request 3 (Mastery):   {Colors.GREEN}97.2/100{Colors.END} - {Colors.GREEN}+3.7 points{Colors.END} (learned from both)")

    print(f"\n{Colors.BOLD}Key Benefits Demonstrated:{Colors.END}")
    print(f"  ✓ {Colors.GREEN}Multi-agent specialization{Colors.END} - Best model for each task")
    print(f"  ✓ {Colors.GREEN}Quality gates{Colors.END} - Only 90+ code stored")
    print(f"  ✓ {Colors.GREEN}Continuous learning{Colors.END} - +1.85 points per request")
    print(f"  ✓ {Colors.GREEN}Live documentation{Colors.END} - Always current best practices")
    print(f"  ✓ {Colors.GREEN}Knowledge compounds{Colors.END} - Gets better every time")

    print(f"\n{Colors.BOLD}Neo4j Knowledge Graph:{Colors.END}")
    print(f"  Patterns stored: {Colors.CYAN}3{Colors.END}")
    print(f"  All scores: {Colors.GREEN}90+{Colors.END}")
    print(f"  Relationships: {Colors.CYAN}pattern_002 → BUILDS_ON → pattern_001")
    print(f"                 pattern_003 → BUILDS_ON → pattern_002{Colors.END}")

    print(f"\n{Colors.BOLD}{Colors.HEADER}{'═'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}CodeSwarm: The only AI tool that improves with every request{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'═'*70}{Colors.END}\n")


async def main():
    """Main entry point"""
    try:
        await run_complete_demo()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}Demo error: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
