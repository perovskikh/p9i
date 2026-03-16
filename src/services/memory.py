# src/services/memory.py
"""
Memory service for project context management

Handles storing and retrieving project-specific context.
"""

from pathlib import Path
import json
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryService:
    """Manages project memory and context."""

    def __init__(self, memory_dir: str = "./memory"):
        self.memory_dir = Path(memory_dir)

    def get(self, project_id: str) -> dict:
        """
        Get memory for a project.

        Args:
            project_id: Project identifier

        Returns:
            dict: Project memory
        """
        memory_file = self.memory_dir / project_id / "context.json"
        if memory_file.exists():
            return json.loads(memory_file.read_text())
        return {"memory": [], "context": {}, "created_at": datetime.now().isoformat()}

    def save(self, project_id: str, data: dict) -> None:
        """
        Save memory for a project.

        Args:
            project_id: Project identifier
            data: Memory data to save
        """
        project_dir = self.memory_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        memory_file = project_dir / "context.json"
        memory_file.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved memory for project {project_id}")

    def add_entry(self, project_id: str, entry: dict) -> None:
        """
        Add a memory entry.

        Args:
            project_id: Project identifier
            entry: Memory entry to add
        """
        memory = self.get(project_id)
        memory["memory"].append({
            **entry,
            "timestamp": datetime.now().isoformat()
        })
        memory["last_updated"] = datetime.now().isoformat()
        self.save(project_id, memory)

    def clear(self, project_id: str) -> None:
        """Clear memory for a project."""
        memory_file = self.memory_dir / project_id / "context.json"
        if memory_file.exists():
            memory_file.unlink()
        logger.info(f"Cleared memory for project {project_id}")