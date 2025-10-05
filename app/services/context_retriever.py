"""Retrieve relevant context for chat queries"""

from typing import List, Dict, Any
import logging

from app.utils.bigquery_client import bq_client
from app.config import settings

logger = logging.getLogger(__name__)


class ContextRetriever:
    """Retrieve relevant data context for queries"""
    
    def retrieve_context(
        self,
        user_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using hybrid search
        
        Strategy:
        1. Keyword matching on query
        2. Recent data (time-weighted)
        3. Aggregate statistics
        """
        
        # Extract intent from query
        query_lower = query.lower()
        
        # Determine context type
        if any(word in query_lower for word in ['top', 'best', 'popular', 'selling']):
            return self._get_top_products_context(user_id)
        
        elif any(word in query_lower for word in ['revenue', 'sales', 'money', 'earned']):
            return self._get_revenue_context(user_id, query_lower)
        
        elif any(word in query_lower for word in ['category', 'categories']):
            return self._get_category_context(user_id)
        
        elif any(word in query_lower for word in ['payment', 'mpesa', 'cash', 'method']):
            return self._get_payment_context(user_id)
        
        elif any(word in query_lower for word in ['growth', 'trend', 'change', 'compare']):
            return self._get_trend_context(user_id)
        
        else:
            # Default: overview context
            return self._get_overview_context(user_id)
    
    def _get_top_products_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get top products data"""
        query = f"""
        SELECT 
            item_name,
            category,
            SUM(amount) as total_sales,
            COUNT(*) as transaction_count
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY item_name, category
        ORDER BY total_sales DESC
        LIMIT 5
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        return [{
            'type': 'top_products',
            'data': [dict(row) for row in results]
        }]
    
    def _get_revenue_context(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Get revenue data with time period detection"""
        
        # Detect time period
        if 'month' in query or 'last month' in query:
            days = 30
            period = 'last_month'
        elif 'quarter' in query:
            days = 90
            period = 'last_quarter'
        elif 'year' in query:
            days = 365
            period = 'last_year'
        else:
            days = 30
            period = 'last_30_days'
        
        query_sql = f"""
        WITH current_period AS (
            SELECT SUM(amount) as revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        ),
        previous_period AS (
            SELECT SUM(amount) as prev_revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days*2 DAY)
                AND date < DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        )
        SELECT 
            c.revenue,
            p.prev_revenue,
            SAFE_DIVIDE((c.revenue - p.prev_revenue), p.prev_revenue) * 100 as growth_percent
        FROM current_period c
        CROSS JOIN previous_period p
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('days', 'INT64', days)
            ]
        )
        
        results = list(bq_client.client.query(query_sql, job_config=job_config).result())
        
        return [{
            'type': 'revenue',
            'period': period,
            'data': dict(results[0]) if results else {}
        }]
    
    def _get_category_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get category breakdown"""
        query = f"""
        SELECT 
            category,
            SUM(amount) as sales,
            COUNT(*) as transactions
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY category
        ORDER BY sales DESC
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        return [{
            'type': 'categories',
            'data': [dict(row) for row in results]
        }]
    
    def _get_payment_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get payment method breakdown"""
        query = f"""
        SELECT 
            payment_method,
            COUNT(*) as count,
            SUM(amount) as total
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY payment_method
        ORDER BY total DESC
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        return [{
            'type': 'payment_methods',
            'data': [dict(row) for row in results]
        }]
    
    def _get_trend_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get trend data"""
        query = f"""
        SELECT 
            FORMAT_DATE('%Y-%m', date) as month,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
        GROUP BY month
        ORDER BY month
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = bq_client.client.query(query, job_config=job_config).result()
        
        return [{
            'type': 'trends',
            'data': [dict(row) for row in results]
        }]
    
    def _get_overview_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get general overview"""
        query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_transaction,
            COUNT(DISTINCT item_name) as unique_products
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
            ]
        )
        
        results = list(bq_client.client.query(query, job_config=job_config).result())
        
        return [{
            'type': 'overview',
            'data': dict(results[0]) if results else {}
        }]


context_retriever = ContextRetriever()

