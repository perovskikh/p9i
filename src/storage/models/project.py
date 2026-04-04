# src/storage/models/project.py
"""
SQLAlchemy Project Model for multi-project SaaS.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Project(Base):
    """SQLAlchemy model for projects."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, default="")

    # SFTP Configuration
    sftp_host = Column(String(255), nullable=True)
    sftp_port = Column(Integer, default=22)
    sftp_username = Column(String(100), nullable=True)
    sftp_key_fingerprint = Column(String(255), nullable=True)
    sftp_project_path = Column(String(500), nullable=True)  # Remote path on SFTP server

    # Project Configuration
    default_project_path = Column(String(500), default="/project")
    stack = Column(JSON, default=list)  # List[str] - detected technologies

    # Ownership
    owner_id = Column(String(100), nullable=False, index=True)

    # Metadata (renamed to avoid SQLAlchemy reserved name conflict)
    project_metadata = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    api_keys = relationship("ApiKey", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "sftp_host": self.sftp_host,
            "sftp_port": self.sftp_port,
            "sftp_username": self.sftp_username,
            "sftp_key_fingerprint": self.sftp_key_fingerprint,
            "sftp_project_path": self.sftp_project_path,
            "default_project_path": self.default_project_path,
            "stack": self.stack or [],
            "owner_id": self.owner_id,
            "project_metadata": self.project_metadata or {},
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
