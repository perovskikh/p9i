from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Item
from app.schemas import ItemCreate
import json

class ItemCRUD:
    def __init__(self, redis):
        self.redis = redis

    async def get_item(self, db: AsyncSession, item_id: int):
        # 1. Проверяем кэш
        cache_key = f"item:{item_id}"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return ItemResponse(**json.loads(cached_data))

        # 2. Если нет в кэше, ищем в БД
        result = await db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        
        if item:
            # 3. Записываем в кэш
            item_dict = ItemResponse.model_validate(item).model_dump()
            await self.redis.set(cache_key, json.dumps(item_dict), ex=60)
            return item_dict
        
        return None

    async def create_item(self, db: AsyncSession, item: ItemCreate):
        db_item = Item(**item.model_dump())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def update_item(self, db: AsyncSession, item_id: int, item_data: dict):
        # Инвалидируем кэш
        await self.redis.delete(f"item:{item_id}")
        
        result = await db.execute(select(Item).where(Item.id == item_id))
        db_item = result.scalar_one_or_none()
        
        if db_item:
            for key, value in item_data.items():
                setattr(db_item, key, value)
            await db.commit()
            await db.refresh(db_item)
            return db_item
        return None

item_crud = ItemCRUD(redis=None) # Будет инициализирован в main.py