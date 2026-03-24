# src/domain/repositories/__init__.py
"""Domain repositories - Abstract interfaces for data access."""

from src.domain.repositories.prompt_repository import IPromptRepository
from src.domain.repositories.project_repository import IProjectRepository

__all__ = ["IPromptRepository", "IProjectRepository"]
