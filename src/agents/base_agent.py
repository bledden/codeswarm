"""
Base Agent for CodeSwarm
All specialized agents inherit from this base class
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AgentOutput:
    """Standardized output from any agent"""
    agent_name: str
    code: str
    reasoning: str
    confidence: float  # 0-1 scale
    latency_ms: int
    model_used: str
    galileo_score: Optional[float] = None  # Set by evaluator
    iterations: int = 1  # How many improvement iterations


class BaseAgent(ABC):
    """
    Base class for all CodeSwarm agents

    Each agent:
    1. Uses a specific model (Claude Sonnet 4.5, GPT-5 Pro, etc.)
    2. Has a specialized role (architecture, implementation, security, testing)
    3. Can iterate to improve quality (Galileo feedback loop)
    4. Outputs standardized AgentOutput format
    """

    def __init__(
        self,
        name: str,
        model: str,
        openrouter_client,
        evaluator = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """Initialize base agent

        Args:
            name: Agent name (e.g., "architecture", "implementation")
            model: Model to use (e.g., "claude-sonnet-4.5", "gpt-5-pro")
            openrouter_client: OpenRouter client instance
            evaluator: Optional Galileo evaluator for quality scoring
            temperature: Model temperature (default 0.7)
            max_tokens: Max tokens to generate (default 4000)
        """
        self.name = name
        self.model = model
        self.client = openrouter_client
        self.evaluator = evaluator
        self.temperature = temperature
        self.max_tokens = max_tokens

        print(f"[{self.name.upper()}]  Agent initialized (model: {model})")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass

    @abstractmethod
    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build the user prompt for this specific task"""
        pass

    async def execute(
        self,
        task: str,
        context: Dict[str, Any],
        quality_threshold: float = 90.0,
        max_iterations: int = 3
    ) -> AgentOutput:
        """
        Execute the agent with quality improvement loop

        Args:
            task: User's task description
            context: Shared context (RAG patterns, previous agent outputs, etc.)
            quality_threshold: Minimum Galileo score to accept (default 90.0)
            max_iterations: Max improvement iterations (default 3)

        Returns:
            AgentOutput with code, reasoning, and quality metrics
        """
        print(f"\n[{self.name.upper()}]  Starting execution...")

        iteration = 0
        best_output = None
        best_score = 0.0

        while iteration < max_iterations:
            iteration += 1
            print(f"[{self.name.upper()}]  Iteration {iteration}/{max_iterations}")

            start_time = time.time()

            # Build prompt
            if iteration == 1:
                user_prompt = self.build_user_prompt(task, context)
            else:
                # Improvement iteration - add Galileo feedback
                user_prompt = self._build_improvement_prompt(
                    task, context, best_output, best_score
                )

            # Call model
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.client.complete(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse response
            content = response["choices"][0]["message"]["content"]
            code, reasoning = self._parse_response(content)

            # Create output
            output = AgentOutput(
                agent_name=self.name,
                code=code,
                reasoning=reasoning,
                confidence=0.85,  # Base confidence
                latency_ms=latency_ms,
                model_used=self.model,
                iterations=iteration
            )

            # Evaluate with Galileo if available
            if self.evaluator:
                try:
                    # Get token counts from response
                    usage = response.get("usage", {})
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)

                    score = await self.evaluator.evaluate(
                        task=task,
                        output=code,
                        agent=self.name,
                        model=self.model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=latency_ms
                    )
                    output.galileo_score = score
                    print(f"[{self.name.upper()}]  Galileo score: {score:.1f}/100")

                    # Update best if better
                    if score > best_score:
                        best_score = score
                        best_output = output

                    # Check quality threshold
                    if score >= quality_threshold:
                        print(f"[{self.name.upper()}]  Quality threshold met ({score:.1f} >= {quality_threshold})")
                        return output

                except Exception as e:
                    print(f"[{self.name.upper()}]   Galileo evaluation failed: {e}")
                    output.galileo_score = 85.0  # Default score
            else:
                # No evaluator - accept after 1 iteration
                output.galileo_score = 85.0
                return output

        # Max iterations reached - return best attempt
        print(f"[{self.name.upper()}] ⏸  Max iterations reached. Best score: {best_score:.1f}/100")
        return best_output if best_output else output

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        Parse agent response into code and reasoning

        Expected format:
        ```language
        code here
        ```

        Reasoning: explanation here
        """
        code = ""
        reasoning = ""

        # Extract code blocks
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                code_block = parts[1]
                # Remove language identifier (e.g., "python\n")
                lines = code_block.split("\n")
                if lines and lines[0].strip() in ["python", "javascript", "typescript", "java", "go", "rust"]:
                    code = "\n".join(lines[1:])
                else:
                    code = code_block

            # Get reasoning (text after code block)
            if len(parts) >= 3:
                reasoning = parts[2].strip()
        else:
            # No code block - entire content is reasoning
            reasoning = content

        return code.strip(), reasoning.strip()

    def _build_improvement_prompt(
        self,
        task: str,
        context: Dict[str, Any],
        previous_output: AgentOutput,
        previous_score: float
    ) -> str:
        """Build prompt for improvement iteration"""
        base_prompt = self.build_user_prompt(task, context)

        improvement = f"""
PREVIOUS ATTEMPT (Score: {previous_score:.1f}/100):
```
{previous_output.code[:500]}...
```

Your previous code scored {previous_score:.1f}/100, which is below the quality threshold of 90.

IMPROVEMENT REQUIRED:
1. Review your previous attempt
2. Identify quality issues (correctness, completeness, security, performance)
3. Generate IMPROVED code that addresses all issues
4. Ensure score >= 90/100

{base_prompt}
"""
        return improvement
