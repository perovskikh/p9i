import redis
import json
from app.config import settings

# Создаем подключение к Redis
redis_client = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    decode_responses=True
)

class CacheService:
    def __init__(self, client):
        self.client = client

    def get(self, key: str):
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: dict, expire: int = 60):
        self.client.set(key, json.dumps(value), ex=expire)

    def delete(self, key: str):
        self.client.delete(key)

cache_service = CacheService(redis_client)