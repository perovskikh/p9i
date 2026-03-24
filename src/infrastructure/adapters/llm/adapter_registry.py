# src/infrastructure/adapters/llm/adapter_registry.py
"""
LLM Adapter Registry - Unifies all LLM providers under one interface.

Provides adapter pattern for LLM providers with failover support.
"""

from typing import Optional, AsyncGenerator
from abc import ABC, abstractmethod
import os
import logging

logger = logging.getLogger(__name__)


class LLMAdapter(ABC):
    """Base adapter interface for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Default model name."""
        pass

    @property
    @abstractmethod
    def api_key_env(self) -> str:
        """Environment variable name for API key."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """Generate response from messages."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        pass


class LLMProviderRegistry:
    """Registry for managing LLM adapters with automatic failover."""

    # Priority order for auto-detection (aligned with CLAUDE.md)
    PRIORITY_ORDER = [
        "minimax",   # MiniMax (best price/performance)
        "glm-4-7",   # Z.ai (best quality)
        "hunter",    # OpenRouter (free)
        "deepseek",  # DeepSeek
        "anthropic", # Anthropic direct (requires explicit permission)
    ]

    # Error codes that trigger failover
    FAILOVER_ON_STATUS = {401, 403, 429, 500, 502, 503, 504}

    def __init__(self, preferred_provider: str = "auto"):
        self._adapters = {}
        self._current_provider = None
        self._preferred = preferred_provider

        # Initialize adapters
        self._init_adapters()

    def _init_adapters(self):
        """Initialize all available adapters."""
        # Import and register adapters
        try:
            from src.infrastructure.adapters.llm import AnthropicAdapter, GLMAdapter, DeepSeekAdapter

            self._adapters["anthropic"] = AnthropicAdapter()
            self._adapters["glm-4-7"] = GLMAdapter()
            self._adapters["glm-4-5-air"] = GLMAdapter()
            self._adapters["deepseek"] = DeepSeekAdapter()

            logger.info(f"Registered adapters: {list(self._adapters.keys())}")
        except ImportError as e:
            logger.warning(f"Some adapters not available: {e}")

        # Also allow LLMClient to be used as adapter
        from src.services.llm_client import LLMClient, PROVIDERS

        # Create wrapper adapters for providers not in custom adapters
        for provider_name, config in PROVIDERS.items():
            if provider_name not in self._adapters:
                api_key = os.getenv(config["env_key"])
                if api_key:
                    self._adapters[provider_name] = _LLMClientWrapper(
                        provider_name, config, api_key
                    )

    def _detect_provider(self) -> str:
        """Detect best available provider based on API keys."""
        explicit = os.getenv("LLM_PROVIDER")
        if explicit and explicit in self._adapters:
            return explicit

        for provider in self.PRIORITY_ORDER:
            if provider in self._adapters:
                adapter = self._adapters[provider]
                api_key = os.getenv(adapter.api_key_env)
                if api_key:
                    return provider

        # Fallback to first available
        return list(self._adapters.keys())[0] if self._adapters else "glm-4-7"

    def get_adapter(self, provider: Optional[str] = None) -> LLMAdapter:
        """Get adapter for specified provider."""
        if provider is None or provider == "auto":
            provider = self._detect_provider()

        if provider not in self._adapters:
            provider = self._detect_provider()

        self._current_provider = provider
        return self._adapters[provider]

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        provider: Optional[str] = None,
    ) -> dict:
        """Generate with automatic failover."""
        adapters_to_try = self._get_failover_chain(provider)

        last_error = None
        for adapter_name in adapters_to_try:
            try:
                adapter = self._adapters[adapter_name]
                result = await adapter.generate(messages, temperature, max_tokens)

                # Check for errors that should trigger failover
                if isinstance(result, dict) and "error" in result:
                    error_str = str(result.get("error", ""))
                    if any(x in error_str for x in ["401", "403", "429", "500", "502", "503", "504"]):
                        logger.warning(f"Provider {adapter_name} failed: {error_str}, trying next")
                        continue

                return result
            except Exception as e:
                logger.warning(f"Adapter {adapter_name} exception: {e}, trying next")
                last_error = e
                continue

        return {"error": f"All providers failed. Last error: {last_error}"}

    def _get_failover_chain(self, preferred: Optional[str]) -> list:
        """Get ordered list of providers to try."""
        chain = []

        if preferred and preferred in self._adapters:
            chain.append(preferred)

        # Add fallbacks
        for provider in self.PRIORITY_ORDER:
            if provider not in chain and provider in self._adapters:
                chain.append(provider)

        # Add any remaining adapters
        for provider in self._adapters:
            if provider not in chain:
                chain.append(provider)

        return chain

    def list_providers(self) -> dict:
        """List all available providers with status."""
        result = {}
        for name, adapter in self._adapters.items():
            # Handle both custom adapters and LLMClient wrappers
            env_key = getattr(adapter, "api_key_env", None) or getattr(adapter, "env_key", None) or "UNKNOWN"
            api_key = os.getenv(env_key, "")
            result[name] = {
                "available": bool(api_key),
                "model": adapter.model,
            }
        return result


class _LLMClientWrapper(LLMAdapter):
    """Wrapper to use LLMClient as an adapter."""

    def __init__(self, name: str, config: dict, api_key: str):
        from src.services.llm_client import LLMClient

        self._name = name
        self._config = config
        self._client = LLMClient(provider=name, api_key=api_key)

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> str:
        return self._config["model"]

    @property
    def api_key_env(self) -> str:
        return self._config["env_key"]

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        return await self._client.chat(messages, temperature, max_tokens, stream=False)

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response - returns async generator directly.

        Note: Usage is captured from message_stop event for Anthropic/MiniMax,
        or from final chunk for OpenAI format. The caller should track usage
        by examining the stream results.
        """
        import httpx
        import json

        # Use the same streaming logic that works in llm_client.py
        headers = self._client._get_headers()
        payload = self._client._build_payload(messages, temperature, max_tokens, True)
        endpoint = f"{self._client.base_url}{self._client.endpoint}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        # Handle event: format (Anthropic/MiniMax)
                        if line.startswith("event: "):
                            continue
                        # Handle data: JSON
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                # Capture usage from message_delta (Anthropic/MiniMax)
                                if chunk.get("type") == "message_delta":
                                    # Usage is in the message_delta event
                                    usage_data = chunk.get("usage", {})
                                    if usage_data:
                                        yield {"type": "usage", "usage": usage_data}
                                # Also capture from message_stop if available
                                elif chunk.get("type") == "message_stop":
                                    yield {"type": "usage", "usage": chunk.get("usage", {})}
                                elif chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if delta.get("text"):
                                        yield delta["text"]
                                elif "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if delta.get("content"):
                                        yield delta["content"]
                                    # Check for usage in OpenAI format
                                    if chunk.get("usage"):
                                        yield {"type": "usage", "usage": chunk["usage"]}
                            except json.JSONDecodeError:
                                continue

    def get_stream(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """Get streaming generator without await."""
        return self._stream_generator(messages)

    async def _stream_generator(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """Internal streaming generator."""
        return await self.generate_stream(messages)


# Global registry instance
_registry: Optional[LLMProviderRegistry] = None


def get_registry() -> LLMProviderRegistry:
    """Get global LLM provider registry."""
    global _registry
    if _registry is None:
        _registry = LLMProviderRegistry()
    return _registry