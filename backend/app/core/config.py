from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = "AIMOS - AI Marketing Operating System"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "default_secret_key_change_in_production"
    API_V1_STR: str = "/api/v1"

    # Database Configuration (Default to local SQLite file for standalone execution without Docker/Postgres)
    DATABASE_URL: str = "sqlite+aiosqlite:///./aimos.db"

    # Telegram Configuration (Phase 2)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ALLOWED_USERS: str = ""  # Comma-separated list of allowed Telegram user IDs, e.g. "12345678,98765432"

    # Job Worker Configuration (Phase 2)
    JOB_WORKER_POLL_INTERVAL: float = 2.0  # seconds
    JOB_DEFAULT_MAX_RETRIES: int = 3

    # LLM Provider Configuration (Phase 3 AI Core)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "mock"

    # Future Integrations (Prepared Settings)
    META_MARKETING_API_TOKEN: Optional[str] = None
    META_AD_ACCOUNT_ID: Optional[str] = None
    TIKTOK_MARKETING_API_TOKEN: Optional[str] = None

    REDIS_URL: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET: str = "aimos-assets"

    def is_telegram_enabled(self) -> bool:
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_BOT_TOKEN.strip())

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
