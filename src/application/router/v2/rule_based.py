"""Rule-based routing strategy."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.application.router.v2.base import BaseRouter, RouterConfig, RouterStrategy
from src.application.router.v2.context import RoutingContext, RoutingResult, Confidence
from src.application.router.v2.registry import PromptEntry, PromptRegistry

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


@dataclass
class RoutingRule:
    """A single routing rule."""
    patterns: list[str]
    prompt_id: str
    priority: int = 0
    conditions: dict[str, Any] = field(default_factory=dict)

    def matches(self, text: str) -> bool:
        """Check if text matches any pattern."""
        text_lower = text.lower()
        return any(p.lower() in text_lower for p in self.patterns)


class RuleBasedRouter(BaseRouter[RoutingResult]):
    """
    Fast rule-based routing using keyword matching.

    This is the "fast path" - used when rules can make a deterministic decision.
    No AI/LLM required for routing.
    """

    def __init__(
        self,
        config: RouterConfig | None = None,
        rules: list[RoutingRule] | None = None,
        keyword_map: dict[str, str] | None = None,
    ):
        super().__init__(config, "RuleBasedRouter")
        self._rules = rules or []
        self._keyword_map = keyword_map or {}

        # Build keyword patterns for faster matching
        self._keyword_patterns = {
            kw.lower(): pid for kw, pid in self._keyword_map.items()
        }

    def add_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def add_keyword_mapping(self, keyword: str, prompt_id: str) -> None:
        """Add a keyword → prompt mapping."""
        self._keyword_map[keyword] = prompt_id
        self._keyword_patterns[keyword.lower()] = prompt_id

    async def supports(self, context: RoutingContext) -> bool:
        """Check if this router can handle the context."""
        query_lower = context.query.lower()

        # Check keyword patterns
        if any(kw in query_lower for kw in self._keyword_patterns):
            return True

        # Check rules
        for rule in self._rules:
            if rule.matches(context.query):
                return True

        return False

    async def route(
        self,
        context: RoutingContext,
        candidates: Sequence[PromptEntry] | None = None,
    ) -> RoutingResult | None:
        """Route based on keyword matching."""
        query_lower = context.query.lower()
        candidates_by_id = {c.id: c for c in candidates} if candidates else {}

        # Try keyword matching first
        for keyword, prompt_id in self._keyword_patterns.items():
            if keyword in query_lower:
                prompt_entry = candidates_by_id.get(prompt_id)
                if prompt_entry:
                    return RoutingResult(
                        prompt_entry=prompt_entry,
                        confidence=Confidence.HIGH,
                        confidence_score=0.95,
                        reasoning=f"Keyword '{keyword}' matched",
                        routing_strategy=RouterStrategy.RULE_BASED.value,
                    )

        # Try rule matching
        for rule in self._rules:
            if rule.matches(context.query):
                prompt_entry = candidates_by_id.get(rule.prompt_id)
                if prompt_entry:
                    return RoutingResult(
                        prompt_entry=prompt_entry,
                        confidence=Confidence.HIGH,
                        confidence_score=0.90,
                        reasoning=f"Rule matched: {rule.patterns}",
                        routing_strategy=RouterStrategy.RULE_BASED.value,
                    )

        # No match found
        if self.config.mode == RoutingMode.FALLBACK and candidates:
            return RoutingResult(
                prompt_entry=candidates[0],
                confidence=Confidence.LOW,
                confidence_score=0.1,
                reasoning="No rule matched, using fallback",
                routing_strategy=RouterStrategy.RULE_BASED.value,
            )

        return None
