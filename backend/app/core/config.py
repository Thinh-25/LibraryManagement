from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: SecretStr | None = None
    jwt_secret: SecretStr | None = None
    access_token_minutes: int = 30
    auth_rate_limit: int = 20
    auth_rate_window_seconds: int = 300
    reservation_hold_hours: int = 48
    cover_upload_dir: Path = Path(__file__).resolve().parents[3] / ".local" / "uploads" / "covers"
    cors_origins: list[str] = ["http://localhost:5000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
