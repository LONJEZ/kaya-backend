"""Advanced analytics endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.auth import verify_token
from app.services.advanced_analytics import AdvancedAnalytics
from app.utils.bigquery_client import bq_client
from app.config import settings

router = APIRouter()
advanced_analytics = AdvancedAnalytics()


@router.get("/growth-metrics")
async def get_growth_metrics(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get MoM and YoY growth metrics
    
    Returns current month revenue with growth percentages
    """
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_growth_metrics(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer-insights")
async def get_customer_insights(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get customer behavior insights
    
    Returns transaction patterns and average values
    """
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_customer_insights(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profit-analysis")
async def get_profit_analysis(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get profit analysis by category
    
    Returns estimated profit margins for each category
    """
    user_id = token.get("sub")
    
    try:
        return advanced_analytics.get_profit_analysis(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cohort-analysis")
async def get_cohort_analysis(
    period: str = Query("month", regex="^(day|week|month)$"),
    token: dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get cohort analysis for customer retention
    
    Args:
        period: Cohort period (day, week, or month)
    """
    user_id = token.get("sub")
    
    try:
        query = f"""
        WITH first_purchase AS (
            SELECT 
                user_id,
                MIN(date) as first_purchase_date
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
            GROUP BY user_id
        ),
        cohorts AS (
            SELECT 
                DATE_TRUNC(f.first_purchase_date, {period.upper()}) as cohort,
                COUNT(DISTINCT t.id) as transactions,
                SUM(t.amount) as revenue
            FROM first_purchase f
            JOIN `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions` t
                ON f.user_id = t.user_id
            GROUP BY cohort
        )
        SELECT * FROM cohorts ORDER BY cohort DESC LIMIT 12
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        cohorts = [
            {
                'cohort': str(row['cohort']),
                'transactions': int(row['transactions']),
                'revenue': float(row['revenue'])
            }
            for row in results
        ]
        
        return {
            'period': period,
            'cohorts': cohorts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-forecast")
async def get_revenue_forecast(
    months: int = Query(3, ge=1, le=12),
    token: dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Simple revenue forecast using linear regression
    
    Args:
        months: Number of months to forecast
    """
    user_id = token.get("sub")
    
    try:
        # Get historical data
        query = f"""
        SELECT 
            DATE_TRUNC(date, MONTH) as month,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY month
        ORDER BY month
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = list(bq_client.client.query(query, job_config=job_config).result())
        
        if len(results) < 3:
            return {
                'forecast': [],
                'message': 'Insufficient historical data for forecast'
            }
        
        # Simple linear regression
        import statistics
        revenues = [float(r['revenue']) for r in results]
        avg_growth = statistics.mean([
            (revenues[i] - revenues[i-1]) / revenues[i-1] * 100
            for i in range(1, len(revenues))
        ])
        
        # Generate forecast
        last_revenue = revenues[-1]
        forecast = []
        
        for i in range(1, months + 1):
            projected = last_revenue * (1 + avg_growth/100) ** i
            forecast.append({
                'month': f"Month +{i}",
                'projected_revenue': round(projected, 2),
                'confidence': 'medium' if i <= 3 else 'low'
            })
        
        return {
            'historical_growth_rate': round(avg_growth, 2),
            'forecast': forecast,
            'note': 'Simple projection based on historical growth'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-performance")
async def get_product_performance(
    limit: int = Query(20, ge=1, le=100),
    token: dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Detailed product performance analysis
    
    Returns products with sales velocity, trend, and ranking
    """
    user_id = token.get("sub")
    
    try:
        query = f"""
        WITH current_period AS (
            SELECT 
                item_name,
                COUNT(*) as current_count,
                SUM(amount) as current_revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            GROUP BY item_name
        ),
        previous_period AS (
            SELECT 
                item_name,
                COUNT(*) as previous_count,
                SUM(amount) as previous_revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
                AND date < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            GROUP BY item_name
        )
        SELECT 
            c.item_name,
            c.current_revenue,
            c.current_count,
            IFNULL(p.previous_revenue, 0) as previous_revenue,
            SAFE_DIVIDE(
                (c.current_revenue - IFNULL(p.previous_revenue, 0)), 
                IFNULL(p.previous_revenue, 1)
            ) * 100 as growth_percent,
            CASE 
                WHEN SAFE_DIVIDE(c.current_revenue, IFNULL(p.previous_revenue, 1)) > 1.2 THEN 'rising'
                WHEN SAFE_DIVIDE(c.current_revenue, IFNULL(p.previous_revenue, 1)) < 0.8 THEN 'falling'
                ELSE 'stable'
            END as trend
        FROM current_period c
        LEFT JOIN previous_period p ON c.item_name = p.item_name
        ORDER BY c.current_revenue DESC
        LIMIT @limit
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('limit', 'INT64', limit)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        products = [
            {
                'name': row['item_name'],
                'current_revenue': float(row['current_revenue']),
                'transaction_count': int(row['current_count']),
                'growth_percent': round(float(row['growth_percent'] or 0), 2),
                'trend': row['trend']
            }
            for row in results
        ]
        
        return {
            'products': products,
            'period': 'last_30_days'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasonal-analysis")
async def get_seasonal_analysis(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Analyze seasonal patterns in sales
    
    Returns day-of-week and hour-of-day patterns
    """
    user_id = token.get("sub")
    
    try:
        # Day of week analysis
        dow_query = f"""
        SELECT 
            FORMAT_DATE('%A', date) as day_of_week,
            EXTRACT(DAYOFWEEK FROM date) as dow_num,
            COUNT(*) as transactions,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY day_of_week, dow_num
        ORDER BY dow_num
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        dow_results = bq_client.client.query(dow_query, job_config=job_config).result()
        
        by_day = [
            {
                'day': row['day_of_week'],
                'transactions': int(row['transactions']),
                'revenue': float(row['revenue'])
            }
            for row in dow_results
        ]
        
        # Hour of day analysis (if timestamp available)
        hour_query = f"""
        SELECT 
            EXTRACT(HOUR FROM timestamp) as hour,
            COUNT(*) as transactions,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            AND timestamp IS NOT NULL
        GROUP BY hour
        ORDER BY hour
        """
        
        hour_results = bq_client.client.query(hour_query, job_config=job_config).result()
        
        by_hour = [
            {
                'hour': int(row['hour']),
                'transactions': int(row['transactions']),
                'revenue': float(row['revenue'])
            }
            for row in hour_results
        ]
        
        return {
            'by_day_of_week': by_day,
            'by_hour_of_day': by_hour,
            'analysis_period': '90_days'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer-segments")
async def get_customer_segments(token: dict = Depends(verify_token)) -> Dict[str, Any]:
    """
    Segment customers by value
    
    Returns high-value, medium-value, and low-value segments
    """
    user_id = token.get("sub")
    
    try:
        query = f"""
        WITH customer_stats AS (
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_spent,
                AVG(amount) as avg_transaction
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        )
        SELECT 
            CASE 
                WHEN total_spent > (SELECT AVG(total_spent) * 1.5 FROM customer_stats) THEN 'high_value'
                WHEN total_spent > (SELECT AVG(total_spent) * 0.5 FROM customer_stats) THEN 'medium_value'
                ELSE 'low_value'
            END as segment,
            COUNT(*) as customer_count
        FROM customer_stats
        GROUP BY segment
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        segments = {row['segment']: int(row['customer_count']) for row in results}
        
        return {
            'segments': segments,
            'total_customers': sum(segments.values()),
            'period': 'last_90_days'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory-velocity")
async def get_inventory_velocity(
    limit: int = Query(10, ge=1, le=50),
    token: dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Calculate inventory turnover velocity
    
    Returns products with their sales velocity
    """
    user_id = token.get("sub")
    
    try:
        query = f"""
        SELECT 
            item_name,
            COUNT(*) as units_sold,
            SUM(amount) as revenue,
            COUNT(*) / 30.0 as units_per_day,
            category
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY item_name, category
        ORDER BY units_per_day DESC
        LIMIT @limit
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('limit', 'INT64', limit)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        products = [
            {
                'name': row['item_name'],
                'category': row['category'],
                'units_sold': int(row['units_sold']),
                'revenue': float(row['revenue']),
                'velocity_per_day': round(float(row['units_per_day']), 2),
                'velocity_category': (
                    'fast_moving' if row['units_per_day'] > 3 else
                    'medium_moving' if row['units_per_day'] > 1 else
                    'slow_moving'
                )
            }
            for row in results
        ]
        
        return {
            'products': products,
            'period': 'last_30_days'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
