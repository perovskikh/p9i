# src/domain/entities/__init__.py
"""Domain entities - Core business objects."""

from src.domain.entities.prompt import PromptEntity, PromptTier
from src.domain.entities.project import ProjectEntity
from src.domain.entities.agent import AgentEntity
from src.domain.entities.tool_permissions import (
    ToolPermission,
    ToolPermissions,
    READ_ONLY_PERMISSIONS,
)
from src.domain.entities.architect import (
    AgentStatus,
    Phase,
    ToolActivity,
    AgentProgress,
    ArchitectTaskState,
    ResearchResult,
    SynthesisResult,
)

__all__ = [
    "PromptEntity", "PromptTier", "ProjectEntity", "AgentEntity",
    "ToolPermission", "ToolPermissions", "READ_ONLY_PERMISSIONS",
    "AgentStatus", "Phase", "ToolActivity", "AgentProgress",
    "ArchitectTaskState", "ResearchResult", "SynthesisResult",
]
