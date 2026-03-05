from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ABS Industrial Intelligence Platform"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://abs:abs@db:5432/abs_iip"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:8501,http://localhost:3000"

    fernet_key: str = ""

    abs_logo_path: str = ""
    default_report_dir: str = "reports"

    redis_url: str = "redis://redis:6379/0"
    enable_redis_broadcast: bool = False

    seed_super_admin_email: str = "superadmin@abs.com"
    seed_super_admin_password: str = "ChangeMe@123"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def report_dir(self) -> Path:
        path = Path(self.default_report_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
