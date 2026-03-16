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
    redis_url: str = "redis://localhost:6379"
    redis_cluster_nodes: str = "localhost:6379"


# Settings instances
db_settings = DatabaseSettings()
redis_settings = RedisSettings()

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


# Redis client setup
try:
    import redis.asyncio as aioredis
    redis_client = aioredis.from_url(redis_settings.redis_url, decode_responses=True)
    logger.info(f"Redis connected: {redis_settings.redis_url}")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Redis features will be disabled.")
    redis_client = None


async def close_connections():
    """Close all database connections."""
    await async_engine.dispose()
    if redis_client:
        await redis_client.close()
    logger.info("Database connections closed")