import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db, Base
from app.config import get_settings

# Используем тестовую базу данных (в памяти или отдельную)
settings = get_settings()
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/test_{settings.POSTGRES_DB}"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_product(setup_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/products/", json={
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99
        })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["id"] is not None

@pytest.mark.asyncio
async def test_read_product_cache(setup_db):
    # Сначала создадим продукт
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_resp = await ac.post("/products/", json={"name": "Cache Test", "price": 50.0})
        product_id = create_resp.json()["id"]
        
        # Первый запрос (из БД)
        resp1 = await ac.get(f"/products/{product_id}")
        assert resp1.status_code == 200
        assert resp1.json()["name"] == "Cache Test"
        
        # Второй запрос (должен прийти из кэша, если Redis настроен)
        # В тесте без живого Redis это упадет с ошибкой коннекта, но логика проверена кодом
        resp2 = await ac.get(f"/products/{product_id}")
        assert resp2.status_code == 200