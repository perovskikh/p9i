"""Prompt registry for managing available prompts."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Iterator


class PromptCategory(Enum):
    """Categories for organizing prompts."""
    GENERAL = "general"
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    QA = "qa"
    CUSTOM = "custom"


class PromptPriority(Enum):
    """Priority levels for prompts."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class PromptMetadata:
    """Metadata for a prompt."""
    category: PromptCategory = PromptCategory.GENERAL
    tags: set[str] = field(default_factory=set)
    priority: PromptPriority = PromptPriority.MEDIUM
    version: str = "1.0.0"
    author: str | None = None
    description: str = ""
    examples: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def matches_tags(self, query_tags: set[str]) -> bool:
        """Check if any query tags match prompt tags."""
        if not query_tags:
            return True
        return bool(self.tags & query_tags)

    def matches_category(self, query_category: PromptCategory | None) -> bool:
        """Check if category matches."""
        if query_category is None:
            return True
        return self.category == query_category


@dataclass
class PromptEntry:
    """
    A registered prompt entry.

    Attributes:
        id: Unique identifier
        name: Human-readable name
        template: The prompt template (supports {variable} interpolation)
        metadata: Prompt metadata
        rules: Optional routing rules
        examples: Example inputs that match this prompt
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template: str = ""
    metadata: PromptMetadata = field(default_factory=PromptMetadata)
    rules: list[dict[str, Any]] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    # Pre-computed fields for faster matching
    _keywords: set[str] = field(default_factory=set, repr=False)
    _keyword_pattern: re.Pattern | None = field(default=None, repr=False)

    def __post_init__(self):
        """Compute derived fields after initialization."""
        if not self.name:
            self.name = f"prompt_{self.id[:8]}"

        # Extract keywords from template
        self._keywords = self._extract_keywords(self.template)

        # Build keyword pattern
        if self._keywords:
            pattern_str = "|".join(re.escape(k) for k in self._keywords)
            self._keyword_pattern = re.compile(pattern_str, re.IGNORECASE)

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        """Extract meaningful keywords from text."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can",
            "please", "thanks", "thank", "you", "i", "me", "my"
        }
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        return {w for w in words if w not in stop_words}

    def matches_keyword(self, text: str) -> bool:
        """Check if text contains any keywords from this prompt."""
        if not self._keyword_pattern:
            return False
        return bool(self._keyword_pattern.search(text.lower()))

    def matches_example(self, query: str, similarity_fn: Callable[[str, str], float], threshold: float = 0.7) -> float:
        """Check if query matches any example and return best similarity."""
        if not self.examples:
            return 0.0

        max_similarity = 0.0
        for example in self.examples:
            sim = similarity_fn(query, example)
            max_similarity = max(max_similarity, sim)

        return max_similarity if max_similarity >= threshold else 0.0

    def render(self, **kwargs: Any) -> str:
        """Render the prompt template with variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def matches_rules(self, context: dict[str, Any]) -> bool:
        """Check if context matches any routing rules."""
        if not self.rules:
            return True  # No rules = always matches

        for rule in self.rules:
            if self._evaluate_rule(rule, context):
                return True
        return False

    def _evaluate_rule(self, rule: dict[str, Any], context: dict[str, Any]) -> bool:
        """Evaluate a single rule against context."""
        rule_type = rule.get("type")

        if rule_type == "keyword":
            keywords = rule.get("keywords", [])
            text = context.get("query", "")
            return any(kw.lower() in text.lower() for kw in keywords)

        elif rule_type == "regex":
            pattern = rule.get("pattern", "")
            text = context.get("query", "")
            return bool(re.search(pattern, text))

        elif rule_type == "metadata":
            key = rule.get("key")
            value = rule.get("value")
            return context.get("metadata", {}).get(key) == value

        elif rule_type == "category":
            categories = rule.get("categories", [])
            category = context.get("category")
            return category in categories if category else False

        return False


class PromptRegistry:
    """
    Registry for managing and retrieving prompts.

    Features:
    - CRUD operations for prompts
    - Filtering by metadata, tags, category
    - Keyword-based search
    - Priority-based retrieval
    """

    def __init__(self):
        self._prompts: dict[str, PromptEntry] = {}
        self._index_by_name: dict[str, str] = {}
        self._index_by_category: dict[PromptCategory, list[str]] = {}
        self._index_by_tag: dict[str, set[str]] = {}

    def register(self, entry: PromptEntry) -> PromptEntry:
        """Register a new prompt entry."""
        if entry.id in self._prompts:
            raise ValueError(f"Prompt with ID {entry.id} already exists")

        if entry.name in self._index_by_name:
            raise ValueError(f"Prompt with name '{entry.name}' already exists")

        # Add to main storage
        self._prompts[entry.id] = entry
        self._index_by_name[entry.name] = entry.id

        # Update category index
        cat = entry.metadata.category
        if cat not in self._index_by_category:
            self._index_by_category[cat] = []
        self._index_by_category[cat].append(entry.id)

        # Update tag index
        for tag in entry.metadata.tags:
            if tag not in self._index_by_tag:
                self._index_by_tag[tag] = set()
            self._index_by_tag[tag].add(entry.id)

        return entry

    def unregister(self, prompt_id: str) -> PromptEntry | None:
        """Unregister a prompt by ID."""
        entry = self._prompts.pop(prompt_id, None)
        if entry is None:
            return None

        # Remove from indices
        self._index_by_name.pop(entry.name, None)
        # Safely remove from category index (list.remove can raise ValueError)
        cat_list = self._index_by_category.get(entry.metadata.category)
        if cat_list and prompt_id in cat_list:
            cat_list.remove(prompt_id)
        for tag in entry.metadata.tags:
            tag_set = self._index_by_tag.get(tag)
            if tag_set:
                tag_set.discard(prompt_id)

        return entry

    def get(self, prompt_id: str) -> PromptEntry | None:
        """Get a prompt by ID."""
        return self._prompts.get(prompt_id)

    def get_by_name(self, name: str) -> PromptEntry | None:
        """Get a prompt by name."""
        prompt_id = self._index_by_name.get(name)
        return self._prompts.get(prompt_id) if prompt_id else None

    def find_by_category(self, category: PromptCategory) -> list[PromptEntry]:
        """Find all prompts in a category."""
        prompt_ids = self._index_by_category.get(category, [])
        return [self._prompts[pid] for pid in prompt_ids if pid in self._prompts]

    def find_by_tags(self, tags: set[str]) -> list[PromptEntry]:
        """Find prompts matching any of the tags."""
        matching_ids: set[str] = set()
        for tag in tags:
            matching_ids.update(self._index_by_tag.get(tag, set()))

        return [self._prompts[pid] for pid in matching_ids if pid in self._prompts]

    def search(self, query: str, limit: int = 10) -> list[PromptEntry]:
        """Search prompts by keyword matching."""
        results = []
        for prompt in self._prompts.values():
            if prompt.matches_keyword(query):
                results.append(prompt)

        # Sort by priority
        results.sort(key=lambda p: p.metadata.priority.value)
        return results[:limit]

    def list_all(self) -> list[PromptEntry]:
        """List all registered prompts."""
        return list(self._prompts.values())

    def __len__(self) -> int:
        """Return the number of registered prompts."""
        return len(self._prompts)

    def __iter__(self) -> Iterator[PromptEntry]:
        """Iterate over all prompts."""
        return iter(self._prompts.values())
