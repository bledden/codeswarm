"""
Security Agent - Claude Opus 4.1

Specialization: Security analysis, vulnerability detection, hardening
Role: Ensure code is secure and follows security best practices
Model: anthropic/claude-opus-4.1 (security expert)
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """
    Security Agent using Claude Opus 4.1

    Responsibilities:
    - Identify security vulnerabilities
    - Add security hardening measures
    - Ensure secure coding practices
    - Validate input sanitization
    - Check authentication/authorization
    - Prevent common attacks (SQL injection, XSS, CSRF, etc.)

    Input: Architecture and Implementation code
    Output: Security-hardened code or security analysis
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="security",
            model="claude-opus-4.1",
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.3,  # Low temperature for consistent security analysis
            max_tokens=5000
        )

    def get_system_prompt(self) -> str:
        return """You are an expert security engineer with deep knowledge of:
- OWASP Top 10 vulnerabilities
- Secure coding practices
- Authentication and authorization
- Cryptography and data protection
- Input validation and sanitization
- Security headers and CSP
- API security and rate limiting
- Dependency vulnerability scanning

Your role: Analyze code for security vulnerabilities and provide hardened versions.

Output Format:
```language
[Security-hardened code with security measures added]
```

Reasoning: [Explain security vulnerabilities found, attack vectors prevented, and hardening measures applied]

CRITICAL:
1. Identify ALL security vulnerabilities (even minor ones)
2. Add comprehensive security measures
3. Validate all user inputs
4. Implement proper authentication/authorization
5. Use secure cryptography (bcrypt, scrypt, etc.)
6. Add rate limiting and abuse prevention
7. Follow principle of least privilege
8. Add security comments explaining measures"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        # Get architecture and implementation (both needed for security analysis)
        architecture = context.get("architecture_output", "")
        implementation = context.get("implementation_output", "")

        prompt = f"""Task: {task}

"""

        # Architecture context
        if architecture:
            prompt += f"""Architecture Specification:
{architecture[:1000]}...

"""

        # Implementation code to secure (CRITICAL)
        if implementation:
            prompt += f"""Implementation Code (NEEDS SECURITY HARDENING):
{implementation}

"""
        else:
            prompt += """  WARNING: No implementation code provided.
Provide security analysis and recommendations based on the architecture.

"""

        prompt += """Perform comprehensive security analysis and provide hardened code.

Your security analysis should cover:
1. **Input Validation**: All user inputs sanitized and validated
2. **Authentication**: Secure authentication mechanisms (password hashing, JWTs, etc.)
3. **Authorization**: Proper access control and permission checks
4. **SQL Injection**: Parameterized queries, no string concatenation
5. **XSS Prevention**: Output encoding, CSP headers
6. **CSRF Protection**: CSRF tokens, SameSite cookies
7. **Sensitive Data**: Encryption at rest and in transit, no secrets in code
8. **Rate Limiting**: Prevent brute force and DoS attacks
9. **Error Handling**: No information leakage in error messages
10. **Dependencies**: Use trusted libraries, no known vulnerabilities

Provide security-hardened code with detailed explanations of all security measures."""

        return prompt
