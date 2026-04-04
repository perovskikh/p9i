"""
Prompt MCP Tools - Prompt execution and management tools.

These tools provide prompt execution, chaining, and listing functionality.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Global references - will be set during registration
_prompt_executor = None
_validate_auth_func = None
_load_prompt_func = None
_load_registry_func = None
_audit_logger = None
_PROMPTS_DIR = None


def register_prompt_tools(
    mcp,
    prompts_dir: Path,
    prompt_executor,
    validate_auth_func,
    load_prompt_func,
    load_registry_func,
    audit_logger
):
    """
    Register prompt execution tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        prompts_dir: Path to prompts directory
        prompt_executor: PromptExecutor instance
        validate_auth_func: Function for JWT authentication
        load_prompt_func: Function to load a prompt
        load_registry_func: Function to load prompt registry
        audit_logger: AuditLogger instance
    """
    global _prompt_executor, _validate_auth_func, _load_prompt_func
    global _load_registry_func, _audit_logger, _PROMPTS_DIR

    _prompt_executor = prompt_executor
    _validate_auth_func = validate_auth_func
    _load_prompt_func = load_prompt_func
    _load_registry_func = load_registry_func
    _audit_logger = audit_logger
    _PROMPTS_DIR = prompts_dir

    @mcp.tool()
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
            is_valid, auth_data = _validate_auth_func(jwt_token=jwt_token)
            if not is_valid:
                return {"status": "error", "error": "Authentication required"}

            # Load prompt with error handling
            try:
                prompt = _load_prompt_func(prompt_name)
            except FileNotFoundError as e:
                logger.error(f"Prompt not found: {prompt_name}")
                return {"status": "error", "error": f"Prompt not found: {prompt_name}"}

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
            executor = _prompt_executor
            logger.info(f"Executor provider: {executor.client.provider}, model: {executor.client.model}")
            result = await executor.execute(prompt["content"], input_data, stream=stream)

            # Record token usage if available
            try:
                usage = result.get("usage", {})
                if usage:
                    # Token tracking would go here if Redis is available
                    pass
            except Exception as e:
                logger.warning(f"Token usage tracking failed: {e}")

            return {
                "status": "success",
                "content": result.get("content", ""),
                "model": result.get("model"),
                "usage": result.get("usage", {}),
            }

        except Exception as e:
            logger.error(f"Error running prompt: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
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
        is_valid, auth_data = _validate_auth_func(jwt_token=jwt_token)
        if not is_valid:
            return {"status": "error", "error": "Authentication required"}

        results = []
        prompts_data = []

        # Load all prompts in the chain
        for stage in stages:
            try:
                prompt = _load_prompt_func(f"promt-{stage.lower()}")
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
        chain_results = await _prompt_executor.execute_chain(prompts_data, {"idea": idea})

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

    @mcp.tool()
    def list_prompts(tier: str = None, limit: int = None) -> dict:
        """
        List all available prompts.

        Args:
            tier: Filter by tier (core, universal, pack, project)
            limit: Limit number of results

        Returns:
            dict: List of prompts
        """
        registry = _load_registry_func()
        prompts = registry.get("prompts", {})

        # Filter by tier if specified
        if tier:
            prompts = {k: v for k, v in prompts.items() if v.get("tier") == tier}

        # Apply limit
        if limit and limit > 0:
            prompts = dict(list(prompts.items())[:limit])

        # Audit logging
        if _audit_logger:
            _audit_logger.log(
                action="prompts_listed",
                resource_type="registry",
                details={"count": len(prompts)}
            )

        return {
            "status": "success",
            "registry_version": registry.get("registry_version", "unknown"),
            "count": len(prompts),
            "prompts": prompts
        }

    @mcp.tool()
    def get_prompt(prompt_name: str) -> dict:
        """
        Get a single prompt by name.

        Args:
            prompt_name: Name of the prompt (e.g. 'system-init' or 'promt-mvp-baseline-generator')

        Returns:
            dict: Prompt content and metadata
        """
        from src.storage.prompts_v2 import get_storage

        storage = get_storage()
        try:
            prompt = storage.load_prompt(prompt_name)
            return {
                "status": "success",
                "prompt_name": prompt.name,
                "version": prompt.version,
                "tier": prompt.tier.value if hasattr(prompt.tier, 'value') else str(prompt.tier),
                "content": prompt.content,
                "description": getattr(prompt, 'description', None) or '',
                "tags": prompt.tags
            }
        except Exception as e:
            logger.error(f"Error loading prompt '{prompt_name}': {e}")
            return {"status": "error", "error": f"Prompt not found: {prompt_name}"}

    return [run_prompt, run_prompt_chain, list_prompts, get_prompt]
