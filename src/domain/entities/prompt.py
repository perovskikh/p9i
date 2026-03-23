# src/domain/entities/prompt.py
"""
Prompt Entity - Core domain model for prompts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class PromptTier(str, Enum):
    """Prompt tier enumeration."""
    CORE = "core"
    UNIVERSAL = "universal"
    MPV_STAGE = "mpv_stage"
    PROJECTS = "projects"


@dataclass
class PromptEntity:
    """
    Core domain entity for a prompt.

    Represents the fundamental business object for prompts.
    """
    name: str
    content: str
    tier: PromptTier = PromptTier.UNIVERSAL
    version: str = "1.0.0"
    immutable: bool = False
    overridable: bool = True
    checksum: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def can_override(self) -> bool:
        """Check if this prompt can be overridden."""
        return self.overridable and not self.immutable

    def is_core(self) -> bool:
        """Check if this is a core (baseline) prompt."""
        return self.tier == PromptTier.CORE or self.immutable

    def validate(self) -> List[str]:
        """Validate entity and return list of errors."""
        errors = []

        if not self.name or len(self.name) > 100:
            errors.append("Name must be 1-100 characters")

        if not self.content:
            errors.append("Content cannot be empty")

        if self.version:
            parts = self.version.split(".")
            if len(parts) != 3:
                errors.append("Version must be in format x.y.z")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "content": self.content,
            "tier": self.tier.value,
            "version": self.version,
            "immutable": self.immutable,
            "overridable": self.overridable,
            "checksum": self.checksum,
            "tags": self.tags,
            "variables": self.variables,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptEntity":
        """Create entity from dictionary."""
        tier = data.get("tier", "universal")
        if isinstance(tier, str):
            tier = PromptTier(tier)

        return cls(
            name=data["name"],
            content=data["content"],
            tier=tier,
            version=data.get("version", "1.0.0"),
            immutable=data.get("immutable", False),
            overridable=data.get("overridable", True),
            checksum=data.get("checksum"),
            tags=data.get("tags", []),
            variables=data.get("variables", {}),
        )
