# src/storage/repositories/project_repository.py
"""
SQLAlchemy implementation of Project Repository.
"""

import hashlib
import secrets
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.project import ProjectEntity
from src.domain.repositories.project_repository import IProjectRepository
from src.storage.models.project import Project
from src.storage.models.api_key import ApiKey


class SQLAlchemyProjectRepository(IProjectRepository):
    """SQLAlchemy implementation of project repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: Project) -> ProjectEntity:
        """Convert SQLAlchemy model to domain entity."""
        return ProjectEntity(
            id=str(model.id),
            name=model.name,
            description=model.description or "",
            stack=model.stack or [],
            prompts_path=model.default_project_path,
            metadata=model.metadata or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: ProjectEntity, model: Optional[Project] = None) -> Project:
        """Convert domain entity to SQLAlchemy model."""
        if model is None:
            model = Project()

        model.name = entity.name
        model.description = entity.description
        model.stack = entity.stack
        model.default_project_path = entity.prompts_path or "/project"
        model.project_metadata = entity.project_metadata

        if entity.id:
            model.id = UUID(entity.id)

        return model

    async def get_by_id(self, project_id: str) -> Optional[ProjectEntity]:
        """Get a project by ID."""
        stmt = select(Project).where(Project.id == UUID(project_id), Project.is_active == True)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_id_with_keys(self, project_id: str) -> Optional[Project]:
        """Get a project by ID with API keys loaded."""
        stmt = (
            select(Project)
            .options(selectinload(Project.api_keys))
            .where(Project.id == UUID(project_id), Project.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> List[ProjectEntity]:
        """List all active projects."""
        stmt = select(Project).where(Project.is_active == True).order_by(Project.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def list_by_owner(self, owner_id: str) -> List[ProjectEntity]:
        """List all projects for a specific owner."""
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id, Project.is_active == True)
            .order_by(Project.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def save(self, project: ProjectEntity) -> ProjectEntity:
        """Save a project (create or update)."""
        existing = None
        if project.id:
            stmt = select(Project).where(Project.id == UUID(project.id))
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

        model = self._entity_to_model(project, existing)
        if not existing:
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, project_id: str) -> bool:
        """Soft delete a project."""
        stmt = (
            update(Project)
            .where(Project.id == UUID(project_id))
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0


class SQLAlchemyApiKeyRepository:
    """Repository for API key operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def create(
        self,
        project_id: str,
        name: str,
        permissions: List[str],
        rate_limit: int = 100,
    ) -> tuple[ApiKey, str]:
        """
        Create a new API key for a project.

        Returns:
            Tuple of (ApiKey model, raw API key)
            The raw key is only returned once for display to user
        """
        # Generate a secure random key
        raw_key = f"sk-p9i-{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(raw_key)

        model = ApiKey(
            key_hash=key_hash,
            project_id=UUID(project_id),
            name=name,
            permissions=permissions,
            rate_limit=rate_limit,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return model, raw_key

    async def get_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        """Get an API key by its hash."""
        stmt = (
            select(ApiKey)
            .options(selectinload(ApiKey.project))
            .where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def validate(self, raw_key: str) -> Optional[ApiKey]:
        """Validate an API key and return the model if valid."""
        key_hash = self._hash_key(raw_key)
        model = await self.get_by_hash(key_hash)

        if model and model.is_active and model.project and model.project.is_active:
            return model
        return None

    async def revoke(self, key_id: str) -> bool:
        """Revoke an API key."""
        stmt = (
            update(ApiKey)
            .where(ApiKey.id == UUID(key_id))
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def list_by_project(self, project_id: str) -> List[ApiKey]:
        """List all API keys for a project."""
        stmt = (
            select(ApiKey)
            .where(ApiKey.project_id == UUID(project_id), ApiKey.is_active == True)
            .order_by(ApiKey.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_last_used(self, key_id: str) -> None:
        """Update last_used_at timestamp."""
        stmt = (
            update(ApiKey)
            .where(ApiKey.id == UUID(key_id))
            .values(last_used_at=func.now())
        )
        await self.session.execute(stmt)
        await self.session.commit()
