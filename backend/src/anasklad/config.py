"""Typed settings loaded from env."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "anasklad"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 30

    credentials_fernet_key: str = ""

    cors_origins: str = "http://localhost:5173"

    sentry_dsn: str | None = None
    otel_exporter_otlp_endpoint: str | None = None
    otel_service_name: str = "anasklad-api"

    log_level: str = "INFO"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.app_env == "production"

    def assert_production_ready(self) -> None:
        if not self.is_prod:
            return
        problems: list[str] = []
        if self.jwt_secret in ("", "change_me_to_long_random_string") or len(self.jwt_secret) < 32:
            problems.append("JWT_SECRET must be set to a strong random value (>=32 chars)")
        if not self.credentials_fernet_key:
            problems.append("CREDENTIALS_FERNET_KEY must be set")
        if "localhost" in self.database_url:
            problems.append("DATABASE_URL points to localhost")
        if problems:
            raise RuntimeError("Unsafe production config: " + "; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
