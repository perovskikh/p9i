"""
Explorer MCP Tools - Provides code exploration as MCP tools.

These tools wrap ExplorerService for use by the Explorer Agent.
They provide fast, cached access to code navigation.

Based on Claude Code exploreAgent pattern:
- READ-ONLY operations only
- Caching for performance
- Parallel-friendly design
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

from src.services.explorer_service import get_explorer_service, ExplorerService

logger = logging.getLogger(__name__)


def _hash_query(query: str) -> str:
    """Create short hash of query for cache key."""
    return hashlib.md5(query.encode()).hexdigest()[:16]


class ExplorerTools:
    """
    Explorer tools for MCP integration.

    These tools provide cached access to code exploration:
    - explorer_search: Fast symbol/file search
    - explorer_index: Rebuild project index
    - explorer_call_graph: Get call graph
    - explorer_module: Analyze module structure
    """

    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self._service: Optional[ExplorerService] = None

    @property
    def service(self) -> ExplorerService:
        """Lazy initialization of explorer service."""
        if self._service is None:
            self._service = get_explorer_service(self.project_path)
        return self._service

    async def explorer_search(
        self,
        query: str,
        file_pattern: str = "*.py",
    ) -> Dict[str, Any]:
        """
        Search code using cached index.

        Args:
            query: Search query (symbol name, keyword)
            file_pattern: File pattern to search (default: *.py)

        Returns:
            Dict with:
            - results: List of {file, line, type, name, context}
            - cached: Whether result was from cache
            - count: Number of results
        """
        # Use hash for cache key
        cache_key = _hash_query(f"{query}:{file_pattern}")

        # Get from cache if available
        cached = await self.service.cache.get_search_result(
            self.project_path, cache_key
        )
        if cached is not None:
            return {
                "results": cached,
                "cached": True,
                "count": len(cached),
            }

        # Search in index
        await self.service.ensure_index()

        # Simple search - in real impl would use indexed search
        results = []
        index = self.service.indexer

        for indexed_file in index._cache.values():
            for symbol in indexed_file.symbols:
                if query.lower() in symbol["name"].lower():
                    results.append({
                        "file": indexed_file.relative_path,
                        "line": symbol["line"],
                        "type": symbol["type"],
                        "name": symbol["name"],
                        "context": f"{symbol['type']} {symbol['name']}",
                    })

        # Cache result
        await self.service.cache.set_search_result(
            self.project_path, cache_key, results
        )

        return {
            "results": results,
            "cached": False,
            "count": len(results),
        }

    async def explorer_index(
        self,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Get or rebuild project index.

        Args:
            force: Force full rescan even if cached

        Returns:
            Dict with:
            - total_files: Number of indexed files
            - total_symbols: Number of extracted symbols
            - entry_points: Number of detected entry points
            - indexed_at: Timestamp of indexing
            - cached: Whether result was from cache
        """
        index = await self.service.ensure_index(force_refresh=force)

        return {
            "total_files": index.total_files,
            "total_symbols": index.total_symbols,
            "entry_points": len(index.entry_points),
            "indexed_at": index.indexed_at,
            "cached": not force,
        }

    async def explorer_call_graph(
        self,
        entry_point: str,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """
        Get call graph for entry point.

        Args:
            entry_point: File path or symbol name
            max_depth: Maximum traversal depth (default: 5)

        Returns:
            Dict with:
            - entry: Entry point
            - depth: Current depth
            - calls: List of {symbol, file, depth, calls}
            - cycles: List of detected cycles
        """
        # Check cache
        cached = await self.service.cache.get_call_graph(
            self.project_path, entry_point
        )
        if cached is not None:
            cached["cached"] = True
            return cached

        # Build graph
        graph = await self.service.indexer.build_call_graph(
            entry_point, max_depth
        )

        # Cache result
        await self.service.cache.set_call_graph(
            self.project_path, entry_point, graph
        )

        graph["cached"] = False
        return graph

    async def explorer_module(
        self,
        module_path: str,
    ) -> Dict[str, Any]:
        """
        Analyze module structure.

        Args:
            module_path: Path to module (file or directory)

        Returns:
            Dict with:
            - module: Module path
            - files: Number of files
            - symbols: Number of symbols
            - imports: Number of imports
            - health_score: Module health (0-100)
            - external_deps: External dependencies
            - internal_deps: Internal dependencies
        """
        return await self.service.analyze_module(module_path)

    async def explorer_whereis(
        self,
        symbol_name: str,
    ) -> Dict[str, Any]:
        """
        Find where symbol is defined.

        Args:
            symbol_name: Symbol to find

        Returns:
            Dict with:
            - found: Whether symbol was found
            - file: File path
            - line: Line number
            - type: Symbol type (function, class, etc.)
            - cached: Whether result was from cache
        """
        result = await self.service.search_symbol(symbol_name)

        if result is None:
            return {
                "found": False,
                "cached": False,
            }

        return {
            "found": True,
            "file": result.get("file"),
            "line": result.get("line"),
            "type": result.get("type"),
            "name": result.get("name"),
            "cached": result.get("cached", False),
        }

    async def explorer_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with:
            - total_keys: Number of cache keys
            - index_size_bytes: Cache size
            - last_updated: Last update timestamp
            - cache_hits: Number of hits
            - cache_misses: Number of misses
            - hit_rate: Hit rate percentage
        """
        return await self.service.get_cache_stats()


# Global instance per project
_explorer_tools: Dict[str, ExplorerTools] = {}


def get_explorer_tools(project_path: str = ".") -> ExplorerTools:
    """Get or create ExplorerTools for project."""
    if project_path not in _explorer_tools:
        _explorer_tools[project_path] = ExplorerTools(project_path)
    return _explorer_tools[project_path]
