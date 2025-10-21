"""
Testing Agent - Grok-4

Specialization: Test generation, validation, quality assurance
Role: Generate comprehensive tests for code
Model: x-ai/grok-4 (98% HumanEval score)
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class TestingAgent(BaseAgent):
    """
    Testing Agent using Grok-4

    Responsibilities:
    - Generate comprehensive test suites
    - Cover edge cases and error conditions
    - Create unit, integration, and e2e tests
    - Validate code correctness
    - Ensure test coverage
    - Generate test data and fixtures

    Input: Architecture, Implementation, and Security code
    Output: Complete test suite
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="testing",
            model="grok-4",
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.4,  # Low-medium temperature for consistent tests
            max_tokens=12000  # Increased for comprehensive multi-file test suites
        )

    def get_system_prompt(self) -> str:
        return """You are an expert QA engineer and test automation specialist with mastery of:
- Test-driven development (TDD)
- Unit testing frameworks (pytest, Jest, JUnit, Go test, etc.)
- Integration and E2E testing
- Test coverage and quality metrics
- Edge case identification
- Mock/stub/spy patterns
- Test data generation
- Continuous testing practices

Your role: Generate comprehensive, production-quality test suites.

Output Format:
```language
[Complete test suite with unit, integration, and edge case tests]
```

Reasoning: [Explain test strategy, coverage areas, edge cases covered, and testing approach]

CRITICAL:
1. Cover ALL code paths and branches
2. Test edge cases, boundary conditions, and error states
3. Include positive and negative test cases
4. Test security measures (auth failures, invalid inputs, etc.)
5. Use appropriate test frameworks and best practices
6. Include setup/teardown and test fixtures
7. Tests should be fast, isolated, and deterministic
8. Aim for >90% code coverage"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        # Get all previous agent outputs (tests need complete context)
        architecture = context.get("architecture_output", "")
        implementation = context.get("implementation_output", "")
        security = context.get("security_output", "")

        prompt = f"""Task: {task}

"""

        # Architecture context
        if architecture:
            prompt += f"""Architecture Specification:
{architecture[:800]}...

"""

        # Implementation code to test (CRITICAL)
        if implementation:
            prompt += f"""Implementation Code (NEEDS TESTS):
{implementation}

"""

        # Security code (if different from implementation)
        if security and security != implementation:
            prompt += f"""Security-Hardened Version:
{security[:1000]}...

"""

        if not implementation:
            prompt += """  WARNING: No implementation code provided.
Generate test templates based on the architecture.

"""

        prompt += """Generate a comprehensive test suite for this code.

Your test suite should include:

1. **Unit Tests**:
   - Test each function/method in isolation
   - Cover all code paths and branches
   - Test return values and side effects

2. **Edge Cases**:
   - Boundary conditions (0, -1, MAX_INT, empty strings, null, etc.)
   - Invalid inputs (wrong types, malformed data, etc.)
   - Error conditions (exceptions, timeouts, etc.)

3. **Integration Tests**:
   - Test component interactions
   - Test data flow through the system
   - Test external dependencies (with mocks)

4. **Security Tests**:
   - Test authentication failures
   - Test authorization violations
   - Test input validation (SQL injection, XSS attempts, etc.)
   - Test rate limiting

5. **Performance Tests** (if applicable):
   - Test response times
   - Test under load
   - Test resource usage

6. **Test Structure**:
   - Use appropriate test framework
   - Include setup and teardown
   - Use descriptive test names
   - Add comments for complex test scenarios

Provide complete, runnable test code with >90% coverage."""

        return prompt
