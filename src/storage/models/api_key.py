# src/storage/models/api_key.py
"""
SQLAlchemy ApiKey Model for multi-project SaaS.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.storage.models.project import Base


class ApiKey(Base):
    """SQLAlchemy model for API keys."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash

    # Link to project
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Key metadata
    name = Column(String(100), nullable=False)
    permissions = Column(JSON, default=list)  # List[str] - e.g., ["read_prompts", "run_prompt"]

    # Rate limiting
    rate_limit = Column(Integer, default=100)  # requests per minute

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="api_keys")

    def to_dict(self) -> dict:
        """Convert to dictionary (without key_hash)."""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "name": self.name,
            "permissions": self.permissions or [],
            "rate_limit": self.rate_limit,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }

    def to_full_dict(self) -> dict:
        """Convert to dictionary including key_hash for initial display."""
        d = self.to_dict()
        d["key_hash"] = self.key_hash
        return d
