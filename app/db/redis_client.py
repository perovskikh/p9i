import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True
        )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def add_to_blacklist(self, jti: str, expire_seconds: int):
        await self.redis.setex(f"blacklist:{jti}", expire_seconds, "1")

    async def is_blacklisted(self, jti: str) -> bool:
        return await self.redis.exists(f"blacklist:{jti}")

redis_client = RedisClient()