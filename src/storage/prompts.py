# src/storage/prompts.py
"""
Prompt storage and management

Handles loading, searching, and managing AI prompts.
"""

from pathlib import Path
from typing import Optional
import json
import logging
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)


class Prompt(BaseModel):
    """Prompt model with Pydantic v2 validation."""
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    type: Optional[str] = None
    layer: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)


class PromptNotFoundError(Exception):
    """Raised when a prompt is not found."""
    pass


class PromptStorage:
    """Manages prompt storage and retrieval."""

    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._registry = None

    def load_prompt(self, name: str) -> dict:
        """Load a prompt by name."""
        prompt_file = self.prompts_dir / f"{name}.md"

        if not prompt_file.exists():
            raise PromptNotFoundError(f"Prompt not found: {name}")

        content = prompt_file.read_text()

        # Try to load metadata from registry
        registry = self.get_registry()
        prompt_meta = next(
            (p for p in registry.get("prompts", []) if p.get("name", "").replace("promt-", "") == name),
            {}
        )

        return {
            "name": name,
            "file": prompt_file.name,
            "content": content,
            "version": prompt_meta.get("version", "1.0.0"),
            "type": prompt_meta.get("type"),
            "layer": prompt_meta.get("layer"),
            "tags": prompt_meta.get("tags", [])
        }

    def get_registry(self) -> dict:
        """Load the prompt registry."""
        if self._registry is None:
            registry_file = self.prompts_dir / "registry.json"
            if registry_file.exists():
                self._registry = json.loads(registry_file.read_text())
            else:
                self._registry = {"registry_version": "1.0", "prompts": []}
        return self._registry

    def list_prompts(self) -> list[dict]:
        """List all available prompts."""
        registry = self.get_registry()
        return registry.get("prompts", [])

    def search_prompts(self, query: str) -> list[dict]:
        """Search prompts by query string."""
        registry = self.get_registry()
        prompts = registry.get("prompts", [])

        query_lower = query.lower()
        return [
            p for p in prompts
            if query_lower in p.get("name", "").lower()
            or query_lower in p.get("tags", [])
        ]


# Storage instance
storage = PromptStorage()