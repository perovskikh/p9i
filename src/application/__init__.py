# src/application/__init__.py
"""Application layer - Use cases and orchestration."""

from src.application.container import Container, get_container, setup_container
from src.application.agent_router import AgentRouter

__all__ = ["Container", "get_container", "setup_container", "AgentRouter"]
