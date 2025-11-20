"""Configuration management with environment variables."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///news_database.db"

    # OpenAI (optional - if not provided, AI features will be disabled)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Sentry
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 1.0
    sentry_profiles_sample_rate: float = 1.0

    # CORS
    cors_origins: list[str] = ["http://localhost:8080"]

    # Background Scheduler
    news_fetch_interval_minutes: int = 100

    # External APIs
    necessities_price_api_url: str = "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice?CategoryName=%27%2A%27&Name=%27%2A%27"
    udn_news_api_url: str = "https://udn.com/api/more"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
