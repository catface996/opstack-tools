"""Application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AIOps Tools"
    app_version: str = "0.1.0"
    app_description: str = "LLM Tool Management System - Create, manage, and execute tools for LLM function calling"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8083

    # API
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Database
    database_url: PostgresDsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/aiops_tools"  # type: ignore

    # Redis
    redis_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Tool Execution
    tool_execution_timeout: int = 30  # seconds (spec: FR-014)
    max_concurrent_executions: int = 10


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
