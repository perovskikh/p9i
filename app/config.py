from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db" # Фоллбек для тестов/локального запуска
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    class Config:
        env_file = ".env"

settings = Settings()