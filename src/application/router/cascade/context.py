"""Context and result data structures for routing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.router.cascade.registry import PromptEntry


class Confidence(Enum):
    """Confidence levels for routing decisions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

    @classmethod
    def from_score(cls, score: float) -> Confidence:
        """Convert numeric score to confidence level."""
        if score >= 0.8:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MEDIUM
        elif score >= 0.2:
            return cls.LOW
        return cls.NONE


@dataclass
class RoutingContext:
    """
    Context object containing all information needed for routing.

    Attributes:
        query: User's input query or message
        history: Previous conversation turns
        user_id: Optional user identifier
        session_id: Optional session identifier
        metadata: Additional context metadata
        preferences: User preferences for routing
        filters: Filters to apply during routing
    """
    query: str
    history: list[dict[str, Any]] = field(default_factory=list)
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    preferences: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)

    # Internal tracking
    _timestamp: float = field(default_factory=time.time, repr=False)
    _trace_id: str | None = field(default=None, repr=False)

    def with_trace_id(self, trace_id: str) -> RoutingContext:
        """Add trace ID to context."""
        self._trace_id = trace_id
        return self

    def add_to_history(self, role: str, content: str) -> None:
        """Add a turn to conversation history."""
        self.history.append({"role": role, "content": content})

    @property
    def recent_history(self) -> list[dict[str, Any]]:
        """Get last 5 conversation turns."""
        return self.history[-5:] if self.history else []

    def get_keywords(self) -> set[str]:
        """Extract keywords from query."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could"
        }
        words = self.query.lower().split()
        return {w.strip("?!.,:;") for w in words if w.lower() not in stop_words}


@dataclass
class RoutingResult:
    """
    Result of a routing decision.

    Attributes:
        prompt_entry: The matched prompt entry
        confidence: Confidence level of the match
        confidence_score: Numeric confidence score (0-1)
        reasoning: Explanation of why this prompt was chosen
        alternative_prompts: Other possible matches with scores
        metadata: Additional routing metadata
        routing_strategy: Which strategy was used
        latency_ms: Time taken for routing decision
    """
    prompt_entry: "PromptEntry | None" = None
    confidence: Confidence = Confidence.NONE
    confidence_score: float = 0.0
    reasoning: str = ""
    alternative_prompts: list[tuple["PromptEntry", float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    routing_strategy: str = "unknown"
    latency_ms: float = 0.0

    def is_successful(self) -> bool:
        """Check if routing was successful."""
        return self.prompt_entry is not None and self.confidence != Confidence.NONE

    def has_high_confidence(self) -> bool:
        """Check if confidence is high."""
        return self.confidence == Confidence.HIGH

    def get_top_alternatives(self, n: int = 3) -> list["PromptEntry"]:
        """Get top N alternative prompts."""
        sorted_alts = sorted(self.alternative_prompts, key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in sorted_alts[:n]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prompt_id": self.prompt_entry.id if self.prompt_entry else None,
            "prompt_name": self.prompt_entry.name if self.prompt_entry else None,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "routing_strategy": self.routing_strategy,
            "latency_ms": self.latency_ms,
            "alternatives_count": len(self.alternative_prompts),
            "metadata": self.metadata,
        }
