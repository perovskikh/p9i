# src/services/llm_client.py
"""
LLM Client - Multi-provider support (MiniMax, Z.ai, Anthropic, OpenRouter)

Provides async client for executing prompts through various LLM providers.
"""

import os
import json
import logging
import asyncio
from typing import Optional, AsyncGenerator
import httpx

logger = logging.getLogger(__name__)

# Provider configurations (updated March 2026)
# Each provider has its own API endpoint and uses its own API key
# Per-provider settings can be overridden via environment variables
PROVIDERS = {
    # === Z.ai (https://docs.z.ai) ===
    # Z.ai provides access to GLM models via their API
    # Endpoint: https://api.z.ai/api/coding/paas/v4
    "glm-4-7": {
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "endpoint": "/chat/completions",
        "model": "GLM-4.7",
        "env_key": "ZAI_API_KEY",
        "enabled_env": "ZAI_ENABLED",
        "model_env": "ZAI_MODEL",
        "temperature_env": "ZAI_TEMPERATURE",
        "max_tokens_env": "ZAI_MAX_TOKENS",
    },
    "glm-4-5-air": {
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "endpoint": "/chat/completions",
        "model": "GLM-4.5-Air",
        "env_key": "ZAI_API_KEY",
        "enabled_env": "ZAI_ENABLED",
        "model_env": "ZAI_MODEL",
        "temperature_env": "ZAI_TEMPERATURE",
        "max_tokens_env": "ZAI_MAX_TOKENS",
    },
    # Z.ai also supports Anthropic models via /anthropic/v1/messages
    "zai-claude": {
        "base_url": "https://api.z.ai/api",
        "endpoint": "/anthropic/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "env_key": "ZAI_API_KEY",
        "enabled_env": "ZAI_ENABLED",
        "model_env": "ZAI_MODEL",
        "temperature_env": "ZAI_TEMPERATURE",
        "max_tokens_env": "ZAI_MAX_TOKENS",
    },

    # === MiniMax (https://platform.minimax.io) ===
    "minimax": {
        "base_url": "https://api.minimax.io/anthropic",
        "endpoint": "/v1/messages",
        "model": "MiniMax-M2.7",
        "env_key": "MINIMAX_API_KEY",
        "enabled_env": "MINIMAX_ENABLED",
        "model_env": "MINIMAX_MODEL",
        "temperature_env": "MINIMAX_TEMPERATURE",
        "max_tokens_env": "MINIMAX_MAX_TOKENS",
    },

    # === DeepSeek (https://api-docs.deepseek.com) ===
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "enabled_env": "DEEPSEEK_ENABLED",
        "model_env": "DEEPSEEK_MODEL",
        "temperature_env": "DEEPSEEK_TEMPERATURE",
        "max_tokens_env": "DEEPSEEK_MAX_TOKENS",
    },
    "deepseek-reasoner": {
        "base_url": "https://api.deepseek.com",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-reasoner",
        "env_key": "DEEPSEEK_API_KEY",
        "enabled_env": "DEEPSEEK_ENABLED",
        "model_env": "DEEPSEEK_MODEL",
        "temperature_env": "DEEPSEEK_TEMPERATURE",
        "max_tokens_env": "DEEPSEEK_MAX_TOKENS",
    },

    # === Anthropic Direct ===
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "endpoint": "/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "env_key": "ANTHROPIC_API_KEY",
        "enabled_env": "ANTHROPIC_ENABLED",
        "model_env": "ANTHROPIC_MODEL",
        "temperature_env": "ANTHROPIC_TEMPERATURE",
        "max_tokens_env": "ANTHROPIC_MAX_TOKENS",
    },

    # === OpenRouter (https://openrouter.ai) - Free models ===
    "hunter": {
        "base_url": "https://openrouter.ai/api/v1",
        "endpoint": "/chat/completions",
        "model": "anthropic/claude-3-haiku",
        "env_key": "OPENROUTER_API_KEY",
        "enabled_env": "OPENROUTER_ENABLED",
        "model_env": "OPENROUTER_MODEL",
        "temperature_env": "OPENROUTER_TEMPERATURE",
        "max_tokens_env": "OPENROUTER_MAX_TOKENS",
    },
}


# Quick provider switcher
def set_provider(provider: str) -> str:
    """Quick switch LLM provider via environment variable.

    Usage:
        set_provider("glm-4-7")    # Z.ai GLM-4.7
        set_provider("minimax")    # MiniMax M2.7
        set_provider("deepseek")   # DeepSeek Chat
        set_provider("anthropic")   # Claude Sonnet
        set_provider("hunter")      # Free via OpenRouter

    Returns: provider name or error message
    """
    valid = list(PROVIDERS.keys())
    if provider not in valid:
        return f"Error: invalid provider '{provider}'. Valid: {valid}"

    os.environ["LLM_PROVIDER"] = provider
    return f"Provider switched to: {provider} ({PROVIDERS[provider]['model']})"


def get_available_providers() -> dict:
    """Get list of available providers with their status."""
    result = {}
    for name, config in PROVIDERS.items():
        api_key = os.getenv(config["env_key"])
        enabled_env = config.get("enabled_env")
        # Check if provider is explicitly disabled
        enabled = True
        if enabled_env:
            enabled = os.getenv(enabled_env, "true").lower() == "true"

        result[name] = {
            "model": config["model"],
            "env_key": config["env_key"],
            "available": bool(api_key),
            "enabled": enabled,
        }
    return result


def _get_provider_settings(provider: str) -> dict:
    """Get per-provider settings from environment variables."""
    config = PROVIDERS.get(provider, {})
    settings = {}

    if config:
        # Model override
        model_env = config.get("model_env")
        if model_env:
            settings["model"] = os.getenv(model_env)

        # Temperature override
        temp_env = config.get("temperature_env")
        if temp_env:
            settings["temperature"] = float(os.getenv(temp_env, "0.7"))

        # Max tokens override
        tokens_env = config.get("max_tokens_env")
        if tokens_env:
            settings["max_tokens"] = int(os.getenv(tokens_env, "4096"))

    return settings


def _get_fallback_order() -> list:
    """Get custom fallback order from LLM_FAILOVER_ORDER env var."""
    custom_order = os.getenv("LLM_FAILOVER_ORDER", "")
    if custom_order:
        return [p.strip() for p in custom_order.split(",") if p.strip() in PROVIDERS]

    # Default fallback order
    return ["glm-4-7", "hunter", "deepseek", "anthropic"]


def _get_provider_priority() -> list:
    """Get custom provider priority order from LLM_PROVIDER_PRIORITY env var.

    This defines the order for auto-detection when LLM_PROVIDER=auto.
    Format: "minimax,glm-4-7,deepseek,hunter,anthropic"

    Higher priority = checked first for API key availability.
    """
    custom_priority = os.getenv("LLM_PROVIDER_PRIORITY", "")
    if custom_priority:
        return [p.strip() for p in custom_priority.split(",") if p.strip() in PROVIDERS]

    # Default priority order (best price/performance first)
    return ["minimax", "glm-4-7", "hunter", "deepseek", "anthropic"]


class LLMClient:
    """Async client for multiple LLM providers with automatic failover."""

    # Default fallback order when primary provider fails
    # Priority: MiniMax → ZAI → OpenRouter → DeepSeek → Anthropic
    # Can be overridden via LLM_FAILOVER_ORDER env var
    DEFAULT_FALLBACK_ORDER = {
        "minimax": ["glm-4-7", "hunter", "deepseek", "anthropic"],
        "glm-4-7": ["hunter", "minimax", "deepseek", "anthropic"],
        "glm-4-5-air": ["glm-4-7", "hunter", "minimax", "deepseek"],
        "zai-claude": ["glm-4-7", "hunter", "minimax", "deepseek"],
        "hunter": ["glm-4-7", "minimax", "deepseek", "anthropic"],
        "deepseek": ["hunter", "glm-4-7", "minimax", "anthropic"],
        "deepseek-reasoner": ["deepseek", "hunter", "glm-4-7", "minimax"],
        "anthropic": ["minimax", "glm-4-7", "hunter", "deepseek"],  # Only if explicitly allowed
    }

    # Error codes that trigger failover
    FAILOVER_ON_CODES = {401, 403, 429, 500, 502, 503, 504, 529}

    def __init__(
        self,
        provider: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        enable_failover: bool = True,
    ):
        # Load per-provider settings from environment
        settings = _get_provider_settings(provider) if provider != "auto" else {}

        self.temperature = settings.get("temperature", temperature)
        self.max_tokens = settings.get("max_tokens", max_tokens)
        self.enable_failover = os.getenv("LLM_FAILOVER_ENABLED", "true").lower() == "true" if enable_failover else False

        # Auto-detect provider based on available keys
        if provider == "auto":
            provider = self._detect_provider()

        self.provider = provider
        self.original_provider = provider  # Track primary provider
        config = PROVIDERS.get(provider, PROVIDERS["hunter"])

        self.base_url = config["base_url"]
        self.endpoint = config["endpoint"]
        self.default_model = config["model"]

        # Use provided key or fall back to env
        self.api_key = api_key or os.getenv(config["env_key"])

        # Model override: param > env provider setting > default
        self.model = model or settings.get("model") or self.default_model

        if not self.api_key:
            logger.warning(f"No API key for provider: {provider}")

    def _detect_provider(self) -> str:
        """Detect best available provider based on API keys in .env.

        Uses LLM_PROVIDER_PRIORITY env var for custom priority order.
        Default priority: MiniMax → ZAI → OpenRouter → DeepSeek → Anthropic
        """
        # Check explicit provider first (LLM_PROVIDER=minimax, etc.)
        explicit = os.getenv("LLM_PROVIDER")
        if explicit and explicit in PROVIDERS:
            return explicit

        # Get priority order from env or use default
        priority = _get_provider_priority()

        # Check providers in priority order, return first one with API key
        for provider in priority:
            config = PROVIDERS[provider]
            if os.getenv(config["env_key"]):
                return provider

        return "hunter"  # Fallback to free

    def _get_headers(self) -> dict:
        """Get provider-specific headers."""
        if self.provider in ("anthropic", "minimax"):
            # Anthropic direct and MiniMax (Anthropic-compatible) use x-api-key
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
        elif self.provider == "zai-claude":
            # Z.ai Claude uses Bearer (Anthropic-compatible)
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            # All others use Bearer (GLM, MiniMax, DeepSeek, OpenRouter)
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

    def _build_payload(
        self,
        messages: list[dict],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> dict:
        """Build provider-specific payload."""
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens

        if self.provider == "anthropic":
            # Anthropic format (no stream in payload)
            return {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
            }
        elif self.provider == "zai-claude":
            # Z.ai Claude format (Anthropic-compatible)
            return {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
            }
        else:
            # GLM, MiniMax, DeepSeek, OpenRouter use OpenAI-like format
            return {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "stream": stream,
            }

    def _parse_response(self, response: dict) -> dict:
        """Parse provider-specific response format."""
        if self.provider in ("anthropic", "zai-claude", "minimax"):
            # Anthropic format: {"content": [...], "stop_reason": "..."}
            content = response.get("content", [])
            if content and isinstance(content, list):
                # Extract text from "text" type blocks, skip "thinking" blocks
                text_parts = []
                for block in content:
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                text = "\n".join(text_parts)
            else:
                text = ""
            return {
                "choices": [{"message": {"content": text}}],
                "usage": response.get("usage", {}),
            }
        else:
            # OpenRouter, DeepSeek use OpenAI format
            return response

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict | AsyncGenerator[str, None]:
        """
        Send chat request to LLM provider with automatic failover.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stream: Enable streaming response

        Returns:
            dict response or async generator for streaming
        """
        if not self.api_key:
            return {"error": "No API key configured"}

        # For streaming, don't do failover (complex to handle)
        if stream:
            return await self._chat_single_provider(messages, temperature, max_tokens, stream)

        # Non-streaming: try with failover
        fallback_providers = self.DEFAULT_FALLBACK_ORDER.get(self.provider, _get_fallback_order())

        for attempt_provider in [self.provider] + fallback_providers:
            result = await self._try_provider(
                attempt_provider, messages, temperature, max_tokens, stream
            )

            logger.debug(f"Provider {attempt_provider} result: {result}")

            # Check if result is an error that should trigger failover
            if isinstance(result, dict) and "error" in result:
                error_code = result.get("error", "")

                # Check if we should failover
                should_failover = False
                if "API error: 401" in error_code or "API error: 403" in error_code:
                    should_failover = True  # Auth issues - switch provider
                elif "API error: 429" in error_code:
                    should_failover = True  # Rate limit - try next
                elif any(x in error_code for x in ["API error: 500", "API error: 502", "API error: 503", "API error: 504"]):
                    should_failover = True  # Server errors - temporary, try next
                elif "401" in error_code or "403" in error_code:
                    should_failover = True  # Auth issues without "API error" prefix
                elif "ReadTimeout" in error_code or "Timeout" in error_code:
                    should_failover = True  # Timeout - try next provider

                logger.warning(f"Provider {attempt_provider} failed: {error_code}, failover={should_failover}")

                if should_failover and attempt_provider != fallback_providers[-1]:
                    # Find next provider in the list
                    try:
                        idx = fallback_providers.index(attempt_provider)
                        next_provider = fallback_providers[idx + 1]
                        logger.warning(f"Failover from {attempt_provider} to {next_provider}")
                        # Continue to next provider
                        continue
                    except (ValueError, IndexError):
                        pass

            # Return successful result
            return result

        # All providers failed
        return {"error": "All providers failed", "last_provider": attempt_provider}

    async def _try_provider(
        self,
        provider: str,
        messages: list[dict],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> dict | AsyncGenerator[str, None]:
        """Try a single provider and return result."""
        # Temporarily switch provider config
        old_provider = self.provider
        old_config = PROVIDERS[provider]

        self.provider = provider
        self.base_url = old_config["base_url"]
        self.endpoint = old_config["endpoint"]
        self.default_model = old_config["model"]
        self.api_key = os.getenv(old_config["env_key"])
        self.model = self.default_model

        try:
            return await self._chat_single_provider(messages, temperature, max_tokens, stream)
        finally:
            # Restore original provider
            self.provider = old_provider

    async def _chat_single_provider(
        self,
        messages: list[dict],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> dict | AsyncGenerator[str, None]:
        """Send chat request to a single LLM provider (no failover)."""
        headers = self._get_headers()
        payload = self._build_payload(messages, temperature, max_tokens, stream)
        endpoint = f"{self.base_url}{self.endpoint}"

        logger.info(f"[LLM] Request: provider={self.provider}, model={self.model}, endpoint={endpoint}, stream={stream}")

        try:
            # Explicit timeout configuration (connect=30s, read=300s for long LLM responses)
            timeout_config = httpx.Timeout(30.0, connect=30.0, read=300.0)
            logger.info(f"[LLM] Timeout config: connect=30s, read=300s")

            async with httpx.AsyncClient(timeout=timeout_config) as client:
                if stream:
                    logger.info(f"[LLM] Starting stream request...")
                    return self._stream_response(client, endpoint, headers, payload)
                else:
                    # Retry logic for rate limiting (429)
                    max_retries = 3
                    retry_delay = 2.0
                    for attempt in range(max_retries):
                        logger.info(f"[LLM] Sending POST request (attempt {attempt + 1}/{max_retries})...")
                        response = await client.post(endpoint, headers=headers, json=payload)
                        logger.info(f"[LLM] Response received: status={response.status_code}")

                        if response.status_code == 429:
                            # Rate limited - retry with exponential backoff
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                logger.warning(f"Rate limited (429), retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                logger.error(f"Rate limit exceeded after {max_retries} retries")
                                return {"error": "Rate limit exceeded", "details": "Too many requests to LLM provider", "retry_after": response.headers.get("retry-after")}

                        response.raise_for_status()
                        return self._parse_response(response.json())
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"API error: {e.response.status_code}", "details": e.response.text[:200]}
        except Exception as e:
            import traceback
            logger.error(f"LLM request failed: {type(e).__name__}: {e}\n{traceback.format_exc()}")
            return {"error": f"{type(e).__name__}: {e}"}

    async def _stream_response(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        headers: dict,
        payload: dict,
    ) -> AsyncGenerator[str, None]:
        """Handle streaming response from provider."""
        logger.info(f"[LLM] Stream: Starting connection to {endpoint}")
        async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
            logger.info(f"[LLM] Stream: Response status={response.status_code}")
            response.raise_for_status()
            line_count = 0
            async for line in response.aiter_lines():
                line_count += 1
                if line_count % 10 == 0:
                    logger.info(f"[LLM] Stream: Received {line_count} lines")
                if line.strip():
                    if self.provider in ("anthropic", "zai"):
                        # SSE format: data: {"type":"content_block_delta"...}
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if delta.get("text"):
                                        yield delta["text"]
                            except json.JSONDecodeError:
                                continue
                    else:
                        # OpenAI format: data: {"choices":[...]}
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if delta.get("content"):
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[dict] = None,
        stream: bool = False,
    ) -> dict:
        """
        Generate response from prompt.

        Args:
            system_prompt: System instructions
            user_prompt: User input
            context: Additional context data
            stream: Enable streaming output

        Returns:
            dict with generated text and metadata, or generator if stream=True
        """
        messages = []

        # Build system message with context if provided
        if context:
            context_str = self._format_context(context)
            full_system = f"{system_prompt}\n\n## Context\n{context_str}"
        else:
            full_system = system_prompt

        # Some providers don't support system role - combine with first user message
        if self.provider in ("zai-claude",):
            messages.append({
                "role": "user",
                "content": f"[System: {full_system}]\n\nUser request: {user_prompt}"
            })
        else:
            messages.append({"role": "system", "content": full_system})
            messages.append({"role": "user", "content": user_prompt})

        # Streaming mode - return dict with stream and usage tracker
        if stream:
            result = await self._stream_chat(messages)
            return {
                "status": "streaming",
                "stream": result["stream"],
                "usage": result["usage"],
                "model": self.model,
            }

        result = await self.chat(messages)

        if "error" in result:
            return {
                "status": "error",
                "error": result["error"],
            }

        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "status": "success",
                "content": content,
                "model": self.model,
                "usage": result.get("usage", {}),
            }
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse response: {e}, result: {result}")
            return {
                "status": "error",
                "error": "Invalid response format",
            }

    async def _stream_chat(self, messages: list[dict]) -> dict:
        """
        Streaming chat - returns dict with stream generator and usage tracker.

        Returns:
            dict: {"stream": async generator, "usage": dict to be updated}
        """
        if not self.api_key:
            return {
                "stream": self._error_stream("Error: No API key configured"),
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }

        # Create a shared usage dict that can be updated during streaming
        usage = {"input_tokens": 0, "output_tokens": 0}

        headers = self._get_headers()
        payload = self._build_payload(messages, None, None, True)
        endpoint = f"{self.base_url}{self.endpoint}"

        logger.info(f"LLM Streaming: provider={self.provider}, model={self.model}")

        # Create streaming generator with closure to update usage
        async def stream_generator():
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line.strip():
                                # MiniMax uses event: prefix (Anthropic-compatible)
                                if line.startswith("event: "):
                                    continue
                                # Handle data: JSON
                                if line.startswith("data: "):
                                    data = line[6:]
                                    if data == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data)
                                        # Anthropic event format - capture usage from message_stop
                                        if chunk.get("type") == "message_stop":
                                            usage_data = chunk.get("usage", {})
                                            if usage_data:
                                                usage["input_tokens"] = usage_data.get("input_tokens", 0)
                                                usage["output_tokens"] = usage_data.get("output_tokens", 0)
                                                logger.info(f"Captured streaming usage: {usage}")
                                        elif chunk.get("type") == "content_block_delta":
                                            delta = chunk.get("delta", {})
                                            if delta.get("text"):
                                                yield delta["text"]
                                        # OpenAI format - capture usage from final chunk
                                        elif "choices" in chunk and chunk["choices"]:
                                            delta = chunk["choices"][0].get("delta", {})
                                            if delta.get("content"):
                                                yield delta["text"]
                                            # Check for usage in OpenAI format
                                            if chunk.get("usage"):
                                                usage["input_tokens"] = chunk["usage"].get("prompt_tokens", 0)
                                                usage["output_tokens"] = chunk["usage"].get("completion_tokens", 0)
                                    except json.JSONDecodeError:
                                        continue
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"Error: {e}"

        return {
            "stream": stream_generator(),
            "usage": usage,
        }

    def _error_stream(self, error_msg: str) -> AsyncGenerator[str, None]:
        """Yield error message as stream."""
        yield error_msg

    def _format_context(self, context: dict) -> str:
        """Format context dict as string for prompt."""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)


# Current provider override (set by provider manager)
_current_provider_override: str = None


def set_provider_override(provider: str):
    """Set provider override for subsequent LLM client calls."""
    global _current_provider_override
    _current_provider_override = provider


def get_llm_client(provider_override: str = None) -> LLMClient:
    """
    Get configured LLM client from environment.

    Now uses LLMProviderRegistry (adapter pattern) for unified interface.
    Falls back to LLMClient for backward compatibility.

    Args:
        provider_override: Optional provider to use instead of env var
    """
    import os
    from dotenv import load_dotenv

    # Try to load from common .env locations
    load_dotenv("/app/.env")
    load_dotenv()  # Try current directory

    # Check for override (from provider manager) or use env
    provider = provider_override or _current_provider_override or os.getenv("LLM_PROVIDER", "auto")
    model = os.getenv("LLM_MODEL", None)  # Optional model override

    # Try to use adapter registry first (new pattern)
    try:
        from src.infrastructure.adapters.llm import get_registry
        registry = get_registry()

        # Create a wrapper that uses adapters but provides LLMClient interface
        return _AdapterRegistryWrapper(registry, provider, model)
    except ImportError:
        # Fallback to direct LLMClient (legacy)
        return LLMClient(provider=provider, model=model)


class _AdapterRegistryWrapper:
    """
    Wrapper to provide LLMClient-compatible interface using adapter registry.

    This integrates the adapter pattern while maintaining backward compatibility.
    """

    def __init__(self, registry, provider: str = "auto", model: str = None):
        self._registry = registry
        self._provider_name = provider
        self._model = model

        # Get adapter and sync properties
        adapter = registry.get_adapter(provider)
        self.provider = adapter.name
        self.model = model or adapter.model
        self.api_key = os.getenv(adapter.api_key_env)

        # Copy relevant methods from adapter
        self._adapter = adapter

    @property
    def base_url(self):
        return getattr(self._adapter, 'base_url', '')

    @property
    def endpoint(self):
        return getattr(self._adapter, 'endpoint', '/chat/completions')

    async def generate(self, system_prompt: str, user_prompt: str, context: dict = None, stream: bool = False) -> dict:
        """Generate using adapter registry with streaming support."""
        # Build messages
        full_system = system_prompt
        if context:
            context_str = self._format_context(context)
            full_system = f"{system_prompt}\n\n## Context\n{context_str}"

        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_prompt}
        ]

        # Use streaming if requested
        if stream:
            return await self._stream_generate(messages)

        # Regular generate with failover
        result = await self._registry.generate(messages)

        if "error" in result:
            return {"status": "error", "error": result["error"]}

        # Standardize response format (handle both OpenAI and Anthropic formats)
        content = result.get("content", "")
        if not content and "choices" in result:
            # OpenAI format: {"choices": [{"message": {"content": "..."}}]}
            content = result["choices"][0].get("message", {}).get("content", "")

        return {
            "status": "success",
            "content": content,
            "model": self.model,
            "usage": result.get("usage", {}),
        }

    async def _stream_generate(self, messages: list) -> dict:
        """Streaming generate using adapter with usage tracking."""
        # Create shared usage dict for tracking during streaming
        usage = {"input_tokens": 0, "output_tokens": 0}

        async def tracked_stream():
            """Wrapper that tracks usage during streaming."""
            try:
                adapter = self._registry.get_adapter()
                # Get stream from adapter
                stream_gen = adapter.generate_stream(messages)

                logger.info(f"Stream generator type: {type(stream_gen)}")

                # Iterate over the stream and capture usage
                async for chunk in stream_gen:
                    # Check if chunk is a dict with usage info (some providers send this)
                    if isinstance(chunk, dict):
                        if "usage" in chunk:
                            usage.update(chunk["usage"])
                        if "content" in chunk:
                            yield chunk["content"]
                    elif isinstance(chunk, str):
                        # Regular text chunk
                        yield chunk
                # Note: Usage is captured at the end from provider's final message
                # For now we keep the usage dict accessible
            except Exception as e:
                logger.error(f"Stream generate error: {e}")
                yield f"Error: {e}"

        return {
            "status": "streaming",
            "stream": tracked_stream(),
            "usage": usage,
            "model": self.model,
        }

    def _format_context(self, context: dict) -> str:
        """Format context as string."""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)