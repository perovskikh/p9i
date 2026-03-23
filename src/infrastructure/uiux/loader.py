# src/infrastructure/uiux/loader.py
"""
Lazy loading of UI/UX design resources.

Loads embedded data only when first accessed.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class UIUXLoader:
    """
    Lazy loader for UI/UX design resources.

    Uses singleton pattern and on-demand loading.
    """

    _instance: Optional['UIUXLoader'] = None
    _cache: Dict[str, List[Dict[str, Any]]] = {}
    _loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'UIUXLoader':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_all(self, force: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all embedded data.

        Args:
            force: Force reload even if cached

        Returns:
            Dict mapping category to list of resources
        """
        if self._loaded and not force:
            return self._cache

        # Import embedded data lazily
        from .data.embedded import UIUX_EMBEDDED_DATA

        self._cache = UIUX_EMBEDDED_DATA
        self._loaded = True
        total = sum(len(v) for v in self._cache.values())
        logger.info(f"Loaded {total} UI/UX resources")

        return self._cache

    def load_category(self, category: str, force: bool = False) -> List[Dict[str, Any]]:
        """
        Load resources for a specific category.

        Args:
            category: Category name (styles, colors, typography, etc.)
            force: Force reload even if cached

        Returns:
            List of resources in that category
        """
        # Ensure all data is loaded
        self.load_all(force=force)

        if category not in self._cache:
            logger.warning(f"Category '{category}' not found in UI/UX resources")
            return []

        return self._cache.get(category, [])

    def get_resource(self, category: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific resource by ID.

        Args:
            category: Category name
            resource_id: Resource ID

        Returns:
            Resource dict or None
        """
        resources = self.load_category(category)

        for resource in resources:
            if resource.get("id") == resource_id:
                return resource

        return None

    def search_category(
        self,
        category: str,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Simple text search within a category.

        Args:
            category: Category to search
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of matching resources
        """
        resources = self.load_category(category)
        query_lower = query.lower()

        # Score by matches
        scored = []
        for resource in resources:
            score = 0
            name = resource.get("name", "").lower()
            desc = resource.get("description", "").lower()
            tags = " ".join(resource.get("tags", [])).lower()

            # Exact match in name
            if query_lower in name:
                score += 10
            # Partial in name
            elif any(q in name for q in query_lower.split()):
                score += 5

            # In description
            if query_lower in desc:
                score += 3

            # In tags
            if query_lower in tags:
                score += 5

            if score > 0:
                resource_copy = resource.copy()
                resource_copy["_score"] = score
                scored.append(resource_copy)

        # Sort by score and limit
        scored.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return scored[:max_results]

    def clear_cache(self):
        """Clear the cache to force reload on next access."""
        self._cache = {}
        self._loaded = False
        logger.info("UI/UX cache cleared")


# Singleton instance
_loader: Optional[UIUXLoader] = None


def get_loader() -> UIUXLoader:
    """Get the UI/UX loader singleton."""
    global _loader
    if _loader is None:
        _loader = UIUXLoader.get_instance()
    return _loader
