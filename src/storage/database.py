# src/storage/database.py
"""
Database connection and models for AI Prompt System

PostgreSQL + Redis hybrid storage approach:
- PostgreSQL: persistent data (prompts, versions, projects, API keys)
- Redis: hot data (sessions, cache, pub/sub, rate limiting)
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_prompts"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


class RedisSettings(BaseSettings):
    """Redis configuration."""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_url: str = ""

    class Config:
        env_prefix = "REDIS_"

    def build_url(self) -> str:
        """Build Redis URL dynamically."""
        import os
        from urllib.parse import urlparse

        # Check environment variables at runtime
        host = os.getenv("REDIS_HOST", self.redis_host)
        # Handle K8s service URLs like "redis:tcp://10.43.164.63:6379"
        if "://" in host:
            parsed = urlparse(f"redis://{host}" if not host.startswith("redis") else host)
            host = parsed.hostname or host.split(":")[0]
        port = os.getenv("REDIS_PORT", str(self.redis_port))
        # Clean port if it has protocol prefix
        if "tcp://" in port:
            port = port.split(":")[-1]
        password = os.getenv("REDIS_PASSWORD", self.redis_password)
        url = os.getenv("REDIS_URL")

        if url:
            return url
        if password:
            return f"redis://:{password}@{host}:{port}"
        return f"redis://{host}:{port}"


# Settings instances
db_settings = DatabaseSettings()
redis_settings = RedisSettings()


def get_redis_client():
    """Get Redis client with dynamic URL resolution."""
    import os
    import redis.asyncio as aioredis

    redis_url = redis_settings.build_url()
    logger.info(f"Connecting to Redis: {redis_url.replace(redis_url.split('@')[-1] if '@' in redis_url else '', '***')}")

    try:
        client = aioredis.from_url(redis_url, decode_responses=True)
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Redis features will be disabled.")
        return None


# Redis client setup (lazy - will be created on first use)
redis_client = None


# Redis client setup
try:
    import redis.asyncio as aioredis
    redis_url = redis_settings.build_url()
    redis_client = aioredis.from_url(redis_url, decode_responses=True)
    logger.info(f"Redis connected: {redis_url}")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Redis features will be disabled.")
    redis_client = None


# Async engine for PostgreSQL
async_engine = create_async_engine(
    db_settings.database_url,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    echo=db_settings.echo,
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine for migrations/setup
sync_engine = create_engine(
    db_settings.database_url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql"),
    pool_size=5,
    echo=db_settings.echo,
)


async def get_db_session() -> AsyncSession:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def close_connections():
    """Close all database connections."""
    await async_engine.dispose()
    if redis_client:
        await redis_client.close()
    logger.info("Database connections closed")