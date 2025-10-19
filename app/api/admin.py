"""Admin endpoints for system management"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.auth import verify_token
from app.services.monitoring import metrics_collector
from app.services.error_tracker import error_tracker
from app.services.feature_flags import feature_flags, Feature
from app.utils.bigquery_client import bq_client
from app.config import settings

router = APIRouter()


def verify_admin(token: dict = Depends(verify_token)):
    """Verify admin privileges"""
    # TODO: Implement proper admin check
    # For now, accept any valid token
    return token


@router.get("/system/stats")
async def get_system_stats(token: dict = Depends(verify_admin)) -> Dict[str, Any]:
    """Get comprehensive system statistics"""
    
    # Get metrics
    metrics = metrics_collector.get_summary()
    
    # Get error summary
    errors = error_tracker.get_error_summary()
    
    # Get BigQuery stats
    try:
        query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT user_id) as total_users,
            SUM(amount) as total_revenue,
            MIN(date) as earliest_date,
            MAX(date) as latest_date
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        """
        bq_stats = bq_client.query(query)[0] if bq_client.query(query) else {}
    except Exception as e:
        bq_stats = {"error": str(e)}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "errors": errors,
        "database": bq_stats,
        "feature_flags": {f.value: feature_flags.is_enabled(f) for f in Feature},
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }


@router.post("/feature-flags/{feature}/enable")
async def enable_feature(
    feature: str,
    user_id: str = None,
    token: dict = Depends(verify_admin)
):
    """Enable a feature flag"""
    try:
        feature_enum = Feature(feature)
        feature_flags.enable(feature_enum, user_id)
        return {"status": "enabled", "feature": feature, "user_id": user_id}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")


@router.post("/feature-flags/{feature}/disable")
async def disable_feature(
    feature: str,
    user_id: str = None,
    token: dict = Depends(verify_admin)
):
    """Disable a feature flag"""
    try:
        feature_enum = Feature(feature)
        feature_flags.disable(feature_enum, user_id)
        return {"status": "disabled", "feature": feature, "user_id": user_id}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")


@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = 50,
    token: dict = Depends(verify_admin)
):
    """Get recent errors"""
    return {
        "errors": error_tracker.get_recent_errors(limit),
        "summary": error_tracker.get_error_summary()
    }


@router.post("/cache/warm")
async def warm_cache(token: dict = Depends(verify_admin)):
    """Pre-warm cache with common queries"""
    from app.services.analytics_service import analytics_service
    
    # Get all users
    query = f"""
    SELECT DISTINCT user_id 
    FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
    LIMIT 100
    """
    
    users = bq_client.query(query)
    warmed = 0
    
    for user in users:
        user_id = user['user_id']
        try:
            # Warm common queries
            analytics_service.get_overview(user_id, days=30)
            analytics_service.get_revenue_trends(user_id, months=6)
            analytics_service.get_top_products(user_id, limit=10)
            warmed += 1
        except Exception:
            continue
    
    return {"status": "complete", "users_warmed": warmed}


@router.post("/maintenance/mode")
async def toggle_maintenance_mode(
    enabled: bool,
    token: dict = Depends(verify_admin)
):
    """Toggle maintenance mode"""
    # TODO: Implement maintenance mode flag
    return {"maintenance_mode": enabled}

