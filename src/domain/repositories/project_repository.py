# src/domain/repositories/project_repository.py
"""
Project Repository Interface - Abstract data access for projects.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.project import ProjectEntity


class IProjectRepository(ABC):
    """Abstract repository interface for project storage."""

    @abstractmethod
    def get_by_id(self, project_id: str) -> Optional[ProjectEntity]:
        """Get a project by ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[ProjectEntity]:
        """List all projects."""
        pass

    @abstractmethod
    def save(self, project: ProjectEntity) -> ProjectEntity:
        """Save a project."""
        pass

    @abstractmethod
    def delete(self, project_id: str) -> bool:
        """Delete a project."""
        pass
