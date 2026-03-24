# src/application/ports/llm_port.py
"""
LLM Provider Port - Abstract interface for LLM services.

This follows the Port/Adapter pattern to allow easy swapping of LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implement this interface to add new LLM providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'glm', 'deepseek')."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Default model name."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            dict with 'content', 'usage', etc.
        """
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks of the response
        """
        pass


class LLMProviderRegistry:
    """Registry for LLM providers."""

    _providers: dict[str, type[LLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a new LLM provider."""
        cls._providers[name] = provider_class

    @classmethod
    def get(cls, name: str) -> Optional[type[LLMProvider]]:
        """Get provider class by name."""
        return cls._providers.get(name)

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())
