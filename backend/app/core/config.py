from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blinkit Stock Sentinel"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel"
    redis_url: str | None = None
    cors_origins: list[AnyHttpUrl] | list[str] = ["https://web-production-bd4d.up.railway.app"]
    force_https: bool = False
    trust_proxy_headers: bool = True
    bootstrap_mode: bool = False
    dependency_retry_interval_seconds: int = 20
    provider_base_delay_seconds: float = 1.5
    provider_max_requests_per_minute: int = 30
    provider_timeout_seconds: int = 12
    playwright_headless: bool = True
    playwright_timeout_seconds: int = 30
    playwright_browser_pool_size: int = 1
    playwright_max_retries: int = 3
    playwright_stealth_mode: bool = True
    blinkit_search_url_template: str | None = None
    blinkit_product_url_template: str | None = None
    blinkit_headers: dict[str, str] = Field(default_factory=dict)
    live_provider_required: bool = False
    stock_confirmation_delay_seconds: float = 2.0
    stock_response_max_age_seconds: int = 120
    duplicate_alert_window_seconds: int = 1800
    default_poll_interval_seconds: int = 900
    min_poll_interval_seconds: int = 300
    fcm_credentials_path: str | None = None
    sentry_dsn: str | None = None
    email_from: str | None = None
    smtp_url: str | None = None
    # Internal auth: this app is intended to run behind a VPN/private network.
    # No app-level user secrets are accepted or stored; routes resolve to this service user.
    internal_auth_enabled: bool = True
    internal_device_email: str = "internal.device@blinkitsentinel.app"
    internal_device_full_name: str = "Internal Device User"
    internal_device_is_admin: bool = True
    expose_internal_errors: bool = False
    celery_worker_pool: str = "prefork"
    celery_worker_concurrency: int = 1
    celery_worker_max_tasks_per_child: int = 25
    celery_worker_prefetch_multiplier: int = 1
    celery_task_time_limit_seconds: int = 600
    celery_task_soft_time_limit_seconds: int = 540

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str | None) -> str:
        raw = (value or "").strip()
        if raw.startswith("postgres://"):
            return raw.replace("postgres://", "postgresql+asyncpg://", 1)
        if raw.startswith("postgresql://") and not raw.startswith("postgresql+asyncpg://"):
            return raw.replace("postgresql://", "postgresql+asyncpg://", 1)
        return raw or "postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel"

    @field_validator("redis_url", mode="before")
    @classmethod
    def _normalize_redis_url(cls, value: str | None) -> str | None:
        raw = (value or "").strip()
        if not raw:
            return None
        if raw.startswith("rediss://"):
            parsed = urlsplit(raw)
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            query.setdefault("ssl_cert_reqs", "none")
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
        return raw

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
