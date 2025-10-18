"""
Browser Use Client for Documentation Scraping
Automated web scraping using Browser Use API

NOTE: Browser Use SDK requires an API key from https://browser-use.com
This is a cloud-based browser automation service.
"""
import os
from typing import Dict, Any, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

# Browser Use SDK requires API key
try:
    from browser_use_sdk import BrowserUse
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning("[BROWSER_USE]   Package not installed. Run: pip3 install browser-use-sdk")


class BrowserUseClient:
    """
    Client for automated documentation scraping using Browser Use API

    Uses Browser Use cloud service to:
    1. Scrape documentation from URLs
    2. Extract code examples
    3. Navigate complex documentation sites
    4. Retrieve RAG context for code generation
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Browser Use client

        Args:
            api_key: Browser Use API key (or from BROWSER_USE_API_KEY env var)
        """
        if not BROWSER_USE_AVAILABLE:
            raise ImportError(
                " BROWSER-USE SDK NOT INSTALLED!\n"
                "Please run: pip3 install browser-use-sdk\n"
                "See COMPLETE_SETUP_GUIDE.md Section 3 for instructions."
            )

        # Check both BROWSER_USE_API_KEY and BROWSERUSE_API_KEY
        self.api_key = api_key or os.getenv("BROWSER_USE_API_KEY") or os.getenv("BROWSERUSE_API_KEY")

        if not self.api_key or self.api_key == "your_browser_use_key_here":
            raise ValueError(
                " NO BROWSER USE API KEY FOUND!\n"
                "Please set BROWSER_USE_API_KEY or BROWSERUSE_API_KEY in .env file.\n"
                "Get your API key from https://browser-use.com\n"
                "See COMPLETE_SETUP_GUIDE.md Section 3 for instructions."
            )

        self.client = BrowserUse(api_key=self.api_key)
        logger.info("[BROWSER_USE]  Client initialized with API key")

    async def scrape_documentation(
        self,
        url: str,
        extract_code: bool = True,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Scrape documentation from URL using Browser Use API

        Args:
            url: Documentation URL to scrape
            extract_code: Whether to extract code examples
            max_depth: Maximum link depth to follow (not used by SDK)

        Returns:
            Dict with {text, code_examples, links, url, scraped_at}
        """
        logger.info(f"[BROWSER_USE]  Scraping documentation: {url}")

        # Create a task to scrape the URL
        task_instruction = f"Navigate to {url} and extract all text content"
        if extract_code:
            task_instruction += " and code examples"

        try:
            # Create browsing task using correct API parameters
            task = self.client.tasks.create_task(
                task=task_instruction,
                start_url=url,
                max_steps=10
            )

            task_id = task.id
            logger.info(f"[BROWSER_USE]  Created task {task_id}")

            # Wait for task completion
            max_attempts = 30
            for attempt in range(max_attempts):
                task_status = self.client.tasks.get_task(task_id=task_id)

                if task_status.status == "completed":
                    logger.info(f"[BROWSER_USE]  Task completed")
                    break
                elif task_status.status == "failed":
                    raise Exception(f"Task failed: {task_status.error}")

                await asyncio.sleep(2)
            else:
                raise TimeoutError("Task did not complete within timeout")

            # Get task result
            result_text = task_status.result or ""

            # Extract code examples (simple regex-based extraction)
            code_examples = []
            if extract_code and result_text:
                import re
                # Find code blocks (markdown style)
                code_blocks = re.findall(r'```[\s\S]*?```', result_text)
                code_examples = [block.strip('`').strip() for block in code_blocks[:20]]

            result = {
                "url": url,
                "text": result_text[:50000],  # Limit to 50K chars
                "code_examples": code_examples[:20],  # Limit to 20 examples
                "links": [],  # Browser Use SDK doesn't provide links separately
                "scraped_at": self._get_timestamp(),
                "task_id": task_id
            }

            logger.info(
                f"[BROWSER_USE]  Scraped {len(result_text)} chars, "
                f"{len(code_examples)} code examples"
            )

            return result

        except Exception as e:
            logger.error(f"[BROWSER_USE]  Scraping failed: {e}")
            raise

    async def search_and_scrape(
        self,
        search_query: str,
        search_engine: str = "https://www.google.com/search?q=",
        max_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for documentation and scrape top results

        Args:
            search_query: Search query (e.g., "FastAPI authentication docs")
            search_engine: Search engine URL template
            max_results: Maximum number of results to scrape

        Returns:
            List of scraped documentation dictionaries
        """
        logger.info(f"[BROWSER_USE]  Searching: {search_query}")

        # Create a search task
        task_instruction = f"Search Google for '{search_query}' and extract the top {max_results} result URLs"

        try:
            task = self.client.tasks.create_task(
                task=task_instruction,
                start_url=search_engine + search_query.replace(' ', '+'),
                max_steps=10
            )

            task_id = task.id

            # Wait for task completion (fail fast to Tavily fallback if slow)
            max_attempts = 15  # 15 attempts × 2s = 30 seconds timeout
            for attempt in range(max_attempts):
                task_status = self.client.tasks.get_task(task_id=task_id)

                if task_status.status == "completed":
                    logger.info(f"[BROWSER_USE]  Task completed after {attempt * 2}s")
                    break
                elif task_status.status == "failed":
                    raise Exception(f"Search task failed: {task_status.error}")

                # Log progress every 5 attempts (10 seconds)
                if attempt > 0 and attempt % 5 == 0:
                    logger.info(f"[BROWSER_USE]  Still waiting... ({attempt * 2}s elapsed)")

                await asyncio.sleep(2)
            else:
                raise TimeoutError(f"Search task timed out after {max_attempts * 2}s (falling back to Tavily)")

            # Extract URLs from search result
            result_text = task_status.result or ""

            # Extract URLs using regex
            import re
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:[^\s<>"{}|\\^`\[\].,;!?])'
            found_urls = re.findall(url_pattern, result_text)

            # Filter to likely documentation URLs
            doc_keywords = ['docs', 'documentation', 'guide', 'tutorial', 'reference',
                          'api', 'getting-started', 'quickstart', 'manual', 'learn',
                          'developer', 'examples', 'readme']

            doc_urls = []
            for url in found_urls:
                url_lower = url.lower()
                # Check if URL contains documentation keywords
                if any(keyword in url_lower for keyword in doc_keywords):
                    # Avoid duplicate URLs
                    if url not in doc_urls:
                        doc_urls.append(url)
                        if len(doc_urls) >= max_results:
                            break

            # If no documentation URLs found, try first few URLs
            if not doc_urls and found_urls:
                doc_urls = found_urls[:max_results]

            logger.info(f"[BROWSER_USE]  Found {len(doc_urls)} documentation URLs")

            # Scrape each URL
            results = []
            for url in doc_urls[:max_results]:
                try:
                    logger.info(f"[BROWSER_USE]  Scraping {url}")
                    doc = await self.scrape_documentation(url, extract_code=True)
                    results.append(doc)
                except Exception as e:
                    logger.error(f"[BROWSER_USE]  Failed to scrape {url}: {e}")
                    continue

            logger.info(f"[BROWSER_USE]  Successfully scraped {len(results)} documents")
            return results

        except Exception as e:
            logger.error(f"[BROWSER_USE]  Search failed: {e}")
            return []

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


async def test_browser_use():
    """Test Browser Use client"""
    try:
        client = BrowserUseClient()

        # Test scraping a simple documentation page
        result = await client.scrape_documentation(
            "https://example.com",
            extract_code=False,
            max_depth=1
        )

        print(" Scraped example.com")
        print(f"   Text: {len(result['text'])} chars")
        print(f"   Task ID: {result['task_id']}")

        return True

    except ImportError as e:
        print(f"  Browser Use SDK not installed: {e}")
        print("   Run: pip3 install browser-use-sdk")
        return False
    except ValueError as e:
        print(f"  Browser Use API key not configured: {e}")
        print("   Set BROWSER_USE_API_KEY in .env file")
        return False
    except Exception as e:
        print(f" Browser Use test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_browser_use())
