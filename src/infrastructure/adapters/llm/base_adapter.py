# src/infrastructure/adapters/llm/base_adapter.py
"""
Base LLM Adapter - Common functionality for all LLM providers.
"""

import os
import logging
from abc import ABC
from typing import Optional, AsyncGenerator
import httpx

from src.application.ports.llm_port import LLMProvider

logger = logging.getLogger(__name__)


class BaseLLMAdapter(LLMProvider, ABC):
    """Base adapter with common functionality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self._api_key = api_key or self._get_api_key()
        self._model = model or self.default_model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Adapter", "").lower()

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        """Override in subclass."""
        raise NotImplementedError

    @property
    def endpoint(self) -> str:
        """Override in subclass."""
        raise NotImplementedError

    @property
    def env_key(self) -> str:
        """Environment variable for API key. Override in subclass."""
        raise NotImplementedError

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        return os.getenv(self.env_key)

    def _get_headers(self) -> dict:
        """Get HTTP headers. Override in subclass for custom headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> dict:
        """Build request payload. Override in subclass for custom format."""
        return {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

    def _parse_response(self, response: dict) -> dict:
        """Parse response. Override in subclass for custom format."""
        raise NotImplementedError

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """Send non-streaming request."""
        url = f"{self.base_url}{self.endpoint}"
        headers = self._get_headers()
        payload = self._build_payload(messages, temperature, max_tokens, stream=False)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return self._parse_response(response.json())

    async def stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Send streaming request."""
        url = f"{self.base_url}{self.endpoint}"
        headers = self._get_headers()
        payload = self._build_payload(messages, temperature, max_tokens, stream=True)

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        chunk = self._parse_stream_chunk(data)
                        if chunk:
                            yield chunk
