"""
Base Agent for CodeSwarm
All specialized agents inherit from this base class
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .model_selector import ModelSelector, TaskType


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
    parsed_files: Optional[Dict[str, str]] = None  # For Implementation agent: filename -> content mapping


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
        self._last_validation_error = None  # For validation hook
        self._parsed_files = None  # For file validation

        print(f"[{self.name.upper()}]  Agent initialized (model: {model})")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass

    @abstractmethod
    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build the user prompt for this specific task"""
        pass

    async def _validate_output(
        self,
        code: str,
        reasoning: str,
        context: Dict[str, Any],
        task: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validation hook for subclasses to add custom validation.

        Subclasses can override this to validate output before creating AgentOutput.
        If validation fails, return error dict. If passes, return None.

        Args:
            code: Generated code
            reasoning: Generated reasoning
            context: Execution context
            task: User's task

        Returns:
            None if validation passes, or error dict if validation fails:
            {
                "message": "Human-readable error message",
                "missing_files": [...],  # Optional: specific error details
                "parsing_error": "...",  # Optional: specific error details
            }
        """
        # Base implementation: no validation
        return None

    async def execute(
        self,
        task: str,
        context: Dict[str, Any],
        quality_threshold: float = 90.0,
        max_iterations: int = 3,
        enable_model_fallback: bool = True
    ) -> AgentOutput:
        """
        Execute the agent with quality improvement loop and model fallback

        Args:
            task: User's task description
            context: Shared context (RAG patterns, previous agent outputs, etc.)
            quality_threshold: Minimum Galileo score to accept (default 90.0)
            max_iterations: Max improvement iterations per model (default 3)
            enable_model_fallback: Allow switching models if threshold not met (default True)

        Returns:
            AgentOutput with code, reasoning, and quality metrics
        """
        print(f"\n[{self.name.upper()}]  Starting execution...")

        # Detect task type for intelligent model selection
        task_type = ModelSelector.detect_task_type(task, context)
        print(f"[{self.name.upper()}]  📊 Task type detected: {task_type.value}")
        print(f"[{self.name.upper()}]  🤖 Using model: {self.model}")

        iteration = 0
        best_output = None
        best_score = 0.0
        first_iteration_score = 0.0
        original_model = self.model
        model_attempt_number = 1  # Track which model we're on
        max_model_attempts = 3  # Try up to 3 different models
        last_code = ""  # Track last code for improvement prompt (even if validation fails)
        last_reasoning = ""  # Track last reasoning for improvement prompt

        while iteration < max_iterations and model_attempt_number <= max_model_attempts:
            iteration += 1
            print(f"[{self.name.upper()}]  Iteration {iteration}/{max_iterations}")

            start_time = time.time()

            # Build prompt
            if iteration == 1:
                user_prompt = self.build_user_prompt(task, context)
            else:
                # Improvement iteration - add Galileo feedback
                user_prompt = self._build_improvement_prompt(
                    task, context, best_output, best_score, last_code, last_reasoning
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

            # Store for improvement prompt (even if validation fails)
            last_code = code
            last_reasoning = reasoning

            # CRITICAL VALIDATION: Check for empty outputs
            if not code or not code.strip():
                print(f"[{self.name.upper()}]  ❌ ERROR: Empty code output detected!")
                print(f"[{self.name.upper()}]  Response length: {len(content)} chars")
                print(f"[{self.name.upper()}]  Response preview: {content[:500]}...")

                # If this is the last iteration with fallback enabled, create temp output for fallback
                if iteration >= max_iterations and enable_model_fallback:
                    print(f"[{self.name.upper()}]  ⚠️  Empty code on last iteration - triggering model fallback")
                    # Create minimal temp output to trigger fallback
                    temp_output = AgentOutput(
                        agent_name=self.name,
                        code="",  # Empty code
                        reasoning="",
                        confidence=0.0,  # Zero confidence
                        latency_ms=latency_ms,
                        model_used=self.model,
                        iterations=iteration,
                        parsed_files=None
                    )
                    best_output = temp_output
                    best_score = 0.0
                    # Break to fallback logic
                    break
                elif iteration >= max_iterations:
                    # No fallback enabled, raise error
                    raise ValueError(f"{self.name} agent produced empty code after {max_iterations} iterations")

                # Otherwise, continue to next iteration
                print(f"[{self.name.upper()}]  Retrying in next iteration...")
                continue

            if not reasoning or not reasoning.strip():
                print(f"[{self.name.upper()}]  ⚠️  WARNING: Empty reasoning (code is present, continuing)")

            # HOOK: Allow subclasses to validate output before creating AgentOutput
            validation_result = await self._validate_output(code, reasoning, context, task)

            if validation_result is not None:
                # Validation failed - store error and retry
                if isinstance(validation_result, dict):
                    self._last_validation_error = validation_result
                else:
                    self._last_validation_error = {"error": str(validation_result)}

                print(f"[{self.name.upper()}]  ❌ Validation failed: {validation_result.get('message', validation_result)}")

                # Check if we've exhausted retries for this model
                if iteration >= max_iterations:
                    print(f"[{self.name.upper()}]  ⚠️  Max iterations reached with validation failures")
                    # Create a temporary output for potential fallback evaluation
                    # Even though validation failed, we need this for Galileo/fallback logic
                    temp_output = AgentOutput(
                        agent_name=self.name,
                        code=code,
                        reasoning=reasoning,
                        confidence=0.50,  # Low confidence due to validation failure
                        latency_ms=latency_ms,
                        model_used=self.model,
                        iterations=iteration,
                        parsed_files=None  # No parsed files since validation failed
                    )
                    # Store as best_output so fallback logic can access it
                    if not best_output or iteration == max_iterations:
                        best_output = temp_output
                    # Break from validation retry and let fallback logic decide
                    break
                else:
                    print(f"[{self.name.upper()}]  🔄 Retrying with validation feedback...")
                    continue

            # Validation passed or no validation - create output
            output = AgentOutput(
                agent_name=self.name,
                code=code,
                reasoning=reasoning,
                confidence=0.85,  # Base confidence
                latency_ms=latency_ms,
                model_used=self.model,
                iterations=iteration,
                parsed_files=getattr(self, '_parsed_files', None)  # Get from validation hook
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

                    # Track first iteration score for improvement calculation
                    if iteration == 1:
                        first_iteration_score = score

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

            # Check if we've exhausted iterations for this model
            if iteration >= max_iterations:
                # Max iterations reached for current model
                print(f"[{self.name.upper()}] ⏸  Max iterations reached. Best score: {best_score:.1f}/100")

                # Check if validation failed (no parsed_files means validation never passed)
                validation_failed = (
                    best_output and
                    hasattr(best_output, 'parsed_files') and
                    best_output.parsed_files is None
                )

                if validation_failed:
                    print(f"[{self.name.upper()}]  ⚠️  Validation failed all iterations - triggering model fallback")

                # Check if we should try fallback model
                # Trigger fallback if: (1) score below threshold OR (2) validation failed
                if enable_model_fallback and (best_score < quality_threshold or validation_failed):
                    score_improvement = best_score - first_iteration_score

                    # Determine if fallback should happen
                    should_fallback = ModelSelector.should_fallback(
                        iterations_completed=iteration,
                        max_iterations=max_iterations,
                        best_score=best_score,
                        quality_threshold=quality_threshold,
                        score_improvement=score_improvement
                    )

                    if should_fallback:
                        # Get next model to try
                        next_model = ModelSelector.get_next_model(
                            current_model=self.model,
                            task_type=task_type,
                            attempts_with_current=iteration
                        )

                        if next_model and next_model != self.model:
                            # Print fallback rationale
                            rationale = ModelSelector.get_fallback_rationale(
                                current_model=self.model,
                                next_model=next_model,
                                task_type=task_type,
                                best_score=best_score,
                                quality_threshold=quality_threshold
                            )
                            print(rationale)

                            # Switch to fallback model
                            self.model = next_model
                            model_attempt_number += 1

                            # Reset iteration counter for new model
                            iteration = 0
                            first_iteration_score = 0.0

                            print(f"[{self.name.upper()}]  🔄 Starting attempt #{model_attempt_number} with {next_model}...")
                            print(f"[{self.name.upper()}]  Resetting iteration counter (0/{max_iterations})")

                            # Continue loop with new model (don't return yet!)
                            continue

                # No more fallbacks or fallback not needed - return best attempt
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
        previous_output: Optional[AgentOutput],
        previous_score: float,
        last_code: str = "",
        last_reasoning: str = ""
    ) -> str:
        """Build prompt for improvement iteration"""
        base_prompt = self.build_user_prompt(task, context)

        # Use previous_output if available (Galileo evaluated), otherwise use last_code (validation failed)
        code_preview = previous_output.code[:500] if previous_output else last_code[:500]

        improvement = f"""
PREVIOUS ATTEMPT (Score: {previous_score:.1f}/100):
```
{code_preview}...
```

Your previous code scored {previous_score:.1f}/100, which is below the quality threshold of 90.
"""

        # Add validation error feedback if present
        if hasattr(self, '_last_validation_error') and self._last_validation_error:
            error = self._last_validation_error

            if "missing_files" in error:
                missing_files = error["missing_files"]
                improvement += f"""

❌ VALIDATION ERROR:
Your code references {len(missing_files)} files that you did not create!

Missing files:
"""
                for source_file, missing_import in missing_files[:5]:
                    improvement += f"  - {source_file} imports '{missing_import}' (FILE NOT FOUND)\n"

                if len(missing_files) > 5:
                    improvement += f"  ... and {len(missing_files) - 5} more\n"

                improvement += """
CRITICAL FIX REQUIRED:
1. Generate ALL files that are referenced in imports, links, or requires
2. If you import "./styles.css", you MUST create "# File: styles.css"
3. Do NOT reference files you haven't created
4. Every import/require MUST point to an actual file you generated

"""

            elif "parsing_error" in error:
                improvement += f"""

❌ PARSING ERROR:
Your code could not be parsed into files!

Error: {error["parsing_error"]}

FIX REQUIRED:
1. Use proper file markers: "# File: filename.ext" or "// File: filename.ext"
2. Each file MUST start with a file marker
3. Follow the format shown in the system prompt exactly

"""

            elif "missing_required_files" in error:
                missing_required = error["missing_required_files"]
                improvement += f"""

❌ INCOMPLETE PROJECT:
Your code is missing {len(missing_required)} REQUIRED files!

The project won't run without these critical files:
"""
                for required_file in missing_required:
                    improvement += f"  - {required_file}\n"

                improvement += """
CRITICAL FIX REQUIRED:
1. You generated only config/setup files without actual application code
2. Generate ALL required files for a complete, working project
3. For Next.js: Must include app/page.tsx AND app/layout.tsx (or pages/index.tsx)
4. For Vite: Must include index.html AND src/main.tsx
5. For Express: Must include server.js or index.js
6. Include ALL component files, not just package.json/config

"""

        improvement += f"""
IMPROVEMENT REQUIRED:
1. Review your previous attempt and errors above
2. Fix all validation issues first
3. Identify quality issues (correctness, completeness, security, performance)
4. Generate IMPROVED code that addresses all issues
5. Ensure score >= 90/100

{base_prompt}
"""
        return improvement
