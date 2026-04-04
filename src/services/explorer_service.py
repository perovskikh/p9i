"""
Explorer Service - Orchestrates code exploration with caching.

Part of ADR-016b Explorer Agent Extended.
Integrates CacheManager and FileIndexer for fast exploration.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.services.explorer_cache import (
    ExplorerCacheManager,
    get_explorer_cache_manager,
    init_explorer_cache,
    hash_query,
)
from src.services.explorer_indexer import ExplorerFileIndexer, ProjectIndex

logger = logging.getLogger(__name__)


class ExplorerService:
    """
    Main service for code exploration.

    Features:
    - Cache-aware exploration
    - Project indexing
    - Call graph building
    - Symbol lookups
    """

    def __init__(
        self,
        cache_manager: Optional[ExplorerCacheManager] = None,
        project_path: str = "."
    ):
        """
        Initialize Explorer Service.

        Args:
            cache_manager: Cache manager instance
            project_path: Project root to explore
        """
        self.cache = cache_manager or get_explorer_cache_manager()
        self.project_path = Path(project_path).resolve()
        self.indexer = ExplorerFileIndexer(str(self.project_path))
        self._current_index: Optional[ProjectIndex] = None

    async def ensure_index(self, force_refresh: bool = False) -> ProjectIndex:
        """
        Ensure project is indexed.

        Args:
            force_refresh: Force full rescan

        Returns:
            ProjectIndex
        """
        # Check cache first
        if not force_refresh:
            cached = await self.cache.get_file_index(str(self.project_path))
            if cached:
                logger.info("Using cached index")
                # Reconstruct ProjectIndex from cached data
                self._current_index = ProjectIndex(
                    project_path=cached.get("project_path", str(self.project_path)),
                    files=[],  # Don't store full file data in cache
                    entry_points=cached.get("entry_points", []),
                    total_files=cached.get("total_files", 0),
                    total_symbols=cached.get("total_symbols", 0),
                    indexed_at=cached.get("indexed_at", "")
                )
                return self._current_index

        # Build fresh index
        logger.info("Building fresh index")
        self._current_index = await self.indexer.scan(force_refresh=True)

        # Cache the index metadata
        await self.cache.set_file_index(
            str(self.project_path),
            {
                "project_path": self._current_index.project_path,
                "entry_points": self._current_index.entry_points,
                "total_files": self._current_index.total_files,
                "total_symbols": self._current_index.total_symbols,
                "indexed_at": self._current_index.indexed_at,
            }
        )

        return self._current_index

    async def search_symbol(self, symbol_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for symbol across project.

        Args:
            symbol_name: Symbol to find

        Returns:
            Dict with file, line, type or None
        """
        # Check cache
        cached = await self.cache.get_symbol(str(self.project_path), symbol_name)
        if cached:
            return {
                "file": cached.file_path,
                "line": cached.line_number,
                "type": cached.symbol_type,
                "name": cached.symbol_name,
                "cached": True
            }

        # Search in index
        await self.ensure_index()
        result = self.indexer.get_symbol_by_name(symbol_name)

        if result:
            # Cache the result
            from src.services.explorer_cache import SymbolEntry
            entry = SymbolEntry(
                file_path=result["file"],
                symbol_name=symbol_name,
                symbol_type=result["type"],
                line_number=result["line"]
            )
            await self.cache.set_symbol(str(self.project_path), entry)

        return result

    async def search_code(self, query: str, file_pattern: str = "*.py") -> List[Dict[str, Any]]:
        """
        Search code content with caching.

        Args:
            query: Search query
            file_pattern: File pattern to search

        Returns:
            List of matches with file, line, content
        """
        # Create cache key from query
        cache_key = hash_query(f"{query}:{file_pattern}")

        # Check cache
        cached = await self.cache.get_search_result(str(self.project_path), cache_key)
        if cached:
            logger.info(f"Search cache hit for '{query}'")
            return cached

        # Ensure index is built
        await self.ensure_index()

        # Search through indexed files
        results = []
        search_lower = query.lower()

        # Normalize file pattern for matching (e.g., "*.py" -> "py")
        pattern_parts = file_pattern.replace("*", "").split(".")

        for indexed_file in self.indexer._cache.values():
            # Check if file matches pattern
            file_path_lower = indexed_file.relative_path.lower()
            if not any(fp in file_path_lower for fp in pattern_parts if fp):
                continue

            # Search in symbols
            for symbol in indexed_file.symbols:
                symbol_name_lower = symbol.get("name", "").lower()
                if search_lower in symbol_name_lower:
                    results.append({
                        "file": indexed_file.relative_path,
                        "line": symbol.get("line", 0),
                        "type": symbol.get("type", "unknown"),
                        "name": symbol.get("name", ""),
                        "context": f"{symbol.get('type', 'unknown')} {symbol.get('name', '')}"
                    })

            # Search in imports
            for imp in indexed_file.imports:
                if search_lower in imp.lower():
                    results.append({
                        "file": indexed_file.relative_path,
                        "line": 0,
                        "type": "import",
                        "name": imp,
                        "context": f"import {imp}"
                    })

        # Cache results
        if results:
            await self.cache.set_search_result(str(self.project_path), cache_key, results)
            logger.info(f"Search '{query}' found {len(results)} results")

        return results

    async def get_call_graph(self, entry_point: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Build call graph from entry point.

        Args:
            entry_point: Starting file or symbol
            max_depth: Maximum traversal depth

        Returns:
            Call graph structure
        """
        # Check cache
        cached = await self.cache.get_call_graph(str(self.project_path), entry_point)
        if cached:
            return cached

        # Build graph
        graph = await self.indexer.build_call_graph(entry_point, max_depth)

        # Cache result
        await self.cache.set_call_graph(str(self.project_path), entry_point, graph)

        return graph

    async def analyze_module(self, module_path: str) -> Dict[str, Any]:
        """
        Analyze a module and return detailed info.

        Args:
            module_path: Path to module (file or directory)

        Returns:
            Analysis result with symbols, dependencies, health
        """
        path = Path(module_path)

        # Find files in module
        if path.is_dir():
            files = list(path.glob("*.py")) + list(path.glob("*.js"))
        else:
            files = [path]

        symbols = []
        imports = []

        for file in files:
            indexed = await self.indexer._index_file(str(file))
            if indexed:
                symbols.extend(indexed.symbols)
                imports.extend(indexed.imports)

        # Calculate health score (simplified)
        health_score = 100 - (len([i for i in imports if '..' in i]) * 10)

        return {
            "module": str(module_path),
            "files": len(files),
            "symbols": len(symbols),
            "imports": len(imports),
            "health_score": min(100, max(0, health_score)),
            "external_deps": [i for i in imports if not i.startswith('.')],
            "internal_deps": [i for i in imports if i.startswith('.')],
        }

    async def refresh_index(self) -> Dict[str, Any]:
        """
        Force refresh of project index.

        Returns:
            Refresh result with stats
        """
        # Clear cache
        await self.cache.invalidate_all(str(self.project_path))

        # Rebuild index
        index = await self.ensure_index(force_refresh=True)

        return {
            "status": "refreshed",
            "total_files": index.total_files,
            "total_symbols": index.total_symbols,
            "entry_points": len(index.entry_points),
            "indexed_at": index.indexed_at
        }

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = await self.cache.get_stats(str(self.project_path))
        return {
            "total_keys": stats.total_keys,
            "index_size_bytes": stats.index_size_bytes,
            "last_updated": stats.last_updated,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_rate": (
                f"{stats.cache_hits / (stats.cache_hits + stats.cache_misses) * 100:.1f}%"
                if (stats.cache_hits + stats.cache_misses) > 0 else "N/A"
            )
        }


# Global instance per project
_explorer_services: Dict[str, ExplorerService] = {}


def get_explorer_service(project_path: str = ".") -> ExplorerService:
    """Get or create ExplorerService for project."""
    if project_path not in _explorer_services:
        _explorer_services[project_path] = ExplorerService(
            cache_manager=get_explorer_cache_manager(),
            project_path=project_path
        )
    return _explorer_services[project_path]
