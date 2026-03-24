# src/infrastructure/adapters/external/__init__.py
"""External service adapters."""

from src.infrastructure.adapters.external.figma_adapter import get_figma_client

__all__ = ["get_figma_client"]
