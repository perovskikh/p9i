# promt-fastapi-conventions

## Назначение
Определяет стандарты для структуры FastAPI проекта, использования APIRouter, внедрения зависимостей для auth/db, и управления lifespan событиями.

## Когда использовать
- "fastapi", "api route", "endpoint", "роутинг"
- Создание новых эндпоинтов
- Рефакторинг структуры API
- Добавление middleware или зависимостей

## Входные данные
- `task` — что нужно реализовать
- `existing_code` — текущий код для контекста (опционально)
- `context` — информация о проекте

## Шаблон для FastAPI эндпоинтов

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["items"])

# Dependency injection pattern
def get_db():
    """Получение сессии базы данных"""
    yield db_session

def get_current_user():
    """Получение текущего пользователя"""
    yield user

# Proper endpoint structure
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get item by ID with proper error handling
    """
    try:
        item = await db.get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found"
            )
        return item
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Request/Response models with Pydantic
class ItemRequest(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
```

## Лучшие практики

### 1. APIRouter организация
- Разделяйте роутеры по доменам: `items_router`, `users_router`, `auth_router`
- Используйте `prefix` для группировки эндпоинтов
- Добавляйте `tags` для документации

### 2. Dependency injection
```python
# Dependencies для БД, кэша, внешних сервисов
def get_db():
    yield db_session

def get_cache():
    yield redis_client

# Композиция зависимостей
@router.post("/items")
async def create_item(
    item: ItemRequest,
    db: Session = Depends(get_db),
    cache: Redis = Depends(get_cache)
):
    ...
```

### 3. Lifespan management
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление ресурсами приложения"""
    # Startup
    await startup_resources()
    yield
    # Shutdown
    await cleanup_resources()

app = FastAPI(lifespan=lifespan)
```

### 4. Error handling
- Используйте `HTTPException` для клиентских ошибок
- Логируйте server errors отдельно
- Возвращайте структурированные error responses

### 5. Pydantic интеграция
- Используйте `response_model` для валидации ответов
- Определяйте Request/Response модели
- Используйте `Field(..., description="...")` для документации

## Примеры запросов

**"Создай эндпоинт для получения пользователя по ID"**:
```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**"Добавь middleware для rate limiting"**:
```python
from fastapi import Request
from starlette.middleware.base import HTTPMiddleware

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    if await is_rate_limited(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    response = await call_next(request)
    return response

app.add_middleware(HTTPMiddleware, dispatch=rate_limit_middleware)
```

## Интеграция с MCP

Эндпоинты могут быть автоматически документированы через MCP:
- `get_available_mcp_tools()` — список доступных инструментов
- `context7_lookup()` — документация FastAPI

## Сhecklist для кода
- [ ] Используется `APIRouter` для маршрутизации
- [ ] Dependencies определены через `Depends()`
- [ ] Request/Response модели с Pydantic
- [ ] Error handling с `HTTPException`
- [ ] Логирование через стандартный logger
- [ ] Lifespan events для ресурсов
- [ ] Теги для Swagger документации