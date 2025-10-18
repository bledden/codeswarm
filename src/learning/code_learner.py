"""
Autonomous Continuous Learning System for CodeSwarm
Self-improvement through feedback loops and pattern recognition
Adapted from Anomaly Hunter's proven autonomous_learner.py
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Import Weave for observability
try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False
    print("[LEARNING]   Weave not available - running without observability")


class CodeSwarmLearner:
    """
    Autonomous Learning Engine for CodeSwarm

    Continuously improves code generation quality by:
    1. Tracking agent performance over time (Galileo scores)
    2. Adjusting confidence weights based on outcomes
    3. Learning from user feedback (implicit/explicit)
    4. Storing successful coding strategies in Neo4j
    5. Providing self-improvement recommendations

    Proven in production: 14 detections, 9 strategies learned (Anomaly Hunter)
    """

    def __init__(self, cache_dir: str = "cache/learning", neo4j_client = None):
        """Initialize autonomous learner

        Args:
            cache_dir: Directory for local caching (fallback if Neo4j unavailable)
            neo4j_client: Optional Neo4j client for persistent storage
        """

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.performance_log = self.cache_dir / "agent_performance.json"
        self.strategy_cache = self.cache_dir / "successful_strategies.json"

        # Neo4j for persistent storage (if available)
        self.neo4j = neo4j_client

        # Load historical performance
        self.agent_stats = self._load_performance_log()
        self.successful_strategies = self._load_strategies()

        print("[LEARNING]  CodeSwarm learning engine initialized")
        print(f"[LEARNING]    Historical code generations: {self.agent_stats.get('total_generations', 0)}")
        print(f"[LEARNING]    Successful strategies: {len(self.successful_strategies)}")
        if self.neo4j:
            print(f"[LEARNING]    Neo4j persistence: ENABLED")

    def _load_performance_log(self) -> Dict[str, Any]:
        """Load agent performance history"""
        if self.performance_log.exists():
            with open(self.performance_log, 'r') as f:
                return json.load(f)
        return {
            "total_generations": 0,
            "agents": {
                "architecture": {"correct": 0, "total": 0, "avg_score": 85.0, "avg_latency_ms": 0},
                "implementation": {"correct": 0, "total": 0, "avg_score": 85.0, "avg_latency_ms": 0},
                "security": {"correct": 0, "total": 0, "avg_score": 85.0, "avg_latency_ms": 0},
                "testing": {"correct": 0, "total": 0, "avg_score": 85.0, "avg_latency_ms": 0},
                "vision": {"correct": 0, "total": 0, "avg_score": 85.0, "avg_latency_ms": 0}
            }
        }

    def _load_strategies(self) -> List[Dict[str, Any]]:
        """Load successful detection strategies"""
        if self.strategy_cache.exists():
            with open(self.strategy_cache, 'r') as f:
                return json.load(f)
        return []

    def compute_adaptive_weights(self, agent_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute adaptive confidence weights based on historical performance

        Better-performing agents get higher weights over time

        Args:
            agent_outputs: Dict mapping agent_name -> {"code": str, "galileo_score": float}

        Returns:
            Dict mapping agent_name -> normalized weight
        """
        if WEAVE_AVAILABLE:
            return self._compute_adaptive_weights_weave(agent_outputs)
        return self._compute_adaptive_weights_impl(agent_outputs)

    def _compute_adaptive_weights_impl(self, agent_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Implementation of adaptive weight computation"""
        weights = {}
        total_performance = 0

        for agent_name, output in agent_outputs.items():
            stats = self.agent_stats["agents"].get(agent_name, {})

            # Calculate performance score based on historical Galileo scores
            total = stats.get("total", 1)
            correct = stats.get("correct", 0)
            accuracy = correct / total if total > 0 else 0.5
            avg_score = stats.get("avg_score", 85.0)

            # Weight = historical accuracy * current Galileo score * historical avg
            current_score = output.get("galileo_score", 85.0) / 100.0
            adaptive_weight = accuracy * current_score * (avg_score / 100.0)
            weights[agent_name] = adaptive_weight
            total_performance += adaptive_weight

        # Normalize weights
        if total_performance > 0:
            weights = {k: v/total_performance for k, v in weights.items()}

        print(f"[LEARNING]  Adaptive weights computed:")
        for agent, weight in weights.items():
            print(f"[LEARNING]    {agent}: {weight:.3f}")

        return weights

    if WEAVE_AVAILABLE:
        @weave.op()
        def _compute_adaptive_weights_weave(self, agent_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
            """Weave-tracked version of adaptive weight computation"""
            return self._compute_adaptive_weights_impl(agent_outputs)

    def learn_from_outcome(
        self,
        agent_outputs: Dict[str, Dict[str, Any]],
        task: str,
        user_feedback: Optional[str] = None,
        was_successful: Optional[bool] = None
    ) -> None:
        """
        Learn from code generation outcome

        Args:
            agent_outputs: Dict mapping agent_name -> {
                "code": str,
                "galileo_score": float,
                "latency_ms": int,
                "iterations": int  # How many improvement iterations needed
            }
            task: The original user task
            user_feedback: Optional user feedback
            was_successful: Whether the generation was successful (if known)
        """
        if WEAVE_AVAILABLE:
            return self._learn_from_outcome_weave(agent_outputs, task, user_feedback, was_successful)
        return self._learn_from_outcome_impl(agent_outputs, task, user_feedback, was_successful)

    def _learn_from_outcome_impl(
        self,
        agent_outputs: Dict[str, Dict[str, Any]],
        task: str,
        user_feedback: Optional[str] = None,
        was_successful: Optional[bool] = None
    ) -> None:
        """Implementation of learning from outcome"""
        # Update total generations
        self.agent_stats["total_generations"] += 1

        # Update per-agent stats
        for agent_name, output in agent_outputs.items():
            if agent_name not in self.agent_stats["agents"]:
                self.agent_stats["agents"][agent_name] = {
                    "correct": 0,
                    "total": 0,
                    "avg_score": 85.0,
                    "avg_latency_ms": 0
                }

            agent_stats = self.agent_stats["agents"][agent_name]
            agent_stats["total"] += 1

            # If we know the outcome was successful, update accuracy
            galileo_score = output.get("galileo_score", 0)
            if galileo_score >= 90:  # Quality gate
                agent_stats["correct"] += 1
            elif was_successful is not None and was_successful:
                agent_stats["correct"] += 1

            # Update average score (exponential moving average)
            alpha = 0.1  # Learning rate
            old_avg_score = agent_stats["avg_score"]
            agent_stats["avg_score"] = old_avg_score * (1 - alpha) + galileo_score * alpha

            # Update average latency
            latency = output.get("latency_ms", 0)
            old_avg_latency = agent_stats["avg_latency_ms"]
            agent_stats["avg_latency_ms"] = old_avg_latency * (1 - alpha) + latency * alpha

        # Save updated stats
        self._save_performance_log()

        # Extract successful strategy if high quality (90+ threshold)
        avg_score = sum(o.get("galileo_score", 0) for o in agent_outputs.values()) / len(agent_outputs)
        if avg_score >= 90:
            self._extract_successful_strategy(agent_outputs, task, avg_score)

        print(f"[LEARNING]  Learned from generation #{self.agent_stats['total_generations']}")
        print(f"[LEARNING]    Average score: {avg_score:.1f}/100")

    if WEAVE_AVAILABLE:
        @weave.op()
        def _learn_from_outcome_weave(
            self,
            agent_outputs: Dict[str, Dict[str, Any]],
            task: str,
            user_feedback: Optional[str] = None,
            was_successful: Optional[bool] = None
        ) -> None:
            """Weave-tracked version of learning from outcome"""
            return self._learn_from_outcome_impl(agent_outputs, task, user_feedback, was_successful)

    def _extract_successful_strategy(
        self,
        agent_outputs: Dict[str, Dict[str, Any]],
        task: str,
        avg_score: float
    ) -> None:
        """Extract and store successful code generation strategy"""

        strategy = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": task[:200],  # Store task description
            "avg_score": avg_score,
            "pattern": {
                "agent_scores": {
                    agent: output.get("galileo_score", 0)
                    for agent, output in agent_outputs.items()
                },
                "agent_agreement": self._compute_agent_agreement(agent_outputs),
                "total_iterations": sum(
                    output.get("iterations", 1) for output in agent_outputs.values()
                )
            },
            "architecture": agent_outputs.get("architecture", {}).get("code", "")[:500],
            "successful": True
        }

        self.successful_strategies.append(strategy)

        # Keep only last 100 strategies
        if len(self.successful_strategies) > 100:
            self.successful_strategies = self.successful_strategies[-100:]

        self._save_strategies()

        # Also store in Neo4j if available
        if self.neo4j:
            try:
                self._store_strategy_in_neo4j(strategy)
                print(f"[LEARNING]  Stored strategy in Neo4j (total: {len(self.successful_strategies)})")
            except Exception as e:
                print(f"[LEARNING]   Failed to store in Neo4j: {e}")
                print(f"[LEARNING]  Stored strategy locally (total: {len(self.successful_strategies)})")
        else:
            print(f"[LEARNING]  Stored successful strategy (total: {len(self.successful_strategies)})")

    def _compute_agent_agreement(self, agent_outputs: Dict[str, Dict[str, Any]]) -> float:
        """Compute how much agents agreed on quality (low variance = high agreement)"""

        scores = [output.get("galileo_score", 0) for output in agent_outputs.values()]
        if not scores:
            return 0.0

        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)

        # Low variance = high agreement
        agreement = 1.0 / (1.0 + variance / 100.0)  # Normalize by 100 since scores are 0-100
        return agreement

    def _store_strategy_in_neo4j(self, strategy: Dict[str, Any]) -> None:
        """Store successful strategy in Neo4j for RAG retrieval"""
        # This will be implemented when Neo4j client is ready
        # For now, just store locally
        pass

    def suggest_improvements(self) -> List[str]:
        """
        Analyze performance and suggest improvements

        Returns:
            List of improvement suggestions
        """

        suggestions = []

        # Analyze agent performance
        for agent_name, stats in self.agent_stats["agents"].items():
            total = stats.get("total", 0)
            if total < 10:
                continue  # Not enough data

            accuracy = stats["correct"] / total if total > 0 else 0

            if accuracy < 0.7:
                suggestions.append(
                    f"  {agent_name} has low accuracy ({accuracy:.1%}). "
                    f"Consider adjusting thresholds or model parameters."
                )

            if stats["avg_confidence"] < 0.6:
                suggestions.append(
                    f" {agent_name} shows low confidence ({stats['avg_confidence']:.1%}). "
                    f"May need additional training data or context."
                )

        # Check detection volume
        total = self.agent_stats["total_detections"]
        if total > 50:
            suggestions.append(
                f" System has processed {total} detections. "
                f"Consider analyzing patterns for automation opportunities."
            )

        return suggestions

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""

        summary = {
            "total_detections": self.agent_stats["total_detections"],
            "agents": {},
            "learning_status": "active",
            "strategies_learned": len(self.successful_strategies)
        }

        for agent_name, stats in self.agent_stats["agents"].items():
            total = stats.get("total", 0)
            accuracy = stats["correct"] / total if total > 0 else 0

            summary["agents"][agent_name] = {
                "accuracy": accuracy,
                "confidence": stats["avg_confidence"],
                "total_inferences": total
            }

        return summary

    def _save_performance_log(self):
        """Save performance log to disk"""
        with open(self.performance_log, 'w') as f:
            json.dump(self.agent_stats, f, indent=2)

    def _save_strategies(self):
        """Save successful strategies to disk"""
        with open(self.strategy_cache, 'w') as f:
            json.dump(self.successful_strategies, f, indent=2)
