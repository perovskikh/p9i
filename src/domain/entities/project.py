# src/domain/entities/project.py
"""
Project Entity - Core domain model for projects.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class ProjectEntity:
    """
    Core domain entity for a project.

    Represents a project that can have its own prompts.
    """
    id: str
    name: str
    description: str = ""
    stack: List[str] = field(default_factory=list)
    prompts_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def add_stack_item(self, item: str) -> None:
        """Add a technology to the project stack."""
        if item not in self.stack:
            self.stack.append(item)

    def remove_stack_item(self, item: str) -> None:
        """Remove a technology from the project stack."""
        if item in self.stack:
            self.stack.remove(item)

    def has_stack(self) -> bool:
        """Check if project has a defined stack."""
        return len(self.stack) > 0

    def validate(self) -> List[str]:
        """Validate entity and return list of errors."""
        errors = []

        if not self.id or len(self.id) > 50:
            errors.append("ID must be 1-50 characters")

        if not self.name or len(self.name) > 100:
            errors.append("Name must be 1-100 characters")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stack": self.stack,
            "prompts_path": self.prompts_path,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectEntity":
        """Create entity from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            stack=data.get("stack", []),
            prompts_path=data.get("prompts_path"),
            metadata=data.get("metadata", {}),
        )
