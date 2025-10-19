"""Monitoring and health check endpoints"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime

from app.auth import verify_token
from app.services.monitoring import metrics_collector
from app.utils.bigquery_client import bq_client
from app.config import settings

router = APIRouter()


@router.get("/metrics")
async def get_metrics(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """Get application metrics"""
    return metrics_collector.get_summary()


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status"""
    
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Check BigQuery
    try:
        query = f"SELECT 1 as test"
        bq_client.query(query)
        health["services"]["bigquery"] = {"status": "up"}
    except Exception as e:
        health["services"]["bigquery"] = {"status": "down", "error": str(e)}
        health["status"] = "degraded"
    
    # Check Vertex AI
    try:
        from app.services.gemini_service import gemini_service
        health["services"]["vertex_ai"] = {"status": "up"}
    except Exception as e:
        health["services"]["vertex_ai"] = {"status": "down", "error": str(e)}
        health["status"] = "degraded"
    
    # Check cache
    from app.services.analytics_service import analytics_service
    health["services"]["cache"] = {
        "status": "up",
        "entries": len(analytics_service.cache.cache)
    }
    
    return health


@router.get("/health/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Check if app is ready to serve traffic
    try:
        # Test BigQuery connection
        query = "SELECT 1"
        bq_client.query(query)
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503


@router.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    # Simple check that app is running
    return {"status": "alive"}

