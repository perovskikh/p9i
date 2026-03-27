# src/infrastructure/adapters/llm/deepseek_adapter.py
"""
DeepSeek Adapter - DeepSeek models via api.deepseek.com
"""

from typing import Optional, AsyncGenerator
import json

from src.infrastructure.adapters.llm.base_adapter import BaseLLMAdapter


class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek adapter."""

    @property
    def default_model(self) -> str:
        return "deepseek-chat"

    @property
    def base_url(self) -> str:
        return "https://api.deepseek.com"

    @property
    def endpoint(self) -> str:
        return "/v1/chat/completions"

    @property
    def env_key(self) -> str:
        return "DEEPSEEK_API_KEY"

    def _parse_response(self, response: dict) -> dict:
        choices = response.get("choices", [])
        message = choices[0].get("message", {}) if choices else {}
        return {
            "content": message.get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choices[0].get("finish_reason") if choices else None,
        }

    def _parse_stream_chunk(self, data: str) -> Optional[str]:
        try:
            chunk = json.loads(data)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            return delta.get("content", "")
        except Exception:
            return None
