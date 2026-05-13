from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blinkit Stock Sentinel"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: list[AnyHttpUrl] | list[str] = ["https://example.com"]
    force_https: bool = True
    trust_proxy_headers: bool = True
    provider_base_delay_seconds: float = 1.5
    provider_max_requests_per_minute: int = 30
    provider_timeout_seconds: int = 12
    blinkit_search_url_template: str | None = None
    blinkit_product_url_template: str | None = None
    blinkit_headers: dict[str, str] = Field(default_factory=dict)
    live_provider_required: bool = True
    stock_confirmation_delay_seconds: float = 2.0
    stock_response_max_age_seconds: int = 120
    duplicate_alert_window_seconds: int = 1800
    default_poll_interval_seconds: int = 900
    min_poll_interval_seconds: int = 300
    fcm_credentials_path: str | None = None
    sentry_dsn: str | None = None
    email_from: str | None = None
    smtp_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
