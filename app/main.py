from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
import json
from typing import Optional

from app.database import get_db, engine, Base
from app.models import Product
from app.schemas import ProductCreate, Product as ProductSchema
from app.config import get_settings

settings = get_settings()

# Инициализация Redis
redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)

app = FastAPI(title="Product Service with Redis Cache")

# Создание таблиц при старте (для примера)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/products/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    # Инвалидируем кэш списка продуктов (если бы он был), здесь просто сохраняем
    return db_product

@app.get("/products/{product_id}", response_model=ProductSchema)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Пытаемся получить из Redis
    cache_key = f"product:{product_id}"
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        print(f"Cache HIT for {product_id}")
        return ProductSchema.model_validate_json(cached_data)
    
    print(f"Cache MISS for {product_id}")
    
    # 2. Если нет в кэше, берем из PostgreSQL
    result = await db.get(Product, product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_schema = ProductSchema.model_validate(result)
    
    # 3. Сохраняем в Redis (например, на 60 секунд)
    await redis_client.setex(cache_key, 60, product_schema.model_dump_json())
    
    return product_schema

@app.put("/products/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_product = await db.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    
    # Удаляем из кэша, чтобы при следующем запросе обновились данные
    await redis_client.delete(f"product:{product_id}")
    
    return db_product