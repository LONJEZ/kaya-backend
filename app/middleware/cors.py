"""Enhanced CORS configuration for frontend integration"""

from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def setup_cors(app):
    """Configure CORS for production"""
    
    # Get origins - support both ALLOWED_ORIGINS and CORS_ORIGINS
    origins = getattr(settings, 'ALLOWED_ORIGINS', None) or settings.CORS_ORIGINS
    
    # Production-ready CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Requested-With",
        ],
        expose_headers=["X-Process-Time", "X-Request-ID"],
        max_age=3600,  # Cache preflight for 1 hour
    )