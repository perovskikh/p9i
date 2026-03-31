"""Hybrid router combining multiple strategies."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.application.router.v2.base import BaseRouter, RouterConfig, RouterStrategy
from src.application.router.v2.context import RoutingContext, RoutingResult, Confidence
from src.application.router.v2.registry import PromptEntry

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.application.router.v2.rule_based import RuleBasedRouter
    from src.application.router.v2.semantic import SemanticRouter
    from src.application.router.v2.llm import LLMRouter

logger = logging.getLogger(__name__)


@dataclass
class HybridConfig:
    """Configuration for hybrid router."""
    rule_confidence_threshold: float = 0.9
    semantic_confidence_threshold: float = 0.7
    use_llm_fallback: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300


class HybridPromptRouter:
    """
    Hybrid router that combines rule-based, semantic, and LLM routing.

    Follows the LangChain LCEL (LangChain Expression Language) pattern
    of composing runnables into chains.

    Routing cascade:
      1. Rule-based (fast path) — if confidence >= 0.9
      2. Semantic (medium path) — if confidence >= 0.7
      3. LLM (slow path) — as last resort
    """

    def __init__(
        self,
        config: RouterConfig | None = None,
        rule_router: "RuleBasedRouter | None" = None,
        semantic_router: "SemanticRouter | None" = None,
        llm_router: "LLMRouter | None" = None,
        hybrid_config: HybridConfig | None = None,
    ):
        self.config = config or RouterConfig()
        self.hybrid_config = hybrid_config or HybridConfig()

        # Initialize routers
        from src.application.router.v2.rule_based import RuleBasedRouter
        from src.application.router.v2.semantic import SemanticRouter
        from src.application.router.v2.llm import LLMRouter

        self._rule = rule_router or RuleBasedRouter(self.config)
        self._semantic = semantic_router or SemanticRouter(self.config)
        self._llm = llm_router

        # Cache
        self._cache: dict[str, tuple[RoutingResult, float]] = {}
        self._cache_ttl = self.hybrid_config.cache_ttl_seconds

        # Metrics
        self._metrics: dict[str, int] = {
            "rule_hits": 0,
            "semantic_hits": 0,
            "llm_hits": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        self._logger = logging.getLogger(f"{__name__}.HybridPromptRouter")

    def register_prompts(self, variants: Sequence[PromptEntry]) -> None:
        """Register all available prompt variants."""
        self._variants = list(variants)
        self._semantic.build_index(self._variants)
        self._logger.info(f"Registered {len(self._variants)} prompt variants")

    async def route(
        self,
        context: RoutingContext,
    ) -> RoutingResult:
        """Main routing entry point."""
        start = time.perf_counter()

        # 1. Check cache
        if self.hybrid_config.enable_caching:
            cached = self._get_cached(context.query)
            if cached:
                self._metrics["cache_hits"] += 1
                self._logger.debug("Cache hit for routing")
                return cached
            self._metrics["cache_misses"] += 1

        result = None

        # 2. Rule-based routing (fast path)
        if await self._rule.supports(context):
            result = await self._rule.route(context, self._variants)
            if result and result.confidence_score >= self.hybrid_config.rule_confidence_threshold:
                self._metrics["rule_hits"] += 1
                return self._finish(context, result, start)

        # 3. Semantic routing
        result = await self._semantic.route(context, self._variants)
        if result and result.confidence_score >= self.hybrid_config.semantic_confidence_threshold:
            self._metrics["semantic_hits"] += 1
            return self._finish(context, result, start)

        # 4. LLM routing (slow path)
        if self._llm and self.hybrid_config.use_llm_fallback:
            if await self._llm.supports(context):
                result = await self._llm.route(context, self._variants)
                if result:
                    self._metrics["llm_hits"] += 1
                    return self._finish(context, result, start)

        # 5. Ultimate fallback
        if self._variants:
            result = RoutingResult(
                prompt_entry=self._variants[0],
                confidence=Confidence.LOW,
                confidence_score=0.3,
                reasoning="All strategies returned low confidence, using default",
                routing_strategy=RouterStrategy.HYBRID.value,
            )
            self._metrics["semantic_hits"] += 1  # Count as semantic hit
        else:
            result = RoutingResult(
                prompt_entry=None,
                confidence=Confidence.NONE,
                confidence_score=0.0,
                reasoning="No prompts registered",
                routing_strategy=RouterStrategy.HYBRID.value,
            )

        return self._finish(context, result, start)

    def route_sync(self, context: RoutingContext) -> RoutingResult:
        """Synchronous wrapper for non-async contexts."""
        import asyncio
        return asyncio.run(self.route(context))

    def _finish(
        self,
        context: RoutingContext,
        result: RoutingResult,
        start: float,
    ) -> RoutingResult:
        """Complete routing with timing and caching."""
        result.latency_ms = (time.perf_counter() - start) * 1000

        # Cache result
        if self.hybrid_config.enable_caching and result.is_successful():
            self._cache[context.query] = (result, time.time())

        self._logger.info(
            f"Routed to {result.prompt_entry.name if result.prompt_entry else 'None'} "
            f"with {result.confidence_score:.2f} confidence "
            f"({result.routing_strategy}) in {result.latency_ms:.1f}ms"
        )

        return result

    def _get_cached(self, query: str) -> RoutingResult | None:
        """Get cached result if not expired."""
        if query not in self._cache:
            return None

        result, timestamp = self._cache[query]
        if time.time() - timestamp > self._cache_ttl:
            del self._cache[query]
            return None

        return result

    def get_metrics(self) -> dict[str, int]:
        """Get routing metrics."""
        return self._metrics.copy()

    def clear_cache(self) -> None:
        """Clear the routing cache."""
        self._cache.clear()
        self._logger.info("Routing cache cleared")
