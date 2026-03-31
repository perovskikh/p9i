"""Base classes and interfaces for routers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar, Generic

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RouterStrategy(Enum):
    """Available routing strategies."""
    RULE_BASED = "rule_based"
    SEMANTIC = "semantic"
    LLM = "llm"
    HYBRID = "hybrid"


class RoutingMode(Enum):
    """Routing execution modes."""
    STRICT = "strict"  # Must return a result
    FLEXIBLE = "flexible"  # Can return None
    FALLBACK = "fallback"  # Use default if no match


@dataclass
class RouterConfig:
    """Configuration for router behavior."""
    mode: RoutingMode = RoutingMode.FLEXIBLE
    min_confidence: float = 0.5
    timeout_seconds: float = 30.0
    cache_enabled: bool = True
    fallback_prompt_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseRouter(ABC, Generic[T]):
    """Abstract base class for all routers."""

    def __init__(
        self,
        config: RouterConfig | None = None,
        name: str | None = None,
    ):
        self.config = config or RouterConfig()
        self.name = name or self.__class__.__name__
        self._logger = logging.getLogger(f"{__name__}.{self.name}")

    @abstractmethod
    async def route(self, context: Any) -> T | None:
        """Route the request based on context."""
        pass

    @abstractmethod
    async def supports(self, context: Any) -> bool:
        """Check if this router supports the given context."""
        pass

    def _log_routing(self, context: Any, result: T | None) -> None:
        """Log routing decision."""
        self._logger.debug(
            f"Routing decision for context type={type(context).__name__}: "
            f"result={'found' if result else 'not found'}"
        )

    def validate_result(self, result: T | None) -> bool:
        """Validate routing result."""
        return result is not None or self.config.mode != RoutingMode.STRICT
