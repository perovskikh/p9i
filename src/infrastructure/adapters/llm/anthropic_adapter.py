# src/infrastructure/adapters/llm/anthropic_adapter.py
"""
Anthropic Adapter - Claude models via anthropic.com
"""

from typing import Optional, AsyncGenerator
import httpx

from src.infrastructure.adapters.llm.base_adapter import BaseLLMAdapter


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Claude adapter."""

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    @property
    def base_url(self) -> str:
        return "https://api.anthropic.com"

    @property
    def endpoint(self) -> str:
        return "/v1/messages"

    @property
    def env_key(self) -> str:
        return "ANTHROPIC_API_KEY"

    def _get_headers(self) -> dict:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> dict:
        return {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _parse_response(self, response: dict) -> dict:
        content = response.get("content", [])
        text = content[0].get("text", "") if content else ""
        return {
            "content": text,
            "usage": response.get("usage", {}),
            "stop_reason": response.get("stop_reason"),
        }

    def _parse_stream_chunk(self, data: str) -> Optional[str]:
        import json
        try:
            chunk = json.loads(data)
            if chunk.get("type") == "content_block_delta":
                return chunk.get("delta", {}).get("text", "")
        except Exception:
            pass
        return None
