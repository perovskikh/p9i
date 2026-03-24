# src/domain/entities/agent.py
"""
Agent Entity - Core domain model for AI agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AgentEntity:
    """
    Core domain entity for an AI agent.

    Represents a specialized agent that can execute prompts.
    """
    key: str
    name: str
    prompts: List[str] = field(default_factory=list)
    memory_key: str = ""
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a specific task."""
        task_lower = task.lower()

        # Check capabilities
        for cap in self.capabilities:
            if cap.lower() in task_lower:
                return True

        # Check prompt names
        for prompt in self.prompts:
            if prompt.lower().replace("-", "_") in task_lower:
                return True

        return False

    def get_default_prompt(self) -> Optional[str]:
        """Get the default prompt for this agent."""
        return self.prompts[0] if self.prompts else None

    def validate(self) -> List[str]:
        """Validate entity and return list of errors."""
        errors = []

        if not self.key or len(self.key) > 30:
            errors.append("Key must be 1-30 characters")

        if not self.name or len(self.name) > 50:
            errors.append("Name must be 1-50 characters")

        if not self.prompts:
            errors.append("Agent must have at least one prompt")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "prompts": self.prompts,
            "memory_key": self.memory_key,
            "description": self.description,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentEntity":
        """Create entity from dictionary."""
        return cls(
            key=data["key"],
            name=data["name"],
            prompts=data.get("prompts", []),
            memory_key=data.get("memory_key", ""),
            description=data.get("description", ""),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
        )
