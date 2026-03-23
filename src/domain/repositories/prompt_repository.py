# src/domain/repositories/prompt_repository.py
"""
Prompt Repository Interface - Abstract data access for prompts.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.domain.entities.prompt import PromptEntity, PromptTier


class IPromptRepository(ABC):
    """Abstract repository interface for prompt storage."""

    @abstractmethod
    def get_by_name(self, name: str, tier: Optional[PromptTier] = None) -> Optional[PromptEntity]:
        """Get a prompt by name."""
        pass

    @abstractmethod
    def list_all(self, tier: Optional[PromptTier] = None) -> List[PromptEntity]:
        """List all prompts, optionally filtered by tier."""
        pass

    @abstractmethod
    def save(self, prompt: PromptEntity) -> PromptEntity:
        """Save a prompt."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a prompt."""
        pass

    @abstractmethod
    def search(self, query: str) -> List[PromptEntity]:
        """Search prompts by query."""
        pass
