from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from app.api import cache, advanced_analytics as adv_analytics
from app.middleware.performance import PerformanceMiddleware
import time

from app.config import settings
from app.api import analytics, chat, settings as settings_api
from app.auth import verify_token
from app.api import ingestion
from app.api import connectors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Kaya AI Backend starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"BigQuery Project: {settings.GCP_PROJECT_ID}")
    yield
    logger.info("👋 Kaya AI Backend shutting down...")


app = FastAPI(
    title="Kaya AI Backend",
    description="Smart Business Assistant API for African SMEs",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PerformanceMiddleware)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Data Ingestion"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache Management"])
app.include_router(adv_analytics.router, prefix="/api/analytics/advanced", tags=["Advanced Analytics"])




@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kaya AI Backend",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/protected")
async def protected_route(token: dict = Depends(verify_token)):
    """Example protected route"""
    return {
        "message": "This is a protected route",
        "user_id": token.get("sub"),
        "business_name": token.get("business_name")
    }
