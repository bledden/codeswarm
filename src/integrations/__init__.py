"""
External integrations for CodeSwarm
- OpenRouter (multi-model LLM access)
- Tavily (AI-powered documentation search - PRIMARY)
- Browser Use (browser automation - for testing only)
- Neo4j (RAG storage)
- Daytona (workspace integration)
- WorkOS (authentication)
"""

from .openrouter_client import OpenRouterClient
from .neo4j_client import Neo4jRAGClient
from .tavily_client import TavilyClient
from .browser_use_client import BrowserUseClient
from .workos_client import WorkOSAuthClient
from .daytona_client import DaytonaClient

__all__ = [
    "OpenRouterClient",
    "Neo4jRAGClient",
    "TavilyClient",
    "BrowserUseClient",
    "WorkOSAuthClient",
    "DaytonaClient"
]
