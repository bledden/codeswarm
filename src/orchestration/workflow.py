"""
CodeSwarm LangGraph Workflow

Sequential stages with safe parallel execution:
1. RAG Retrieval (sequential)
2. Vision Analysis (conditional, sequential)
3. Architecture Agent (sequential - defines structure)
4. Implementation + Security (parallel - both see architecture)
5. Testing Agent (sequential - sees all previous outputs)
6. Synthesis (sequential)
"""

import asyncio
from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, END


class CodeSwarmState(TypedDict):
    """
    Shared state across all agents (collective blackboard pattern)

    All agents read from and write to this shared state.
    This prevents synthesis conflicts by ensuring agents have complete context.
    """
    # User Input
    task: str
    image_path: Optional[str]
    user_id: str

    # Context (from RAG, Browser Use, Vision)
    rag_patterns: List[Dict[str, Any]]
    browsed_docs: Dict[str, str]
    vision_analysis: Optional[str]

    # Agent Outputs (sequential stages)
    architecture_output: Optional[str]
    implementation_output: Optional[str]
    security_output: Optional[str]
    testing_output: Optional[str]

    # Evaluation & Learning
    galileo_scores: Dict[str, float]
    improvement_iterations: int
    final_code: Optional[str]
    synthesis_complete: bool


class CodeSwarmWorkflow:
    """
    LangGraph workflow orchestrating CodeSwarm agents

    Flow:
    User Request → RAG → Vision? → Architecture → [Impl + Security] → Testing → Synthesis
    """

    def __init__(
        self,
        architecture_agent,
        implementation_agent,
        security_agent,
        testing_agent,
        vision_agent,
        rag_client=None,
        browser_client=None,
        learner=None
    ):
        """Initialize workflow with all agents and components"""
        self.architecture_agent = architecture_agent
        self.implementation_agent = implementation_agent
        self.security_agent = security_agent
        self.testing_agent = testing_agent
        self.vision_agent = vision_agent

        self.rag_client = rag_client
        self.browser_client = browser_client
        self.learner = learner

        # Build LangGraph workflow
        self.graph = self._build_graph()

        print("[WORKFLOW]  CodeSwarm workflow initialized")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        workflow = StateGraph(CodeSwarmState)

        # Add nodes
        workflow.add_node("rag_retrieve", self._rag_retrieve_stage)
        workflow.add_node("vision_analyze", self._vision_analyze_stage)
        workflow.add_node("architecture", self._architecture_stage)
        workflow.add_node("parallel_impl_security", self._parallel_impl_security_stage)
        workflow.add_node("testing", self._testing_stage)
        workflow.add_node("synthesis", self._synthesis_stage)

        # Define edges (sequential flow with conditional vision)
        workflow.set_entry_point("rag_retrieve")

        # RAG → Vision (conditional)
        workflow.add_conditional_edges(
            "rag_retrieve",
            self._should_use_vision,
            {
                "vision": "vision_analyze",
                "skip_vision": "architecture"
            }
        )

        # Vision → Architecture
        workflow.add_edge("vision_analyze", "architecture")

        # Architecture → Parallel (Implementation + Security)
        workflow.add_edge("architecture", "parallel_impl_security")

        # Parallel → Testing
        workflow.add_edge("parallel_impl_security", "testing")

        # Testing → Synthesis
        workflow.add_edge("testing", "synthesis")

        # Synthesis → END
        workflow.add_edge("synthesis", END)

        return workflow.compile()

    async def run(self, task: str, image_path: Optional[str] = None, user_id: str = "default") -> Dict[str, Any]:
        """
        Run the complete CodeSwarm workflow

        Args:
            task: User's task description
            image_path: Optional path to sketch/mockup image
            user_id: User identifier

        Returns:
            Dict with final_code, all agent outputs, and metrics
        """
        print(f"\n{'='*60}")
        print(f" CodeSwarm Starting")
        print(f"{'='*60}")
        print(f"Task: {task[:100]}...")
        if image_path:
            print(f"Image: {image_path}")
        print(f"{'='*60}\n")

        # Initialize state
        initial_state: CodeSwarmState = {
            "task": task,
            "image_path": image_path,
            "user_id": user_id,
            "rag_patterns": [],
            "browsed_docs": {},
            "vision_analysis": None,
            "architecture_output": None,
            "implementation_output": None,
            "security_output": None,
            "testing_output": None,
            "galileo_scores": {},
            "improvement_iterations": 0,
            "final_code": None,
            "synthesis_complete": False
        }

        # Run workflow
        final_state = await self.graph.ainvoke(initial_state)

        # Learn from outcome (if learner available)
        if self.learner:
            agent_outputs = {
                "architecture": {
                    "code": final_state["architecture_output"],
                    "galileo_score": final_state["galileo_scores"].get("architecture", 85.0),
                    "latency_ms": 0,
                    "iterations": 1
                },
                "implementation": {
                    "code": final_state["implementation_output"],
                    "galileo_score": final_state["galileo_scores"].get("implementation", 85.0),
                    "latency_ms": 0,
                    "iterations": 1
                },
                "security": {
                    "code": final_state["security_output"],
                    "galileo_score": final_state["galileo_scores"].get("security", 85.0),
                    "latency_ms": 0,
                    "iterations": 1
                },
                "testing": {
                    "code": final_state["testing_output"],
                    "galileo_score": final_state["galileo_scores"].get("testing", 85.0),
                    "latency_ms": 0,
                    "iterations": 1
                }
            }

            self.learner.learn_from_outcome(
                agent_outputs=agent_outputs,
                task=task,
                was_successful=final_state["synthesis_complete"]
            )

        print(f"\n{'='*60}")
        print(f" CodeSwarm Complete")
        print(f"{'='*60}\n")

        return final_state

    # ==================== Stage Implementations ====================

    async def _rag_retrieve_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 1: Retrieve relevant patterns from Neo4j RAG"""
        print("\n[STAGE 1]  RAG Retrieval")

        if self.rag_client:
            try:
                patterns = await self.rag_client.retrieve(state["task"])
                state["rag_patterns"] = patterns
                print(f"[RAG]  Retrieved {len(patterns)} relevant patterns")
            except Exception as e:
                print(f"[RAG]   Failed: {e}")
                state["rag_patterns"] = []
        else:
            print("[RAG]   No RAG client available")
            state["rag_patterns"] = []

        return state

    async def _vision_analyze_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 2 (conditional): Analyze image with vision model"""
        print("\n[STAGE 2]   Vision Analysis")

        if state["image_path"]:
            try:
                context = {
                    "rag_patterns": state["rag_patterns"],
                    "browsed_docs": state["browsed_docs"]
                }

                output = await self.vision_agent.analyze_image(
                    image_path=state["image_path"],
                    task=state["task"],
                    context=context
                )

                state["vision_analysis"] = output.code
                state["galileo_scores"]["vision"] = output.galileo_score or 85.0
                print(f"[VISION]  Analysis complete")
            except Exception as e:
                print(f"[VISION]  Failed: {e}")
                state["vision_analysis"] = None
        else:
            print("[VISION] ⏭  Skipped (no image)")

        return state

    async def _architecture_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 3: Architecture design (sequential - defines structure)"""
        print("\n[STAGE 3]   Architecture Design")

        context = {
            "rag_patterns": state["rag_patterns"],
            "browsed_docs": state["browsed_docs"],
            "vision_analysis": state["vision_analysis"]
        }

        try:
            output = await self.architecture_agent.execute(
                task=state["task"],
                context=context,
                quality_threshold=90.0,
                max_iterations=3
            )

            state["architecture_output"] = output.code
            state["galileo_scores"]["architecture"] = output.galileo_score or 85.0
            state["improvement_iterations"] += output.iterations

            print(f"[ARCHITECTURE]  Complete (score: {output.galileo_score:.1f}/100)")
        except Exception as e:
            print(f"[ARCHITECTURE]  Failed: {e}")
            state["architecture_output"] = f"Error: {e}"

        return state

    async def _parallel_impl_security_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 4: Implementation + Security (parallel - both see architecture)"""
        print("\n[STAGE 4]  Parallel: Implementation + Security")

        # Build context with architecture (CRITICAL - prevents synthesis conflicts)
        context = {
            "rag_patterns": state["rag_patterns"],
            "browsed_docs": state["browsed_docs"],
            "vision_analysis": state["vision_analysis"],
            "architecture_output": state["architecture_output"]  # Both agents see this!
        }

        # Run implementation and security in parallel
        try:
            impl_task = self.implementation_agent.execute(
                task=state["task"],
                context=context,
                quality_threshold=90.0,
                max_iterations=3
            )

            security_task = self.security_agent.execute(
                task=state["task"],
                context=context,
                quality_threshold=90.0,
                max_iterations=3
            )

            # Wait for both to complete
            impl_output, security_output = await asyncio.gather(impl_task, security_task)

            state["implementation_output"] = impl_output.code
            state["security_output"] = security_output.code
            state["galileo_scores"]["implementation"] = impl_output.galileo_score or 85.0
            state["galileo_scores"]["security"] = security_output.galileo_score or 85.0
            state["improvement_iterations"] += impl_output.iterations + security_output.iterations

            print(f"[IMPLEMENTATION]  Complete (score: {impl_output.galileo_score:.1f}/100)")
            print(f"[SECURITY]  Complete (score: {security_output.galileo_score:.1f}/100)")
        except Exception as e:
            print(f"[PARALLEL]  Failed: {e}")
            state["implementation_output"] = f"Error: {e}"
            state["security_output"] = f"Error: {e}"

        return state

    async def _testing_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 5: Testing (sequential - sees all previous outputs)"""
        print("\n[STAGE 5]  Test Generation")

        # Context includes ALL previous outputs
        context = {
            "rag_patterns": state["rag_patterns"],
            "browsed_docs": state["browsed_docs"],
            "vision_analysis": state["vision_analysis"],
            "architecture_output": state["architecture_output"],
            "implementation_output": state["implementation_output"],
            "security_output": state["security_output"]
        }

        try:
            output = await self.testing_agent.execute(
                task=state["task"],
                context=context,
                quality_threshold=90.0,
                max_iterations=3
            )

            state["testing_output"] = output.code
            state["galileo_scores"]["testing"] = output.galileo_score or 85.0
            state["improvement_iterations"] += output.iterations

            print(f"[TESTING]  Complete (score: {output.galileo_score:.1f}/100)")
        except Exception as e:
            print(f"[TESTING]  Failed: {e}")
            state["testing_output"] = f"Error: {e}"

        return state

    async def _synthesis_stage(self, state: CodeSwarmState) -> CodeSwarmState:
        """Stage 6: Synthesize final output"""
        print("\n[STAGE 6]  Synthesis")

        # Combine all outputs
        final_code = f"""# CodeSwarm Generated Code
# Task: {state['task']}

# ========================================
# ARCHITECTURE
# ========================================
{state['architecture_output']}

# ========================================
# IMPLEMENTATION
# ========================================
{state['implementation_output']}

# ========================================
# SECURITY MEASURES
# ========================================
{state['security_output']}

# ========================================
# TESTS
# ========================================
{state['testing_output']}
"""

        state["final_code"] = final_code
        state["synthesis_complete"] = True

        # Print summary
        avg_score = sum(state["galileo_scores"].values()) / len(state["galileo_scores"]) if state["galileo_scores"] else 85.0
        print(f"\n[SYNTHESIS]  Complete")
        print(f"[SYNTHESIS]    Average Score: {avg_score:.1f}/100")
        print(f"[SYNTHESIS]    Total Iterations: {state['improvement_iterations']}")

        return state

    # ==================== Conditional Logic ====================

    def _should_use_vision(self, state: CodeSwarmState) -> str:
        """Determine if vision analysis is needed"""
        if self.vision_agent.needs_vision(state["task"], state):
            return "vision"
        return "skip_vision"
