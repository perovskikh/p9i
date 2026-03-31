"""
Router V2 - Advanced Prompt Routing System

Multi-strategy routing combining:
- Rule-based matching
- Semantic similarity
- LLM classification
"""

from src.application.router.cascade.base import BaseRouter, RouterStrategy, RoutingMode, RouterConfig
from src.application.router.cascade.context import RoutingContext, RoutingResult, Confidence
from src.application.router.cascade.registry import PromptRegistry, PromptEntry, PromptMetadata, PromptCategory, PromptPriority
from src.application.router.cascade.rule_based import RuleBasedRouter
from src.application.router.cascade.semantic import SemanticRouter
from src.application.router.cascade.llm import LLMRouter
from src.application.router.cascade.hybrid import HybridPromptRouter

__all__ = [
    # Base
    "BaseRouter",
    "RouterStrategy",
    "RoutingMode",
    "RouterConfig",
    # Context & Results
    "RoutingContext",
    "RoutingResult",
    "Confidence",
    # Registry
    "PromptRegistry",
    "PromptEntry",
    "PromptMetadata",
    "PromptCategory",
    "PromptPriority",
    # Routers
    "RuleBasedRouter",
    "SemanticRouter",
    "LLMRouter",
    "HybridPromptRouter",
]
