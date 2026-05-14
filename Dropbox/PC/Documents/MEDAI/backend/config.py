"""
MedAI Configuration Module
Centralized configuration management using Pydantic Settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "MedAI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'medai.db'}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Provider
    LLM_PROVIDER: str = "openai"  # "openai", "ollama", or "groq"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Vector Database
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chromadb")
    CHROMA_COLLECTION: str = "medical_knowledge"

    # JWT Authentication
    JWT_SECRET_KEY: str = "jwt-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ML Models
    MODEL_DIR: str = str(BASE_DIR / "models" / "saved_models")
    DATASET_PATH: str = str(BASE_DIR / "datasets" / "diabetic_data.csv")

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BASE_DIR / "logs" / "medai.log")

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Singleton settings instance
settings = Settings()

# Ensure required directories exist
for dir_path in [
    settings.CHROMA_PERSIST_DIR,
    settings.MODEL_DIR,
    os.path.dirname(settings.LOG_FILE),
    str(BASE_DIR / "data"),
]:
    os.makedirs(dir_path, exist_ok=True)
