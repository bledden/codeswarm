"""
External integrations for CodeSwarm
- OpenRouter (multi-model LLM access)
- Browser Use (documentation scraping)
- Neo4j (RAG storage)
- Daytona (workspace integration)
- WorkOS (authentication)
"""

from .openrouter_client import OpenRouterClient
from .neo4j_client import Neo4jRAGClient
from .browser_use_client import BrowserUseClient
from .workos_client import WorkOSAuthClient
from .daytona_client import DaytonaClient

__all__ = [
    "OpenRouterClient",
    "Neo4jRAGClient",
    "BrowserUseClient",
    "WorkOSAuthClient",
    "DaytonaClient"
]
