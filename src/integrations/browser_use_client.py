"""
Browser Use Client for Documentation Scraping
Local browser automation using Browser Use Agent framework

NOTE: This uses the LOCAL browser-use package (Python 3.11+ required)
NOT the cloud browser-use-sdk. Runs Playwright locally without API keys.
"""
import os
import sys
from typing import Dict, Any, List, Optional
import logging
import asyncio
import re

logger = logging.getLogger(__name__)

# Check Python version
if sys.version_info < (3, 11):
    raise RuntimeError(
        "Browser Use requires Python 3.11+\n"
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}\n"
        "Please use: /opt/homebrew/bin/python3.11"
    )

# Try to import browser-use (local agent framework)
try:
    from browser_use import Agent, Browser, ChatBrowserUse
    BROWSER_USE_AVAILABLE = True
except ImportError as e:
    BROWSER_USE_AVAILABLE = False
    logger.warning(f"[BROWSER_USE] Package not installed: {e}")
    logger.warning("[BROWSER_USE] Run: pip3.11 install browser-use playwright")


class BrowserUseClient:
    """
    Client for automated documentation scraping using local Browser Use Agent

    Uses LOCAL Playwright browser automation (no API key needed):
    1. Scrape documentation from URLs
    2. Extract code examples and text
    3. Navigate complex documentation sites
    4. Search and extract documentation URLs
    """

    def __init__(self):
        """Initialize Browser Use client with local agent

        Uses ChatBrowserUse() - browser-use's built-in LLM that gets
        $10 free credits on signup.
        """
        if not BROWSER_USE_AVAILABLE:
            raise ImportError(
                "BROWSER-USE NOT INSTALLED!\n"
                "Requires Python 3.11+ and browser-use package.\n"
                "Install: pip3.11 install browser-use playwright\n"
                "Then: python3.11 -m playwright install chromium"
            )

        # Use browser-use's built-in ChatBrowserUse LLM
        # New signups get $10 free credits
        self.llm = ChatBrowserUse()

        logger.info("[BROWSER_USE] Client initialized (LOCAL mode with ChatBrowserUse)")

    async def scrape_documentation(
        self,
        url: str,
        extract_code: bool = True,
        max_depth: int = 1
    ) -> Dict[str, Any]:
        """
        Scrape documentation from URL using local browser agent

        Args:
            url: Documentation URL to scrape
            extract_code: Whether to extract code examples
            max_depth: Not used (kept for API compatibility)

        Returns:
            Dict with {url, text, code_examples, title, scraped_at}
        """
        logger.info(f"[BROWSER_USE] Scraping documentation: {url}")

        # Build task instruction
        task = f"Navigate to {url} and extract all text content"
        if extract_code:
            task += ". Also find and extract all code examples (in code blocks, pre tags, etc)"

        try:
            # Create browser and agent
            browser = Browser()
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser
            )

            # Run agent
            result = await agent.run()

            # Extract text from result
            result_text = str(result) if result else ""

            # Extract code examples using regex
            code_examples = []
            if extract_code and result_text:
                # Find code blocks (markdown style ```code```)
                code_blocks = re.findall(r'```[\s\S]*?```', result_text)
                code_examples.extend([block.strip('`').strip() for block in code_blocks])

                # Find code in <code> or <pre> tags
                html_code = re.findall(r'<(?:code|pre)>(.*?)</(?:code|pre)>', result_text, re.DOTALL)
                code_examples.extend([code.strip() for code in html_code])

                # Limit to 20 unique examples
                code_examples = list(set(code_examples))[:20]

            return {
                "url": url,
                "text": result_text[:50000],  # Limit to 50K chars
                "code_examples": code_examples,
                "title": url.split('//')[-1].split('/')[0],  # Extract domain as title
                "scraped_at": self._get_timestamp()
            }

        except Exception as e:
            logger.error(f"[BROWSER_USE] Scraping failed: {e}")
            raise

    async def search_and_scrape(
        self,
        search_query: str,
        search_engine: str = "https://www.google.com/search?q=",
        max_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for documentation and scrape top results using local browser agent

        Args:
            search_query: Search query (e.g., "FastAPI authentication docs")
            search_engine: Search engine URL (default: Google)
            max_results: Maximum number of results to scrape

        Returns:
            List of scraped documentation dictionaries
        """
        logger.info(f"[BROWSER_USE] Searching: {search_query}")

        # Build search task
        search_url = search_engine + search_query.replace(' ', '+')
        task = f"""Navigate to {search_url} and extract the top {max_results} documentation URLs.

Look for URLs containing keywords like: docs, documentation, tutorial, guide, api, reference, getting-started.
Return ONLY the URLs, one per line."""

        try:
            # Create browser and agent for search
            browser = Browser()
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser
            )

            # Run search agent
            result = await agent.run()
            result_text = str(result) if result else ""

            # Extract URLs from result
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:[^\s<>"{}|\\^`\[\].,;!?])'
            found_urls = re.findall(url_pattern, result_text)

            # Filter to documentation URLs
            doc_keywords = ['docs', 'documentation', 'guide', 'tutorial', 'reference',
                          'api', 'getting-started', 'quickstart', 'manual', 'learn',
                          'developer', 'examples', 'readme']

            doc_urls = []
            for url in found_urls:
                url_lower = url.lower()
                if any(keyword in url_lower for keyword in doc_keywords):
                    if url not in doc_urls:
                        doc_urls.append(url)
                        if len(doc_urls) >= max_results:
                            break

            # Fallback to first N URLs if no doc URLs found
            if not doc_urls and found_urls:
                doc_urls = found_urls[:max_results]

            logger.info(f"[BROWSER_USE] Found {len(doc_urls)} documentation URLs")

            # Scrape each URL
            results = []
            for url in doc_urls[:max_results]:
                try:
                    logger.info(f"[BROWSER_USE] Scraping {url}")
                    doc = await self.scrape_documentation(url, extract_code=True)
                    results.append(doc)
                except Exception as e:
                    logger.error(f"[BROWSER_USE] Failed to scrape {url}: {e}")
                    continue

            logger.info(f"[BROWSER_USE] Successfully scraped {len(results)} documents")
            return results

        except Exception as e:
            logger.error(f"[BROWSER_USE] Search failed: {e}")
            return []

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


async def test_browser_use():
    """Test Browser Use client with local agent"""
    try:
        print("=" * 80)
        print("  BROWSER USE LOCAL AGENT TEST")
        print("=" * 80)
        print()

        client = BrowserUseClient()
        print("✅ Client initialized (local mode)")
        print()

        # Test simple scraping
        print("Testing: Scrape example.com...")
        result = await client.scrape_documentation(
            "https://example.com",
            extract_code=False
        )

        print(f"✅ Scraped: {result['url']}")
        print(f"   Text: {len(result['text'])} chars")
        print()

        print("=" * 80)
        print("  ✅ BROWSER USE LOCAL AGENT TEST PASSED!")
        print("=" * 80)
        return True

    except ImportError as e:
        print(f"❌ Browser Use not installed: {e}")
        return False
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Must use Python 3.11+ to run this
    asyncio.run(test_browser_use())
