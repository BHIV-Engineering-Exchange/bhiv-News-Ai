"""
Configuration management for News AI Backend
"""
import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_requests_per_hour: int = 1000

    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "news_ai_dev"

    # External APIs
    uniguru_api_key: Optional[str] = None
    uniguru_base_url: str = "https://api.uniguru.com"

    # BHIV Core
    bhiv_core_url: str = "http://localhost:8080"
    bhiv_api_key: Optional[str] = None

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    api_key_salt: str = "your-salt-change-in-production"

    # Scheduler
    scheduler_enabled: bool = True
    max_workers: int = 5
    queue_size_limit: int = 1000

    # RL Settings
    rl_adaptive_scaling: bool = True
    rl_reward_threshold: float = 0.6
    rl_max_corrections: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("cors_allow_methods", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @validator("cors_allow_headers", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v


# Global settings instance
settings = Settings()