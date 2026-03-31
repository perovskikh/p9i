"""LLM-based routing strategy."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from src.application.router.cascade.base import BaseRouter, RouterConfig, RouterStrategy
from src.application.router.cascade.context import RoutingContext, RoutingResult, Confidence
from src.application.router.cascade.registry import PromptEntry, PromptRegistry

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class LLMClientProtocol(Protocol):
    """Protocol for LLM clients."""

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> str:
        """Generate response from LLM."""
        ...

    async def agenerate(
        self,
        prompt: str,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> str:
        """Async generate response from LLM."""
        ...


# Default router prompt for LLM-based routing
DEFAULT_ROUTER_PROMPT = """You are a prompt routing expert. Given a user query and available
prompt variants, select the most appropriate one.

Available prompts:
{prompts}

User query: {query}

Respond with JSON:
{{
    "selected_prompt": "prompt_id",
    "confidence": 0.0-1.0,
    "reasoning": "why this prompt is best",
    "alternatives": [["alt_id", 0.5], ...]
}}
"""


@dataclass
class LLMRouter(BaseRouter[RoutingResult]):
    """
    LLM-powered routing.

    Uses a language model to decide which prompt variant fits best.
    Inspired by LangChain's ChatPromptTemplate + tool calling pattern.

    Uses structured output (JSON mode) for deterministic routing.
    """

    def __init__(
        self,
        config: RouterConfig | None = None,
        llm_client: LLMClientProtocol | None = None,
        router_prompt: str | None = None,
        temperature: float = 0.0,
        max_retries: int = 2,
    ):
        super().__init__(config, "LLMRouter")
        self._llm = llm_client
        self._router_prompt = router_prompt or DEFAULT_ROUTER_PROMPT
        self._temperature = temperature
        self._max_retries = max_retries

    async def supports(self, context: RoutingContext) -> bool:
        """Use LLM when explicitly requested or as last resort."""
        return context.metadata.get("use_llm", False)

    async def route(
        self,
        context: RoutingContext,
        candidates: Sequence[PromptEntry] | None = None,
    ) -> RoutingResult | None:
        """Route using LLM decision-making."""
        if not self._llm or not candidates:
            return None

        candidate_descriptions = self._build_candidate_summary(candidates)

        for attempt in range(self._max_retries):
            try:
                result = self._call_llm(context.query, candidate_descriptions, candidates)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"LLM routing attempt {attempt + 1} failed: {e}")

        # Ultimate fallback
        if candidates:
            return RoutingResult(
                prompt_entry=candidates[0],
                confidence=Confidence.LOW,
                confidence_score=0.1,
                reasoning="LLM routing failed, using default",
                routing_strategy=RouterStrategy.LLM.value,
            )

        return None

    def _call_llm(
        self,
        query: str,
        candidate_descriptions: str,
        candidates: list[PromptEntry],
    ) -> RoutingResult | None:
        """Call LLM and parse response."""
        candidates_by_id = {c.id: c for c in candidates}

        prompt = self._router_prompt.format(
            prompts=candidate_descriptions,
            query=query,
        )

        # Try async first, then sync
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # We're in async context
            response = asyncio.run(self._llm.agenerate(
                prompt,
                temperature=self._temperature,
                json_mode=True,
            ))
        except RuntimeError:
            # Not in async context
            response = self._llm.generate(
                prompt,
                temperature=self._temperature,
                json_mode=True,
            )

        # Parse structured response
        try:
            data = json.loads(response)
            selected_id = data.get("selected_prompt")
            reasoning = data.get("reasoning", "")
            confidence = float(data.get("confidence", 0.5))
            alternatives_raw = data.get("alternatives", [])

            if selected_id and selected_id in candidates_by_id:
                alternatives = []
                for alt_id, conf in alternatives_raw:
                    if alt_id in candidates_by_id:
                        alternatives.append((candidates_by_id[alt_id], conf))

                return RoutingResult(
                    prompt_entry=candidates_by_id[selected_id],
                    confidence=Confidence.from_score(confidence),
                    confidence_score=confidence,
                    reasoning=reasoning,
                    alternative_prompts=alternatives,
                    routing_strategy=RouterStrategy.LLM.value,
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")

        return None

    def _build_candidate_summary(self, candidates: list[PromptEntry]) -> str:
        """Build a summary of candidates for the LLM prompt."""
        lines = []
        for i, v in enumerate(candidates, 1):
            tags_str = ", ".join(sorted(v.metadata.tags)) if v.metadata.tags else "none"
            lines.append(
                f"{i}. ID: {v.id}\n"
                f"   Name: {v.name}\n"
                f"   Description: {v.metadata.description or 'N/A'}\n"
                f"   Tags: [{tags_str}]"
            )
        return "\n\n".join(lines)
