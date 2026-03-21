# src/api/server.py
"""
AI Prompt System - FastMCP Server

MCP-сервер для управления AI-промтами с полным циклом:
- Генерация промтов из любой идеи (Prompt Factory)
- Верификация качества (Self-Verification)
- Версионирование и rollback
- Multi-tenant изоляция (API Keys)
"""

from fastmcp import FastMCP
from pathlib import Path
import json
import logging
import os
import time
from typing import Optional
from functools import wraps
import asyncio

# Load .env file for local development
from dotenv import load_dotenv
from pathlib import Path

# Redis imports for distributed rate limiting
import redis.asyncio as redis

# Try to load .env from multiple locations
env_paths = [
    Path.cwd() / ".env",
    Path(__file__).parent.parent / ".env",
    Path("/app/.env"),
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)  # Force override existing env vars
        break

# Import executor for LLM integration
from src.services.executor import PromptExecutor

# Import v2 storage and middleware
from src.storage.prompts_v2 import (
    PromptStorageV2,
    get_storage,
    get_prompt,
    get_tier_prompts,
    verify_baseline,
    PromptTier
)
from src.middleware import (
    verify_baseline_on_startup,
    configure_baseline_verification
)

# Import distributed rate limiting
from src.services.redis_rate_limiter import (
    create_redis_rate_limiter,
    LimitConfig,
    DistributedRateLimiter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_ENABLED = os.getenv("JWT_ENABLED", "false").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")

# Import JWT service if enabled
_jwt_service = None
if JWT_ENABLED:
    from src.middleware.jwt_auth import JWTService, get_jwt_service as _get_jwt_service
    _jwt_service = _get_jwt_service()
    logger.info("JWT authentication enabled")

# Create MCP server
mcp = FastMCP("AI Prompt System")


# JWT Auth Tools (only if JWT_ENABLED)
if JWT_ENABLED:
    @mcp.tool()
    def generate_jwt_token(
        subject: str,
        role: str = "user",
        expiry_hours: int = 24
    ) -> dict:
        """
        Generate a JWT access token for API authentication.

        Args:
            subject: User or project identifier
            role: Role (admin, developer, user)
            expiry_hours: Token expiration in hours (default 24)
        """
        global _jwt_service

        if not JWT_ENABLED:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        try:
            token = _jwt_service.generate_token(
                subject=subject,
                role=role,
                expiry=expiry_hours * 3600
            )
            return {
                "status": "success",
                "token": token,
                "subject": subject,
                "role": role,
                "expires_in": expiry_hours * 3600
            }
        except Exception as e:
            logger.error(f"JWT token generation error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    def validate_jwt_token(token: str) -> dict:
        """
        Validate a JWT token and return its payload.

        Args:
            token: JWT token to validate
        """
        global _jwt_service

        if not JWT_ENABLED:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        if not token:
            return {"status": "error", "error": "Token is required"}

        payload = _jwt_service.validate_token(token)

        if payload:
            return {
                "status": "success",
                "valid": True,
                "subject": payload.sub,
                "role": payload.role,
                "permissions": payload.permissions,
                "tier_access": payload.tier_access,
                "expires_at": payload.exp
            }
        else:
            return {
                "status": "success",
                "valid": False,
                "error": "Invalid or expired token"
            }

    @mcp.tool()
    def revoke_jwt_token(token: str) -> dict:
        """
        Revoke a JWT token.

        Args:
            token: JWT token to revoke
        """
        global _jwt_service

        if not JWT_ENABLED:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        if _jwt_service.revoke_token(token):
            return {"status": "success", "message": "Token revoked"}
        return {"status": "error", "error": "Failed to revoke token"}

# Configuration
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"


def validate_auth(api_key: str = None, jwt_token: str = None) -> tuple[bool, Optional[dict]]:
    """
    Validate authentication via API key or JWT token.

    Returns:
        tuple: (is_valid, auth_data)
    """
    global _jwt_service

    # Check JWT first if enabled
    if JWT_ENABLED and jwt_token:
        if _jwt_service:
            payload = _jwt_service.validate_token(jwt_token)
            if payload:
                return True, {
                    "type": "jwt",
                    "subject": payload.sub,
                    "role": payload.role,
                    "permissions": payload.permissions,
                    "tier_access": payload.tier_access
                }

    # Check API key
    if api_key:
        # Will be validated by APIKeyManager later
        return True, {"type": "api_key", "key": api_key}

    # No auth provided
    if JWT_ENABLED:
        return False, {"error": "Authentication required (JWT or API key)"}

    # JWT not enabled, allow API key auth later
    return True, None


# API Keys Configuration
class APIKeyManager:
    """Manages API keys with distributed rate limiting via Redis."""

    def __init__(self, redis_client=None):
        self._keys = {}
        self._rate_limit_client = redis_client  # Distributed rate limiter
        self._load_keys()

    def _load_keys(self):
        """Load API keys from environment."""
        system_key = os.getenv("API_KEYS__SYSTEM", "sk-system-dev")
        self._keys[system_key] = {
            "project_id": "system",
            "permissions": ["*"],
            "rate_limit": 1000
        }

        # Load additional keys from environment if present
        for i in range(1, 10):
            key = os.getenv(f"API_KEYS__PROJECT_{i}")
            if key:
                self._keys[key] = {
                    "project_id": f"project_{i}",
                    "permissions": ["read_prompts", "run_prompt"],
                    "rate_limit": 100
                }

    async def validate_key(self, api_key: str, ip_address: str = "unknown") -> tuple[Optional[dict], dict]:
        """
        Validate API key and return key data with rate limit info.

        Returns:
            tuple: (key_data or None, rate_limit_info dict)
        """
        if not api_key:
            return None, {}

        # Check key exists
        key_data = self._keys.get(api_key)
        if not key_data:
            return None, {}

        # Check rate limit using distributed limiter
        rate_limit_config = LimitConfig(
            limit=key_data.get("rate_limit", 100),
            window_seconds=60,
            burst=10,
            enabled=True,
            grace_period=60,
            distributed=True
        )

        if self._rate_limit_client:
            allowed, limit_info = await self._rate_limit_client.check_rate_limit(
                api_key=api_key,
                ip_address=ip_address,
                limit_config=rate_limit_config
            )

            if not allowed:
                return None, limit_info
        else:
            # Fallback to in-memory if Redis not available
            if not self._check_rate_limit_memory(api_key, key_data.get("rate_limit", 100)):
                return None, {}

        return key_data, {}

    def _check_rate_limit_memory(self, api_key: str, limit: int) -> bool:
        """
        Fallback in-memory rate limiter when Redis is unavailable.
        This maintains backward compatibility.
        """
        now = time.time()
        if not hasattr(self, '_memory_rate_limits'):
            self._memory_rate_limits = {}

        key_data = self._memory_rate_limits.get(api_key)

        if key_data is None:
            self._memory_rate_limits[api_key] = [1, now]
            return True

        count, timestamp = key_data
        # Reset if more than 60 seconds passed
        if now - timestamp > 60:
            self._memory_rate_limits[api_key] = [1, now]
            return True

        # Check limit
        if count >= limit:
            return False

        self._memory_rate_limits[api_key] = [count + 1, timestamp]
        return True

    def check_permission(self, api_key: str, permission: str) -> bool:
        """Check if API key has specific permission."""
        key_data = self._keys.get(api_key)
        if not key_data:
            return False

        permissions = key_data.get("permissions", [])
        # Admin (*) has all permissions
        if "*" in permissions:
            return True

        return permission in permissions


# Global Redis client and distributed rate limiter
_redis_client: Optional[redis.Redis] = None
_distributed_rate_limiter: Optional[DistributedRateLimiter] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        # Use REDIS_URL from docker-compose or fallback
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_password = os.getenv("REDIS_PASSWORD", None)

        try:
            _redis_client = await redis.from_url(
                redis_url,
                password=redis_password,
                encoding="utf-8",
                decode_responses=True,
                max_connections=100,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await _redis_client.ping()
            logger.info(f"Redis client connected to {redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory rate limiting: {e}")
            _redis_client = None

    return _redis_client


async def get_distributed_rate_limiter() -> Optional[DistributedRateLimiter]:
    """Get or create distributed rate limiter."""
    global _distributed_rate_limiter
    if _distributed_rate_limiter is None:
        redis_client = await get_redis_client()
        if redis_client:
            try:
                _distributed_rate_limiter = DistributedRateLimiter(redis_client)
                logger.info("Distributed rate limiter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize distributed rate limiter: {e}")
                _distributed_rate_limiter = None
        else:
            logger.warning("Redis not available, using in-memory rate limiting")

    return _distributed_rate_limiter


# Global API key manager (will be initialized with Redis in startup)
api_keys = APIKeyManager()


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditLogger:
    """Audit logger for tracking API actions."""

    def __init__(self):
        self._logs = []  # In-memory logs (in production, would use database)
        self._max_logs = 10000

    def log(self, action: str, api_key: str = None, resource_type: str = None,
            resource_id: int = None, details: dict = None, ip_address: str = None):
        """Log an action."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "api_key": api_key[:10] + "..." if api_key and len(api_key) > 10 else api_key,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address
        }

        self._logs.append(entry)

        # Keep only last N logs
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]

        # Log to standard logger
        logger.info(f"AUDIT: {action} | key={entry.get('api_key')} | resource={resource_type}")

    def get_logs(self, limit: int = 100) -> list:
        """Get recent audit logs."""
        return self._logs[-limit:]

    def get_logs_by_action(self, action: str, limit: int = 100) -> list:
        """Get logs by action type."""
        return [log for log in self._logs if log["action"] == action][-limit:]

    def get_logs_by_key(self, api_key: str, limit: int = 100) -> list:
        """Get logs by API key."""
        return [log for log in self._logs if api_key in log.get("api_key", "")][-limit:]

    def clear_logs(self):
        """Clear all logs."""
        self._logs = []
        logger.info("Audit logs cleared")


# Global audit logger
audit_logger = AuditLogger()

# Global prompt executor with LLM integration (lazy init)
_prompt_executor: Optional[PromptExecutor] = None

def get_prompt_executor() -> PromptExecutor:
    """Get or create prompt executor."""
    global _prompt_executor
    if _prompt_executor is None:
        _prompt_executor = PromptExecutor()
    return _prompt_executor


# Audit action constants
class AuditActions:
    PROMPT_EXECUTED = "prompt_executed"
    CHAIN_EXECUTED = "chain_executed"
    MEMORY_SAVED = "memory_saved"
    MEMORY_READ = "memory_read"
    PROMPTS_LISTED = "prompts_listed"
    PROJECT_ADAPTED = "project_adapted"
    CONTEXT_CLEANED = "context_cleaned"
    API_KEY_VALIDATED = "api_key_validated"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


def require_api_key(func):
    """Decorator to require valid API key."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get API key from headers or context
        # For MCP, we need to handle this differently
        # This is a placeholder - real implementation would check MCP context
        return await func(*args, **kwargs)
    return wrapper


def load_prompt(prompt_name: str) -> dict:
    """Load a prompt from the prompts directory using registry."""
    # First try direct path
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if prompt_file.exists():
        content = prompt_file.read_text()
        return {
            "name": prompt_name,
            "file": prompt_file.name,
            "content": content
        }

    # Try with .md extension already present
    if prompt_name.endswith(".md"):
        prompt_file = PROMPTS_DIR / prompt_name
        if prompt_file.exists():
            content = prompt_file.read_text()
            return {
                "name": prompt_name,
                "file": prompt_file.name,
                "content": content
            }

    # Use registry to find the correct path
    registry = load_registry()
    prompts = registry.get("prompts", {})

    # Try exact match first
    if prompt_name in prompts:
        file_path = prompts[prompt_name].get("file", prompt_name)
        prompt_file = PROMPTS_DIR / file_path
        if prompt_file.exists():
            content = prompt_file.read_text()
            return {
                "name": prompt_name,
                "file": file_path,
                "content": content
            }

    # Try with .md extension added
    prompt_with_md = f"{prompt_name}.md"
    if prompt_with_md in prompts:
        file_path = prompts[prompt_with_md].get("file", prompt_with_md)
        prompt_file = PROMPTS_DIR / file_path
        if prompt_file.exists():
            content = prompt_file.read_text()
            return {
                "name": prompt_name,
                "file": file_path,
                "content": content
            }

    # Try removing .md extension if present
    prompt_without_md = prompt_name[:-3] if prompt_name.endswith(".md") else prompt_name
    if prompt_without_md in prompts:
        file_path = prompts[prompt_without_md].get("file", prompt_without_md)
        prompt_file = PROMPTS_DIR / file_path
        if prompt_file.exists():
            content = prompt_file.read_text()
            return {
                "name": prompt_name,
                "file": file_path,
                "content": content
            }

    raise FileNotFoundError(f"Prompt not found: {prompt_name}")


def load_registry() -> dict:
    """Load the prompt registry."""
    registry_file = PROMPTS_DIR / "registry.json"
    if registry_file.exists():
        return json.loads(registry_file.read_text())
    return {"registry_version": "1.0", "prompts": []}


def get_memory(project_id: str) -> dict:
    """Get project memory."""
    memory_file = MEMORY_DIR / project_id / "context.json"
    if memory_file.exists():
        return json.loads(memory_file.read_text())
    return {"memory": [], "context": {}}


async def _llm_route_intent(request: str) -> Optional[str]:
    """
    LLM-based intent routing (Siri-like).

    Uses LLM to classify user request and select appropriate prompt.
    """
    # Prompt for LLM to classify intent
    # Build intent options string for LLM
    intent_options = """promt-feature-add: добавить функцию, компонент, создать что-то новое
promt-bug-fix: исправить баг, найти ошибку, починить
promt-refactoring: рефакторинг, улучшить код, переписать
promt-security-audit: безопасность, уязвимости, аудит
promt-quality-test: тесты, проверка качества, unit тесты
promt-ci-cd-pipeline: деплой, CI/CD, pipeline,部署
promt-project-adaptation: адаптация, подключить проект
promt-prompt-creator: создать промт, новый шаблон
promt-system-adapt: инициализация, новый проект
promt-versioning-policy: версионирование"""

    classification_prompt = f"""Классифицируй запрос пользователя.

Доступные промты:
{intent_options}

Запрос: "{request}"

Ответь ТОЛЬКО названием промта (например: promt-feature-add).
Если не уверен - выбери наиболее подходящий."""

    try:
        from src.services.executor import PromptExecutor
        executor = PromptExecutor()

        # Use minimal settings for fast classification
        result = await executor.execute(
            classification_prompt,
            {"request": request, "context": {}}
        )

        if result.get("status") == "success":
            content = str(result.get("content", ""))

            # Handle MiniMax response format (dict with 'thinking' key)
            try:
                if content.startswith("{"):
                    import ast
                    content_dict = ast.literal_eval(content)
                    if isinstance(content_dict, dict) and "thinking" in content_dict:
                        content = content_dict["thinking"]
            except:
                pass

            # Extract prompt name from response
            content_lower = content.lower()
            for prompt_name in [
                "promt-feature-add", "promt-bug-fix", "promt-refactoring",
                "promt-security-audit", "promt-quality-test", "promt-ci-cd-pipeline",
                "promt-project-adaptation", "promt-prompt-creator",
                "promt-system-adapt", "promt-versioning-policy"
            ]:
                if prompt_name in content_lower:
                    logger.info(f"LLM routed '{request}' -> {prompt_name}")
                    return prompt_name

        return None
    except Exception as e:
        logger.error(f"LLM routing failed: {e}")
        return None


def save_memory(project_id: str, data: dict) -> None:
    """Save project memory."""
    project_dir = MEMORY_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    memory_file = project_dir / "context.json"
    memory_file.write_text(json.dumps(data, indent=2))


@mcp.tool
async def ai_prompts(request: str, context: dict = None, jwt_token: str = None) -> dict:
    """
    Universal handler for 'use ai-prompts' pattern.

    Parse natural language request and automatically select/execute
    the appropriate prompt from the library.

    Usage in Claude Code:
        "Добавь в README.md секцию с примерами. use ai-prompts"
        "Найди и исправь баги в коде. use ai-prompts"
        "Создай API эндпоинт для пользователей. use ai-prompts"

    Args:
        request: Natural language request (e.g., "добавь функцию")
        context: Optional context data
        jwt_token: JWT token for authentication (optional if JWT disabled)
        request: Natural language request (what you want to do)
        context: Optional context (file paths, project info, etc.)

    Returns:
        dict: Execution result with selected prompt and generated content

    Pattern:
        "action target. use ai-prompts"
        - action: что сделать (добавить, найти, создать, исправить, etc.)
        - target: над чем (README.md, API, функцию, баг, etc.)
    """
    try:
        # JWT Authentication
        is_valid, auth_data = validate_auth(jwt_token=jwt_token)
        if not is_valid:
            return {"status": "error", "error": "Authentication required", "hint": "Provide valid jwt_token or API key"}

        # Load registry for prompt selection
        registry = load_registry()
        prompts_list = registry.get("prompts", [])

        # Intent keywords mapping to prompts
        INTENT_MAP = {
            # Code operations (feature-add)
            "feature": "promt-feature-add",
            "добавить": "promt-feature-add",
            "добавить функт": "promt-feature-add",
            "создать": "promt-feature-add",
            "создай": "promt-feature-add",
            "создать компонент": "promt-feature-add",
            "new feature": "promt-feature-add",
            "add feature": "promt-feature-add",
            "фича": "promt-feature-add",
            "новую возможность": "promt-feature-add",

            # Bug/fix operations
            "bug": "promt-bug-fix",
            "исправить": "promt-bug-fix",
            "исправь": "promt-bug-fix",
            "исправить ошибку": "promt-bug-fix",
            "фикс": "promt-bug-fix",
            "fix bug": "promt-bug-fix",
            "баг": "promt-bug-fix",
            "ошибку": "promt-bug-fix",
            "найди": "promt-bug-fix",

            # Refactoring
            "refactor": "promt-refactoring",
            "рефакторинг": "promt-refactoring",
            "улучшить код": "promt-refactoring",
            "улучшить": "promt-refactoring",
            "улучши": "promt-refactoring",
            "модернизируй": "promt-refactoring",
            "перепиши": "promt-refactoring",
            "оптимизируй": "promt-refactoring",
            "упрости": "promt-refactoring",
            "упрости код": "promt-refactoring",

            # Security
            "security": "promt-security-audit",
            "безопасност": "promt-security-audit",
            "audit": "promt-security-audit",
            "аудит": "promt-security-audit",
            "уязвимост": "promt-security-audit",

            # Testing
            "test": "promt-quality-test",
            "тест": "promt-quality-test",
            "напиши тест": "promt-quality-test",
            "quality": "promt-quality-test",
            "проверь": "promt-quality-test",

            # Onboarding/adaptation
            "adapt": "promt-project-adaptation",
            "адаптац": "promt-project-adaptation",
            "onboard": "promt-onboarding",
            "подключи": "promt-project-adaptation",

            # CI/CD
            "ci-cd": "promt-ci-cd-pipeline",
            "ci cd": "promt-ci-cd-pipeline",
            "pipeline": "promt-ci-cd-pipeline",
            "deploy": "promt-ci-cd-pipeline",
            "деплой": "promt-ci-cd-pipeline",
            "github": "promt-ci-cd-pipeline",
            "github actions": "promt-ci-cd-pipeline",

            # Versioning
            "version": "promt-versioning-policy",
            "версион": "promt-versioning-policy",

            # Prompt creation (meta)
            "создай промт": "promt-prompt-creator",
            "добавь промт": "promt-prompt-creator",
            "new prompt": "promt-prompt-creator",
            "prompt creator": "promt-prompt-creator",
            "шаблон": "promt-prompt-creator",

            # System adaptation
            "адаптируй": "promt-system-adapt",
            "подключи систему": "promt-system-adapt",
            "init ai-promts": "promt-system-adapt",
            "инициализация ai-promts": "promt-system-adapt",
            "new project": "promt-system-adapt",
            "новый проект": "promt-system-adapt",

            # Bottleneck analysis & research (2026 docs standards)
            "bottleneck": "promt-bottleneck-analysis-2026",
            "узкие места": "promt-bottleneck-analysis-2026",
            "узких мест": "promt-bottleneck-analysis-2026",
            "всех узких": "promt-bottleneck-analysis-2026",
            "исследование": "promt-bottleneck-analysis-2026",
            "иследуй": "promt-bottleneck-analysis-2026",
            "проведи исследование": "promt-bottleneck-analysis-2026",
            "проанализируй": "promt-documentation-refactoring-standards-2026",
            "аудит": "promt-documentation-refactoring-standards-2026",
        }

        request_lower = request.lower()

        # Find matching prompt via keywords
        selected_prompt = None
        matched_keyword = None
        for keyword, prompt_name in INTENT_MAP.items():
            if keyword in request_lower:
                selected_prompt = prompt_name
                matched_keyword = keyword
                break

        # LLM-based routing fallback (when keyword fails)
        if not selected_prompt or matched_keyword == "default":
            llm_selected = await _llm_route_intent(request)
            if llm_selected:
                selected_prompt = llm_selected
                matched_keyword = "llm"

        # Default to feature-add if no match
        if not selected_prompt:
            selected_prompt = "promt-feature-add"
            matched_keyword = "default"

        # Build input data from request and context
        input_data = {
            "request": request,
            "context": context or {},
        }

        # Add file/project info if provided in context
        if context:
            input_data.update(context)

        # Extract simple info from request
        if "readme" in request_lower:
            input_data["file"] = "README.md"
        elif ".md" in request_lower:
            # Try to extract filename
            import re
            match = re.search(r'(\S+\.md)', request)
            if match:
                input_data["file"] = match.group(1)

        # Execute the selected prompt
        prompt = load_prompt(selected_prompt)
        result = await get_prompt_executor().execute(prompt["content"], input_data)

        # Audit logging
        audit_logger.log(
            action=AuditActions.PROMPT_EXECUTED,
            resource_type="ai_prompts",
            details={
                "request": request[:100],
                "selected_prompt": selected_prompt,
                "matched_keyword": matched_keyword
            }
        )

        return {
            "status": result.get("status", "success"),
            "request": request,
            "selected_prompt": selected_prompt,
            "matched_keyword": matched_keyword,
            "model": result.get("model", "unknown"),
            "content": result.get("content", ""),
            "error": result.get("error"),
            "usage": result.get("usage", {}),
            "hint": f"Used '{matched_keyword}' intent → {selected_prompt}"
        }

    except FileNotFoundError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Error in ai_prompts: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
async def run_prompt(prompt_name: str, input_data: dict, jwt_token: str = None) -> dict:
    """
    Execute a single prompt through LLM.

    Args:
        prompt_name: Name of the prompt to run (without .md)
        input_data: Input data for the prompt
        jwt_token: JWT token for authentication (optional if JWT disabled)

    Returns:
        dict: Execution result with generated content
    """
    try:
        # JWT Authentication
        is_valid, auth_data = validate_auth(jwt_token=jwt_token)
        if not is_valid:
            return {"status": "error", "error": "Authentication required"}
        prompt = load_prompt(prompt_name)
        logger.info(f"Running prompt: {prompt_name}")

        # Execute prompt through LLM
        executor = get_prompt_executor()
        logger.info(f"Executor provider: {executor.client.provider}, model: {executor.client.model}")
        result = await executor.execute(prompt["content"], input_data)

        return {
            "status": result.get("status", "success"),
            "prompt": prompt_name,
            "input": input_data,
            "model": result.get("model", "claude-3-5-sonnet"),
            "content": result.get("content", ""),
            "error": result.get("error"),
            "usage": result.get("usage", {}),
        }
    except FileNotFoundError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Error running prompt: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
async def run_prompt_chain(idea: str, stages: list[str], jwt_token: str = None) -> dict:
    """
    Execute full chain: idea → finish through LLM.

    Args:
        idea: The initial idea/concept
        stages: List of stages to execute (ideation, analysis, design, etc.)
        jwt_token: JWT token for authentication (optional if JWT disabled)

    Returns:
        dict: Chain execution results with generated content
    """
    # JWT Authentication
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    results = []
    prompts_data = []

    # Load all prompts in the chain
    for stage in stages:
        try:
            prompt = load_prompt(f"promt-{stage.lower()}")
            prompts_data.append({
                "name": stage,
                "content": prompt["content"]
            })
        except FileNotFoundError:
            results.append({
                "stage": stage,
                "status": "skipped",
                "reason": f"Prompt for stage '{stage}' not found"
            })

    # Execute chain through executor
    chain_results = await get_prompt_executor().execute_chain(prompts_data, {"idea": idea})

    # Format results
    for cr in chain_results:
        results.append({
            "stage": cr["name"],
            "status": cr["result"].get("status", "unknown"),
            "content": cr["result"].get("content", ""),
            "model": cr["result"].get("model"),
        })

    final_output = chain_results[-1]["result"].get("content", "") if chain_results else ""

    return {
        "status": "success",
        "idea": idea,
        "stages_executed": len([r for r in results if r["status"] == "success"]),
        "results": results,
        "final_output": final_output
    }


@mcp.tool
def list_prompts() -> dict:
    """
    List all available prompts.

    Returns:
        dict: List of prompts
    """
    registry = load_registry()

    # Audit logging
    audit_logger.log(
        action=AuditActions.PROMPTS_LISTED,
        resource_type="registry",
        details={"count": len(registry.get("prompts", []))}
    )

    return {
        "status": "success",
        "registry_version": registry.get("registry_version", "unknown"),
        "count": len(registry.get("prompts", [])),
        "prompts": registry.get("prompts", [])
    }


@mcp.tool
def get_project_memory(project_id: str) -> dict:
    """
    Get memory/context for a specific project.

    Args:
        project_id: ID of the project

    Returns:
        dict: Project memory
    """
    memory = get_memory(project_id)
    return {
        "status": "success",
        "project_id": project_id,
        "memory": memory
    }


@mcp.tool
def save_project_memory(project_id: str, key: str, value: dict) -> dict:
    """
    Save memory entry for a project.

    Args:
        project_id: ID of the project
        key: Memory key
        value: Memory value (dict)

    Returns:
        dict: Save result
    """
    try:
        memory = get_memory(project_id)
        memory["context"][key] = value
        memory["context"]["last_updated"] = __import__("datetime").datetime.now().isoformat()
        save_memory(project_id, memory)
        return {"status": "success", "project_id": project_id, "key": key}
    except Exception as e:
        logger.error(f"Error saving memory: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
def adapt_to_project(project_path: str) -> dict:
    """
    Auto-detect stack and adapt prompts.

    Args:
        project_path: Path to the project

    Returns:
        dict: Detected stack and adaptations
    """
    path = Path(project_path)
    if not path.exists():
        return {"status": "error", "error": "Project path does not exist"}

    stack = {"language": None, "framework": None, "database": None}

    # Detect language/framework
    if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
        stack["language"] = "Python"
        if (path / "fastapi" in open(path / "requirements.txt").read() if (path / "requirements.txt").exists() else False):
            stack["framework"] = "FastAPI"
        elif (path / "aiogram" in open(path / "requirements.txt").read() if (path / "requirements.txt").exists() else False):
            stack["framework"] = "aiogram"

    if (path / "package.json").exists():
        stack["language"] = "JavaScript/TypeScript"
        if (path / "next" in open(path / "package.json").read() if (path / "package.json").exists() else False):
            stack["framework"] = "Next.js"

    # Detect database
    if (path / "docker-compose.yml").exists():
        content = (path / "docker-compose.yml").read_text()
        if "postgres" in content:
            stack["database"] = "PostgreSQL"
        elif "redis" in content:
            stack["database"] = "Redis"

    return {
        "status": "success",
        "stack": stack,
        "adaptations": [
            f"Selected prompts for {stack.get('language', 'unknown')} project",
            f"Framework: {stack.get('framework', 'not detected')}"
        ]
    }


@mcp.tool
def context7_lookup(library: str, query: str = None) -> dict:
    """
    Get Context7 library ID and query documentation.

    This tool queries Context7 for library documentation in real-time.

    Args:
        library: Library/framework name (e.g., "fastapi", "react", "supabase")
        query: Optional specific question about the library

    Returns:
        dict: Library ID, query results, and suggested query for Context7
    """
    # Map common library names to Context7 IDs
    # Note: These IDs work with Claude Code's built-in Context7 MCP
    LIBRARY_MAP = {
        "fastapi": "/fastapi/fastapi",  # Updated: was /tiangolo/fastapi
        "flask": "/pallets/flask",
        "django": "/django/django",
        "react": "/facebook/react",
        "nextjs": "/vercel/next.js",
        "vue": "/vuejs/core",
        "angular": "/angular/angular",
        "nodejs": "/nodejs/node",
        "express": "/expressjs/express",
        "supabase": "/supabase/supabase",
        "prisma": "/prisma/prisma",
        "postgresql": "/postgresql/postgresql",
        "redis": "/redis/redis",
        "docker": "/docker/cli",
        "kubernetes": "/kubernetes/kubernetes",
        "aws": "/awsdocs/aws-cloud-development-kit",
        "gcp": "/googlecloudplatform/cloud-foundation-toolkit",
        "terraform": "/hashicorp/terraform",
        "pytest": "/pytest-dev/pytest",
        "pydantic": "/pydantic/pydantic",
        "sqlalchemy": "/sqlalchemy/sqlalchemy",
        "requests": "/psf/requests",
        "aiogram": "/aiogram/aiogram",
        "telebot": "/pyTelegramBotAPI/pytelegrambotapi",
        "anthropic": "/anthropics/anthropic-sdk-python",
        "openai": "/openai/openai-python",
    }

    library_lower = library.lower()
    context7_id = LIBRARY_MAP.get(library_lower)

    # Build query
    if query:
        full_query = query
    else:
        full_query = f"How to use {library}?"

    result = {
        "status": "success",
        "library": library,
        "context7_id": context7_id,
        "query": full_query,
        "mcp_call": None
    }

    if context7_id:
        result["mcp_call"] = {
            "server": "context7",
            "tool": "query_docs",
            "library_id": context7_id,
            "query": full_query
        }
        result["instructions"] = f"Use Context7 MCP: mcp__context7__query-docs with library_id={context7_id}, query=\"{full_query}\""
    else:
        result["instructions"] = f"Library '{library}' not in auto-map. Use Context7 MCP directly with library_id=\"/org/project\""
        # Try to help with common patterns
        if "python" in library_lower:
            result["suggestion"] = "Try '/pallets/flask' for Flask or '/tiangolo/fastapi' for FastAPI"
        elif "js" in library_lower or "javascript" in library_lower:
            result["suggestion"] = "Try '/facebook/react' for React or '/vercel/next.js' for Next.js"

    return result


async def _context7_query_docs(library_id: str, query: str) -> dict:
    """
    Query Context7 API for documentation.

    Uses Context7's MCP protocol via HTTP SSE.
    """
    import httpx

    context7_api_key = os.getenv("CONTEXT7_API_KEY")
    if not context7_api_key:
        return {"status": "error", "error": "CONTEXT7_API_KEY not configured"}

    try:
        # Context7 MCP endpoint
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First resolve library ID if needed
            if not library_id.startswith("/"):
                # Search for library
                search_url = "https://api.context7.com/v1/libraries/search"
                search_resp = await client.get(
                    search_url,
                    params={"q": library_id},
                    headers={"Authorization": f"Bearer {context7_api_key}"}
                )

                if search_resp.status_code == 200:
                    data = search_resp.json()
                    if data.get("results"):
                        library_id = data["results"][0]["id"]
                    else:
                        return {"status": "error", "error": f"Library not found: {library_id}"}

            # Query documentation
            query_url = f"https://api.context7.com/v1/library{library_id}/query"
            query_resp = await client.post(
                query_url,
                json={"query": query},
                headers={
                    "Authorization": f"Bearer {context7_api_key}",
                    "Content-Type": "application/json"
                }
            )

            if query_resp.status_code == 200:
                data = query_resp.json()
                return {
                    "status": "success",
                    "library_id": library_id,
                    "results": data.get("chunks", [])[:5],  # Top 5 results
                    "query": query
                }
            else:
                return {"status": "error", "error": f"API error: {query_resp.status_code}"}

    except Exception as e:
        logger.error(f"Context7 API error: {e}")
        # Check if it's a DNS error or API error - suggest MCP alternative
        error_str = str(e)
        if "Name or service not known" in error_str or "nodename nor servname" in error_str or "ConnectError" in error_str or "404" in error_str:
            return {
                "status": "error",
                "error": "Context7 API endpoint unavailable (404 or connection error)",
                "suggestion": "Use Claude Code's built-in Context7 MCP: mcp__context7__query-docs",
                "library_id": library_id,
                "query": query,
                "mcp_alternative": {
                    "server": "context7",
                    "tool": "query_docs",
                    "library_id": library_id,
                    "query": query
                }
            }
        return {"status": "error", "error": str(e)}


@mcp.tool
async def context7_query(library: str, query: str) -> dict:
    """
    Query Context7 documentation API directly.

    Note: The Context7 API (api.context7.com) is currently unavailable (404).
    This tool now returns instructions for using Claude Code's built-in Context7 MCP.

    Args:
        library: Library name (e.g., "fastapi", "react")
        query: Question about the library

    Returns:
        dict: Documentation results or instructions for Claude Code MCP
    """
    # First get library ID
    lookup_result = context7_lookup(library, query)
    library_id = lookup_result.get("context7_id")

    if not library_id:
        return lookup_result

    # Since API is unavailable, return instructions for Claude Code MCP
    return {
        "status": "unavailable",
        "message": "Context7 API endpoint is unavailable (404). Use Claude Code's built-in Context7 MCP instead.",
        "library": library,
        "library_id": library_id,
        "query": query,
        "instructions": {
            "step 1": "Use mcp__context7__resolve-library-id to get library ID",
            "step 2": "Use mcp__context7__query-docs with library_id and query",
            "example": f"mcp__context7__query-docs library_id={library_id} query=\"{query}\""
        },
        "alternative": {
            "tool": "mcp__context7__query-docs",
            "library_id": library_id,
            "query": query
        }
    }


@mcp.tool
def clean_context(current_tokens: int, threshold: int = 35000) -> dict:
    """
    Auto-clean context when token threshold is exceeded.

    Args:
        current_tokens: Current token count
        threshold: Token threshold to trigger cleanup

    Returns:
        dict: Cleanup result
    """
    if current_tokens < threshold:
        return {
            "status": "no_action",
            "current_tokens": current_tokens,
            "threshold": threshold,
            "message": "Token threshold not reached"
        }

    # In a real implementation, this would clean up old memory entries
    # For now, return a placeholder
    return {
        "status": "cleaned",
        "current_tokens": current_tokens,
        "threshold": threshold,
        "cleaned_entries": 0,
        "message": f"Context cleaned. Was at {current_tokens} tokens, threshold was {threshold}"
    }


@mcp.tool
def execute_bash(command: str, cwd: str = "/app") -> dict:
    """
    Execute a bash command and return output.

    This tool enables the documentation agent to execute shell commands
    for analysis tasks.

    Args:
        command: Shell command to execute
        cwd: Working directory (default: /app)

    Returns:
        dict: Command output and status
    """
    import subprocess
    import os

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "success",
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout[:5000] if result.stdout else "",
            "stderr": result.stderr[:1000] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "command": command,
            "error": "Command timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "command": command,
            "error": str(e)
        }


@mcp.tool
def get_available_mcp_tools() -> dict:
    """
    Get list of available MCP tools in this server.

    Returns:
        dict: List of tools with descriptions
    """
    tools = [
        {"name": "ai_prompts", "description": "Natural language prompt router (use ai-prompts)"},
        {"name": "run_prompt", "description": "Execute a single prompt"},
        {"name": "run_prompt_chain", "description": "Execute full chain (ideation → finish)"},
        {"name": "list_prompts", "description": "List all available prompts"},
        {"name": "get_project_memory", "description": "Get project memory/context"},
        {"name": "save_project_memory", "description": "Save project memory"},
        {"name": "adapt_to_project", "description": "Auto-detect stack and adapt prompts"},
        {"name": "clean_context", "description": "Clean context when token limit exceeded"},
        {"name": "context7_lookup", "description": "Get Context7 library ID for documentation lookup"},
        {"name": "context7_query", "description": "Query Context7 documentation API directly"},
        {"name": "get_available_mcp_tools", "description": "Get this list of tools"}
    ]

    audit_logger.log(
        action=AuditActions.PROMPTS_LISTED,
        resource_type="tools",
        details={"count": len(tools)}
    )

    return {
        "status": "success",
        "server": "AI Prompt System",
        "version": "1.0.0",
        "tools": tools,
        "external_integrations": {
            "context7": {
                "description": "Use Context7 MCP for up-to-date documentation",
                "tool": "context7_lookup",
                "example": "context7_lookup('fastapi', 'how to create API endpoint')",
                "mcp_call": "mcp__context7__query-docs"
            },
            "github": "Use GitHub MCP for repository operations"
        }
    }


async def startup_event():
    """Startup event handler."""
    logger.info("Starting AI Prompt System MCP Server...")

    # Initialize distributed rate limiting
    try:
        rate_limiter = await get_distributed_rate_limiter()
        if rate_limiter:
            global api_keys
            api_keys = APIKeyManager(redis_client=rate_limiter.redis)
            logger.info("Distributed rate limiting enabled (Redis-based)")
        else:
            logger.info("Rate limiting: enabled (in-memory fallback)")
    except Exception as e:
        logger.warning(f"Failed to initialize distributed rate limiting: {e}")
        logger.info("Rate limiting: enabled (in-memory fallback)")

    # Configure baseline verification
    verify_enabled = os.getenv("BASELINE_VERIFY_ENABLED", "true").lower() == "true"
    verify_on_load = os.getenv("BASELINE_VERIFY_ON_LOAD", "false").lower() == "true"
    action_on_mismatch = os.getenv("BASELINE_ACTION_ON_MISMATCH", "log_warning")

    configure_baseline_verification(
        enabled=verify_enabled,
        verify_on_startup=True,
        verify_on_load=verify_on_load,
        verify_interval_seconds=3600,
        action_on_mismatch=action_on_mismatch
    )

    # Verify baseline on startup
    if verify_enabled:
        try:
            storage = get_storage()
            results = verify_baseline_on_startup(storage)

            if not results.get("verified", True):
                logger.warning(
                    "Baseline verification completed with warnings. "
                    "System will continue operating but core prompts may not be trusted."
                )
        except Exception as e:
            logger.error(f"Baseline verification error: {e}")

    logger.info("MCP Tools: ai_prompts, run_prompt, run_prompt_chain, list_prompts, get_project_memory, save_project_memory, adapt_to_project, clean_context, context7_lookup")
    logger.info(f"API Keys loaded: {len(api_keys._keys)} keys")
    logger.info(f"Rate limiting: {'distributed (Redis)' if _distributed_rate_limiter else 'in-memory (fallback)'}")
    logger.info(f"Baseline verification: {'enabled' if verify_enabled else 'disabled'}")


async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down AI Prompt System MCP Server...")

    # Close Redis connection
    try:
        if _redis_client:
            await _redis_client.close()
            logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")

    # Clear prompt storage cache
    try:
        storage = get_storage()
        storage.clear_cache()
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

    logger.info("Shutdown complete")


# Note: FastMCP doesn't support add_event_handler, call startup/shutdown in main()
# See main() below for startup/shutdown handling

if __name__ == "__main__":
    # Run startup logic
    import asyncio
    asyncio.run(startup_event())
    # Support both transport modes
    # stdio: for Claude Code MCP (docker run --rm -i)
    # sse: for HTTP-based MCP clients
    transport = os.getenv("MCP_TRANSPORT", "sse")

    if transport == "stdio":
        # Claude Code uses stdio transport
        mcp.run(transport="stdio")
    else:
        # Default: SSE transport for HTTP
        mcp.run(transport="sse", host="0.0.0.0", port=8000)