#!/usr/bin/env python3
"""
Test Browser Use Integration
Quick verification that Browser Use search_and_scrape() is working
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.integrations.browser_use_client import BrowserUseClient


async def test_browser_use():
    """Test Browser Use search and scrape"""
    print("=" * 80)
    print("  BROWSER USE INTEGRATION TEST")
    print("=" * 80)
    print()

    try:
        # Initialize client
        print("1. Initializing Browser Use client...")
        client = BrowserUseClient()
        print("   ✅ Client initialized")
        print()

        # Test search and scrape
        print("2. Testing search_and_scrape()...")
        print("   Query: 'FastAPI tutorial documentation'")
        print()

        results = await client.search_and_scrape(
            search_query="FastAPI tutorial documentation",
            max_results=2
        )

        print(f"   Results: {len(results)} documents")
        print()

        if results:
            print("3. Results:")
            for i, doc in enumerate(results, 1):
                print(f"\n   Document {i}:")
                print(f"     URL: {doc.get('url', 'N/A')}")
                print(f"     Title: {doc.get('title', 'N/A')[:60]}...")
                print(f"     Text: {len(doc.get('text', ''))} characters")
                print(f"     Code examples: {len(doc.get('code_examples', []))}")

                if doc.get('code_examples'):
                    print(f"\n     First code example:")
                    first_code = doc['code_examples'][0][:200]
                    print(f"     {first_code}...")

            print()
            print("=" * 80)
            print("  ✅ BROWSER USE INTEGRATION TEST PASSED!")
            print("=" * 80)
            return True

        else:
            print("   ⚠️  No results returned")
            print()
            print("=" * 80)
            print("  ❌ BROWSER USE INTEGRATION TEST FAILED")
            print("=" * 80)
            return False

    except ImportError as e:
        print(f"   ❌ Browser Use not installed: {e}")
        print("   Run: pip3 install browseruse")
        return False

    except ValueError as e:
        print(f"   ❌ Configuration error: {e}")
        print("   Check BROWSERUSE_API_KEY in .env")
        return False

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_browser_use())
    sys.exit(0 if success else 1)
