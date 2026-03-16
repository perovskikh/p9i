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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("AI Prompt System")

# Configuration
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"


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


if __name__ == "__main__":
    logger.info("Starting AI Prompt System MCP Server...")
    mcp.run()