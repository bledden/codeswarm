#!/usr/bin/env python3
"""Quick integration test for all services"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n🐝 CODESWARM - QUICK SERVICE TEST")
print("=" * 60)

# Test OpenRouter
print("\n1. Testing OpenRouter...")
try:
    from integrations.openrouter_client import OpenRouterClient
    async def test_openrouter():
        async with OpenRouterClient() as client:
            response = await client.complete(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hi!"}],
                max_tokens=10
            )
            return response['choices'][0]['message']['content']

    result = asyncio.run(test_openrouter())
    print(f"   ✅ OpenRouter: {result}")
except Exception as e:
    print(f"   ❌ OpenRouter: {e}")

# Test Neo4j
print("\n2. Testing Neo4j...")
try:
    from integrations.neo4j_client import Neo4jRAGClient
    async def test_neo4j():
        async with Neo4jRAGClient() as client:
            await client.verify_connection()
            count = await client.get_pattern_count()
            return count

    count = asyncio.run(test_neo4j())
    print(f"   ✅ Neo4j: Connected ({count} patterns stored)")
except Exception as e:
    print(f"   ❌ Neo4j: {e}")

# Test Galileo
print("\n3. Testing Galileo...")
try:
    from evaluation.galileo_evaluator import GalileoEvaluator
    async def test_galileo():
        evaluator = GalileoEvaluator()
        score = await evaluator.evaluate(
            task="test",
            output="test output",
            agent="test-agent",
            model="gpt-3.5-turbo"
        )
        return score

    score = asyncio.run(test_galileo())
    print(f"   ✅ Galileo: Working (test score: {score}/100)")
except Exception as e:
    print(f"   ❌ Galileo: {e}")

# Test WorkOS
print("\n4. Testing WorkOS...")
try:
    from integrations.workos_client import WorkOSAuthClient
    client = WorkOSAuthClient()
    url = client.get_authorization_url(
        redirect_uri="http://localhost:3000/callback",
        provider="GoogleOAuth"
    )
    print(f"   ✅ WorkOS: Connected (auth URL generated)")
except Exception as e:
    print(f"   ❌ WorkOS: {e}")

# Test Daytona
print("\n5. Testing Daytona...")
try:
    from integrations.daytona_client import DaytonaClient
    async def test_daytona():
        async with DaytonaClient() as client:
            workspaces = await client.list_workspaces()
            return len(workspaces)

    count = asyncio.run(test_daytona())
    print(f"   ✅ Daytona: Connected ({count} workspaces)")
except Exception as e:
    print(f"   ❌ Daytona: {e}")

# Test Browser Use (expect fail on Python 3.9)
print("\n6. Testing Browser Use...")
try:
    from integrations.browser_use_client import BrowserUseClient
    print(f"   ✅ Browser Use: Installed")
except ImportError as e:
    print(f"   ⚠️  Browser Use: Not available (requires Python 3.11+)")
except Exception as e:
    print(f"   ❌ Browser Use: {e}")

print("\n" + "=" * 60)
print("Test complete!\n")
