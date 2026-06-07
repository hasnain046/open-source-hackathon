# Module: app.config
# Description: Global configuration settings parsed from environment variables.

from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "InflationIQ – AI Economic Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & Tokens
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Relational Databases
    DATABASE_URL: str

    # Caches & Queues
    REDIS_URL: Optional[str] = None

    # AI Model Settings & Integrations
    GEMINI_API_KEY: Optional[str] = None
    VECTOR_DB_URL: Optional[str] = None

    # Ingest Gateways Keys
    FRED_API_KEY: Optional[str] = None
    BLS_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    GOOGLE_TRENDS_KEYWORDS: List[str] = ["inflation", "price hike", "vegetable prices", "gold rate", "repo rate"]

    # RAG Knowledge Base Settings (Phase 12)
    CHROMA_PERSIST_DIR: str = "./chroma_store"
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 5
    RAG_MIN_SCORE: float = 0.35
    RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RAG_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RAG_DOCUMENT_STORE: str = "./rag_documents"
    RAG_CONFIDENCE_HIGH: float = 0.75
    RAG_CONFIDENCE_MEDIUM: float = 0.50
    RAG_FRESHNESS_ENABLED: bool = True
    RAG_FRESHNESS_WEIGHT: float = 0.15
    RAG_FRESHNESS_DECAY_RATE: float = 0.002
    RAG_FRESHNESS_DELTA: float = 0.05

    # Email Integration Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    ALERT_FROM_EMAIL: str = "alerts@inflationiq.ai"
    ALERT_FROM_NAME: str = "InflationIQ Alert System"
    SENDGRID_API_KEY: Optional[str] = None

    # Telegram Integration Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_USERNAME: str = "@InflationIQ_Bot"

    # WhatsApp Integration Settings
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_API_VERSION: str = "v18.0"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_FROM: Optional[str] = None

    # Alert Engine Settings
    ALERT_EVAL_INTERVAL_MINUTES: int = 15
    ALERT_MAX_RETRIES: int = 5
    ALERT_BASE_RETRY_DELAY_MIN: int = 5
    ALERT_DAILY_LIMIT_DEFAULT: int = 20
    ALERT_LOG_RETENTION_DAYS: int = 90

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )


settings = Settings(_env_file="D:/open-source hackathon/backend/.env.template") # Fallback to template for skeleton compile checks
