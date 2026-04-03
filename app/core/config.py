from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI Upload POC"
    ENVIRONMENT: str = "dev"          # "dev" | "prod"
    DEBUG: bool = False

    # JWT
    JWT_SECRET_KEY: str               # MUST be set via env var
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Upload
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "png", "jpg", "jpeg", "csv"]

    # Azure (used in prod)
    AZURE_STORAGE_CONNECTION_STRING: str = ""

    model_config = SettingsConfigDict(
        env_file=".env.dev",          # override with ENV_FILE env var
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()           # singleton — reads env once
def get_settings() -> Settings:
    return Settings()