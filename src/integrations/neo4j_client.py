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
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store successful code generation pattern (90+ quality)

        Args:
            task: Original user task
            agent_outputs: Dict mapping agent_name -> {code, galileo_score, etc}
            avg_score: Average Galileo score across all agents
            metadata: Optional additional metadata

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

        logger.info(f"[NEO4J]  Stored pattern {pattern_id} (score: {avg_score})")
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
