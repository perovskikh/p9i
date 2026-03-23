# src/application/container.py
"""
Dependency Injection Container.

Simple container for managing dependencies in Clean Architecture.
"""

from typing import Callable, Any, Optional, TypeVar, Type
from functools import lru_cache

T = TypeVar('T')


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._singleton_flags: set[str] = set()

    def register(
        self,
        interface: str | Type,
        factory: Callable[..., Any],
        singleton: bool = False
    ) -> None:
        """
        Register a dependency.

        Args:
            interface: Interface or class name
            factory: Factory function that creates the instance
            singleton: If True, create only one instance
        """
        key = interface if isinstance(interface, str) else interface.__name__
        self._factories[key] = factory

        if singleton:
            self._singleton_flags.add(key)

    def resolve(self, interface: str | Type[T]) -> T:
        """
        Resolve a dependency.

        Args:
            interface: Interface or class to resolve

        Returns:
            Instance of the requested type
        """
        key = interface if isinstance(interface, str) else interface.__name__

        # Return cached singleton if exists
        if key in self._singleton_flags and key in self._singletons:
            return self._singletons[key]

        # Get factory
        if key not in self._factories:
            raise ValueError(f"No factory registered for: {key}")

        factory = self._factories[key]
        instance = factory()

        # Cache if singleton
        if key in self._singleton_flags:
            self._singletons[key] = instance

        return instance

    def clear(self) -> None:
        """Clear all cached singletons."""
        self._singletons.clear()


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get or create global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reset global container (useful for testing)."""
    global _container
    _container = None


def setup_container() -> Container:
    """
    Setup container with all dependencies.

    This is called once at application startup.
    """
    from src.storage.prompts_v2 import PromptStorageV2
    from src.services.orchestrator import AgentOrchestrator
    from src.services.llm_client import LLMClient
    from src.services.executor import PromptExecutor
    from src.middleware.jwt_auth import JWTService
    from src.middleware.rbac import RBACService
    from src.storage.packs import PackLoader

    container = get_container()

    # Register services as singletons
    container.register("PromptStorageV2", lambda: PromptStorageV2(), singleton=True)
    container.register("AgentOrchestrator", lambda: AgentOrchestrator(), singleton=True)
    container.register("LLMClient", lambda: LLMClient(), singleton=True)
    container.register("PromptExecutor", lambda: PromptExecutor(), singleton=True)
    container.register("JWTService", lambda: JWTService(), singleton=True)
    container.register("RBACService", lambda: RBACService(), singleton=True)
    container.register("PackLoader", lambda: PackLoader(), singleton=True)

    return container
