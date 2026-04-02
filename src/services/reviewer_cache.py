"""
Reviewer Cache Manager - Redis-based caching for code review.

Part of ADR-017 Reviewer Agent Refactoring.
Uses Redis for fast caching with operation-specific TTLs.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics."""
    total_keys: int
    index_size_bytes: int
    last_updated: Optional[str]
    cache_hits: int
    cache_misses: int


class ReviewerCacheManager:
    """
    Manages review cache with Redis primary storage.

    Features:
    - Diff result caching (TTL: 5 minutes)
    - Search/pattern result caching (TTL: 1 hour)
    - Security scan caching (TTL: 1 hour)
    - Quality metrics caching (TTL: 1 hour)
    - Code complexity caching (TTL: 1 hour)
    """

    # Key prefixes
    PREFIX = "reviewer"
    DIFF_PREFIX = f"{PREFIX}:diff"
    SEARCH_PREFIX = f"{PREFIX}:search"
    SECURITY_PREFIX = f"{PREFIX}:security"
    QUALITY_PREFIX = f"{PREFIX}:quality"
    METRICS_PREFIX = f"{PREFIX}:metrics"
    STATS_PREFIX = f"{PREFIX}:stats"

    # TTLs (in seconds)
    DIFF_TTL = 300  # 5 minutes - git diff changes frequently
    SEARCH_TTL = 3600  # 1 hour
    SECURITY_TTL = 3600  # 1 hour
    QUALITY_TTL = 3600  # 1 hour
    METRICS_TTL = 3600  # 1 hour

    def __init__(self, redis_client=None):
        """
        Initialize cache manager.

        Args:
            redis_client: Redis client instance. If None, creates new connection.
        """
        self._redis = redis_client

    async def initialize(self, redis_client) -> None:
        """Initialize with Redis client."""
        self._redis = redis_client
        logger.info("ReviewerCacheManager initialized with Redis")

    @property
    def redis(self):
        """Get Redis client."""
        return self._redis

    # === Diff Operations ===

    async def get_diff_result(self, project_path: str, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached diff result.

        Args:
            project_path: Project root path
            query_hash: Hash of diff query

        Returns:
            Dict with diff results or None
        """
        key = f"{self.DIFF_PREFIX}:{project_path}:{query_hash}"
        try:
            data = await self._redis.get(key)
            if data:
                await self._incr_stat("hits")
                return json.loads(data)
            await self._incr_stat("misses")
            return None
        except Exception as e:
            logger.error(f"Diff cache get error: {e}")
            return None

    async def set_diff_result(self, project_path: str, query_hash: str, result: Dict[str, Any]) -> bool:
        """
        Cache diff result.

        Args:
            project_path: Project root path
            query_hash: Hash of diff query
            result: Diff result to cache

        Returns:
            True if successful
        """
        key = f"{self.DIFF_PREFIX}:{project_path}:{query_hash}"
        try:
            result["_cached_at"] = datetime.now().isoformat()
            await self._redis.setex(key, self.DIFF_TTL, json.dumps(result))
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Diff cache set error: {e}")
            return False

    # === Search Operations ===

    async def get_search_result(self, project_path: str, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached search results.

        Args:
            project_path: Project root path
            query_hash: Hash of search query

        Returns:
            List of search results or None
        """
        key = f"{self.SEARCH_PREFIX}:{project_path}:{query_hash}"
        try:
            data = await self._redis.get(key)
            if data:
                await self._incr_stat("hits")
                return json.loads(data)
            await self._incr_stat("misses")
            return None
        except Exception as e:
            logger.error(f"Search cache get error: {e}")
            return None

    async def set_search_result(self, project_path: str, query_hash: str, results: List[Dict[str, Any]]) -> bool:
        """
        Cache search results.

        Args:
            project_path: Project root path
            query_hash: Hash of search query
            results: Search results to cache

        Returns:
            True if successful
        """
        key = f"{self.SEARCH_PREFIX}:{project_path}:{query_hash}"
        try:
            await self._redis.setex(key, self.SEARCH_TTL, json.dumps(results))
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Search cache set error: {e}")
            return False

    # === Security Operations ===

    async def get_security_result(self, project_path: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached security scan result.

        Args:
            project_path: Project root path
            file_path: File that was scanned

        Returns:
            Security scan result or None
        """
        key = f"{self.SECURITY_PREFIX}:{project_path}:{file_path}"
        try:
            data = await self._redis.get(key)
            if data:
                await self._incr_stat("hits")
                return json.loads(data)
            await self._incr_stat("misses")
            return None
        except Exception as e:
            logger.error(f"Security cache get error: {e}")
            return None

    async def set_security_result(self, project_path: str, file_path: str, result: Dict[str, Any]) -> bool:
        """
        Cache security scan result.

        Args:
            project_path: Project root path
            file_path: File that was scanned
            result: Security scan result to cache

        Returns:
            True if successful
        """
        key = f"{self.SECURITY_PREFIX}:{project_path}:{file_path}"
        try:
            result["_cached_at"] = datetime.now().isoformat()
            await self._redis.setex(key, self.SECURITY_TTL, json.dumps(result))
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Security cache set error: {e}")
            return False

    # === Quality Operations ===

    async def get_quality_result(self, project_path: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached quality metrics result.

        Args:
            project_path: Project root path
            file_path: File that was analyzed

        Returns:
            Quality metrics result or None
        """
        key = f"{self.QUALITY_PREFIX}:{project_path}:{file_path}"
        try:
            data = await self._redis.get(key)
            if data:
                await self._incr_stat("hits")
                return json.loads(data)
            await self._incr_stat("misses")
            return None
        except Exception as e:
            logger.error(f"Quality cache get error: {e}")
            return None

    async def set_quality_result(self, project_path: str, file_path: str, result: Dict[str, Any]) -> bool:
        """
        Cache quality metrics result.

        Args:
            project_path: Project root path
            file_path: File that was analyzed
            result: Quality metrics result to cache

        Returns:
            True if successful
        """
        key = f"{self.QUALITY_PREFIX}:{project_path}:{file_path}"
        try:
            result["_cached_at"] = datetime.now().isoformat()
            await self._redis.setex(key, self.QUALITY_TTL, json.dumps(result))
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Quality cache set error: {e}")
            return False

    # === Metrics Operations ===

    async def get_metrics_result(self, project_path: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached code metrics result.

        Args:
            project_path: Project root path
            file_path: File that was analyzed

        Returns:
            Code metrics result or None
        """
        key = f"{self.METRICS_PREFIX}:{project_path}:{file_path}"
        try:
            data = await self._redis.get(key)
            if data:
                await self._incr_stat("hits")
                return json.loads(data)
            await self._incr_stat("misses")
            return None
        except Exception as e:
            logger.error(f"Metrics cache get error: {e}")
            return None

    async def set_metrics_result(self, project_path: str, file_path: str, result: Dict[str, Any]) -> bool:
        """
        Cache code metrics result.

        Args:
            project_path: Project root path
            file_path: File that was analyzed
            result: Code metrics result to cache

        Returns:
            True if successful
        """
        key = f"{self.METRICS_PREFIX}:{project_path}:{file_path}"
        try:
            result["_cached_at"] = datetime.now().isoformat()
            await self._redis.setex(key, self.METRICS_TTL, json.dumps(result))
            await self._incr_stat("writes")
            return True
        except Exception as e:
            logger.error(f"Metrics cache set error: {e}")
            return False

    # === Statistics ===

    async def _incr_stat(self, stat_name: str) -> None:
        """Increment a statistic counter."""
        try:
            key = f"{self.STATS_PREFIX}:{stat_name}"
            await self._redis.incr(key)
        except Exception:
            pass

    async def get_stats(self, project_path: str) -> CacheStats:
        """
        Get cache statistics for project.

        Args:
            project_path: Project root path

        Returns:
            CacheStats
        """
        try:
            # Count keys for project
            patterns = [
                f"{self.DIFF_PREFIX}:{project_path}:*",
                f"{self.SEARCH_PREFIX}:{project_path}:*",
                f"{self.SECURITY_PREFIX}:{project_path}:*",
                f"{self.QUALITY_PREFIX}:{project_path}:*",
                f"{self.METRICS_PREFIX}:{project_path}:*",
            ]
            total_keys = 0
            total_size = 0

            for pattern in patterns:
                async for key in self._redis.scan_iter(match=pattern):
                    total_keys += 1
                    size = await self._redis.memory_usage(key)
                    if size:
                        total_size += size

            # Get hit/miss stats
            hits = await self._redis.get(f"{self.STATS_PREFIX}:hits") or 0
            misses = await self._redis.get(f"{self.STATS_PREFIX}:misses") or 0

            return CacheStats(
                total_keys=total_keys,
                index_size_bytes=total_size,
                last_updated=datetime.now().isoformat(),
                cache_hits=int(hits),
                cache_misses=int(misses)
            )
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return CacheStats(0, 0, None, 0, 0)

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
            patterns = [
                f"{self.DIFF_PREFIX}:{project_path}:*",
                f"{self.SEARCH_PREFIX}:{project_path}:*",
                f"{self.SECURITY_PREFIX}:{project_path}:*",
                f"{self.QUALITY_PREFIX}:{project_path}:*",
                f"{self.METRICS_PREFIX}:{project_path}:*",
            ]

            for pattern in patterns:
                async for key in self._redis.scan_iter(match=pattern):
                    await self._redis.delete(key)

            logger.info(f"Invalidated all reviewer cache for {project_path}")
            return True
        except Exception as e:
            logger.error(f"Invalidate all error: {e}")
            return False


# Global instance
_cache_manager: Optional[ReviewerCacheManager] = None


def get_reviewer_cache_manager() -> ReviewerCacheManager:
    """Get or create global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = ReviewerCacheManager()
    return _cache_manager


async def init_reviewer_cache(redis_client) -> ReviewerCacheManager:
    """Initialize global cache manager with Redis client."""
    global _cache_manager
    _cache_manager = ReviewerCacheManager()
    await _cache_manager.initialize(redis_client)
    return _cache_manager