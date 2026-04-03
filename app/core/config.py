import os
import tempfile
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI Upload POC"
    ENVIRONMENT: str = "dev" # "dev", "staging", "prod"    
    DEBUG: bool = False

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str                        # MUST be set via env

    # Storage — "local" or "azure"
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = os.path.join(tempfile.gettempdir(), "uploads")  # nosec B108
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "png", "jpg", "jpeg", "csv"]

    # Azure Blob (prod only)
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "uploads"

    # Rate limiting
    RATE_LIMIT_LOGIN: str = "5/minute"       # per IP
    RATE_LIMIT_UPLOAD: str = "20/minute"     # per user

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()