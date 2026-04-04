"""
API Tools Package - MCP tool modules.

This package contains extracted MCP tools from server.py:
- auth_tools: JWT authentication tools
- memory_tools: Project memory management
- prompt_tools: Prompt execution and management
- project_tools: Project management and SFTP
- session_tools: MCP session management
- reviewer_tools: Code review tools (pre-existing)
- explorer_tools: Code exploration tools (pre-existing)

Usage:
    from src.api.tools import register_all_tools

    # In server.py startup:
    register_all_tools(mcp, {
        "jwt_service": jwt_service,
        "jwt_enabled": JWT_ENABLED,
        "memory_dir": MEMORY_DIR,
        "prompts_dir": PROMPTS_DIR,
        "prompt_executor": get_prompt_executor(),
        "validate_auth": validate_auth,
        "load_prompt": load_prompt,
        "load_registry": load_registry,
        "audit_logger": audit_logger,
        "get_project_service": get_project_service,
        "get_memory": get_memory,
        "save_memory": save_memory,
        "get_session_manager": get_session_manager,
    })
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Import tool modules
from src.api.tools import auth_tools
from src.api.tools import memory_tools
from src.api.tools import prompt_tools
from src.api.tools import project_tools
from src.api.tools import session_tools

# Import pre-existing tools (for reference, not re-registered)
# from src.api.tools import reviewer_tools
# from src.api.tools import explorer_tools

# Guard to prevent double registration
_tools_registered = False


def register_all_tools(mcp, dependencies: Dict[str, Any]) -> list:
    """
    Register all MCP tools with the server.

    Args:
        mcp: FastMCP server instance
        dependencies: Dict containing all required dependencies:
            - jwt_service: JWTService instance (can be None)
            - jwt_enabled: Whether JWT is enabled
            - memory_dir: Path to memory directory
            - prompts_dir: Path to prompts directory
            - prompt_executor: PromptExecutor instance
            - validate_auth: Validation function
            - load_prompt: Load prompt function
            - load_registry: Load registry function
            - audit_logger: AuditLogger instance
            - get_project_service: Function returning ProjectService
            - get_memory: Function to get memory
            - save_memory: Function to save memory
            - get_session_manager: Function returning MCPSessionManager

    Returns:
        list: All registered tool functions
    """
    global _tools_registered

    if _tools_registered:
        logger.info("Tools already registered, skipping")
        return []

    all_tools = []

    # Register auth tools (JWT)
    jwt_service = dependencies.get("jwt_service")
    jwt_enabled = dependencies.get("jwt_enabled", False)

    if jwt_enabled:
        try:
            auth_tools_list = auth_tools.register_auth_tools(mcp, jwt_service, jwt_enabled)
            all_tools.extend(auth_tools_list)
            logger.info(f"Registered {len(auth_tools_list)} auth tools")
        except Exception as e:
            logger.error(f"Failed to register auth tools: {e}")

    # Register memory tools
    memory_dir = dependencies.get("memory_dir")
    if memory_dir:
        try:
            memory_tools_list = memory_tools.register_memory_tools(mcp, memory_dir)
            all_tools.extend(memory_tools_list)
            logger.info(f"Registered {len(memory_tools_list)} memory tools")
        except Exception as e:
            logger.error(f"Failed to register memory tools: {e}")

    # Register prompt tools
    prompts_dir = dependencies.get("prompts_dir")
    prompt_executor = dependencies.get("prompt_executor")
    validate_auth = dependencies.get("validate_auth")
    load_prompt = dependencies.get("load_prompt")
    load_registry = dependencies.get("load_registry")
    audit_logger = dependencies.get("audit_logger")

    if all([prompts_dir, prompt_executor, validate_auth, load_prompt, load_registry]):
        try:
            prompt_tools_list = prompt_tools.register_prompt_tools(
                mcp,
                prompts_dir,
                prompt_executor,
                validate_auth,
                load_prompt,
                load_registry,
                audit_logger
            )
            all_tools.extend(prompt_tools_list)
            logger.info(f"Registered {len(prompt_tools_list)} prompt tools")
        except Exception as e:
            logger.error(f"Failed to register prompt tools: {e}")

    # Register project tools
    get_project_service = dependencies.get("get_project_service")
    get_memory = dependencies.get("get_memory")
    save_memory = dependencies.get("save_memory")

    if get_project_service:
        try:
            project_tools_list = project_tools.register_project_tools(
                mcp,
                get_project_service,
                get_memory,
                save_memory
            )
            all_tools.extend(project_tools_list)
            logger.info(f"Registered {len(project_tools_list)} project tools")
        except Exception as e:
            logger.error(f"Failed to register project tools: {e}")

    # Register session tools
    get_session_manager = dependencies.get("get_session_manager")

    if get_session_manager:
        try:
            session_tools_list = session_tools.register_session_tools(mcp, get_session_manager)
            all_tools.extend(session_tools_list)
            logger.info(f"Registered {len(session_tools_list)} session tools")
        except Exception as e:
            logger.error(f"Failed to register session tools: {e}")

    logger.info(f"Total tools registered: {len(all_tools)}")
    _tools_registered = True
    return all_tools


def get_all_tools() -> list:
    """
    Get list of all tool names (for documentation/listing purposes).

    This function imports all tool modules and returns tool names,
    without actually registering them.

    Returns:
        list: List of tool names
    """
    return [
        # Auth tools
        "generate_jwt_token",
        "validate_jwt_token",
        "revoke_jwt_token",
        # Memory tools
        "get_project_memory",
        "save_project_memory",
        # Prompt tools
        "run_prompt",
        "run_prompt_chain",
        "list_prompts",
        "get_prompt",
        # Project tools
        "adapt_to_project",
        "create_project",
        "get_project",
        "list_projects",
        "update_project",
        "delete_project",
        "create_project_api_key",
        "list_project_api_keys",
        "revoke_project_api_key",
        "connect_project_sftp",
        "disconnect_project_sftp",
        # Session tools
        "create_mcp_session",
        "get_mcp_session",
        "update_mcp_session",
        "delete_mcp_session",
        "list_mcp_sessions",
    ]
