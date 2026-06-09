from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    chroma_persist_dir: str = "./chroma_db"
    whisper_model: str = "base"
    max_file_size_mb: int = 500
    upload_dir: str = "./uploads"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 50
    claude_model: str = "claude-sonnet-4-20250514"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
