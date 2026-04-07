from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    PROJECT_NAME: str = "Agentic AI App"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM — swap OPENAI_BASE_URL to point at Ollama for local inference
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"

    # Ollama (local, Mac Mini M1)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "agentdb"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # Redis (rate limiting + session cache)
    REDIS_URL: str = "redis://localhost:6379"

    # Observability
    LANGSMITH_API_KEY: str = ""
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
