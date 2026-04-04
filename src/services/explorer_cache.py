"""
Explorer Cache Manager - Redis-based caching for code exploration.

Part of ADR-016b Explorer Agent Extended.
Uses Redis for fast caching (SQLite backup for persistence).
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


def hash_query(query: str) -> str:
    """Create hash of search query for cache key."""
    return hashlib.md5(query.encode()).hexdigest()[:16]


@dataclass
class FileIndex:
    """Indexed file information."""
    path: str
    size: int
    mtime: float
    symbols: List[Dict[str, Any]]
    imports: List[str]


@dataclass
class SymbolEntry:
    """Symbol (function/class) definition."""
    file_path: str
    symbol_name: str
    symbol_type: str  # 'function', 'class', 'const'
    line_number: int


@dataclass
class CacheStats:
    """Cache statistics."""
    total_keys: int
    index_size_bytes: int
    last_updated: Optional[str]
    cache_hits: int
    cache_misses: int


class ExplorerCacheManager:
    """
    Manages exploration cache with Redis primary storage.

    Features:
    - File index caching with TTL
    - Symbol lookups
    - Cache invalidation on file changes
    - Statistics tracking
    """

    # Key prefixes
    PREFIX = "explorer"
    INDEX_PREFIX = f"{PREFIX}:index"
    SYMBOL_PREFIX = f"{PREFIX}:symbol"
    STATS_PREFIX = f"{PREFIX}:stats"
    STALE_PREFIX = f"{PREFIX}:stale"

    # TTLs (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    INDEX_TTL = 86400  # 24 hours
    SYMBOL_TTL = 3600  # 1 hour

    def __init__(self, redis_client=None):
        """
        Initialize cache manager.

        Args:
            redis_client: Redis client instance. If None, uses in-memory fallback.
        """
        self._redis = redis_client
        self._memory_cache: Dict[str, str] = {}  # In-memory fallback when Redis unavailable

    async def initialize(self, redis_client) -> None:
        """Initialize with Redis client."""
        self._redis = redis_client
        logger.info("ExplorerCacheManager initialized with Redis")

    @property
    def redis(self):
        """Get Redis client."""
        return self._redis

    @property
    def redis(self):
        """Get Redis client."""
        return self._redis

    # === File Index Operations ===

    async def get_file_index(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached file index for project.

        Args:
            project_path: Project root path

        Returns:
            Cached index dict or None if not found/stale
        """
        key = f"{self.INDEX_PREFIX}:files:{project_path}"
        try:
            if self._redis:
                data = await self._redis.get(key)
                if data:
                    await self._incr_stat("hits")
                    return json.loads(data)
                await self._incr_stat("misses")
                return None
            # In-memory fallback
            data = self._memory_cache.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set_file_index(self, project_path: str, index_data: Dict[str, Any]) -> bool:
        """
        Cache file index for project.

        Args:
            project_path: Project root path
            index_data: Index data to cache

        Returns:
            True if successful
        """
        key = f"{self.INDEX_PREFIX}:files:{project_path}"
        try:
            # Add metadata
            index_data["_cached_at"] = datetime.now().isoformat()
            index_data["_version"] = index_data.get("_version", 1) + 1

            data = json.dumps(index_data)
            if self._redis:
                await self._redis.setex(key, self.INDEX_TTL, data)
            else:
                self._memory_cache[key] = data
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def invalidate_file_index(self, project_path: str) -> bool:
        """
        Invalidate cached index for project.

        Args:
            project_path: Project root path

        Returns:
            True if successful
        """
        key = f"{self.INDEX_PREFIX}:files:{project_path}"
        try:
            if self._redis:
                await self._redis.delete(key)
                await self._redis.sadd(self.STALE_PREFIX, project_path)
            else:
                self._memory_cache.pop(key, None)
            logger.info(f"Invalidated index for {project_path}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return False

    # === Symbol Operations ===

    async def get_symbol(self, project_path: str, symbol_name: str) -> Optional[SymbolEntry]:
        """
        Get cached symbol lookup.

        Args:
            project_path: Project root path
            symbol_name: Symbol name to find

        Returns:
            SymbolEntry or None
        """
        key = f"{self.SYMBOL_PREFIX}:{project_path}:{symbol_name}"
        try:
            if self._redis:
                data = await self._redis.get(key)
                if data:
                    return SymbolEntry(**json.loads(data))
            else:
                data = self._memory_cache.get(key)
                if data:
                    return SymbolEntry(**json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Symbol lookup error: {e}")
            return None

    async def set_symbol(self, project_path: str, symbol: SymbolEntry) -> bool:
        """
        Cache symbol entry.

        Args:
            project_path: Project root path
            symbol: SymbolEntry to cache

        Returns:
            True if successful
        """
        key = f"{self.SYMBOL_PREFIX}:{project_path}:{symbol.symbol_name}"
        try:
            data = json.dumps(asdict(symbol))
            if self._redis:
                await self._redis.setex(key, self.SYMBOL_TTL, data)
            else:
                self._memory_cache[key] = data
            return True
        except Exception as e:
            logger.error(f"Symbol cache set error: {e}")
            return False

    async def get_symbols_for_file(self, project_path: str, file_path: str) -> List[SymbolEntry]:
        """
        Get all cached symbols for a file.

        Args:
            project_path: Project root path
            file_path: File path

        Returns:
            List of SymbolEntry
        """
        pattern = f"{self.SYMBOL_PREFIX}:{project_path}:*"
        results = []
        try:
            if self._redis:
                async for key in self._redis.scan_iter(match=pattern):
                    data = await self._redis.get(key)
                    if data:
                        entry = json.loads(data)
                        if entry.get("file_path") == file_path:
                            results.append(SymbolEntry(**entry))
            else:
                # In-memory fallback - iterate over matching keys
                prefix = f"{self.SYMBOL_PREFIX}:{project_path}:"
                for key, data in self._memory_cache.items():
                    if key.startswith(prefix):
                        entry = json.loads(data)
                        if entry.get("file_path") == file_path:
                            results.append(SymbolEntry(**entry))
            return results
        except Exception as e:
            logger.error(f"Symbols for file error: {e}")
            return []

    # === Call Graph Operations ===

    async def get_call_graph(self, project_path: str, entry_point: str) -> Optional[Dict[str, Any]]:
        """Get cached call graph."""
        key = f"{self.INDEX_PREFIX}:graph:{project_path}:{entry_point}"
        try:
            if self._redis:
                data = await self._redis.get(key)
            else:
                data = self._memory_cache.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Call graph lookup error: {e}")
            return None

    async def set_call_graph(self, project_path: str, entry_point: str, graph_data: Dict[str, Any]) -> bool:
        """Cache call graph."""
        key = f"{self.INDEX_PREFIX}:graph:{project_path}:{entry_point}"
        try:
            data = json.dumps(graph_data)
            if self._redis:
                await self._redis.setex(key, self.INDEX_TTL, data)
            else:
                self._memory_cache[key] = data
            return True
        except Exception as e:
            logger.error(f"Call graph cache set error: {e}")
            return False

    # === Search Result Caching ===

    async def get_search_result(self, project_path: str, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached grep/search results.

        Args:
            project_path: Project root path
            query_hash: Hash of search query

        Returns:
            List of match results or None
        """
        key = f"{self.INDEX_PREFIX}:search:{project_path}:{query_hash}"
        try:
            if self._redis:
                data = await self._redis.get(key)
            else:
                data = self._memory_cache.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Search cache lookup error: {e}")
            return None

    async def set_search_result(self, project_path: str, query_hash: str, results: List[Dict[str, Any]]) -> bool:
        """Cache grep/search results."""
        key = f"{self.INDEX_PREFIX}:search:{project_path}:{query_hash}"
        try:
            # Use shorter TTL for search results
            data = json.dumps(results)
            if self._redis:
                await self._redis.setex(key, self.DEFAULT_TTL, data)
            else:
                self._memory_cache[key] = data
            return True
        except Exception as e:
            logger.error(f"Search cache set error: {e}")
            return False

    # === Statistics ===

    async def get_stats(self, project_path: str) -> CacheStats:
        """
        Get cache statistics for project.

        Args:
            project_path: Project root path

        Returns:
            CacheStats
        """
        try:
            total_keys = len(self._memory_cache)
            total_size = sum(len(v) for v in self._memory_cache.values())

            if self._redis:
                # Count keys for project
                pattern = f"{self.INDEX_PREFIX}:*:{project_path}*"
                async for key in self._redis.scan_iter(match=pattern):
                    total_keys += 1
                    size = await self._redis.memory_usage(key)
                    if size:
                        total_size += size

                # Get hit/miss stats
                hits = await self._redis.get(f"{self.STATS_PREFIX}:hits") or 0
                misses = await self._redis.get(f"{self.STATS_PREFIX}:misses") or 0

                # Get last update time
                index_key = f"{self.INDEX_PREFIX}:files:{project_path}"
                last_updated_data = await self._redis.get(f"{index_key}:_cached_at")
                last_updated = last_updated_data.decode() if last_updated_data else None
            else:
                hits = 0
                misses = 0
                last_updated = None

            return CacheStats(
                total_keys=total_keys,
                index_size_bytes=total_size,
                last_updated=last_updated,
                cache_hits=int(hits),
                cache_misses=int(misses)
            )
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return CacheStats(0, 0, None, 0, 0)

    async def _incr_stat(self, stat_name: str) -> None:
        """Increment a statistic counter."""
        try:
            key = f"{self.STATS_PREFIX}:{stat_name}"
            if self._redis:
                await self._redis.incr(key)
        except Exception:
            pass

    # === Cache Invalidation ===

    async def invalidate_all(self, project_path: str) -> bool:
        """
        Invalidate all cached data for project.

        Args:
            project_path: Project root path

        Returns:
            True if successful
        """
        try:
            if self._redis:
                pattern = f"{self.INDEX_PREFIX}:*:{project_path}*"
                async for key in self._redis.scan_iter(match=pattern):
                    await self._redis.delete(key)

                pattern = f"{self.SYMBOL_PREFIX}:{project_path}:*"
                async for key in self._redis.scan_iter(match=pattern):
                    await self._redis.delete(key)

                await self._redis.sadd(self.STALE_PREFIX, project_path)
            else:
                # In-memory fallback
                prefix_pattern = f"{self.INDEX_PREFIX}:"
                keys_to_delete = [k for k in self._memory_cache if project_path in k]
                for k in keys_to_delete:
                    del self._memory_cache[k]
            logger.info(f"Invalidated all cache for {project_path}")
            return True
        except Exception as e:
            logger.error(f"Invalidate all error: {e}")
            return False

    async def get_stale_projects(self) -> List[str]:
        """Get list of projects with stale cache."""
        try:
            if self._redis:
                return list(await self._redis.smembers(self.STALE_PREFIX))
            return []
        except Exception as e:
            logger.error(f"Get stale projects error: {e}")
            return []

    async def clear_stale_flag(self, project_path: str) -> None:
        """Clear stale flag for project."""
        try:
            if self._redis:
                await self._redis.srem(self.STALE_PREFIX, project_path)
        except Exception as e:
            logger.error(f"Clear stale flag error: {e}")


# Global instance
_cache_manager: Optional[ExplorerCacheManager] = None


_redis_client: Optional[Any] = None


def get_explorer_cache_manager(redis_client=None) -> ExplorerCacheManager:
    """Get or create global cache manager instance.

    Args:
        redis_client: Optional Redis client for lazy initialization.
                     If provided and cache has no Redis, reinitializes with it.
    """
    global _cache_manager, _redis_client

    if _cache_manager is None:
        _cache_manager = ExplorerCacheManager()
        _redis_client = redis_client
        if redis_client:
            import asyncio
            asyncio.create_task(_cache_manager.initialize(redis_client))

    # If we have a redis_client and the existing cache has no redis, reinitialize
    if redis_client and _redis_client is None:
        _redis_client = redis_client
        import asyncio
        asyncio.create_task(_cache_manager.initialize(redis_client))

    return _cache_manager


async def init_explorer_cache(redis_client) -> ExplorerCacheManager:
    """Initialize global cache manager with Redis client."""
    global _cache_manager, _redis_client
    _redis_client = redis_client
    _cache_manager = ExplorerCacheManager()
    await _cache_manager.initialize(redis_client)
    return _cache_manager
