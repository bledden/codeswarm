"""
CodeSwarm Agents

4 Core Agents:
- Architecture Agent (Claude Sonnet 4.5): System design & architecture
- Implementation Agent (GPT-5 Pro): Code generation
- Security Agent (Claude Opus 4.1): Security analysis & hardening
- Testing Agent (Grok-4): Test generation & validation

+ Vision Agent (GPT-5-image): Conditional sketch analysis
"""

from .base_agent import BaseAgent, AgentOutput
from .architecture_agent import ArchitectureAgent
from .implementation_agent import ImplementationAgent
from .security_agent import SecurityAgent
from .testing_agent import TestingAgent
from .vision_agent import VisionAgent

__all__ = [
    "BaseAgent",
    "AgentOutput",
    "ArchitectureAgent",
    "ImplementationAgent",
    "SecurityAgent",
    "TestingAgent",
    "VisionAgent",
]
