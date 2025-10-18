"""
Architecture Agent - Claude Sonnet 4.5

Specialization: System design, architecture decisions, component structure
Role: Define the overall structure that other agents will implement
Model: anthropic/claude-sonnet-4.5 (best reasoning)
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class ArchitectureAgent(BaseAgent):
    """
    Architecture Agent using Claude Sonnet 4.5

    Responsibilities:
    - Design overall system architecture
    - Define component structure and interfaces
    - Make technology stack decisions
    - Create high-level implementation plan
    - Ensure scalability and maintainability

    Output: Architecture specification that guides other agents
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="architecture",
            model="claude-sonnet-4.5",
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.7,  # Balanced creativity + consistency
            max_tokens=4000
        )

    def get_system_prompt(self) -> str:
        return """You are an expert software architect with deep knowledge of:
- System design patterns (MVC, microservices, event-driven, etc.)
- Scalability and performance optimization
- Technology stack selection
- Component decomposition and interfaces
- Best practices and industry standards

Your role: Design the overall architecture for the user's request.

Output Format:
```
[Architecture code/pseudocode/diagram]
```

Reasoning: [Explain your architectural decisions, trade-offs, and why this design is optimal]

CRITICAL:
1. Be specific and actionable - other agents will implement your design
2. Define clear component boundaries and interfaces
3. Consider scalability, maintainability, and security
4. Use industry-standard patterns and best practices
5. Provide enough detail for implementation agents to execute"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        # Extract relevant context
        rag_patterns = context.get("rag_patterns", [])
        browsed_docs = context.get("browsed_docs", {})
        vision_analysis = context.get("vision_analysis", "")

        prompt = f"""Task: {task}

"""

        # Add vision analysis if available
        if vision_analysis:
            prompt += f"""Vision Analysis (from sketch/mockup):
{vision_analysis}

"""

        # Add RAG patterns if available
        if rag_patterns:
            prompt += f"""Relevant Patterns (from knowledge base):
"""
            for i, pattern in enumerate(rag_patterns[:3], 1):
                prompt += f"{i}. {pattern.get('summary', 'No summary')}\n"
            prompt += "\n"

        # Add browsed documentation if available
        if browsed_docs:
            prompt += f"""Relevant Documentation:
"""
            for source, content in list(browsed_docs.items())[:2]:
                prompt += f"- {source}: {content[:200]}...\n"
            prompt += "\n"

        prompt += """Design the architecture for this system.

Your architecture should include:
1. **Component Structure**: What are the main components/modules?
2. **Data Flow**: How does data move through the system?
3. **Technology Stack**: What technologies/frameworks to use?
4. **Key Interfaces**: What are the critical APIs/interfaces between components?
5. **Scalability Considerations**: How will this scale?
6. **Security Considerations**: What security measures are needed?

Provide a clear, implementable architecture specification."""

        return prompt
