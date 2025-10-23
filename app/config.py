"""Application configuration"""
import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Kaya AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Cloud (for BigQuery only)
    GCP_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # BigQuery
    BIGQUERY_DATASET: str = "kaya_data"
    
    # Google AI Studio (FREE - no billing!)
    GEMINI_API_KEY: str = ""  # Get from https://aistudio.google.com/app/apikey
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Search/Retrieval
    MAX_CONTEXT_CHUNKS: int = 5
    CACHE_TTL_SECONDS: int = 300  # 5 minutes cache
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Performance & Caching - ADDED THESE!
    ENABLE_CACHE: bool = True  # ← FIX: Add this
    CHAT_TIMEOUT_SECONDS: int = 30  # ← FIX: Add this
    
    # Feature Flags - ADDED THESE!
    ENABLE_AI_CHAT: bool = True  # ← FIX: Add this
    ENABLE_ADVANCED_ANALYTICS: bool = True  # ← FIX: Add this
    ENABLE_WEBSOCKET: bool = True  # ← FIX: Add this
    
    # CORS - Support both naming conventions
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8007",
        "https://kaya.africainfinityfoundation.org",
        "https://kaya-api.africainfinityfoundation.org",
        "https://kaya-ai.vercel.app",
        "https://*.vercel.app",
    ]
    
    # Alias for CORS (for backward compatibility with cors.py)
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Alias for CORS_ORIGINS to support cors.py middleware"""
        return self.CORS_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Warning if GEMINI_API_KEY not set
if not settings.GEMINI_API_KEY:
    print("⚠️  GEMINI_API_KEY not set. Chat will use fallback responses.")
    print("   Get your FREE API key: https://aistudio.google.com/app/apikey")
