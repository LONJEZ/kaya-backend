"""Combined dashboard endpoint for frontend"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio

from app.auth import verify_token
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/")
async def get_dashboard_data(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get all dashboard data in one request
    Optimized for frontend initial load
    """
    user_id = token.get("sub")
    
    try:
        # Fetch all dashboard data
        overview = analytics_service.get_overview(user_id, days=30)
        revenue_trends = analytics_service.get_revenue_trends(user_id, months=6)
        top_products = analytics_service.get_top_products(user_id, limit=5)
        categories = analytics_service.get_sales_by_category(user_id)
        transactions = analytics_service.get_transactions(user_id, limit=10)
        
        return {
            "overview": overview,
            "revenue_trends": revenue_trends,
            "top_products": top_products,
            "categories": categories,
            "recent_transactions": transactions,
            "timestamp": "2025-10-20T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
