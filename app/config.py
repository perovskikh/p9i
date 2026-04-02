from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "mydb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()