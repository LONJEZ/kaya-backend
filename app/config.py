from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Kaya AI Backend"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://kaya-ai.vercel.app"
    ]
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google Cloud Platform
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "kaya-474008")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "kaya_data")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Vertex AI
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-1.5-pro"
    
    # Elastic Search (optional, fallback to BigQuery)
    ELASTIC_CLOUD_ID: str = os.getenv("ELASTIC_CLOUD_ID", "")
    ELASTIC_API_KEY: str = os.getenv("ELASTIC_API_KEY", "")
    
    # Cache
    ENABLE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Performance
    CHAT_TIMEOUT_SECONDS: int = 3
    MAX_CONTEXT_CHUNKS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
