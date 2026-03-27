# promt-async-db-integration

## Назначение
Лучшие практики для асинхронного взаимодействия с PostgreSQL (через SQLAlchemy/asyncpg) и Redis (через aioredis), обеспечивая управление сессиями и connection pooling.

## Когда использовать
- "postgres", "sql", "redis", "database", "async"
- Создание асинхронных запросов к БД
- Работа с кэшем Redis
- Управление соединениями с базами данных

## Async PostgreSQL с SQLAlchemy

### Connection setup
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# Async engine с connection pool
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,
    pool_size=20,  # Размер пула
    max_overflow=10,  # Дополнительные соединения
    pool_pre_ping=True,  # Проверка alive
    pool_recycle=3600  # Пересоздание каждые 1 час
)

# Session factory
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Session dependency
async def get_db():
    """Dependency для получения async сессии"""
    async with async_session_maker() as session:
        yield session
```

### Async запросы
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(db: AsyncSession, user_id: str):
    """Асинхронный SELECT запрос"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: dict):
    """Асинхронный INSERT с возвратом созданного объекта"""
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(db: AsyncSession, user_id: str, updates: dict):
    """Асинхронный UPDATE с обработкой concurrent модификаций"""
    user = await get_user(db, user_id)
    if not user:
        return None

    for key, value in updates.items():
        setattr(user, key, value)

    await db.commit()
    return user
```

### Transactions и rollback
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def transfer_money(
    db: AsyncSession,
    from_id: str,
    to_id: str,
    amount: float
):
    """Асинхронная транзакция с rollback при ошибке"""
    async with db.begin():
        try:
            sender = await db.get(User, from_id)
            receiver = await db.get(User, to_id)

            if sender.balance < amount:
                raise ValueError("Insufficient funds")

            sender.balance -= amount
            receiver.balance += amount

            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
```

## Async Redis с aioredis

### Connection setup
```python
import aioredis
from contextlib import asynccontextmanager

# Redis connection pool
redis_pool = aioredis.ConnectionPool.from_url(
    "redis://localhost:6379",
    max_connections=20,
    retry_on_timeout=True,
    socket_keepalive=True
)

async def get_redis():
    """Dependency для получения Redis подключения"""
    return await redis_pool.acquire()
```

### Базовые операции
```python
async def cache_get(redis: aioredis.Redis, key: str):
    """Получение значения из кэша"""
    value = await redis.get(key)
    return value.decode('utf-8') if value else None

async def cache_set(
    redis: aioredis.Redis,
    key: str,
    value: str,
    ttl: int = 3600
):
    """Запись в кэш с TTL"""
    await redis.setex(key, ttl, value)

async def cache_delete(redis: aioredis.Redis, key: str):
    """Удаление из кэша"""
    await redis.delete(key)

# Pattern с fallback
async def get_item_with_cache(
    db: AsyncSession,
    redis: aioredis.Redis,
    item_id: str
):
    """Get from cache first, then DB"""
    # Try cache
    cached = await cache_get(redis, f"item:{item_id}")
    if cached:
        return json.loads(cached)

    # Fallback to DB
    item = await get_item(db, item_id)
    if item:
        await cache_set(redis, f"item:{item_id}", item.model_dump_json())

    return item
```

### Pub/Sub для real-time
```python
import aioredis
import asyncio

async def publish_event(redis: aioredis.Redis, channel: str, message: dict):
    """Публикация события в Redis pub/sub"""
    await redis.publish(channel, json.dumps(message))

async def subscribe_to_events(redis: aioredis.Redis, channels: list[str]):
    """Подписка на события"""
    async with redis.pubsub() as pubsub:
        await pubsub.subscribe(*channels)
        async for message in pubsub.listen():
            yield message
```

## Интеграция PostgreSQL + Redis

### Cache-aside pattern
```python
async def get_user_cached(
    db: AsyncSession,
    redis: aioredis.Redis,
    user_id: str
):
    """Get user: cache first, then DB"""
    cache_key = f"user:{user_id}"

    # Try cache
    cached = await cache_get(redis, cache_key)
    if cached:
        return User.model_validate_json(cached)

    # Query DB
    user = await get_user(db, user_id)
    if user:
        # Update cache
        await cache_set(redis, cache_key, user.model_dump_json(), ttl=1800)

    return user
```

### Distributed lock
```python
async def with_lock(
    redis: aioredis.Redis,
    lock_key: str,
    timeout: float = 10.0
):
    """Контекст-менеджер для distributed lock"""
    import uuid
    lock_value = str(uuid.uuid4())

    acquired = await redis.set(
        lock_key,
        lock_value,
        nx=True,
        ex=timeout
    )

    try:
        if not acquired:
            raise TimeoutError(f"Lock {lock_key} held by other process")
        yield
    finally:
        await redis.delete(lock_key)

# Usage
async def process_payment(payment_id: str, amount: float):
    async with with_lock(redis, f"payment:{payment_id}"):
        # Критическая секция с distributed lock
        result = await process_transaction(payment_id, amount)
```

## Best Practices

### 1. Connection pooling
- Используйте пул соединений: `pool_size=20`
- Установите `max_overflow` для пиковых нагрузок
- `pool_pre_ping=True` для проверки alive соединений
- `pool_recycle` для периодического обновления

### 2. Session management
- Каждый request → отдельная сессия
- Используйте dependency injection: `Depends(get_db)`
- Автоматическое закрытие через `async with`
- Не храните сессии между request'ами

### 3. Error handling
```python
from sqlalchemy.exc import SQLAlchemyError

async def safe_db_operation(db: AsyncSession, operation):
    """Обертка с error handling"""
    try:
        result = await operation(db)
        await db.commit()
        return result
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"DB error: {e}")
        raise
```

### 4. Performance tuning
- Batch operations вместо множественных query
- Use `SELECT ... FOR UPDATE` для row-level locking
- Index optimization для частых запросов
- Cache hot keys с правильными TTL

### 5. Monitoring
```python
import time

async def timed_db_operation(db: AsyncSession, operation):
    """Измерение времени выполнения"""
    start = time.perf_counter()
    result = await operation(db)
    elapsed = time.perf_counter() - start

    logger.info(f"DB operation took {elapsed:.3f}s")
    return result
```

## Примеры запросов

**"Создай async функцию для массового импорта"**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

async def bulk_import_items(
    db: AsyncSession,
    items: List[dict]
):
    """Mass import with batch insert"""
    async with db.begin():
        # Batch insert вместо N отдельных INSERT
        await db.execute(
            insert(Item).values(items),
            execution_options={"synchronize_session": False}
        )
        await db.commit()

    return len(items)
```

**"Добавь cache для list endpoints"**:
```python
@router.get("/items")
async def list_items(
    db: AsyncSession,
    redis: aioredis.Redis,
    skip: int = 0,
    limit: int = 100
):
    cache_key = f"items:list:{skip}:{limit}"

    # Try cache first
    cached = await cache_get(redis, cache_key)
    if cached:
        return json.loads(cached)

    # Query DB
    result = await db.execute(
        select(Item)
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()

    # Update cache
    await cache_set(redis, cache_key, json.dumps([i.dict() for i in items]))

    return items
```

## Интеграция с MCP

```python
# В prompts можно использовать:
"""
from src.api.server import adapt_to_project, save_project_memory

# Auto-detect stack
stack = adapt_to_project("/project/path")

# Save to project memory
save_project_memory(
    project_id="my_project",
    key="db_setup",
    value={
        "postgres_enabled": True,
        "redis_enabled": True,
        "connection_pool_size": 20
    }
)
"""
```

## Сhecklist для async кода
- [ ] Используются `async def` для async операций
- [ ] SQLAlchemy `AsyncSession` вместо `Session`
- [ ] Connection pool настроен с разумными значениями
- [ ] Redis connection pooling включен
- [ ] Сессии закрываются через `async with`
- [ ] Transactions имеют `try/except/rollback`
- [ ] Cache keys имеют TTL
- [ ] Используются batch operations где возможно
- [ ] Error handling для database exceptions
- [ ] Lock patterns для critical operations