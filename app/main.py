from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.middleware.cors import setup_cors
from app.middleware.performance import PerformanceMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_tracking import ErrorTrackingMiddleware

# Import all routers
from app.api import (
    analytics, 
    chat, 
    settings as settings_api,
    ingestion,
    connectors,
    cache,
    advanced_analytics as adv_analytics,
    auth as auth_api,
    dashboard,   
    websocket,      
    admin,           
    data_quality,     
    monitoring
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Kaya AI Backend starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Project: {settings.GCP_PROJECT_ID}")
    
    # Initialize services
    try:
        from app.utils.bigquery_client import bq_client
        logger.info("✅ BigQuery client initialized")
    except Exception as e:
        logger.warning(f"⚠️  BigQuery initialization warning: {e}")
    
    yield
    
    logger.info("👋 Kaya AI Backend shutting down...")


# Create app
app = FastAPI(
    title="Kaya AI Backend",
    description="Smart Business Assistant API for African SMEs",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS
setup_cors(app)

# Add middleware (order matters!)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorTrackingMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Include routers
app.include_router(auth_api.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(adv_analytics.router, prefix="/api/analytics/advanced", tags=["Advanced Analytics"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Data Ingestion"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(data_quality.router, prefix="/api/data-quality", tags=["Data Quality"])





@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kaya AI Backend",
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check for load balancers"""
    return {
        "status": "healthy",
        "timestamp": "2025-10-20T00:00:00Z",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )
