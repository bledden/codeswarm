"""
Neo4j Aura Client for RAG Storage
Stores successful code patterns (90+ quality) for retrieval
"""
import os
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, AsyncGraphDatabase
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Neo4jRAGClient:
    """
    Neo4j client for storing and retrieving successful code patterns

    Uses Neo4j Aura cloud database (no Docker required)
    Stores patterns with 90+ Galileo scores for RAG retrieval
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Neo4j client

        Args:
            uri: Neo4j URI (e.g., neo4j+s://xxxxx.databases.neo4j.io)
            user: Neo4j username (usually 'neo4j')
            password: Neo4j password from Aura credentials
        """
        self.uri = uri or os.getenv("NEO4J_URI")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD")

        if not self.uri or not self.password:
            raise ValueError(
                " NO NEO4J CREDENTIALS FOUND!\n"
                "Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in .env file.\n"
                "See COMPLETE_SETUP_GUIDE.md Section 2 for instructions."
            )

        if self.uri == "bolt://localhost:7687":
            raise ValueError(
                " NEO4J_URI is still set to localhost!\n"
                "Please update with your Neo4j Aura URI (starts with neo4j+s://).\n"
                "See COMPLETE_SETUP_GUIDE.md Section 2 for instructions."
            )

        # Create async driver
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

        logger.info(f"[NEO4J]  Connected to Neo4j Aura: {self.uri}")

    async def close(self):
        """Close the driver"""
        await self.driver.close()

    async def __aenter__(self):
        """Context manager entry"""
        await self.verify_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()

    async def verify_connection(self) -> bool:
        """Verify connection to Neo4j"""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 AS test")
                record = await result.single()
                if record and record["test"] == 1:
                    logger.info("[NEO4J]  Connection verified")
                    return True
        except Exception as e:
            logger.error(f"[NEO4J]  Connection failed: {e}")
            raise
        return False

    async def store_successful_pattern(
        self,
        task: str,
        agent_outputs: Dict[str, Dict[str, Any]],
        avg_score: float,
        metadata: Optional[Dict[str, Any]] = None,
        documentation_urls: Optional[List[str]] = None  # PHASE 2: Track doc effectiveness
    ) -> str:
        """
        Store successful code generation pattern (90+ quality)

        Args:
            task: Original user task
            agent_outputs: Dict mapping agent_name -> {code, galileo_score, etc}
            avg_score: Average Galileo score across all agents
            metadata: Optional additional metadata
            documentation_urls: Optional list of Tavily docs used (PHASE 2)

        Returns:
            Pattern ID (UUID)
        """
        if avg_score < 90:
            logger.warning(f"[NEO4J] Pattern score {avg_score} < 90, skipping storage")
            return ""

        pattern_id = f"pattern_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        async with self.driver.session() as session:
            # Create pattern node
            query = """
            CREATE (p:CodePattern {
                id: $pattern_id,
                task: $task,
                avg_score: $avg_score,
                timestamp: datetime(),
                agent_count: $agent_count
            })
            RETURN p.id AS id
            """

            result = await session.run(
                query,
                pattern_id=pattern_id,
                task=task[:500],  # Limit task length
                avg_score=avg_score,
                agent_count=len(agent_outputs)
            )

            # Create agent output nodes and relationships
            for agent_name, output in agent_outputs.items():
                agent_query = """
                MATCH (p:CodePattern {id: $pattern_id})
                CREATE (a:AgentOutput {
                    agent: $agent_name,
                    code: $code,
                    score: $score,
                    latency_ms: $latency_ms,
                    iterations: $iterations
                })
                CREATE (p)-[:GENERATED_BY]->(a)
                """

                await session.run(
                    agent_query,
                    pattern_id=pattern_id,
                    agent_name=agent_name,
                    code=output.get("code", "")[:10000],  # Limit code length
                    score=output.get("galileo_score", 0),
                    latency_ms=output.get("latency_ms", 0),
                    iterations=output.get("iterations", 1)
                )

            # PHASE 2: Link documentation to pattern
            if documentation_urls:
                await self.link_docs_to_pattern(
                    pattern_id=pattern_id,
                    documentation_urls=documentation_urls,
                    galileo_score=avg_score
                )

        logger.info(f"[NEO4J]  Stored pattern {pattern_id} (score: {avg_score})")
        if documentation_urls:
            logger.info(f"[NEO4J]  Linked {len(documentation_urls)} docs to pattern")
        return pattern_id

    async def retrieve_similar_patterns(
        self,
        task: str,
        limit: int = 5,
        min_score: float = 90.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar successful patterns using text similarity

        Args:
            task: Current user task
            limit: Maximum number of patterns to return
            min_score: Minimum quality score threshold

        Returns:
            List of similar patterns with their outputs
        """
        async with self.driver.session() as session:
            # Simple keyword-based retrieval (can be enhanced with vector embeddings)
            # Extract keywords from task
            keywords = self._extract_keywords(task)

            query = """
            MATCH (p:CodePattern)
            WHERE p.avg_score >= $min_score
            AND ANY(keyword IN $keywords WHERE p.task CONTAINS keyword)
            WITH p
            ORDER BY p.avg_score DESC, p.timestamp DESC
            LIMIT $limit

            OPTIONAL MATCH (p)-[:GENERATED_BY]->(a:AgentOutput)
            RETURN p, collect(a) AS agent_outputs
            """

            result = await session.run(
                query,
                keywords=keywords,
                min_score=min_score,
                limit=limit
            )

            patterns = []
            async for record in result:
                pattern_node = record["p"]
                agent_outputs = record["agent_outputs"]

                patterns.append({
                    "id": pattern_node["id"],
                    "task": pattern_node["task"],
                    "avg_score": pattern_node["avg_score"],
                    "timestamp": str(pattern_node["timestamp"]),
                    "agent_outputs": [
                        {
                            "agent": a["agent"],
                            "code": a["code"],
                            "score": a["score"]
                        }
                        for a in agent_outputs
                    ]
                })

            logger.info(f"[NEO4J]  Retrieved {len(patterns)} similar patterns")
            return patterns

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simple version)"""
        # Remove common words and split
        stop_words = {"a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or"}
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:10]  # Limit to 10 keywords

    async def get_pattern_count(self) -> int:
        """Get total number of stored patterns"""
        async with self.driver.session() as session:
            result = await session.run("MATCH (p:CodePattern) RETURN count(p) AS count")
            record = await result.single()
            return record["count"] if record else 0

    # ========== PHASE 1: Tavily Result Caching ==========

    async def cache_tavily_results(
        self,
        query: str,
        results: Dict[str, Any],
        ttl_days: int = 7
    ) -> str:
        """
        Store Tavily search results in Neo4j cache

        Args:
            query: Original search query
            results: Tavily API response (dict with 'results' key)
            ttl_days: Cache TTL in days (default: 7)

        Returns:
            query_hash: SHA-256 hash of normalized query
        """
        import hashlib

        # Normalize query for consistent cache keys
        normalized_query = query.lower().strip()
        query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()

        # Serialize results to JSON
        results_json = json.dumps(results)
        results_count = len(results.get('results', []))

        cypher = """
        MERGE (cache:TavilyCache {query_hash: $query_hash})
        SET cache.original_query = $original_query,
            cache.created_at = datetime(),
            cache.expires_at = datetime() + duration({days: $ttl_days}),
            cache.results_count = $results_count,
            cache.results_json = $results_json
        RETURN cache.query_hash as hash
        """

        async with self.driver.session() as session:
            await session.run(cypher, {
                "query_hash": query_hash,
                "original_query": query,
                "ttl_days": ttl_days,
                "results_count": results_count,
                "results_json": results_json
            })

        logger.info(f"[NEO4J]  Cached Tavily results: {query[:50]}... ({results_count} results, TTL: {ttl_days}d)")
        return query_hash

    async def get_cached_tavily_results(
        self,
        query: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached Tavily results if fresh

        Args:
            query: Search query (will be normalized)

        Returns:
            Tavily results dict if cache hit and fresh, None if cache miss or expired
        """
        import hashlib

        # Normalize query for consistent lookup
        normalized_query = query.lower().strip()
        query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()

        cypher = """
        MATCH (cache:TavilyCache {query_hash: $query_hash})
        WHERE cache.expires_at > datetime()
        RETURN cache.results_json as results_json,
               cache.created_at as cached_at,
               cache.results_count as count
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, {"query_hash": query_hash})
            record = await result.single()

            if record:
                # Parse JSON results
                results = json.loads(record["results_json"])
                logger.info(f"[NEO4J]  Cache HIT: {query[:50]}... ({record['count']} results)")
                return results
            else:
                logger.info(f"[NEO4J]  Cache MISS: {query[:50]}...")
                return None

    # ========== PHASE 2: Documentation Effectiveness Tracking ==========

    async def link_docs_to_pattern(
        self,
        pattern_id: str,
        documentation_urls: List[str],
        galileo_score: float
    ) -> None:
        """
        Link Tavily documentation URLs to a successful pattern

        Creates Documentation nodes and CONTRIBUTED_TO relationships
        to track which docs lead to high-quality code generation.

        Args:
            pattern_id: Pattern ID to link docs to
            documentation_urls: List of Tavily doc URLs used
            galileo_score: Quality score for this pattern
        """
        async with self.driver.session() as session:
            for url in documentation_urls:
                # Extract domain and title from URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
                title = url.split('/')[-1] if '/' in url else url

                cypher = """
                // Create or update Documentation node
                MERGE (doc:Documentation {url: $url})
                ON CREATE SET
                    doc.title = $title,
                    doc.domain = $domain,
                    doc.total_uses = 0,
                    doc.first_used_at = datetime()

                // Update usage counter
                SET doc.total_uses = doc.total_uses + 1,
                    doc.last_used_at = datetime()

                // Find the pattern
                WITH doc
                MATCH (p:CodePattern {id: $pattern_id})

                // Create relationship tracking this contribution
                MERGE (doc)-[r:CONTRIBUTED_TO]->(p)
                ON CREATE SET
                    r.galileo_score = $score,
                    r.used_at = datetime()
                """

                await session.run(cypher, {
                    "url": url,
                    "title": title[:200],  # Limit title length
                    "domain": domain,
                    "pattern_id": pattern_id,
                    "score": galileo_score
                })

        logger.info(f"[NEO4J]  Linked {len(documentation_urls)} docs to pattern {pattern_id}")

    async def get_doc_effectiveness_stats(
        self,
        min_uses: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get documentation effectiveness analytics

        Returns docs ranked by:
        - Total usage count (how often they've been used)
        - Average Galileo score (quality of resulting code)
        - Success rate (% of patterns with 90+ score)

        Args:
            min_uses: Minimum usage count to include (default: 2)
            limit: Maximum docs to return (default: 20)

        Returns:
            List of doc stats sorted by effectiveness
        """
        cypher = """
        MATCH (doc:Documentation)-[r:CONTRIBUTED_TO]->(p:CodePattern)
        WITH doc,
             count(r) as total_uses,
             avg(r.galileo_score) as avg_score,
             collect(r.galileo_score) as all_scores,
             max(doc.last_used_at) as last_used
        WHERE total_uses >= $min_uses
        WITH doc, total_uses, avg_score, all_scores, last_used,
             size([score IN all_scores WHERE score >= 90.0]) as success_count
        RETURN doc.url as url,
               doc.title as title,
               doc.domain as domain,
               total_uses,
               avg_score,
               (toFloat(success_count) / total_uses) * 100 as success_rate,
               last_used
        ORDER BY avg_score DESC, total_uses DESC
        LIMIT $limit
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, {
                "min_uses": min_uses,
                "limit": limit
            })

            stats = []
            async for record in result:
                stats.append({
                    "url": record["url"],
                    "title": record["title"],
                    "domain": record["domain"],
                    "total_uses": record["total_uses"],
                    "avg_score": round(record["avg_score"], 1),
                    "success_rate": round(record["success_rate"], 1),
                    "last_used": str(record["last_used"]) if record["last_used"] else None
                })

            logger.info(f"[NEO4J]  Retrieved {len(stats)} doc effectiveness stats")
            return stats

    # ========== PHASE 3: Semantic Documentation Search ==========

    async def get_proven_docs_for_task(
        self,
        task: str,
        limit: int = 3,
        min_score: float = 90.0
    ) -> List[str]:
        """
        Get documentation URLs that have proven effective for similar tasks

        Uses keyword matching to find patterns similar to the current task,
        then returns the docs that contributed to those successful patterns.

        Args:
            task: Current user task
            limit: Max docs to return (default: 3)
            min_score: Minimum pattern score (default: 90.0)

        Returns:
            List of proven documentation URLs
        """
        # Extract keywords from task
        keywords = self._extract_keywords(task)

        cypher = """
        // Find similar successful patterns
        MATCH (p:CodePattern)
        WHERE p.avg_score >= $min_score
        AND ANY(keyword IN $keywords WHERE p.task CONTAINS keyword)
        WITH p
        ORDER BY p.avg_score DESC
        LIMIT 5

        // Get docs that contributed to these patterns
        MATCH (doc:Documentation)-[r:CONTRIBUTED_TO]->(p)
        WITH doc, avg(r.galileo_score) as avg_doc_score, count(r) as usage_count
        RETURN doc.url as url
        ORDER BY avg_doc_score DESC, usage_count DESC
        LIMIT $limit
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, {
                "keywords": keywords,
                "min_score": min_score,
                "limit": limit
            })

            urls = []
            async for record in result:
                urls.append(record["url"])

            logger.info(f"[NEO4J]  Retrieved {len(urls)} proven docs for similar tasks")
            return urls

    # ========== PHASE 4: User Feedback Loop ==========

    async def store_user_feedback(
        self,
        session_id: str,
        pattern_id: str,
        task: str,
        code_quality: int,
        context_quality: int,
        would_retry: bool = False,
        retry_session_id: Optional[str] = None
    ) -> str:
        """
        Store user feedback for a code generation session

        Args:
            session_id: Unique session identifier
            pattern_id: Pattern ID that was generated
            task: Original user task
            code_quality: User rating 1-5
            context_quality: User rating 1-5
            would_retry: Whether user wants to retry
            retry_session_id: Link to retry session if applicable

        Returns:
            session_id
        """
        cypher = """
        CREATE (f:UserFeedback {
          session_id: $session_id,
          pattern_id: $pattern_id,
          task: $task,
          code_quality: $code_quality,
          context_quality: $context_quality,
          timestamp: datetime(),
          would_retry: $would_retry,
          retry_session_id: $retry_session_id
        })

        WITH f
        MATCH (p:CodePattern {id: $pattern_id})
        CREATE (f)-[:FEEDBACK_FOR]->(p)

        RETURN f.session_id as session_id
        """

        async with self.driver.session() as session:
            await session.run(cypher, {
                "session_id": session_id,
                "pattern_id": pattern_id,
                "task": task[:500],
                "code_quality": code_quality,
                "context_quality": context_quality,
                "would_retry": would_retry,
                "retry_session_id": retry_session_id
            })

        logger.info(f"[NEO4J]  Stored user feedback: code={code_quality}/5, context={context_quality}/5")
        return session_id

    async def mark_doc_unhelpful(
        self,
        url: str,
        session_id: str,
        reason: str = "User marked as irrelevant"
    ) -> None:
        """
        Mark a documentation URL as unhelpful based on user feedback

        Args:
            url: Documentation URL
            session_id: Session where feedback was given
            reason: Why doc was unhelpful
        """
        cypher = """
        // Find or create documentation node
        MERGE (doc:Documentation {url: $url})
        ON CREATE SET
          doc.negative_feedback_count = 0,
          doc.total_uses = 0

        // Increment negative feedback counter
        SET doc.negative_feedback_count = doc.negative_feedback_count + 1

        // Calculate negative feedback rate (protect against division by zero)
        WITH doc
        WHERE doc.total_uses > 0
        SET doc.negative_feedback_rate = toFloat(doc.negative_feedback_count) / doc.total_uses

        // Link negative feedback
        WITH doc
        MATCH (f:UserFeedback {session_id: $session_id})
        MERGE (doc)-[r:RECEIVED_NEGATIVE_FEEDBACK]->(f)
        SET r.user_reason = $reason,
            r.timestamp = datetime()

        RETURN doc.url, doc.negative_feedback_rate
        """

        async with self.driver.session() as session:
            await session.run(cypher, {
                "url": url,
                "session_id": session_id,
                "reason": reason
            })

        logger.info(f"[NEO4J]  Marked doc as unhelpful: {url[:50]}...")

    async def get_high_negative_feedback_docs(
        self,
        min_negative_rate: float = 0.3,
        min_uses: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get documentation URLs with high negative feedback rates

        Used to exclude problematic docs from future searches.

        Args:
            min_negative_rate: Minimum negative feedback rate (default: 30%)
            min_uses: Minimum usage count for statistical significance

        Returns:
            List of docs with url, negative_feedback_rate, total_uses
        """
        cypher = """
        MATCH (doc:Documentation)
        WHERE doc.negative_feedback_rate >= $min_negative_rate
          AND doc.total_uses >= $min_uses
        RETURN doc.url as url,
               doc.negative_feedback_rate as negative_feedback_rate,
               doc.negative_feedback_count as negative_feedback_count,
               doc.total_uses as total_uses
        ORDER BY doc.negative_feedback_rate DESC
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, {
                "min_negative_rate": min_negative_rate,
                "min_uses": min_uses
            })

            docs = []
            async for record in result:
                docs.append({
                    "url": record["url"],
                    "negative_feedback_rate": round(record["negative_feedback_rate"], 2),
                    "negative_feedback_count": record["negative_feedback_count"],
                    "total_uses": record["total_uses"]
                })

            logger.info(f"[NEO4J]  Found {len(docs)} docs with high negative feedback")
            return docs

    # ========== PHASE 5: GitHub Integration ==========

    async def link_github_url_to_pattern(
        self,
        pattern_id: str,
        github_url: str
    ) -> bool:
        """
        Link GitHub repository URL to a successful pattern

        Stores the GitHub URL as a property on the CodePattern node
        and records the timestamp when it was pushed.

        Args:
            pattern_id: Pattern ID to link GitHub URL to
            github_url: GitHub repository URL

        Returns:
            True if successful, False otherwise
        """
        cypher = """
        MATCH (p:CodePattern {pattern_id: $pattern_id})
        SET p.github_url = $github_url,
            p.github_pushed_at = datetime()
        RETURN p.pattern_id
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(cypher, {
                    "pattern_id": pattern_id,
                    "github_url": github_url
                })

                record = await result.single()
                if record:
                    logger.info(f"[NEO4J]  Linked GitHub URL to pattern {pattern_id}")
                    return True
                else:
                    logger.warning(f"[NEO4J]  Pattern {pattern_id} not found")
                    return False

        except Exception as e:
            logger.error(f"[NEO4J]  Failed to link GitHub URL: {e}")
            return False


async def test_neo4j():
    """Test Neo4j connection"""
    try:
        async with Neo4jRAGClient() as client:
            # Verify connection
            connected = await client.verify_connection()
            if not connected:
                print(" Connection failed")
                return False

            # Test storing a pattern
            pattern_id = await client.store_successful_pattern(
                task="Create a REST API",
                agent_outputs={
                    "architecture": {
                        "code": "Sample architecture...",
                        "galileo_score": 92.0,
                        "latency_ms": 1000,
                        "iterations": 1
                    }
                },
                avg_score=92.0
            )

            print(f" Stored pattern: {pattern_id}")

            # Test retrieval
            patterns = await client.retrieve_similar_patterns("Create API", limit=5)
            print(f" Retrieved {len(patterns)} patterns")

            # Get count
            count = await client.get_pattern_count()
            print(f" Total patterns in database: {count}")

            return True

    except Exception as e:
        print(f" Neo4j test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_neo4j())
