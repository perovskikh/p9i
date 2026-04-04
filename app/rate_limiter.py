import time
import json
from typing import Optional
from fastapi import Request, HTTPException, status
from app.redis_client import manager

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        """
        :param times: Количество разрешенных запросов
        :param seconds: Временной интервал в секундах
        """
        self.times = times
        self.seconds = seconds
        self.prefix = "rate_limit"

    async def check(self, request: Request, key: Optional[str] = None) -> bool:
        """
        Проверяет, не превышен ли лимит.
        Использует алгоритм Fixed Window.
        """
        if not key:
            # Если ключ не передан, используем IP клиента
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0]
            else:
                ip = request.client.host if request.client else "unknown"
            key = ip
            
        redis_key = f"{self.prefix}:{key}"
        current_time = int(time.time())
        window_start = current_time - (current_time % self.seconds) # Округляем до начала окна

        async with manager.get_client() as redis:
            # Используем Lua скрипт для атомарности (или pipeline для простоты)
            # Здесь упрощенная логика через pipeline
            
            pipe = redis.pipeline()
            # Удаляем старые ключи (если бы было скользящее окно, здесь была бы логика zremrangebyscore)
            # Для фиксированного окна просто проверяем текущее значение
            
            # Инкрементируем счетчик
            try:
                pipe.incr(redis_key)
                pipe.expire(redis_key, self.seconds)
                results = await pipe.execute()
                
                current_requests = results[0]
                
                # Если счетчик сбросился (истек TTL) и стал 1, значит это новое окно
                # Но с командой expire выше, ключ живет ровно self.seconds.
                # Для точного фиксированного окна лучше хранить время начала окна в ключе.
                
                if current_requests > self.times:
                    # Можно добавить заголовки с информацией о лимите
                    return False
                
                return True
            except Exception as e:
                print(f"Redis error in rate limiter: {e}")
                # В случае ошибки Redis обычно лучше разрешить запрос (fail open)
                return True

    async def __call__(self, request: Request):
        """Использование как FastAPI Dependency."""
        allowed = await self.check(request)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.times),
                    "X-RateLimit-Window": str(self.seconds),
                }
            )

# Готовые лимитеры для использования
default_limiter = RateLimiter(times=10, seconds=60)
strict_limiter = RateLimiter(times=5, seconds=10)