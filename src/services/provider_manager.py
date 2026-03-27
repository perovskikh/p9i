# src/services/provider_manager.py
"""
Provider Manager - dynamic LLM provider selection

Allows per-project provider selection with Redis backend.
"""

import os
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


# Provider configurations
PROVIDERS = {
    "minimax": {
        "name": "MiniMax",
        "model": "MiniMax-M2.7",
        "env_key": "MINIMAX_API_KEY",
        "enabled_env": "MINIMAX_ENABLED",
        "max_tokens_env": "MINIMAX_MAX_TOKENS",
        "default_max_tokens": 16384,
    },
    "zai": {
        "name": "Z.ai (GLM-4.7)",
        "model": "GLM-4.7",
        "env_key": "ZAI_API_KEY",
        "enabled_env": "ZAI_ENABLED",
        "max_tokens_env": "ZAI_MAX_TOKENS",
        "default_max_tokens": 16384,
    },
    "deepseek": {
        "name": "DeepSeek",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "enabled_env": "DEEPSEEK_ENABLED",
        "max_tokens_env": "DEEPSEEK_MAX_TOKENS",
        "default_max_tokens": 16384,
    },
    "openrouter": {
        "name": "OpenRouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "env_key": "OPENROUTER_API_KEY",
        "enabled_env": "OPENROUTER_ENABLED",
        "max_tokens_env": "OPENROUTER_MAX_TOKENS",
        "default_max_tokens": 16384,
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "model": "claude-sonnet-4.6",
        "env_key": "ANTHROPIC_API_KEY",
        "enabled_env": "ANTHROPIC_ENABLED",
        "max_tokens_env": "ANTHROPIC_MAX_TOKENS",
        "default_max_tokens": 4096,
    },
}


class ProviderManager:
    """Manage LLM provider selection per project."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._default_provider = os.getenv("LLM_PROVIDER", "auto")

    def _get_key(self, project_id: str) -> str:
        """Get Redis key for project provider."""
        return f"p9i:provider:{project_id}"

    async def set_provider(self, project_id: str, provider_id: str, model: str = None) -> Dict:
        """Set preferred provider for a project."""
        if provider_id not in PROVIDERS:
            return {"error": f"Unknown provider: {provider_id}"}

        # Verify API key exists
        config = PROVIDERS[provider_id]
        api_key = os.getenv(config["env_key"])
        if not api_key:
            return {"error": f"API key not configured for {config['name']}"}

        if not self.redis:
            logger.warning("Redis not available, storing in memory")
            self._memory_provider = {project_id: {"provider": provider_id, "model": model or config["model"]}}

        key = self._get_key(project_id)
        provider_data = {
            "provider": provider_id,
            "model": model or config["model"],
            "updated_at": datetime.now().isoformat()
        }

        if self.redis:
            import json
            await self.redis.set(key, json.dumps(provider_data))
            await self.redis.expire(key, 365 * 24 * 3600)  # 1 year TTL

        logger.info(f"Provider set for {project_id}: {provider_id}")
        return {"status": "success", "provider": provider_id, "model": provider_data["model"]}

    async def get_provider(self, project_id: str = "default") -> Dict:
        """Get provider for a project."""
        # Try Redis first
        if self.redis:
            import json
            key = self._get_key(project_id)
            data = await self.redis.get(key)
            if data:
                return json.loads(data)

        # Fallback to memory or default
        if hasattr(self, '_memory_provider') and project_id in self._memory_provider:
            return self._memory_provider[project_id]

        # Return default from environment
        return {
            "provider": self._default_provider,
            "model": PROVIDERS.get(self._default_provider, {}).get("model", "auto")
        }

    async def get_available_providers(self) -> List[Dict]:
        """Get list of available providers with their status."""
        available = []
        for pid, config in PROVIDERS.items():
            api_key = os.getenv(config["env_key"], "")
            enabled = os.getenv(config["enabled_env"], "true").lower() == "true"
            max_tokens = int(os.getenv(config["max_tokens_env"], str(config["default_max_tokens"])))

            available.append({
                "id": pid,
                "name": config["name"],
                "model": config["model"],
                "has_key": bool(api_key),
                "enabled": enabled,
                "max_tokens": max_tokens,
            })

        return available

    async def get_current_selection(self, project_id: str = "default") -> Dict:
        """Get current provider selection with full details."""
        current = await self.get_provider(project_id)
        available = await self.get_available_providers()

        current_provider = current.get("provider", self._default_provider)

        # Find full details
        provider_info = next((p for p in available if p["id"] == current_provider), None)

        return {
            "selected": current_provider,
            "model": current.get("model"),
            "available": available,
            "provider_info": provider_info
        }

    async def reset_to_default(self, project_id: str) -> Dict:
        """Reset project to default provider."""
        if self.redis:
            key = self._get_key(project_id)
            await self.redis.delete(key)

        if hasattr(self, '_memory_provider') and project_id in self._memory_provider:
            del self._memory_provider[project_id]

        return {"status": "success", "provider": self._default_provider}


# Global instance
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager(redis_client=None) -> ProviderManager:
    """Get or create provider manager instance."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager(redis_client)
    return _provider_manager
