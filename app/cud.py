# Исправим имя файла на crud.py (Business Logic)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import User
from app.schemas import UserCreate, UserResponse
from app.redis_client import RedisClient
import json

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: int, cache: RedisClient = None):
    # 1. Проверяем кеш (Redis)
    cache_key = f"user:{user_id}"
    if cache:
        cached_data = await cache.get(cache_key)
        if cached_data:
            print("Cache HIT") # Лог для демонстрации
            return UserResponse.model_validate(json.loads(cached_data))
    
    print("Cache MISS") # Лог для демонстрации
    
    # 2. Если нет в кеше, идем в БД (PostgreSQL)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        user_response = UserResponse.model_validate(user)
        # 3. Сохраняем в кеш
        if cache:
            await cache.set(cache_key, user_response.model_dump(), expire=60)
        return user_response
    
    return None