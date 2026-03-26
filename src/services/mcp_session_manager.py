"""
MCP Session Manager - Server-side session management for streamable-http transport.

Allows direct HTTP connections without proxy while maintaining session state.
Sessions are stored in Redis with configurable TTL.
Falls back to in-memory storage when Redis is unavailable.
"""

import os
import uuid
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from collections import OrderedDict

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class InMemorySessionStore:
    """In-memory fallback when Redis is unavailable."""

    def __init__(self, max_sessions: int = 1000):
        self._sessions: OrderedDict = OrderedDict()
        self._max_sessions = max_sessions

    def create(self, session_id: str, data: Dict) -> None:
        self._sessions[session_id] = data
        # Evict oldest if over limit
        while len(self._sessions) > self._max_sessions:
            self._sessions.popitem(last=False)

    def get(self, session_id: str) -> Optional[Dict]:
        if session_id in self._sessions:
            # Move to end (most recently used)
            self._sessions.move_to_end(session_id)
            return self._sessions[session_id]
        return None

    def update(self, session_id: str, data: Dict) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id].update(data)
            self._sessions.move_to_end(session_id)
            return True
        return False

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_all(self, limit: int) -> list:
        sessions = []
        for sid, data in reversed(self._sessions.items()):
            if len(sessions) >= limit:
                break
            sessions.append({
                "session_id": sid,
                "created_at": data.get("created_at"),
                "last_accessed": data.get("last_accessed"),
            })
        return sessions


class MCPSessionManager:
    """
    Server-side session manager for MCP streamable-http transport.
    Stores session data in Redis to survive server restarts and enable direct HTTP connections.
    Falls back to in-memory storage when Redis is unavailable.
    """

    SESSION_PREFIX = "mcp:session:"
    SESSION_TTL = 3600  # 1 hour default TTL

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize session manager.

        Args:
            redis_client: Async Redis client. If None, will be created on first use.
        """
        self._redis = redis_client
        self._ttl = int(os.getenv("MCP_SESSION_TTL", self.SESSION_TTL))
        self._memory_store = InMemorySessionStore()
        self._use_redis = True  # Will be set to False if Redis unavailable

    async def _get_redis(self) -> Optional[redis.Redis]:
        """Get or create Redis client."""
        if self._redis is None:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
            try:
                self._redis = await redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._redis.ping()
                self._use_redis = True
                logger.info(f"MCP Session Manager connected to {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect Redis for sessions, using in-memory fallback: {e}")
                self._use_redis = False
                self._redis = None
        return self._redis

    async def create_session(self, client_info: Dict[str, Any] = None) -> str:
        """
        Create a new MCP session.

        Args:
            client_info: Optional client information (protocol version, capabilities, etc.)

        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "client_info": client_info or {},
            "state": {},
        }

        redis_client = await self._get_redis()
        if redis_client and self._use_redis:
            key = f"{self.SESSION_PREFIX}{session_id}"
            await redis_client.setex(
                key,
                self._ttl,
                json.dumps(session_data)
            )
            logger.info(f"Created MCP session (Redis): {session_id}")
        else:
            # Fallback to in-memory
            self._memory_store.create(session_id, session_data)
            logger.info(f"Created MCP session (in-memory): {session_id}")

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        redis_client = await self._get_redis()

        if redis_client and self._use_redis:
            key = f"{self.SESSION_PREFIX}{session_id}"
            data = await redis_client.get(key)

            if data:
                session_data = json.loads(data)
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                await redis_client.setex(key, self._ttl, json.dumps(session_data))
                return session_data
        else:
            # Fallback to in-memory
            session_data = self._memory_store.get(session_id)
            if session_data:
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                self._memory_store.update(session_id, session_data)
            return session_data

        return None

    async def update_session(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Update session state."""
        redis_client = await self._get_redis()

        if redis_client and self._use_redis:
            key = f"{self.SESSION_PREFIX}{session_id}"
            data = await redis_client.get(key)

            if data:
                session_data = json.loads(data)
                session_data["state"].update(state)
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                await redis_client.setex(key, self._ttl, json.dumps(session_data))
                return True
        else:
            return self._memory_store.update(session_id, state)

        return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        redis_client = await self._get_redis()

        if redis_client and self._use_redis:
            key = f"{self.SESSION_PREFIX}{session_id}"
            result = await redis_client.delete(key)
            logger.info(f"Deleted MCP session (Redis): {session_id}")
            return result > 0
        else:
            result = self._memory_store.delete(session_id)
            logger.info(f"Deleted MCP session (in-memory): {session_id}")
            return result

    async def list_sessions(self, limit: int = 100) -> list:
        """List all active sessions."""
        redis_client = await self._get_redis()

        if redis_client and self._use_redis:
            sessions = []
            cursor = 0
            pattern = f"{self.SESSION_PREFIX}*"

            while len(sessions) < limit:
                cursor, keys = await redis_client.scan(cursor, match=pattern, count=50)
                for key in keys:
                    data = await redis_client.get(key)
                    if data:
                        session_data = json.loads(data)
                        sessions.append({
                            "session_id": session_data.get("session_id"),
                            "created_at": session_data.get("created_at"),
                            "last_accessed": session_data.get("last_accessed"),
                        })
                if cursor == 0:
                    break

            return sessions[:limit]
        else:
            return self._memory_store.list_all(limit)

    async def cleanup_expired(self) -> int:
        """Clean up expired sessions (handled automatically by Redis TTL)."""
        sessions = await self.list_sessions(limit=1000)
        return len(sessions)


# Global session manager instance
_session_manager: Optional[MCPSessionManager] = None


async def get_session_manager() -> MCPSessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        redis_client = await get_redis_client()
        _session_manager = MCPSessionManager(redis_client)
    return _session_manager


# Import from server.py to avoid circular imports
async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client from server.py."""
    from src.api.server import get_redis_client as _get_redis
    try:
        return await _get_redis()
    except Exception:
        return None
