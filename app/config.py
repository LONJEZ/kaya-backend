from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    VERSION: str = "2.0.0"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Kaya AI Backend"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8007",
        "https://kaya-ai.vercel.app",
        "https://*.vercel.app",
    ]
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # GCP
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "kaya-ai-demo")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "kaya_data")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Vertex AI
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-1.5-pro"
    
    # Performance
    ENABLE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 300
    CHAT_TIMEOUT_SECONDS: int = 3
    MAX_CONTEXT_CHUNKS: int = 5
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Feature Flags (default enabled)
    ENABLE_AI_CHAT: bool = True
    ENABLE_ADVANCED_ANALYTICS: bool = True
    ENABLE_WEBSOCKET: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

