#!/usr/bin/env python3
"""
Test Browser Use Direct Scraping
Test if scrape_documentation() works (direct URL scraping)
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.integrations.browser_use_client import BrowserUseClient


async def test_direct_scraping():
    """Test direct documentation scraping"""
    print("=" * 80)
    print("  BROWSER USE DIRECT SCRAPING TEST")
    print("=" * 80)
    print()

    try:
        # Initialize client
        print("1. Initializing Browser Use client...")
        client = BrowserUseClient()
        print("   ✅ Client initialized")
        print()

        # Test direct scraping of a known documentation URL
        print("2. Testing direct scraping...")
        test_url = "https://fastapi.tiangolo.com/tutorial/"
        print(f"   URL: {test_url}")
        print()

        result = await client.scrape_documentation(
            url=test_url,
            extract_code=True,
            max_depth=1
        )

        print("3. Results:")
        print(f"   URL: {result.get('url', 'N/A')}")
        print(f"   Title: {result.get('title', 'N/A')[:60]}...")
        print(f"   Text: {len(result.get('text', ''))} characters")
        print(f"   Code examples: {len(result.get('code_examples', []))}")

        if result.get('code_examples'):
            print(f"\n   First code example:")
            first_code = result['code_examples'][0][:300]
            print(f"   {first_code}...")

        if len(result.get('text', '')) > 100:
            print()
            print("=" * 80)
            print("  ✅ BROWSER USE DIRECT SCRAPING TEST PASSED!")
            print("=" * 80)
            print()
            print("  Note: Direct scraping works, but search_and_scrape() cloud")
            print("  tasks may be slow. Consider using Tavily as primary for demos.")
            return True
        else:
            print()
            print("=" * 80)
            print("  ❌ DIRECT SCRAPING RETURNED INSUFFICIENT DATA")
            print("=" * 80)
            return False

    except Exception as e:
        print(f"\n   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_direct_scraping())
    sys.exit(0 if success else 1)
