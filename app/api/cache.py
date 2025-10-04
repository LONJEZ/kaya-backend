"""Cache management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.auth import verify_token
from app.services.advanced_analytics import AdvancedAnalytics

router = APIRouter()
advanced_analytics = AdvancedAnalytics()


@router.get("/growth-metrics")
async def get_growth_metrics(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """Get MoM and YoY growth metrics"""
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_growth_metrics(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer-insights")
async def get_customer_insights(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """Get customer behavior insights"""
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_customer_insights(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profit-analysis")
async def get_profit_analysis(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """Get profit analysis by category"""
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_profit_analysis(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
