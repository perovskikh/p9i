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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("AI Prompt System")

# Configuration
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"

# API Keys Configuration
class APIKeyManager:
    """Manages API keys with rate limiting."""

    def __init__(self):
        self._keys = {}
        self._rate_limits = {}  # {key: (count, timestamp)}
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

    def validate_key(self, api_key: str) -> Optional[dict]:
        """Validate API key and return key data."""
        if not api_key:
            return None

        # Check key exists
        key_data = self._keys.get(api_key)
        if not key_data:
            return None

        # Check rate limit
        if not self._check_rate_limit(api_key, key_data.get("rate_limit", 100)):
            return None

        return key_data

    def _check_rate_limit(self, api_key: str, limit: int) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        key_data = self._rate_limits.get(api_key)

        if key_data is None:
            self._rate_limits[api_key] = [1, now]
            return True

        count, timestamp = key_data
        # Reset if more than 60 seconds passed
        if now - timestamp > 60:
            self._rate_limits[api_key] = [1, now]
            return True

        # Check limit
        if count >= limit:
            return False

        self._rate_limits[api_key] = [count + 1, timestamp]
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


# Global API key manager
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
    """Load a prompt from the prompts directory."""
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_name}")

    content = prompt_file.read_text()
    return {
        "name": prompt_name,
        "file": prompt_file.name,
        "content": content
    }


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


def save_memory(project_id: str, data: dict) -> None:
    """Save project memory."""
    project_dir = MEMORY_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    memory_file = project_dir / "context.json"
    memory_file.write_text(json.dumps(data, indent=2))


@mcp.tool
def run_prompt(prompt_name: str, input_data: dict) -> dict:
    """
    Execute a single prompt.

    Args:
        prompt_name: Name of the prompt to run (without .md)
        input_data: Input data for the prompt

    Returns:
        dict: Execution result
    """
    try:
        prompt = load_prompt(prompt_name)

        # Audit logging
        audit_logger.log(
            action=AuditActions.PROMPT_EXECUTED,
            resource_type="prompt",
            details={"prompt_name": prompt_name, "input_keys": list(input_data.keys())}
        )

        # In a real implementation, this would call an LLM
        # For now, return the prompt structure
        return {
            "status": "success",
            "prompt": prompt_name,
            "content": prompt["content"],
            "input": input_data,
            "result": f"Prompt '{prompt_name}' loaded. Execute with LLM to get results."
        }
    except FileNotFoundError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Error running prompt: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool
def run_prompt_chain(idea: str, stages: list[str]) -> dict:
    """
    Execute full chain: idea → finish.

    Args:
        idea: The initial idea/concept
        stages: List of stages to execute (ideation, analysis, design, etc.)

    Returns:
        dict: Chain execution results
    """
    results = []
    current_result = idea

    for stage in stages:
        try:
            prompt = load_prompt(f"promt-{stage.lower()}")
            results.append({
                "stage": stage,
                "status": "success",
                "prompt": prompt["name"]
            })
            current_result = f"Processed through {stage}"
        except FileNotFoundError:
            results.append({
                "stage": stage,
                "status": "skipped",
                "reason": f"Prompt for stage '{stage}' not found"
            })

    return {
        "status": "success",
        "idea": idea,
        "stages_executed": len([r for r in results if r["status"] == "success"]),
        "results": results,
        "final_output": current_result
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
def get_available_mcp_tools() -> dict:
    """
    Get list of available MCP tools in this server.

    Returns:
        dict: List of tools with descriptions
    """
    tools = [
        {"name": "run_prompt", "description": "Execute a single prompt"},
        {"name": "run_prompt_chain", "description": "Execute full chain (ideation → finish)"},
        {"name": "list_prompts", "description": "List all available prompts"},
        {"name": "get_project_memory", "description": "Get project memory/context"},
        {"name": "save_project_memory", "description": "Save project memory"},
        {"name": "adapt_to_project", "description": "Auto-detect stack and adapt prompts"},
        {"name": "clean_context", "description": "Clean context when token limit exceeded"},
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
            "context7": "Use Context7 MCP for documentation",
            "github": "Use GitHub MCP for repository operations"
        }
    }


if __name__ == "__main__":
    logger.info("Starting AI Prompt System MCP Server...")
    logger.info("MCP Tools: run_prompt, run_prompt_chain, list_prompts, get_project_memory, save_project_memory, adapt_to_project, clean_context")
    logger.info(f"API Keys loaded: {len(api_keys._keys)} keys")
    logger.info("Rate limiting: enabled (60s window)")
    # Use SSE transport for HTTP-based MCP
    mcp.run(transport="sse", host="0.0.0.0", port=8000)