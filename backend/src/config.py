"""Configuration management with environment variables."""

from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///news_database.db"
    database_echo: bool = False  # Set to True for SQL query logging (development only)
    database_pool_size: int = 5  # Number of connections to maintain in pool
    database_max_overflow: int = 10  # Maximum overflow connections beyond pool_size

    # Trusted Hosts (production)
    trusted_hosts: list[str] = ["*"]  # Use specific domains in production

    # OpenAI (optional - if not provided, AI features will be disabled)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    # JWT Authentication
    jwt_secret_key: str  # Required - no default for security
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

    # Environment (development, staging, production)
    environment: str = "development"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_login: str = "10/minute"  # 10 login attempts per minute per IP
    rate_limit_register: str = "5/hour"  # 5 registrations per hour per IP
    rate_limit_voting: str = "30/minute"  # 30 votes per minute per IP

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key strength.
        
        Prevents use of default or weak secrets in production.
        
        Args:
            v: JWT secret key value
            
        Returns:
            Validated secret key
            
        Raises:
            ValueError: If secret is default or too weak
        """
        if not v:
            raise ValueError("JWT_SECRET_KEY must be set")
        
        # Reject known default secrets
        forbidden_secrets = {
            "your_secret_key_here_change_in_production",
            "secret",
            "changeme",
            "password",
            "default",
        }
        if v.lower() in forbidden_secrets:
            raise ValueError(
                "CRITICAL SECURITY ERROR: Default JWT secret detected! "
                "Generate a strong secret with: "
                "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        # Enforce minimum length
        if len(v) < 32:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least 32 characters (current: {len(v)}). "
                "Generate a strong secret with: "
                "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        return v

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list.

        Args:
            v: CORS origins as string or list

        Returns:
            List of CORS origin URLs
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    @field_validator('trusted_hosts', mode='before')
    @classmethod
    def parse_trusted_hosts(cls, v):
        """Parse trusted hosts from comma-separated string or list.

        Args:
            v: Trusted hosts as string or list

        Returns:
            List of trusted host domains
        """
        if isinstance(v, str):
            return [host.strip() for host in v.split(',') if host.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
