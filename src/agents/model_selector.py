"""
Intelligent Model Selection for Task-Based Fallback

Analyzes task requirements and selects the best model, with automatic
fallback to alternative models if quality threshold isn't met.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class TaskType(Enum):
    """Types of development tasks"""
    WEB_FRONTEND = "web_frontend"
    BACKEND_API = "backend_api"
    DATA_SCIENCE = "data_science"
    MOBILE = "mobile"
    DEVOPS = "devops"
    DATABASE = "database"
    GENERAL = "general"


class ModelSelector:
    """
    Selects optimal models for different task types

    Provides intelligent fallback when primary model fails to meet
    quality threshold after max iterations.
    """

    # Model capabilities and pricing (tokens/$)
    MODEL_PROFILES = {
        "gpt-5-pro": {
            "strengths": ["web", "modern_frameworks", "react", "vue", "typescript", "rapid_prototyping"],
            "weaknesses": ["complex_architecture", "low_level_systems"],
            "speed": "fast",
            "cost_per_1k_tokens": 0.015,
            "reasoning": "medium"
        },
        "claude-opus-4.1": {
            "strengths": ["complex_logic", "architecture", "error_handling", "security", "backend", "refactoring"],
            "weaknesses": ["rapid_iteration", "modern_web_patterns"],
            "speed": "slow",
            "cost_per_1k_tokens": 0.075,
            "reasoning": "excellent"
        },
        "claude-sonnet-4.5": {
            "strengths": ["architecture", "clean_code", "balanced", "general_purpose"],
            "weaknesses": ["cutting_edge_features"],
            "speed": "medium",
            "cost_per_1k_tokens": 0.015,
            "reasoning": "excellent"
        },
        "grok-4": {
            "strengths": ["testing", "edge_cases", "creative_solutions"],
            "weaknesses": ["production_code", "strict_patterns"],
            "speed": "medium",
            "cost_per_1k_tokens": 0.010,
            "reasoning": "good"
        }
    }

    # Task type → Ordered list of models (primary, fallback1, fallback2, ...)
    TASK_MODEL_PREFERENCES = {
        TaskType.WEB_FRONTEND: [
            "gpt-5-pro",          # Best at modern web
            "claude-sonnet-4.5",  # Good architecture
            "claude-opus-4.1"     # Last resort (slower but thorough)
        ],
        TaskType.BACKEND_API: [
            "claude-opus-4.1",    # Best at complex logic
            "gpt-5-pro",          # Fast alternative
            "claude-sonnet-4.5"   # Balanced
        ],
        TaskType.DATA_SCIENCE: [
            "gpt-5-pro",          # Trained on ML code
            "claude-opus-4.1",    # Good at algorithms
            "claude-sonnet-4.5"
        ],
        TaskType.MOBILE: [
            "gpt-5-pro",          # Good at Swift/Kotlin
            "claude-sonnet-4.5",
            "claude-opus-4.1"
        ],
        TaskType.DEVOPS: [
            "claude-opus-4.1",    # Best at infrastructure
            "gpt-5-pro",
            "claude-sonnet-4.5"
        ],
        TaskType.DATABASE: [
            "claude-opus-4.1",    # Best at complex queries
            "claude-sonnet-4.5",
            "gpt-5-pro"
        ],
        TaskType.GENERAL: [
            "claude-sonnet-4.5",  # Most balanced
            "gpt-5-pro",
            "claude-opus-4.1"
        ]
    }

    @staticmethod
    def detect_task_type(task: str, context: Dict[str, Any] = None) -> TaskType:
        """
        Analyze task description to determine task type

        Args:
            task: User's task description
            context: Optional context (architecture, vision analysis, etc.)

        Returns:
            TaskType enum
        """
        task_lower = task.lower()

        # Check for web frontend keywords
        web_keywords = [
            "website", "web", "html", "css", "react", "vue", "angular",
            "frontend", "ui", "interface", "page", "landing", "portfolio",
            "button", "form", "navbar", "header", "footer", "responsive"
        ]
        if any(kw in task_lower for kw in web_keywords):
            return TaskType.WEB_FRONTEND

        # Check for backend/API keywords
        backend_keywords = [
            "api", "backend", "server", "endpoint", "database query",
            "rest", "graphql", "microservice", "authentication", "crud"
        ]
        if any(kw in task_lower for kw in backend_keywords):
            return TaskType.BACKEND_API

        # Check for data science keywords
        ds_keywords = [
            "machine learning", "ml", "data analysis", "pandas",
            "numpy", "tensorflow", "pytorch", "model", "prediction",
            "classification", "regression", "neural network"
        ]
        if any(kw in task_lower for kw in ds_keywords):
            return TaskType.DATA_SCIENCE

        # Check for mobile keywords
        mobile_keywords = [
            "mobile app", "ios", "android", "swift", "kotlin",
            "react native", "flutter", "mobile"
        ]
        if any(kw in task_lower for kw in mobile_keywords):
            return TaskType.MOBILE

        # Check for DevOps keywords
        devops_keywords = [
            "docker", "kubernetes", "k8s", "ci/cd", "pipeline",
            "terraform", "ansible", "infrastructure", "deployment"
        ]
        if any(kw in task_lower for kw in devops_keywords):
            return TaskType.DEVOPS

        # Check for database keywords
        db_keywords = [
            "database", "sql", "postgresql", "mysql", "mongodb",
            "query", "schema", "migration", "orm"
        ]
        if any(kw in task_lower for kw in db_keywords):
            return TaskType.DATABASE

        # Default to general
        return TaskType.GENERAL

    @staticmethod
    def get_model_sequence(task_type: TaskType) -> List[str]:
        """
        Get ordered list of models to try for this task type

        Args:
            task_type: Type of task

        Returns:
            List of model names in order of preference
        """
        return ModelSelector.TASK_MODEL_PREFERENCES.get(
            task_type,
            ModelSelector.TASK_MODEL_PREFERENCES[TaskType.GENERAL]
        )

    @staticmethod
    def get_next_model(
        current_model: str,
        task_type: TaskType,
        attempts_with_current: int
    ) -> Optional[str]:
        """
        Get the next model to try after current model failed

        Args:
            current_model: Current model that's failing
            task_type: Type of task
            attempts_with_current: Number of attempts with current model

        Returns:
            Next model to try, or None if no more fallbacks
        """
        model_sequence = ModelSelector.get_model_sequence(task_type)

        try:
            current_index = model_sequence.index(current_model)
            next_index = current_index + 1

            if next_index < len(model_sequence):
                return model_sequence[next_index]
            else:
                return None  # No more fallbacks
        except ValueError:
            # Current model not in sequence, start from beginning
            return model_sequence[0] if model_sequence else None

    @staticmethod
    def should_fallback(
        iterations_completed: int,
        max_iterations: int,
        best_score: float,
        quality_threshold: float,
        score_improvement: float
    ) -> bool:
        """
        Determine if we should switch to fallback model

        Args:
            iterations_completed: How many iterations we've done
            max_iterations: Max iterations allowed per model
            best_score: Best score achieved so far
            quality_threshold: Required threshold
            score_improvement: Improvement from first to last iteration

        Returns:
            True if should switch to fallback model
        """
        # Completed all iterations without reaching threshold
        if iterations_completed >= max_iterations and best_score < quality_threshold:
            return True

        # Score is getting worse (model is struggling)
        if score_improvement < 0 and iterations_completed >= 2:
            return True

        # Score plateaued (< 1 point improvement over last 2 iterations)
        if score_improvement < 1.0 and iterations_completed >= max_iterations - 1:
            return True

        return False

    @staticmethod
    def get_fallback_rationale(
        current_model: str,
        next_model: str,
        task_type: TaskType,
        best_score: float,
        quality_threshold: float
    ) -> str:
        """
        Generate human-readable explanation for model fallback

        Returns:
            Explanation string for logging
        """
        current_profile = ModelSelector.MODEL_PROFILES.get(current_model, {})
        next_profile = ModelSelector.MODEL_PROFILES.get(next_model, {})

        rationale = f"""
🔄 MODEL FALLBACK TRIGGERED

Current: {current_model} (best score: {best_score:.1f}/100, threshold: {quality_threshold})
Next: {next_model}

Reason: {current_model} reached max iterations without meeting quality threshold.

{next_model} strengths for {task_type.value}:
"""

        strengths = next_profile.get("strengths", [])
        for strength in strengths[:3]:  # Top 3 strengths
            rationale += f"  • {strength.replace('_', ' ').title()}\n"

        return rationale
