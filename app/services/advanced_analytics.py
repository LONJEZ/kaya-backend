"""Advanced analytics calculations"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from app.utils.bigquery_client import bq_client
from app.config import settings

logger = logging.getLogger(__name__)


class AdvancedAnalytics:
    """Advanced analytics beyond basic metrics"""
    
    @staticmethod
    def get_growth_metrics(user_id: str) -> Dict[str, Any]:
        """Calculate MoM and YoY growth"""
        query = f"""
        WITH monthly_revenue AS (
            SELECT 
                DATE_TRUNC(date, MONTH) as month,
                SUM(amount) as revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 13 MONTH)
            GROUP BY month
        ),
        with_previous AS (
            SELECT 
                month,
                revenue,
                LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
                LAG(revenue, 12) OVER (ORDER BY month) as prev_year_revenue
            FROM monthly_revenue
        )
        SELECT 
            month,
            revenue,
            SAFE_DIVIDE((revenue - prev_month_revenue), prev_month_revenue) * 100 as mom_growth,
            SAFE_DIVIDE((revenue - prev_year_revenue), prev_year_revenue) * 100 as yoy_growth
        FROM with_previous
        WHERE month = DATE_TRUNC(CURRENT_DATE(), MONTH)
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = list(bq_client.client.query(query, job_config=job_config).result())
        
        if not results:
            return {'mom_growth': 0, 'yoy_growth': 0}
        
        row = results[0]
        return {
            'current_month_revenue': float(row['revenue'] or 0),
            'mom_growth': round(float(row['mom_growth'] or 0), 2),
            'yoy_growth': round(float(row['yoy_growth'] or 0), 2)
        }
    
    @staticmethod
    def get_customer_insights(user_id: str) -> Dict[str, Any]:
        """Analyze customer behavior patterns"""
        query = f"""
        WITH transaction_patterns AS (
            SELECT 
                DATE_TRUNC(date, WEEK) as week,
                COUNT(DISTINCT DATE(timestamp)) as active_days,
                COUNT(*) as transactions,
                AVG(amount) as avg_transaction
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 WEEK)
            GROUP BY week
        )
        SELECT 
            AVG(active_days) as avg_active_days_per_week,
            AVG(transactions) as avg_transactions_per_week,
            AVG(avg_transaction) as avg_transaction_value
        FROM transaction_patterns
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = list(bq_client.client.query(query, job_config=job_config).result())
        
        if not results:
            return {}
        
        row = results[0]
        return {
            'avg_active_days_per_week': round(float(row['avg_active_days_per_week'] or 0), 1),
            'avg_transactions_per_week': round(float(row['avg_transactions_per_week'] or 0), 1),
            'avg_transaction_value': round(float(row['avg_transaction_value'] or 0), 2)
        }
    
    @staticmethod
    def get_profit_analysis(user_id: str) -> Dict[str, Any]:
        """Analyze profit margins by category"""
        query = f"""
        SELECT 
            category,
            SUM(amount) as revenue,
            COUNT(*) as transactions,
            AVG(amount) as avg_sale
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY category
        ORDER BY revenue DESC
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        # Estimate profit margins by category
        margin_estimates = {
            'Electronics': 0.20,  # 20% margin
            'Accessories': 0.35,  # 35% margin
            'Other': 0.25
        }
        
        analysis = []
        for row in results:
            category = row['category']
            revenue = float(row['revenue'])
            margin_pct = margin_estimates.get(category, 0.25) * 100
            profit = revenue * margin_estimates.get(category, 0.25)
            
            analysis.append({
                'category': category,
                'revenue': revenue,
                'estimated_profit': profit,
                'margin_percent': margin_pct,
                'transactions': int(row['transactions'])
            })
        
        return {'categories': analysis}

