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

    # Phase 4 Provider Integrations & Safety
    CALLING_PROVIDER: str = "mock"  # mock | twilio | telnyx | sip | android
    STT_PROVIDER: str = "mock"      # mock | deepgram | whisper | google
    TTS_PROVIDER: str = "edge"      # edge | google | elevenlabs | mock
    LLM_PROVIDER: str = "mock"      # mock | gemini | openai | anthropic

    LIVE_MODE: bool = False
    ALLOWED_TEST_NUMBERS: str = "+84853631921,+84901234567,+84900000000"

    MAX_CALL_DURATION: int = 300       # seconds
    MAX_LLM_COST: float = 0.10         # USD
    MAX_STT_COST: float = 0.05         # USD
    MAX_TTS_COST: float = 0.05         # USD
    MAX_TOTAL_CALL_COST: float = 0.20  # USD

    # Provider API Credentials
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_TTS_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    EDGE_TTS_VOICE: str = "vi-VN-HoaiMyNeural"

    # Future Integrations (Prepared Settings)
    META_MARKETING_API_TOKEN: Optional[str] = None
    META_AD_ACCOUNT_ID: Optional[str] = None
    TIKTOK_MARKETING_API_TOKEN: Optional[str] = None

    REDIS_URL: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET: str = "aimos-assets"

    def is_telegram_enabled(self) -> bool:
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_BOT_TOKEN.strip())

    def get_allowed_test_numbers(self) -> list[str]:
        if not self.ALLOWED_TEST_NUMBERS:
            return []
        return [p.strip() for p in self.ALLOWED_TEST_NUMBERS.split(",") if p.strip()]

    def is_live_call_allowed(self, phone: str) -> bool:
        if not self.LIVE_MODE:
            return False
        allowed = self.get_allowed_test_numbers()
        return phone in allowed

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
