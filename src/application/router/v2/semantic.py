"""Semantic routing using embeddings."""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Any, Protocol

from src.application.router.v2.base import BaseRouter, RouterConfig, RouterStrategy
from src.application.router.v2.context import RoutingContext, RoutingResult, Confidence
from src.application.router.v2.registry import PromptEntry, PromptRegistry

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class EmbedderProtocol(Protocol):
    """Protocol for embedding providers."""

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        ...

    async def aembed(self, text: str) -> list[float]:
        """Async generate embedding for text."""
        ...


class DefaultEmbedder:
    """Default embedder using simple keyword matching as fallback."""

    def embed(self, text: str) -> list[float]:
        """Simple hash-based embedding fallback."""
        words = text.lower().split()
        vec = [0.0] * 64
        for i, word in enumerate(words[:64]):
            vec[i % 64] += hash(word) % 1000
        # Normalize
        magnitude = math.sqrt(sum(x * x for x in vec))
        if magnitude > 0:
            vec = [x / magnitude for x in vec]
        return vec

    async def aembed(self, text: str) -> list[float]:
        """Async version - delegates to sync."""
        return self.embed(text)


class SemanticRouter(BaseRouter[RoutingResult]):
    """
    Semantic routing using embeddings.

    Uses cosine similarity to find the best matching prompt.
    Inspired by LangChain's embedding-based retrieval patterns.
    """

    def __init__(
        self,
        config: RouterConfig | None = None,
        embedder: EmbedderProtocol | None = None,
        threshold: float = 0.7,
        top_k: int = 5,
    ):
        super().__init__(config, "SemanticRouter")
        self._embedder = embedder or DefaultEmbedder()
        self._threshold = threshold
        self._top_k = top_k
        self._variant_embeddings: dict[str, list[float]] = {}

    def build_index(self, variants: Sequence[PromptEntry]) -> None:
        """Pre-compute embeddings for all variants (call at startup)."""
        self._variant_embeddings.clear()
        for variant in variants:
            emb = self._embedder.embed(variant.template[:500])  # Limit length
            self._variant_embeddings[variant.id] = emb
        logger.info(f"Built semantic index for {len(self._variant_embeddings)} variants")

    async def supports(self, context: RoutingContext) -> bool:
        """Always supported - this is the fallback strategy."""
        return True

    async def route(
        self,
        context: RoutingContext,
        candidates: Sequence[PromptEntry] | None = None,
    ) -> RoutingResult | None:
        """Route based on semantic similarity."""
        if not candidates:
            return None

        # Build index if needed
        if not self._variant_embeddings:
            self.build_index(candidates)

        # Embed query
        try:
            query_emb = self._embedder.embed(context.query[:500])
        except Exception as e:
            logger.warning(f"Failed to embed query: {e}")
            return None

        # Compute similarities
        candidates_by_id = {c.id: c for c in candidates}
        scores: list[tuple[PromptEntry, float]] = []

        for variant in candidates:
            variant_emb = self._variant_embeddings.get(variant.id)
            if variant_emb is None:
                # Compute on-demand
                variant_emb = self._embedder.embed(variant.template[:500])
                self._variant_embeddings[variant.id] = variant_emb

            sim = self._cosine_similarity(query_emb, variant_emb)
            scores.append((variant, sim))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        if not scores:
            return None

        best_variant, best_score = scores[0]

        # Adjust confidence based on threshold
        if best_score >= self._threshold:
            confidence = Confidence.HIGH
            confidence_score = best_score
        elif best_score >= 0.5:
            confidence = Confidence.MEDIUM
            confidence_score = best_score
        else:
            confidence = Confidence.LOW
            confidence_score = best_score * 0.5

        # Build alternatives
        alternatives = [
            (v, s) for v, s in scores[1:self._top_k + 1]
        ]

        return RoutingResult(
            prompt_entry=best_variant,
            confidence=confidence,
            confidence_score=confidence_score,
            reasoning=f"Semantic similarity: {best_score:.3f} (threshold={self._threshold})",
            alternative_prompts=alternatives,
            routing_strategy=RouterStrategy.SEMANTIC.value,
        )

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b:
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)
