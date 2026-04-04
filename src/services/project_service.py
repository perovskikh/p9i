# src/services/project_service.py
"""
Project Service - Manages project lifecycle, SFTP connections, and API keys.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field

from src.storage.database import AsyncSessionLocal
from src.storage.models.project import Project
from src.storage.models.api_key import ApiKey
from src.storage.repositories.project_repository import (
    SQLAlchemyProjectRepository,
    SQLAlchemyApiKeyRepository,
)

logger = logging.getLogger(__name__)


# DTOs
class CreateProjectDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    owner_id: str
    sftp_host: Optional[str] = None
    sftp_port: int = 22
    sftp_username: Optional[str] = None
    sftp_key_fingerprint: Optional[str] = None
    sftp_project_path: Optional[str] = None
    default_project_path: str = "/project"
    stack: List[str] = []
    metadata: Dict[str, Any] = {}


class UpdateProjectDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    sftp_host: Optional[str] = None
    sftp_port: Optional[int] = None
    sftp_username: Optional[str] = None
    sftp_key_fingerprint: Optional[str] = None
    sftp_project_path: Optional[str] = None
    default_project_path: Optional[str] = None
    stack: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CreateApiKeyDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    permissions: List[str] = ["read_prompts", "run_prompt"]
    rate_limit: int = Field(default=100, ge=1, le=1000)


class ProjectService:
    """
    Manages project lifecycle, SFTP connections, and API keys.

    This service provides a high-level interface for multi-project SaaS operations.
    """

    # In-memory SFTP connection pool per project
    _sftp_connections: Dict[str, Any] = {}

    async def create_project(self, data: CreateProjectDTO) -> Project:
        """Create a new project."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyProjectRepository(session)

            # Create project directly as SQLAlchemy model
            from src.storage.models.project import Project as ProjectModel

            model = ProjectModel(
                id=uuid4(),
                name=data.name,
                description=data.description,
                owner_id=data.owner_id,
                sftp_host=data.sftp_host,
                sftp_port=data.sftp_port,
                sftp_username=data.sftp_username,
                sftp_key_fingerprint=data.sftp_key_fingerprint,
                sftp_project_path=data.sftp_project_path,
                default_project_path=data.default_project_path,
                stack=data.stack,
                metadata=data.metadata,
            )

            session.add(model)
            await session.commit()
            await session.refresh(model)

            logger.info(f"Created project: {model.id} ({model.name})")
            return model

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyProjectRepository(session)
            return await repo.get_by_id_with_keys(project_id)

    async def list_projects(self, owner_id: str) -> List[Project]:
        """List all projects for an owner."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyProjectRepository(session)
            models = await repo.list_by_owner(owner_id)
            # Convert entities to models for consistency
            return models

    async def update_project(self, project_id: str, data: UpdateProjectDTO) -> Optional[Project]:
        """Update a project."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyProjectRepository(session)
            model = await repo.get_by_id_with_keys(project_id)

            if not model:
                return None

            # Update fields
            update_dict = data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(model, key, value)

            await session.commit()
            await session.refresh(model)

            logger.info(f"Updated project: {project_id}")
            return model

    async def delete_project(self, project_id: str) -> bool:
        """Delete (deactivate) a project."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyProjectRepository(session)
            result = await repo.delete(project_id)

            # Disconnect SFTP if connected
            if project_id in self._sftp_connections:
                await self.disconnect_sftp(project_id)

            logger.info(f"Deleted project: {project_id}")
            return result

    async def create_api_key(
        self,
        project_id: str,
        name: str,
        permissions: List[str] = None,
        rate_limit: int = 100,
    ) -> tuple[ApiKey, str]:
        """
        Create an API key for a project.

        Returns:
            Tuple of (ApiKey model, raw API key)
            The raw key is only returned once - user must save it
        """
        if permissions is None:
            permissions = ["read_prompts", "run_prompt"]

        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyApiKeyRepository(session)
            model, raw_key = await repo.create(
                project_id=project_id,
                name=name,
                permissions=permissions,
                rate_limit=rate_limit,
            )

            logger.info(f"Created API key {model.id} for project {project_id}")
            return model, raw_key

    async def validate_api_key(self, raw_key: str) -> Optional[ApiKey]:
        """Validate an API key and return the ApiKey model if valid."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyApiKeyRepository(session)
            model = await repo.validate(raw_key)

            if model:
                # Update last used timestamp
                await repo.update_last_used(str(model.id))
                logger.debug(f"Validated API key for project {model.project_id}")

            return model

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyApiKeyRepository(session)
            result = await repo.revoke(key_id)

            logger.info(f"Revoked API key: {key_id}")
            return result

    async def list_api_keys(self, project_id: str) -> List[ApiKey]:
        """List all API keys for a project."""
        async with AsyncSessionLocal() as session:
            repo = SQLAlchemyApiKeyRepository(session)
            return await repo.list_by_project(project_id)

    async def connect_sftp(self, project_id: str) -> Optional[Any]:
        """
        Establish SFTP connection for a project.

        Returns:
            SFTPFilesystem instance or None if SFTP not configured
        """
        if project_id in self._sftp_connections:
            return self._sftp_connections[project_id]

        project = await self.get_project(project_id)
        if not project or not project.sftp_host:
            logger.warning(f"Cannot connect SFTP: project {project_id} has no SFTP config")
            return None

        try:
            from src.services.sftp_filesystem import get_sftp_connection

            sftp = await get_sftp_connection(
                host=project.sftp_host,
                port=project.sftp_port,
                username=project.sftp_username or "root",
                # password or key_file would be stored securely
            )

            self._sftp_connections[project_id] = sftp
            logger.info(f"Connected SFTP for project {project_id} ({project.sftp_host})")
            return sftp

        except Exception as e:
            logger.error(f"Failed to connect SFTP for project {project_id}: {e}")
            return None

    async def disconnect_sftp(self, project_id: str) -> None:
        """Disconnect SFTP connection for a project."""
        if project_id in self._sftp_connections:
            try:
                sftp = self._sftp_connections[project_id]
                await sftp.close()
            except Exception as e:
                logger.error(f"Error closing SFTP for project {project_id}: {e}")
            finally:
                del self._sftp_connections[project_id]
                logger.info(f"Disconnected SFTP for project {project_id}")

    async def get_project_path(self, project_id: str) -> str:
        """Get the project path (SFTP remote or local)."""
        project = await self.get_project(project_id)
        if not project:
            return "/project"

        if project.sftp_host:
            return project.sftp_project_path or "/project"
        return project.default_project_path or "/project"


# Singleton instance
_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """Get or create ProjectService singleton."""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service
