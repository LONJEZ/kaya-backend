from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.schemas import (
    AnalyticsOverview,
    RevenueTrend,
    TopProduct,
    Transaction,
    CategorySales
)
from app.auth import verify_token
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    token: dict = Depends(verify_token)
):
    """Get analytics overview for dashboard"""
    user_id = token.get("sub")
    
    try:
        data = analytics_service.get_overview(user_id, days)
        return AnalyticsOverview(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-trends", response_model=List[RevenueTrend])
async def get_revenue_trends(
    months: int = Query(6, ge=1, le=12),
    token: dict = Depends(verify_token)
):
    """Get revenue trends over time"""
    user_id = token.get("sub")
    
    try:
        return analytics_service.get_revenue_trends(user_id, months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    token: dict = Depends(verify_token)
):
    """Get top selling products"""
    user_id = token.get("sub")
    
    try:
        return analytics_service.get_top_products(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-sales", response_model=List[CategorySales])
async def get_category_sales(token: dict = Depends(verify_token)):
    """Get sales breakdown by category"""
    user_id = token.get("sub")
    
    try:
        return analytics_service.get_sales_by_category(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(verify_token)
):
    """Get recent transactions with pagination"""
    user_id = token.get("sub")
    
    try:
        return analytics_service.get_transactions(user_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-methods")
async def get_payment_methods(token: dict = Depends(verify_token)):
    """Get breakdown by payment method"""
    user_id = token.get("sub")
    
    try:
        return analytics_service.get_payment_methods_breakdown(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

