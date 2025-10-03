from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta

from app.models.schemas import (
    AnalyticsOverview,
    RevenueTrend,
    TopProduct,
    Transaction
)
from app.auth import verify_token
from app.utils.bigquery_client import bq_client

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(token: dict = Depends(verify_token)):
    """Get analytics overview for dashboard"""
    user_id = token.get("sub")
    
    # TODO: Implement real BigQuery queries in Phase 3
    # For now, return mock data
    return AnalyticsOverview(
        total_revenue=328000.0,
        total_expenses=145000.0,
        profit_margin=55.8,
        top_product="iPhone 15",
        period="last_30_days"
    )


@router.get("/revenue-trends", response_model=List[RevenueTrend])
async def get_revenue_trends(token: dict = Depends(verify_token)):
    """Get revenue trends over time"""
    user_id = token.get("sub")
    
    # TODO: Implement real BigQuery queries
    return [
        RevenueTrend(month="Jan", revenue=45000),
        RevenueTrend(month="Feb", revenue=52000),
        RevenueTrend(month="Mar", revenue=48000),
        RevenueTrend(month="Apr", revenue=61000),
        RevenueTrend(month="May", revenue=55000),
        RevenueTrend(month="Jun", revenue=67000),
    ]


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(token: dict = Depends(verify_token)):
    """Get top selling products"""
    user_id = token.get("sub")
    
    # TODO: Implement real BigQuery queries
    return [
        TopProduct(name="iPhone 15 Pro", category="Electronics", sales=55000, quantity=5),
        TopProduct(name="Laptop", category="Electronics", sales=45000, quantity=3),
        TopProduct(name="Bluetooth Speaker", category="Electronics", sales=12000, quantity=15),
    ]


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(token: dict = Depends(verify_token)):
    """Get recent transactions"""
    user_id = token.get("sub")
    
    # TODO: Implement real BigQuery queries
    return [
        Transaction(id="1", date="2025-10-01", item="iPhone 15 Pro", amount=55000, method="M-Pesa"),
        Transaction(id="2", date="2025-10-01", item="Laptop Repair", amount=8500, method="Cash"),
        Transaction(id="3", date="2025-09-30", item="Bluetooth Speaker", amount=3200, method="Card"),
    ]
