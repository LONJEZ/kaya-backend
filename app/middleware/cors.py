"""Enhanced CORS configuration for frontend integration"""
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def setup_cors(app):
    """Configure CORS for production"""
    
    # Get origins from settings and add production domains
    origins = [
        "https://kaya.africainfinityfoundation.org",
        "https://kaya-api.africainfinityfoundation.org",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8007",
    ]
    
    # Add any additional origins from settings
    if hasattr(settings, 'CORS_ORIGINS'):
        for origin in settings.CORS_ORIGINS:
            if origin not in origins:
                origins.append(origin)
    
    print(f"🌐 CORS configured for {len(origins)} origins")
    print(f"   Production: https://kaya.africainfinityfoundation.org")
    
    # Production-ready CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=["*"],  # Allow all headers (simpler and works better)
        expose_headers=["*"],  # Expose all headers
        max_age=3600,  # Cache preflight for 1 hour
    )
