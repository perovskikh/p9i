# Исправленная версия main.py с учетом crud.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db, init_db
from app.redis_client import redis_client
from app.schemas import UserCreate, UserResponse
from app.crud import create_user, get_user # Теперь импорт из crud
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await redis_client.connect()
    yield
    await redis_client.disconnect()

app = FastAPI(title="User System with Cache", lifespan=lifespan)

@app.post("/users/", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await create_user(db, user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Передаем клиент Redis явно или используем глобальный (зависит от архитектуры)
    # В crud.py мы используем аргумент cache, поэтому передадим его
    user = await get_user(db, user_id, cache=redis_client)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user