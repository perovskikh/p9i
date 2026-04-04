"""
Memory MCP Tools - Project memory management tools.

These tools provide project context/memory management functionality.
"""

import json
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# Memory directory - will be set during registration
MEMORY_DIR = None


def register_memory_tools(mcp, memory_dir: Path):
    """
    Register memory management tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        memory_dir: Path to the memory directory
    """
    global MEMORY_DIR
    MEMORY_DIR = memory_dir

    def get_memory(project_id: str) -> dict:
        """Load memory for a project."""
        memory_file = MEMORY_DIR / f"{project_id}.json"
        if memory_file.exists():
            try:
                with open(memory_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"context": {}, "history": []}
        return {"context": {}, "history": []}

    def save_memory(project_id: str, data: dict) -> None:
        """Save memory for a project."""
        memory_file = MEMORY_DIR / f"{project_id}.json"
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, "w") as f:
            json.dump(data, f, indent=2)

    @mcp.tool()
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

    @mcp.tool()
    def save_project_memory(project_id: str, key: str, value: Union[dict, str]) -> dict:
        """
        Save memory entry for a project.

        Args:
            project_id: ID of the project
            key: Memory key
            value: Memory value (dict or JSON string)

        Returns:
            dict: Save result
        """
        try:
            # Handle both dict and string input (MCP sometimes passes string)
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = {"raw": value}

            memory = get_memory(project_id)
            memory["context"][key] = value
            memory["context"]["last_updated"] = __import__("datetime").datetime.now().isoformat()
            save_memory(project_id, memory)
            return {"status": "success", "project_id": project_id, "key": key}
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            return {"status": "error", "error": str(e)}

    return [get_project_memory, save_project_memory]
