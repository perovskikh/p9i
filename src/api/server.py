# src/api/server.py
"""
AI Prompt System - FastMCP Server

MCP-сервер для управления AI-промтами с полным циклом:
- Генерация промтов из любой идеи (Prompt Factory)
- Верификация качества (Self-Verification)
- Версионирование и rollback
- Multi-tenant изоляция (API Keys)
"""

# Load .env FIRST, before any imports that might use os.getenv
from pathlib import Path
from dotenv import load_dotenv

env_paths = [
    Path.cwd() / ".env",
    Path(__file__).parent.parent / ".env",
    Path("/app/.env"),
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break

# Now safe to import other modules
from fastmcp import FastMCP
import json
import logging
import os
import time
from typing import Optional
from functools import wraps
import asyncio

# Redis imports for distributed rate limiting
import redis.asyncio as redis

# Import executor for LLM integration
from src.services.executor import PromptExecutor
from src.services.orchestrator import AgentOrchestrator, get_orchestrator

# Import v2 storage and middleware
from src.storage.prompts_v2 import (
    PromptStorageV2,
    get_storage,
    get_prompt,
    get_tier_prompts,
    verify_baseline,
    PromptTier
)
from src.storage.packs import get_pack_loader
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

# Import UI/UX design resources
from src.infrastructure.uiux import register_uiux_tools

# Import Browser automation resources
from src.infrastructure.browser import register_browser_tools

# Import Deduplication Guard
from src.domain.services.prompt_guard import get_prompt_guard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_ENABLED = os.getenv("JWT_ENABLED", "false").lower() == "true"
# SECURITY: Require JWT_SECRET to be set in production
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    if JWT_ENABLED:
        raise ValueError("JWT_SECRET environment variable must be set when JWT_ENABLED=true")
    JWT_SECRET = "dev-only-secret"  # Only used when JWT is disabled

# Import JWT service if enabled
_jwt_service = None
if JWT_ENABLED:
    from src.middleware.jwt_auth import JWTService, get_jwt_service as _get_jwt_service
    _jwt_service = _get_jwt_service()
    logger.info("JWT authentication enabled")

# Create MCP server
mcp = FastMCP("AI Prompt System")

# Health check endpoint
@mcp.resource("health://system")
def health_check() -> str:
    """Health check endpoint for monitoring."""
    return json.dumps({
        "status": "healthy",
        "service": "AI Prompt System MCP Server",
        "version": "2.0.0",
        "timestamp": time.time()
    })


# JWT Auth Tools (only if JWT_ENABLED)
if JWT_ENABLED:
    @mcp.tool()
    def generate_jwt_token(
        subject: str,
        role: str = "user",
        expiry_hours: int = 24,
        admin_key: str = None
    ) -> dict:
        """
        Generate a JWT access token for API authentication.

        Args:
            subject: User or project identifier
            role: Role (admin, developer, user)
            expiry_hours: Token expiration in hours (default 24)
            admin_key: Required admin key to generate tokens (from JWT_ADMIN_KEY env)
        """
        global _jwt_service

        if not JWT_ENABLED:
            return {"status": "error", "error": "JWT authentication is not enabled"}

        # SECURITY: Require admin key for token generation
        jwt_admin_key = os.getenv("JWT_ADMIN_KEY")
        if jwt_admin_key and admin_key != jwt_admin_key:
            return {"status": "error", "error": "Invalid admin key"}

        # SECURITY: Prevent privilege escalation - only admin can create admin tokens
        if role == "admin" and admin_key != jwt_admin_key:
            return {"status": "error", "error": "Admin role requires valid admin key"}

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
    Universal handler for 'use p9i' pattern.

    Parse natural language request and automatically select/execute
    the appropriate prompt from the library.

    Usage in Claude Code:
        "Добавь в README.md секцию с примерами. use p9i"
        "Найди и исправь баги в коде. use p9i"
        "Создай API эндпоинт для пользователей. use p9i"

    Args:
        request: Natural language request (e.g., "добавь функцию")
        context: Optional context data
        jwt_token: JWT token for authentication (optional if JWT disabled)
        request: Natural language request (what you want to do)
        context: Optional context (file paths, project info, etc.)

    Returns:
        dict: Execution result with selected prompt and generated content

    Pattern:
        "action target. use p9i"
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
            # === ORDER MATTERS: Longest/most specific first ===

            # GitHub MCP - PR, Issues, Workflows (MOST SPECIFIC FIRST)
            "github actions": "promt-github-mcp",
            "github issue": "promt-github-mcp",
            "pull request": "promt-github-mcp",
            "merge request": "promt-github-mcp",
            "create pr": "promt-github-mcp",
            "merge pr": "promt-github-mcp",
            "create issue": "promt-github-mcp",
            "workflow": "promt-github-mcp",
            "мердж": "promt-github-mcp",
            "создай pr": "promt-github-mcp",
            "создай issue": "promt-github-mcp",
            "gitmcp": "promt-gitmcp",
            "изучи репозиторий": "promt-gitmcp",
            "изучи библиотеку": "promt-gitmcp",
            "understand repo": "promt-gitmcp",
            "learn library": "promt-gitmcp",
            "repository analysis": "promt-gitmcp",

            # Claude Cookbook integration
            "claude cookbook": "promt-claude-cookbook",
            "claude api": "promt-claude-cookbook",
            "anthropic api": "promt-claude-cookbook",
            "tool calling": "promt-claude-cookbook",
            "sub-agent": "promt-claude-cookbook",
            "multimodal": "promt-claude-cookbook",
            "json mode": "promt-claude-cookbook",
            "rag": "promt-claude-cookbook",
            "tool use": "promt-claude-cookbook",
            "vision": "promt-claude-cookbook",

            # ADR & Code Review
            "adr review": "promt-llm-review",
            "review adr": "promt-llm-review",
            "llm review": "promt-llm-review",
            "code review": "promt-llm-review",
            "ревью adr": "promt-llm-review",
            "проверь adr": "promt-llm-review",

            # Bottleneck analysis & research (2026 docs standards)
            "проведи исследование": "promt-bottleneck-analysis-2026",
            "узкие места": "promt-bottleneck-analysis-2026",
            "всех узких": "promt-bottleneck-analysis-2026",
            "bottleneck": "promt-bottleneck-analysis-2026",
            "исследуй": "promt-bottleneck-analysis-2026",
            "проанализируй": "promt-documentation-refactoring-standards-2026",

            # System adaptation
            "инициализация p9i": "promt-system-adapt",
            "подключи систему": "promt-system-adapt",
            "init p9i": "promt-system-adapt",
            "p9i init": "promt-system-adapt",  # Alternative order
            "новый проект": "promt-system-adapt",
            "new project": "promt-system-adapt",
            "адаптируй": "promt-system-adapt",

            # Prompt creation (meta)
            "создай промт": "promt-prompt-creator",
            "добавь промт": "promt-prompt-creator",
            "new prompt": "promt-prompt-creator",
            "prompt creator": "promt-prompt-creator",
            "шаблон": "promt-prompt-creator",

            # CI/CD (after GitHub to avoid conflict)
            "ci-cd": "promt-ci-cd-pipeline",
            "pipeline": "promt-ci-cd-pipeline",
            "деплой": "promt-ci-cd-pipeline",
            "github": "promt-ci-cd-pipeline",

            # Versioning
            "версион": "promt-versioning-policy",
            "version": "promt-versioning-policy",

            # Onboarding/adaptation
            "подключи": "promt-project-adaptation",
            "адаптац": "promt-project-adaptation",
            "onboard": "promt-project-adaptation",
            "adapt": "promt-project-adaptation",

            # Refactoring
            "упрости код": "promt-refactoring",
            "улучшить код": "promt-refactoring",
            "рефакторинг": "promt-refactoring",
            "модернизируй": "promt-refactoring",
            "оптимизируй": "promt-refactoring",
            "перепиши": "promt-refactoring",
            "упрости": "promt-refactoring",
            "улучшить": "promt-refactoring",
            "улучши": "promt-refactoring",
            "refactor": "promt-refactoring",

            # Full Cycle Implementation → promt-feature-add (already has full cycle)
            # Shortcuts for Siri - route to existing promt-feature-add
            "реализуй": "promt-feature-add",
            "реализуем": "promt-feature-add",
            "внедри": "promt-feature-add",
            "внедряем": "promt-feature-add",
            "сделай": "promt-feature-add",
            "выполни": "promt-feature-add",
            "выполни полный": "promt-feature-add",
            "полный цикл": "promt-feature-add",
            "end-to-end": "promt-feature-add",
            "e2e": "promt-feature-add",
            "implement": "promt-feature-add",
            "build": "promt-feature-add",

            # Browser Integration (full cycle)
            "browser": "promt-browser-integration",
            "браузер": "promt-browser-integration",
            "автоматизация браузера": "promt-browser-integration",
            "playwright": "promt-browser-integration",
            "puppeteer": "promt-browser-integration",

            # Security (MUST BE BEFORE bug fix!)
            "уязвим": "promt-security-audit",  # уязвимости, уязвимость
            "уязвимост": "promt-security-audit",
            "security": "promt-security-audit",
            "безопасност": "promt-security-audit",
            "audit": "promt-security-audit",

            # Bug/fix operations
            "исправить ошибку": "promt-bug-fix",
            "fix bug": "promt-bug-fix",
            "найди": "promt-bug-fix",
            "баг": "promt-bug-fix",
            "фикс": "promt-bug-fix",
            "ошибку": "promt-bug-fix",
            "исправить": "promt-bug-fix",
            "исправь": "promt-bug-fix",
            "bug": "promt-bug-fix",

            # Testing
            "напиши тест": "promt-quality-test",
            "проверь": "promt-quality-test",
            "quality": "promt-quality-test",
            "тест": "promt-quality-test",
            "test": "promt-quality-test",

            # UI/UX Design (Natural Language Routing)
            "ui component": "promt-ui-generator",
            "ux design": "promt-ui-generator",
            "ui design": "promt-ui-generator",
            "generate ui": "promt-ui-generator",
            "create ui": "promt-ui-generator",
            "ui ": "promt-ui-generator",
            "ux ": "promt-ui-generator",
            "button": "promt-ui-generator",
            "card": "promt-ui-generator",
            "component": "promt-ui-generator",
            "дизайн": "promt-ui-generator",
            "интерфейс": "promt-ui-generator",
            "ui": "promt-ui-generator",
            "ux": "promt-ui-generator",
            "компонент": "promt-ui-generator",
            "кнопка": "promt-ui-generator",
            "карточка": "promt-ui-generator",
            "стиль": "promt-ui-generator",
            "палитра": "promt-ui-generator",
            "шрифт": "promt-ui-generator",
            "иконка": "promt-ui-generator",

            # Code operations (feature-add) - MUST BE LAST (most generic)
            "создать компонент": "promt-feature-add",
            "новую возможность": "promt-feature-add",
            "add feature": "promt-feature-add",
            "new feature": "promt-feature-add",
            "фича": "promt-feature-add",
            "добавить функт": "promt-feature-add",
            "создай": "promt-feature-add",
            "создать": "promt-feature-add",
            "добавить": "promt-feature-add",
            "feature": "promt-feature-add",
        }

        request_lower = request.lower()

        # First, check pack triggers (higher priority than INTENT_MAP)
        pack_loader = get_pack_loader()
        pack_match = pack_loader.find_by_trigger(request_lower)
        if pack_match:
            selected_prompt = pack_match["prompt_file"].replace(".md", "")
            matched_keyword = f"pack:{pack_match['matched_keyword']}"
            logger.info(f"Pack trigger matched: {pack_match}")

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
async def run_prompt(prompt_name: str, input_data: dict, stream: bool = False, jwt_token: str = None) -> dict:
    """
    Execute a single prompt through LLM.

    Args:
        prompt_name: Name of the prompt to run (without .md)
        input_data: Input data for the prompt
        stream: Enable streaming response (default: False)
        jwt_token: JWT token for authentication (optional if JWT disabled)

    Returns:
        dict: Execution result with generated content
        If stream=True, returns status=streaming with stream generator
    """
    try:
        # JWT Authentication
        is_valid, auth_data = validate_auth(jwt_token=jwt_token)
        if not is_valid:
            return {"status": "error", "error": "Authentication required"}
        prompt = load_prompt(prompt_name)
        logger.info(f"Running prompt: {prompt_name}, stream={stream}")

        # UI/UX Context Injection for designer prompts
        uiux_prompts = ["promt-ui-generator", "ui-generator", "design", "ui"]
        if any(p in prompt_name.lower() for p in uiux_prompts):
            try:
                from src.infrastructure.uiux.context import get_uiux_context
                uiux_ctx = get_uiux_context()
                task = input_data.get("task", "")
                uiux_context = await uiux_ctx.build_context(task)
                if uiux_context.get("enabled"):
                    # Inject context into input_data
                    input_data = input_data.copy()
                    input_data["_uiux_context"] = uiux_context
                    logger.info(f"UI/UX context injected: {uiux_context.get('framework', 'auto')}")
            except Exception as e:
                logger.warning(f"UI/UX context injection failed: {e}")

        # Execute prompt through LLM
        executor = get_prompt_executor()
        logger.info(f"Executor provider: {executor.client.provider}, model: {executor.client.model}")
        result = await executor.execute(prompt["content"], input_data, stream=stream)

        # Handle streaming response
        if stream and result.get("status") == "streaming":
            # For streaming, we need to return the content as it arrives
            # Note: MCP doesn't support streaming natively, so we return full content
            content_chunks = []
            async for chunk in result.get("stream", []):
                content_chunks.append(chunk)
            full_content = "".join(content_chunks)
            return {
                "status": "success",
                "prompt": prompt_name,
                "input": input_data,
                "model": result.get("model", "claude-3-5-sonnet"),
                "content": full_content,
                "streaming": True,
                "usage": result.get("usage", {}),
            }

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
    Query Context7 MCP for documentation.

    Uses Context7's MCP protocol via HTTP at https://mcp.context7.com/mcp
    """
    import httpx

    context7_api_key = os.getenv("CONTEXT7_API_KEY")
    if not context7_api_key:
        return {"status": "error", "error": "CONTEXT7_API_KEY not configured"}

    try:
        # Context7 MCP endpoint - uses JSON-RPC over HTTP
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First resolve library ID if needed (using MCP tool)
            if not library_id.startswith("/"):
                # Use resolve-library-id MCP tool
                resolve_resp = await client.post(
                    "https://mcp.context7.com/mcp",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "resolve-library-id",
                            "arguments": {
                                "libraryName": library_id,
                                "query": query
                            }
                        },
                        "id": 1
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                )
                if resolve_resp.status_code == 200:
                    data = resolve_resp.json()
                    if "result" in data and "content" in data["result"]:
                        # Extract library ID from MCP response
                        for item in data["result"]["content"]:
                            if item.get("type") == "text":
                                import json
                                try:
                                    text_data = json.loads(item["text"])
                                    if text_data.get("results"):
                                        library_id = text_data["results"][0]["libraryId"]
                                except:
                                    pass

            # Query documentation using MCP tool
            query_resp = await client.post(
                "https://mcp.context7.com/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "query-docs",
                        "arguments": {
                            "libraryId": library_id,
                            "query": query
                        }
                    },
                    "id": 2
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )

            if query_resp.status_code == 200:
                data = query_resp.json()
                # Parse MCP response
                if "result" in data and "content" in data["result"]:
                    results = []
                    for item in data["result"]["content"]:
                        if item.get("type") == "text":
                            results.append(item["text"])
                    return {
                        "status": "success",
                        "library_id": library_id,
                        "results": results[:5],
                        "query": query
                    }
                return {"status": "error", "error": "Invalid MCP response format"}
            else:
                return {"status": "error", "error": f"MCP error: {query_resp.status_code}"}

    except Exception as e:
        logger.error(f"Context7 MCP error: {e}")
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
    Query Context7 documentation via MCP.

    Uses Context7 MCP at https://mcp.context7.com/mcp

    Args:
        library: Library name (e.g., "fastapi", "react")
        query: Question about the library

    Returns:
        dict: Documentation results from Context7
    """
    # First get library ID
    lookup_result = context7_lookup(library, query)
    library_id = lookup_result.get("context7_id")

    if not library_id:
        return lookup_result

    # Query Context7 MCP
    return await _context7_query_docs(library_id, query or f"How to use {library}?")


async def _github_mcp_call(tool_name: str, arguments: dict) -> dict:
    """Call GitHub MCP tool."""
    import httpx
    from dotenv import load_dotenv
    load_dotenv()

    github_token = os.getenv("GITHUB_TOKEN")
    github_mcp_url = os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")

    if not github_token:
        return {"status": "error", "error": "GITHUB_TOKEN not configured"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                github_mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    },
                    "id": 1
                },
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )

            if resp.status_code != 200:
                return {"status": "error", "error": f"GitHub MCP error: {resp.status_code}"}

            # Parse SSE response
            text = resp.text
            lines = text.split('\n')

            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        import json
                        obj = json.loads(data_str)
                        logger.info(f"GitHub MCP response: {obj.keys()}")

                        # Check for error in response
                        if 'error' in obj:
                            err = obj['error']
                            return {
                                "status": "error",
                                "error": f"GitHub MCP error: {err.get('message', err)}"
                            }

                        # Check for text content in result
                        if 'result' in obj:
                            result = obj['result']
                            if isinstance(result, dict) and 'content' in result:
                                # MCP tool result format
                                results = []
                                for item in result['content']:
                                    if item.get('type') == 'text':
                                        results.append(item['text'])
                                return {
                                    "status": "success",
                                    "tool": tool_name,
                                    "results": results
                                }
                            elif isinstance(result, dict):
                                # Direct dict result - convert to string
                                return {
                                    "status": "success",
                                    "tool": tool_name,
                                    "results": [str(result)]
                                }
                            elif isinstance(result, list):
                                # List result
                                return {
                                    "status": "success",
                                    "tool": tool_name,
                                    "results": result
                                }
                            else:
                                return {
                                    "status": "success",
                                    "tool": tool_name,
                                    "results": [str(result)]
                                }
                    except Exception as e:
                        logger.error(f"Parse error: {e}")

            return {"status": "error", "error": "No results from GitHub MCP"}

    except Exception as e:
        logger.error(f"GitHub MCP error: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
async def github_mcp_list_repos(query: str = "") -> dict:
    """List GitHub repositories accessible to the token.

    Args:
        query: Search query for repositories (optional)
    """
    if query:
        return await _github_mcp_call("search_repositories", {"query": query})
    return await _github_mcp_call("search_repositories", {})


@mcp.tool
async def github_mcp_create_pr(
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main"
) -> dict:
    """Create a pull request on GitHub."""
    return await _github_mcp_call("create_pull_request", {
        "owner": owner,
        "repo": repo,
        "title": title,
        "body": body,
        "head": head,
        "base": base
    })


@mcp.tool
async def github_mcp_create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str = ""
) -> dict:
    """Create an issue on GitHub."""
    return await _github_mcp_call("issue_write", {
        "owner": owner,
        "repo": repo,
        "title": title,
        "body": body,
        "method": "create"
    })


@mcp.tool
async def github_mcp_list_issues(
    owner: str,
    repo: str,
    state: str = "open"
) -> dict:
    """List issues on a GitHub repository."""
    return await _github_mcp_call("list_issues", {
        "owner": owner,
        "repo": repo,
        "state": state
    })


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


# ============================================================================
# PIPELINE TOOLS (ADR-004: Deep-Project Integration)
# ============================================================================

# In-memory pipeline state storage
_pipeline_state: dict = {}


@mcp.tool
async def run_interview(
    goal: str,
    context: dict = None,
    jwt_token: str = None
) -> dict:
    """
    AI-Powered Interview - Clarify requirements through Q&A.

    This tool implements the interview system from deep-project:
    - Ask clarifying questions to understand the goal
    - Extract constraints, preferences, and requirements
    - Return structured context for prompt generation

    Args:
        goal: The high-level goal or task to clarify
        context: Optional existing context
        jwt_token: JWT token for authentication

    Returns:
        dict: Interview results with clarified requirements
    """
    # Validate auth
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    # Generate interview questions using LLM
    interview_prompt = f"""You are conducting an AI interview to clarify requirements.

Goal: {goal}

Generate 3-5 clarifying questions to better understand this task.
For each question, explain why it's important.

Respond in JSON format:
{{
  "questions": [
    {{"question": "...", "why": "..."}}
  ],
  "key_constraints": [],
  "preferred_output_format": null
}}"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(interview_prompt, {"goal": goal})

        return {
            "status": "success",
            "goal": goal,
            "interview_questions": result.get("content", ""),
            "phase": "interview_completed"
        }
    except Exception as e:
        logger.error(f"Interview error: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
async def decompose_prompt(
    complex_goal: str,
    output_format: str = "chain",
    jwt_token: str = None
) -> dict:
    """
    Smart Decomposition - Split complex goals into sub-prompts.

    This tool implements the decomposition feature from deep-project:
    - Analyze the complex goal
    - Break it down into atomic sub-tasks
    - Define dependencies between sub-tasks
    - Create a DAG (Directed Acyclic Graph) of prompts

    Args:
        complex_goal: The complex goal to decompose
        output_format: "chain" (sequential) or "dag" (parallel possible)
        jwt_token: JWT token for authentication

    Returns:
        dict: Decomposition result with sub-prompts and dependencies
    """
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    decomposition_prompt = f"""Decompose this goal into atomic sub-prompts:

Goal: {complex_goal}
Format: {output_format}

Respond in JSON format:
{{
  "sub_prompts": [
    {{"id": "1", "name": "...", "prompt": "...", "depends_on": []}}
  ],
  "execution_order": ["1", "2", ...],
  "estimated_steps": 3
}}"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(decomposition_prompt, {"goal": complex_goal})

        return {
            "status": "success",
            "goal": complex_goal,
            "decomposition": result.get("content", ""),
            "format": output_format
        }
    except Exception as e:
        logger.error(f"Decomposition error: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
async def generate_spec(
    prompt_group: str,
    jwt_token: str = None
) -> dict:
    """
    Automated Spec Generation - Create documentation for prompt groups.

    This tool generates a spec.md file documenting:
    - Purpose of the prompt group
    - Input/output contracts
    - Dependencies and relationships
    - Usage examples

    Args:
        prompt_group: Name of the prompt group to document
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated spec documentation
    """
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    # Get prompts in the group
    registry = load_registry()
    prompts = registry.get("prompts", {})

    group_prompts = {
        name: info for name, info in prompts.items()
        if prompt_group.lower() in name.lower()
    }

    spec_prompt = f"""Generate spec documentation for prompt group '{prompt_group}';

Prompts in group:
{chr(10).join([f'- {k}: {v.get("description", "")}' for k, v in list(group_prompts.items())[:10]])}

Create a spec.md with:
1. Overview
2. Input/Output contracts
3. Dependencies
4. Usage examples"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(spec_prompt, {"group": prompt_group})

        return {
            "status": "success",
            "prompt_group": prompt_group,
            "spec": result.get("content", ""),
            "prompts_count": len(group_prompts)
        }
    except Exception as e:
        logger.error(f"Spec generation error: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
def checkpoint_save(
    session_id: str,
    state: dict,
    jwt_token: str = None
) -> dict:
    """
    Save checkpoint - Store session state for resume capability.

    Args:
        session_id: Unique session identifier
        state: State to save
        jwt_token: JWT token for authentication

    Returns:
        dict: Checkpoint saved confirmation
    """
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    global _pipeline_state
    _pipeline_state[session_id] = {
        "state": state,
        "timestamp": time.time()
    }

    return {
        "status": "success",
        "session_id": session_id,
        "saved_at": time.time()
    }


@mcp.tool
def checkpoint_load(
    session_id: str,
    jwt_token: str = None
) -> dict:
    """
    Load checkpoint - Resume session from saved state.

    Args:
        session_id: Unique session identifier
        jwt_token: JWT token for authentication

    Returns:
        dict: Restored session state
    """
    is_valid, auth_data = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    global _pipeline_state
    checkpoint = _pipeline_state.get(session_id)

    if not checkpoint:
        return {
            "status": "error",
            "error": f"Session {session_id} not found"
        }

    return {
        "status": "success",
        "session_id": session_id,
        "state": checkpoint.get("state", {}),
        "saved_at": checkpoint.get("timestamp")
    }


# ============================================================================
# UI/UX TOOLS (ADR-005: UI/UX Integration)
# ============================================================================

@mcp.tool
async def generate_tailwind(
    component: str,
    style: str = "modern",
    jwt_token: str = None
) -> dict:
    """
    Generate TailwindCSS classes for UI components.

    Args:
        component: Component name (button, card, input, etc.)
        style: Style variant (modern, minimal, brutal, etc.)
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated TailwindCSS code
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    prompt = f"""Generate TailwindCSS classes for a {component} component.

Style: {style}
Output: Complete HTML with TailwindCSS classes"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(prompt, {"component": component, "style": style})
        return {
            "status": "success",
            "component": component,
            "style": style,
            "code": result.get("content", "")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool
async def generate_shadcn(
    component: str,
    framework: str = "react",
    jwt_token: str = None
) -> dict:
    """
    Generate shadcn/ui components.

    Args:
        component: Component name
        framework: Framework (react, vue, svelte)
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated shadcn/ui component code
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    prompt = f"""Generate a shadcn/ui {component} component for {framework}.

Output: Complete component code with TypeScript types"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(prompt, {"component": component, "framework": framework})
        return {
            "status": "success",
            "component": component,
            "framework": framework,
            "code": result.get("content", "")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool
async def generate_textual(
    widget: str,
    theme: str = "dark",
    jwt_token: str = None
) -> dict:
    """
    Generate Textual (Python) CLI interfaces.

    Args:
        widget: Widget type (button, input, table, etc.)
        theme: Theme (dark, light)
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated Textual Python code
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    prompt = f"""Generate a Textual framework Python widget for {widget}.

Theme: {theme}
Output: Complete Python code with Textual"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(prompt, {"widget": widget, "theme": theme})
        return {
            "status": "success",
            "widget": widget,
            "theme": theme,
            "code": result.get("content", "")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool
async def generate_tauri(
    app_name: str,
    template: str = "basic",
    jwt_token: str = None
) -> dict:
    """
    Generate Tauri desktop app scaffolding.

    Args:
        app_name: Application name
        template: Template (basic, react, vue, svelte)
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated Tauri project structure
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    prompt = f"""Generate a Tauri desktop app structure for '{app_name}'.

Template: {template}
Output: Project structure and main files (Cargo.toml, src-tauri/.conf, index.html)"""

    try:
        executor = get_prompt_executor()
        result = await executor.execute(prompt, {"app_name": app_name, "template": template})
        return {
            "status": "success",
            "app_name": app_name,
            "template": template,
            "code": result.get("content", "")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================
# Figma Integration (ADR-006)
# ============================================================

@mcp.tool()
async def get_figma_file(
    file_key: str,
    jwt_token: str = None
) -> dict:
    """
    Get Figma file structure and metadata.

    Args:
        file_key: Figma file key (from URL: figma.com/file/FILE_KEY/...)
        jwt_token: JWT token for authentication

    Returns:
        dict: File structure with pages, frames, and components
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        from src.infrastructure.adapters.external.figma_adapter import get_figma_client

        client = await get_figma_client()

        if not client.token:
            return {"status": "error", "error": "FIGMA_TOKEN not configured"}

        result = await client.get_file(file_key)

        doc = result.get("document", {})
        pages = []

        for page in doc.get("children", []):
            pages.append({
                "id": page.get("id"),
                "name": page.get("name"),
                "type": page.get("type"),
                "childCount": len(page.get("children", []))
            })

        return {
            "status": "success",
            "file_key": file_key,
            "name": result.get("name", "Untitled"),
            "lastModified": result.get("lastModified"),
            "thumbnailUrl": result.get("thumbnailUrl"),
            "pages": pages,
            "version": result.get("version")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def get_figma_components(
    file_key: str,
    jwt_token: str = None
) -> dict:
    """
    Get all components from Figma file.
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        from src.infrastructure.adapters.external.figma_adapter import get_figma_client

        client = await get_figma_client()

        if not client.token:
            return {"status": "error", "error": "FIGMA_TOKEN not configured"}

        result = await client.get_file_components(file_key)

        return {
            "status": "success",
            "file_key": file_key,
            "components": result.get("components", []),
            "total": result.get("total", 0)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def get_figma_styles(
    file_key: str,
    jwt_token: str = None
) -> dict:
    """
    Get design tokens from Figma file.
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        from src.infrastructure.adapters.external.figma_adapter import get_figma_client

        client = await get_figma_client()

        if not client.token:
            return {"status": "error", "error": "FIGMA_TOKEN not configured"}

        styles = await client.get_file_styles(file_key)
        colors = await client.get_color_styles(file_key)

        return {
            "status": "success",
            "file_key": file_key,
            "styles": styles,
            "colors": colors
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def export_figma_nodes(
    file_key: str,
    node_ids: list,
    format: str = "png",
    scale: float = 2.0,
    jwt_token: str = None
) -> dict:
    """
    Export Figma nodes as images.
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        from src.infrastructure.adapters.external.figma_adapter import get_figma_client

        client = await get_figma_client()

        if not client.token:
            return {"status": "error", "error": "FIGMA_TOKEN not configured"}

        result = await client.export_images(file_key, node_ids, format, scale)

        return {
            "status": "success",
            "file_key": file_key,
            "format": format,
            "scale": scale,
            "images": result.get("images", {})
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def figma_to_code(
    file_key: str,
    node_ids: list = None,
    target: str = "tailwind",
    jwt_token: str = None
) -> dict:
    """
    Convert Figma design to code using AI.
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        from src.infrastructure.adapters.external.figma_adapter import get_figma_client

        client = await get_figma_client()

        if not client.token:
            return {"status": "error", "error": "FIGMA_TOKEN not configured"}

        file_data = await client.get_file(file_key)
        name = file_data.get("name", "Untitled")
        colors = await client.get_color_styles(file_key)

        context = f"""Convert this Figma design to {target} code.

Figma File: {name}
Color Palette:"""

        for color in colors[:10]:
            context += f"\n- {color.get('hex')}: {color.get('name')}"

        context += f"\n\nTarget: {target}\nOutput: Complete {target} code"""

        executor = get_prompt_executor()
        result = await executor.execute(context, {"file_key": file_key})

        return {
            "status": "success",
            "file_key": file_key,
            "file_name": name,
            "target": target,
            "colors_extracted": len(colors),
            "code": result.get("content", "")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================
# Multi-Agent Orchestrator (ADR-007)
# ============================================================

@mcp.tool()
async def p9i_siri(
    request: str,
    jwt_token: str = None
) -> dict:
    """
    Central router - Siri-like interface for p9i.

    Automatically detects needed agents and orchestrates their execution.

    Args:
        request: Natural language request
        jwt_token: JWT token for authentication

    Returns:
        dict: Orchestrated results from multiple agents

    Examples:
        "Спроектируй и создай систему авторизации"
        "Добавь функцию и проведи ревью"
        "Создай UI компонент и проверь безопасность"
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.route(request)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def architect_design(
    specification: str,
    jwt_token: str = None
) -> dict:
    """
    Architect Agent - System design and architecture.

    Args:
        specification: What to design
        jwt_token: JWT token for authentication

    Returns:
        dict: Architecture design
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.execute_single_agent("architect", specification)
        return {
            "status": result.status,
            "agent": result.agent,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def developer_code(
    task: str,
    language: str = "python",
    jwt_token: str = None
) -> dict:
    """
    Developer Agent - Code generation.

    Args:
        task: What code to generate
        language: Programming language (python, javascript, go, etc.)
        jwt_token: JWT token for authentication

    Returns:
        dict: Generated code
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        orchestrator = get_orchestrator()
        task_with_lang = f"{task} (language: {language})"
        result = await orchestrator.execute_single_agent("developer", task_with_lang)
        return {
            "status": result.status,
            "agent": result.agent,
            "output": result.output,
            "error": result.error,
            "language": language
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def reviewer_check(
    code: str,
    review_type: str = "general",
    language: str = "python",
    jwt_token: str = None
) -> dict:
    """
    Reviewer Agent - Code review, security audit, quality check.

    Args:
        code: Code to review
        review_type: Type of review (general, security, quality)
        language: Programming language
        jwt_token: JWT token for authentication

    Returns:
        dict: Review results
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        orchestrator = get_orchestrator()
        context = {
            "code": code,
            "language": language,
            "review_type": review_type
        }
        task = f"Проведи {review_type} ревью кода"
        result = await orchestrator.execute_single_agent("reviewer", task, context)
        return {
            "status": result.status,
            "agent": result.agent,
            "output": result.output,
            "error": result.error,
            "review_type": review_type
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def list_agents(
    jwt_token: str = None
) -> dict:
    """
    List all available agents in the orchestrator.

    Args:
        jwt_token: JWT token for authentication

    Returns:
        dict: List of agents with their prompts
    """
    is_valid, _ = validate_auth(jwt_token=jwt_token)
    if not is_valid:
        return {"status": "error", "error": "Authentication required"}

    try:
        orchestrator = get_orchestrator()
        agents = orchestrator.list_agents()
        return {
            "status": "success",
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
def check_prompt_uniqueness(
    prompt_name: str = None,
    keywords: str = None,
    check_similar: bool = False
) -> dict:
    """
    Check if a prompt or keyword already exists (prevent duplicates).

    Use this BEFORE creating a new prompt to avoid duplication.

    Args:
        prompt_name: Prompt name to check (e.g., "feature-add" or "promt-feature-add")
        keywords: Comma-separated keywords to check (e.g., "create,add,feature")
        check_similar: If True, find similar prompts by name

    Returns:
        dict with validation result and suggestions
    """
    guard = get_prompt_guard()

    results = {
        "valid": True,
        "prompt_name_check": None,
        "keyword_check": None,
        "similar_prompts": [],
        "suggestions": [],
        "existing_prompts_count": 0,
        "existing_keywords_count": 0
    }

    # Check prompt name
    if prompt_name:
        result = guard.check_prompt_name(prompt_name)
        results["prompt_name_check"] = {
            "name": prompt_name,
            "is_valid": result.is_valid,
            "duplicates": result.duplicates
        }
        if not result.is_valid:
            results["valid"] = False
            results["suggestions"].extend(result.suggestions)

    # Check keywords
    if keywords:
        kw_list = [k.strip() for k in keywords.split(",")]
        result = guard.check_keywords_batch(kw_list)
        results["keyword_check"] = {
            "keywords": kw_list,
            "is_valid": result.is_valid,
            "duplicates": result.duplicates
        }
        if not result.is_valid:
            results["valid"] = False
            results["suggestions"].extend(result.suggestions)

    # Find similar prompts
    if check_similar and prompt_name:
        similar = guard.get_similar_prompts(prompt_name)
        results["similar_prompts"] = similar
        if similar:
            results["suggestions"].append("Consider using existing similar prompt")

    # Summary
    results["existing_prompts_count"] = len(guard._prompt_index)
    results["existing_keywords_count"] = len(guard._keyword_map)

    return results


@mcp.tool
def get_prompt_deduplication_report() -> dict:
    """
    Get full deduplication report for the prompt system.

    Returns:
        dict with statistics and potential conflicts
    """
    guard = get_prompt_guard()
    return guard.get_report()


@mcp.tool
def get_available_mcp_tools() -> dict:
    """
    Get list of available MCP tools in this server.

    Returns:
        dict: List of tools with descriptions
    """
    tools = [
        {"name": "ai_prompts", "description": "Natural language prompt router (use p9i)"},
        {"name": "run_prompt", "description": "Execute a single prompt"},
        {"name": "run_prompt_chain", "description": "Execute full chain (ideation → finish)"},
        {"name": "list_prompts", "description": "List all available prompts"},
        {"name": "get_project_memory", "description": "Get project memory/context"},
        {"name": "save_project_memory", "description": "Save project memory"},
        {"name": "adapt_to_project", "description": "Auto-detect stack and adapt prompts"},
        {"name": "clean_context", "description": "Clean context when token limit exceeded"},
        # Pipeline tools (ADR-004)
        {"name": "run_interview", "description": "AI interview to clarify requirements"},
        {"name": "decompose_prompt", "description": "Decompose complex goals into sub-prompts"},
        {"name": "generate_spec", "description": "Auto-generate spec documentation"},
        {"name": "checkpoint_save", "description": "Save session checkpoint"},
        {"name": "checkpoint_load", "description": "Load session checkpoint"},
        # UI/UX tools (ADR-005) + Design Resources
        {"name": "generate_tailwind", "description": "Generate TailwindCSS component"},
        {"name": "generate_shadcn", "description": "Generate shadcn/ui component"},
        {"name": "generate_textual", "description": "Generate Textual TUI component"},
        {"name": "generate_tauri", "description": "Generate Tauri desktop app scaffold"},
        # UI/UX Design Resources (new)
        {"name": "search_ui_styles", "description": "Search UI styles (Glassmorphism, Minimalism, etc.)"},
        {"name": "search_colors", "description": "Search color palettes by industry"},
        {"name": "search_typography", "description": "Search font pairings and typography"},
        {"name": "search_icons", "description": "Search icon recommendations"},
        {"name": "search_ux_guidelines", "description": "Search UX best practices and guidelines"},
        {"name": "search_stack", "description": "Search framework-specific guidelines"},
        {"name": "search_all", "description": "Search all UI/UX design resources"},
        {"name": "get_design_system", "description": "Generate complete design system"},
        # Figma tools (ADR-006)
        {"name": "get_figma_file", "description": "Get Figma file structure"},
        {"name": "get_figma_components", "description": "Get components from Figma file"},
        {"name": "get_figma_styles", "description": "Get design tokens from Figma"},
        {"name": "export_figma_nodes", "description": "Export Figma nodes as images"},
        {"name": "figma_to_code", "description": "Convert Figma to TailwindCSS/shadcn code"},
        # Agent Orchestrator tools (ADR-007)
        {"name": "p9i_siri", "description": "Central router - Siri for p9i"},
        {"name": "architect_design", "description": "Architect agent - system design"},
        {"name": "developer_code", "description": "Developer agent - code generation"},
        {"name": "reviewer_check", "description": "Reviewer agent - code review"},
        {"name": "list_agents", "description": "List all available agents"},
        {"name": "context7_lookup", "description": "Get Context7 library ID for documentation lookup"},
        {"name": "context7_query", "description": "Query Context7 documentation API directly"},
        {"name": "github_mcp_list_repos", "description": "List/search GitHub repositories"},
        {"name": "github_mcp_create_issue", "description": "Create a GitHub issue"},
        {"name": "github_mcp_list_issues", "description": "List GitHub issues"},
        {"name": "github_mcp_create_pr", "description": "Create a pull request"},
        {"name": "execute_bash", "description": "Execute bash command"},
        {"name": "generate_jwt_token", "description": "Generate JWT token"},
        {"name": "validate_jwt_token", "description": "Validate JWT token"},
        {"name": "revoke_jwt_token", "description": "Revoke JWT token"},
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
            "github": {
                "description": "Use GitHub MCP for repository operations",
                "tools": ["github_mcp_list_repos", "github_mcp_create_issue", "github_mcp_list_issues", "github_mcp_create_pr"],
                "example": "github_mcp_list_repos('claude') or github_mcp_create_issue('owner', 'repo', 'title', 'body')"
            },
            "ui_ux_generation": {
                "description": "UI/UX code generation (ADR-005)",
                "tools": ["generate_tailwind", "generate_shadcn", "generate_textual", "generate_tauri"],
                "example": "generate_tailwind('button', 'primary button with hover state')"
            },
            "figma": {
                "description": "Figma API integration (ADR-006)",
                "tools": ["get_figma_file", "get_figma_components", "get_figma_styles", "export_figma_nodes", "figma_to_code"],
                "env_var": "FIGMA_TOKEN"
            },
            "agents": {
                "description": "Multi-Agent Orchestrator (ADR-007) - Siri-like interface",
                "tools": ["p9i_siri", "architect_design", "developer_code", "reviewer_check", "list_agents"],
                "example": "p9i_siri('Спроектируй и создай систему авторизации')"
            }
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

    # Register UI/UX design resources tools
    try:
        register_uiux_tools(mcp)
        logger.info("UI/UX design resources tools registered")
    except Exception as e:
        logger.warning(f"Failed to register UI/UX tools: {e}")

    # Register Browser automation tools
    try:
        register_browser_tools(mcp)
        logger.info("Browser automation tools registered")
    except Exception as e:
        logger.warning(f"Failed to register Browser tools: {e}")

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

def _run_webui_thread():
    """Web UI server in separate thread"""
    import uvicorn
    from src.api.webui import app as webui_app
    try:
        uvicorn.run(webui_app, host="0.0.0.0", port=8080, log_level="info")
    except Exception as e:
        print(f"WebUI Error: {e}")
        import traceback
        traceback.print_exc()


def _run_mcp_sse_thread():
    """MCP SSE server in separate thread"""
    mcp.run(transport="sse", host="0.0.0.0", port=8000)


async def main_async():
    """Main async entry point"""
    # Get transport mode
    transport = os.getenv("MCP_TRANSPORT", "sse")
    logger.info(f"Transport mode: {transport}")

    if transport == "stdio":
        # Claude Code uses stdio transport
        logger.info("Running in stdio mode")
        # Run startup in same event loop
        await startup_event()

        # Run MCP stdio in a separate thread to avoid asyncio conflict
        import threading
        stdio_thread = threading.Thread(target=lambda: mcp.run(transport="stdio"), daemon=True)
        stdio_thread.start()
        stdio_thread.join()
    else:
        # Run both Web UI and MCP SSE in separate threads
        logger.info("Running Web UI + MCP SSE mode")
        import threading

        # Start both servers in separate threads
        webui_thread = threading.Thread(target=_run_webui_thread, daemon=True)
        mcp_thread = threading.Thread(target=_run_mcp_sse_thread, daemon=True)

        webui_thread.start()
        mcp_thread.start()

        # Wait for both threads
        try:
            webui_thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main_async())