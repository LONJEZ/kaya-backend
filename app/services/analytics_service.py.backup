"""Analytics service with BigQuery queries and caching"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib
import json
import logging

from google.cloud import bigquery
from app.utils.bigquery_client import bq_client
from app.config import settings

logger = logging.getLogger(__name__)


class AnalyticsCache:
    """Simple in-memory cache for analytics queries"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _get_key(self, query: str, params: Dict) -> str:
        key_str = f"{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, params: Dict) -> Optional[Any]:
        key = self._get_key(query, params)
        cached = self.cache.get(key)
        if cached:
            data, timestamp = cached
            if datetime.utcnow().timestamp() - timestamp < self.ttl:
                logger.info(f"Cache hit: {key[:8]}")
                return data
        return None
    
    def set(self, query: str, params: Dict, data: Any):
        key = self._get_key(query, params)
        self.cache[key] = (data, datetime.utcnow().timestamp())
        logger.info(f"Cache set: {key[:8]}")


class AnalyticsService:
    """Handles all analytics queries with caching"""
    
    def __init__(self):
        self.cache = AnalyticsCache(ttl_seconds=settings.CACHE_TTL_SECONDS)
        self.client = bq_client.client

    def get_overview(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get dashboard overview metrics"""
        params = {'user_id': user_id, 'days': days}
        if settings.ENABLE_CACHE:
            cached = self.cache.get('overview', params)
            if cached:
                return cached
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
        WITH current_period AS (
            SELECT 
                SUM(amount) as total_revenue,
                COUNT(*) as transaction_count,
                COUNT(DISTINCT item_name) as unique_items
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date BETWEEN @start_date AND @end_date
        ),
        previous_period AS (
            SELECT 
                SUM(amount) as prev_revenue
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date BETWEEN DATE_SUB(@start_date, INTERVAL {days} DAY) AND @start_date
        ),
        top_product AS (
            SELECT item_name, SUM(amount) as sales
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
                AND date >= @start_date
            GROUP BY item_name
            ORDER BY sales DESC
            LIMIT 1
        )
        SELECT 
            c.total_revenue,
            c.transaction_count,
            p.prev_revenue,
            t.item_name as top_product,
            SAFE_DIVIDE((c.total_revenue - p.prev_revenue), p.prev_revenue) * 100 as revenue_growth
        FROM current_period c
        CROSS JOIN previous_period p
        CROSS JOIN top_product t
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('start_date', 'DATE', start_date),
                bigquery.ScalarQueryParameter('end_date', 'DATE', end_date),
            ]
        )
        
        results = list(self.client.query(query, job_config=job_config).result())
        if not results:
            return {
                'total_revenue': 0,
                'total_expenses': 0,
                'profit_margin': 0,
                'top_product': None,
                'period': f'last_{days}_days'
            }
        
        row = results[0]
        total_revenue = float(row['total_revenue'] or 0)
        total_expenses = total_revenue * 0.45
        profit_margin = ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0
        
        result = {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'profit_margin': round(profit_margin, 1),
            'top_product': row['top_product'],
            'revenue_growth': round(float(row['revenue_growth'] or 0), 1),
            'period': f'last_{days}_days'
        }
        
        if settings.ENABLE_CACHE:
            self.cache.set('overview', params, result)
        return result

    def get_revenue_trends(self, user_id: str, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly revenue trends"""
        params = {'user_id': user_id, 'months': months}
        if settings.ENABLE_CACHE:
            cached = self.cache.get('revenue_trends', params)
            if cached:
                return cached
        
        query = f"""
        SELECT 
            FORMAT_DATE('%b', date) as month,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @months MONTH)
        GROUP BY month, EXTRACT(MONTH FROM date)
        ORDER BY EXTRACT(MONTH FROM date)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('months', 'INT64', months),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        trends = [{'month': row['month'], 'revenue': float(row['revenue'])} for row in results]
        
        if settings.ENABLE_CACHE:
            self.cache.set('revenue_trends', params, trends)
        return trends

    def get_top_products(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products"""
        params = {'user_id': user_id, 'limit': limit}
        if settings.ENABLE_CACHE:
            cached = self.cache.get('top_products', params)
            if cached:
                return cached
        
        query = f"""
        SELECT 
            item_name as name,
            category,
            SUM(amount) as sales,
            COUNT(*) as quantity
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY name, category
        ORDER BY sales DESC
        LIMIT @limit
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('limit', 'INT64', limit),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        products = [
            {'name': row['name'], 'category': row['category'], 'sales': float(row['sales']), 'quantity': int(row['quantity'])}
            for row in results
        ]
        
        if settings.ENABLE_CACHE:
            self.cache.set('top_products', params, products)
        return products

    def get_sales_by_category(self, user_id: str) -> List[Dict[str, Any]]:
        """Get sales breakdown by category"""
        params = {'user_id': user_id}
        if settings.ENABLE_CACHE:
            cached = self.cache.get('sales_by_category', params)
            if cached:
                return cached
        
        query = f"""
        SELECT 
            category,
            SUM(amount) as sales,
            COUNT(*) as transaction_count
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY category
        ORDER BY sales DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        categories = [
            {'category': row['category'], 'sales': float(row['sales']), 'count': int(row['transaction_count'])}
            for row in results
        ]
        
        if settings.ENABLE_CACHE:
            self.cache.set('sales_by_category', params, categories)
        return categories

    def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get recent transactions with pagination"""
        params = {'user_id': user_id, 'limit': limit, 'offset': offset}
        if settings.ENABLE_CACHE:
            cached = self.cache.get('transactions', params)
            if cached:
                return cached
        
        query = f"""
        SELECT 
            id,
            date,
            item_name as item,
            amount,
            payment_method as method
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
        ORDER BY date DESC, timestamp DESC
        LIMIT @limit
        OFFSET @offset
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
                bigquery.ScalarQueryParameter('limit', 'INT64', limit),
                bigquery.ScalarQueryParameter('offset', 'INT64', offset),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        transactions = [
            {
                'id': row['id'],
                'date': row['date'].isoformat(),
                'item': row['item'],
                'amount': float(row['amount']),
                'method': row['method']
            }
            for row in results
        ]
        
        if settings.ENABLE_CACHE:
            self.cache.set('transactions', params, transactions)
        return transactions

    def get_payment_methods_breakdown(self, user_id: str) -> List[Dict[str, Any]]:
        """Get transaction breakdown by payment method"""
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
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        return [
            {'method': row['payment_method'], 'count': int(row['count']), 'total': float(row['total'])}
            for row in results
        ]


# Initialize service
analytics_service = AnalyticsService()
