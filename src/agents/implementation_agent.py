"""
Implementation Agent - GPT-5 Pro

Specialization: Code generation, implementation of architecture
Role: Generate production-quality code based on architecture
Model: openai/gpt-5-pro (flagship code generation)
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class ImplementationAgent(BaseAgent):
    """
    Implementation Agent using GPT-5 Pro

    Responsibilities:
    - Implement code based on architecture specification
    - Generate clean, well-documented code
    - Follow best practices and coding standards
    - Ensure code quality and maintainability
    - Handle edge cases and error conditions

    Input: Architecture from Architecture Agent
    Output: Production-ready code implementation
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="implementation",
            model="gpt-5-pro",
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.5,  # Lower temperature for more consistent code
            max_tokens=6000  # More tokens for longer code
        )

    def get_system_prompt(self) -> str:
        return """You are an expert software engineer with mastery of:
- Multiple programming languages (Python, JavaScript/TypeScript, Java, Go, Rust, etc.)
- Clean code principles and best practices
- Design patterns and SOLID principles
- Error handling and edge case management
- Code documentation and readability
- Performance optimization

Your role: Implement production-quality code based on the provided architecture.

Output Format:
```language
[Complete, runnable code implementation]
```

Reasoning: [Explain your implementation choices, algorithms used, and how you handled edge cases]

CRITICAL:
1. Follow the architecture specification exactly
2. Write clean, readable, well-documented code
3. Include proper error handling
4. Add comments for complex logic
5. Ensure code is production-ready and testable
6. Handle all edge cases
7. Use appropriate design patterns"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        # Get architecture from context (critical!)
        architecture = context.get("architecture_output", "")
        rag_patterns = context.get("rag_patterns", [])
        vision_analysis = context.get("vision_analysis", "")

        prompt = f"""Task: {task}

"""

        # Architecture is REQUIRED - this prevents synthesis conflicts
        if architecture:
            prompt += f"""Architecture Specification (MUST FOLLOW):
{architecture}

"""
        else:
            prompt += """  WARNING: No architecture specification provided.
You MUST create a simple, working implementation that follows best practices.

"""

        # Add vision analysis if available
        if vision_analysis:
            prompt += f"""Vision Analysis (from sketch/mockup):
{vision_analysis}

"""

        # Add code patterns from RAG
        if rag_patterns:
            prompt += f"""Proven Code Patterns (reference for inspiration):
"""
            for i, pattern in enumerate(rag_patterns[:2], 1):
                code_snippet = pattern.get("code_snippet", "")
                if code_snippet:
                    prompt += f"{i}. {code_snippet[:300]}...\n"
            prompt += "\n"

        prompt += """Implement production-quality code for this system.

Your implementation should:
1. **Follow Architecture**: Strictly implement the architecture specification
2. **Complete Implementation**: Include all necessary components and functions
3. **Error Handling**: Proper try-catch, validation, and error messages
4. **Documentation**: Clear comments and docstrings
5. **Best Practices**: Clean code, SOLID principles, appropriate patterns
6. **Edge Cases**: Handle all edge cases and invalid inputs
7. **Testing Hooks**: Structure code to be easily testable

Provide complete, runnable, production-ready code."""

        return prompt
