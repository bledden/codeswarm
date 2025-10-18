#!/usr/bin/env python3
"""
Test All Service Integrations
Run this after Blake provides all API keys to verify everything is configured
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import (
    OpenRouterClient,
    Neo4jRAGClient,
    BrowserUseClient,
    WorkOSAuthClient,
    DaytonaClient
)
from evaluation.galileo_evaluator import GalileoEvaluator


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


async def test_openrouter():
    """Test OpenRouter (already working)"""
    print_header(" Testing OpenRouter (Multi-Model LLM)")

    try:
        async with OpenRouterClient() as client:
            response = await client.complete(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'OpenRouter works!'"}
                ],
                max_tokens=20
            )

            message = response['choices'][0]['message']['content']
            print(f" OpenRouter: {message}")
            print(f"   Tokens: {response['usage']['total_tokens']}")
            print(f"   Latency: {response['latency_ms']}ms")
            return True

    except Exception as e:
        print(f" OpenRouter failed: {e}")
        return False


async def test_galileo():
    """Test Galileo Observe"""
    print_header(" Testing Galileo Observe (Quality Evaluation)")

    try:
        evaluator = GalileoEvaluator()

        # Test evaluation
        score = await evaluator.evaluate(
            task="Write a hello world function",
            output="def hello(): return 'Hello World'",
            agent="test-agent",
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            latency_ms=500
        )

        print(f" Galileo Observe: Score {score}/100")
        print(f"   Project: {evaluator.project}")
        return True

    except ValueError as e:
        print(f" Galileo not configured: {e}")
        print("   Action: Provide GALILEO_API_KEY (see COMPLETE_SETUP_GUIDE.md Section 1)")
        return False
    except Exception as e:
        print(f" Galileo failed: {e}")
        return False


async def test_neo4j():
    """Test Neo4j Aura"""
    print_header("  Testing Neo4j Aura (RAG Storage)")

    try:
        async with Neo4jRAGClient() as client:
            # Verify connection
            connected = await client.verify_connection()
            if not connected:
                print(" Neo4j connection failed")
                return False

            # Test storing pattern
            pattern_id = await client.store_successful_pattern(
                task="Test pattern storage",
                agent_outputs={
                    "test-agent": {
                        "code": "print('test')",
                        "galileo_score": 92.0,
                        "latency_ms": 100,
                        "iterations": 1
                    }
                },
                avg_score=92.0
            )

            # Test retrieval
            patterns = await client.retrieve_similar_patterns("test", limit=5)

            # Get count
            count = await client.get_pattern_count()

            print(f" Neo4j Aura: Stored pattern {pattern_id}")
            print(f"   Retrieved: {len(patterns)} patterns")
            print(f"   Total patterns: {count}")
            return True

    except ValueError as e:
        print(f" Neo4j not configured: {e}")
        print("   Action: Provide NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
        print("   (see COMPLETE_SETUP_GUIDE.md Section 2)")
        return False
    except Exception as e:
        print(f" Neo4j failed: {e}")
        return False


async def test_browser_use():
    """Test Browser Use"""
    print_header(" Testing Browser Use (Documentation Scraping)")

    try:
        # Note: This test requires 'playwright install chromium' to be run first
        async with BrowserUseClient(headless=True) as client:
            # Test scraping a simple page
            result = await client.scrape_documentation(
                "https://example.com",  # Simple test page
                extract_code=False,
                max_depth=1
            )

            print(f" Browser Use: Scraped {len(result['text'])} chars")
            print(f"   Links found: {len(result['links'])}")
            return True

    except ImportError as e:
        print(f" Browser Use not installed: {e}")
        print("   Action: Run 'pip3 install browser-use'")
        print("   Then run 'playwright install chromium'")
        print("   (see COMPLETE_SETUP_GUIDE.md Section 3)")
        return False
    except Exception as e:
        print(f" Browser Use failed: {e}")
        print("   Note: May need to run 'playwright install chromium' first")
        return False


async def test_workos():
    """Test WorkOS"""
    print_header(" Testing WorkOS (Team Authentication)")

    try:
        client = WorkOSAuthClient()

        # Test getting authorization URL
        auth_url = client.get_authorization_url(
            redirect_uri="http://localhost:3000/callback",
            provider="GoogleOAuth",
            state="test_state_123"
        )

        # Test listing organizations
        orgs = client.list_organizations()

        print(f" WorkOS: Generated auth URL")
        print(f"   URL preview: {auth_url[:80]}...")
        print(f"   Organizations: {len(orgs)}")
        if orgs:
            print(f"   First org: {orgs[0]['name']}")
        return True

    except ValueError as e:
        print(f" WorkOS not configured: {e}")
        print("   Action: Provide WORKOS_API_KEY and WORKOS_CLIENT_ID")
        print("   (see COMPLETE_SETUP_GUIDE.md Section 4)")
        return False
    except ImportError as e:
        print(f" WorkOS not installed: {e}")
        print("   Action: Run 'pip3 install workos'")
        return False
    except Exception as e:
        print(f" WorkOS failed: {e}")
        return False


async def test_daytona():
    """Test Daytona"""
    print_header(" Testing Daytona (Dev Workspace)")

    try:
        async with DaytonaClient() as client:
            # Test listing workspaces
            workspaces = await client.list_workspaces()

            print(f" Daytona: Connected to API")
            print(f"   Workspaces: {len(workspaces)}")
            if workspaces:
                print(f"   First workspace: {workspaces[0]['name']}")

            # If we have a default workspace, check its status
            if client.workspace_id:
                status = await client.get_workspace_status()
                print(f"   Default workspace status: {status['status']}")

            return True

    except ValueError as e:
        print(f" Daytona not configured: {e}")
        print("   Action: Provide DAYTONA_API_KEY and DAYTONA_API_URL")
        print("   (see COMPLETE_SETUP_GUIDE.md Section 5)")
        return False
    except Exception as e:
        print(f" Daytona failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("   CODESWARM - ALL SERVICE INTEGRATION TESTS")
    print("=" * 80)
    print("\n Testing all 6 service integrations...")
    print("   This will verify that all API keys and services are configured correctly.\n")

    results = {}

    # Test each service
    results["OpenRouter"] = await test_openrouter()
    results["Galileo"] = await test_galileo()
    results["Neo4j"] = await test_neo4j()
    results["Browser Use"] = await test_browser_use()
    results["WorkOS"] = await test_workos()
    results["Daytona"] = await test_daytona()

    # Print summary
    print_header(" TEST RESULTS SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for service, result in results.items():
        status = " PASS" if result else " FAIL"
        print(f"   {status}: {service}")

    print(f"\n   Total: {passed}/{total} services configured correctly")

    if passed == total:
        print("\n" + "=" * 80)
        print("   ALL SERVICES READY!")
        print("  You can now run the full CodeSwarm workflow.")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("    SOME SERVICES NOT CONFIGURED")
        print("  Please complete setup for failing services.")
        print("  See COMPLETE_SETUP_GUIDE.md for instructions.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
