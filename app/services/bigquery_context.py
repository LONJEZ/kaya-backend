"""BigQuery context retrieval for AI agent"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from google.cloud import bigquery
from app.utils.bigquery_client import bq_client
from app.config import settings

logger = logging.getLogger(__name__)


class BigQueryContextRetriever:
    """Retrieve business context from BigQuery for AI responses"""
    
    def __init__(self):
        self.client = bq_client.client
    
    def retrieve_context(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant business data based on user query"""
        
        query_lower = query.lower()
        context = []
        
        try:
            # Determine what data to fetch based on query keywords
            if any(word in query_lower for word in ["revenue", "sales", "total", "earnings", "income"]):
                context.extend(self._get_revenue_context(user_id))
            
            if any(word in query_lower for word in ["product", "item", "selling", "popular", "top"]):
                context.extend(self._get_product_context(user_id))
            
            if any(word in query_lower for word in ["trend", "growth", "monthly", "weekly", "over time"]):
                context.extend(self._get_trend_context(user_id))
            
            if any(word in query_lower for word in ["recent", "latest", "today", "yesterday", "last"]):
                context.extend(self._get_recent_transactions(user_id))
            
            if any(word in query_lower for word in ["category", "categories", "type"]):
                context.extend(self._get_category_context(user_id))
            
            # If no specific query, get overview
            if not context:
                context.extend(self._get_overview_context(user_id))
            
            return context[:top_k]
        
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return [{"type": "error", "message": "Unable to fetch business data"}]
    
    def _get_revenue_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get revenue-related context"""
        query = f"""
        SELECT 
            SUM(amount) as total_revenue,
            COUNT(*) as transaction_count,
            AVG(amount) as avg_transaction
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """
        
        results = list(self.client.query(query).result())
        if results and results[0]['total_revenue']:
            row = results[0]
            return [{
                'type': 'revenue',
                'value': float(row['total_revenue']),
                'transaction_count': int(row['transaction_count']),
                'avg_transaction': float(row['avg_transaction']),
                'period': 'last 30 days'
            }]
        return []
    
    def _get_product_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get top products context"""
        query = f"""
        SELECT 
            item_name,
            category,
            SUM(amount) as sales,
            COUNT(*) as quantity
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY item_name, category
        ORDER BY sales DESC
        LIMIT 5
        """
        
        results = list(self.client.query(query).result())
        products = []
        for row in results:
            products.append({
                'type': 'product',
                'name': row['item_name'],
                'category': row['category'],
                'sales': float(row['sales']),
                'quantity': int(row['quantity'])
            })
        return products
    
    def _get_trend_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get trend context"""
        query = f"""
        SELECT 
            FORMAT_DATE('%Y-%m', date) as month,
            SUM(amount) as revenue
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
        GROUP BY month
        ORDER BY month
        """
        
        results = list(self.client.query(query).result())
        if len(results) >= 2:
            # Calculate growth
            first_month = float(results[0]['revenue'])
            last_month = float(results[-1]['revenue'])
            growth = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
            
            return [{
                'type': 'trend',
                'months': len(results),
                'first_month_revenue': first_month,
                'last_month_revenue': last_month,
                'growth_percentage': round(growth, 1),
                'trend': 'growing' if growth > 0 else 'declining'
            }]
        return []
    
    def _get_recent_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent transactions"""
        query = f"""
        SELECT 
            date,
            item_name,
            amount,
            payment_method
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
        ORDER BY date DESC, timestamp DESC
        LIMIT 5
        """
        
        results = list(self.client.query(query).result())
        transactions = []
        for row in results:
            transactions.append({
                'type': 'transaction',
                'date': row['date'].isoformat(),
                'item': row['item_name'],
                'amount': float(row['amount']),
                'payment_method': row['payment_method']
            })
        return transactions
    
    def _get_category_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get category breakdown"""
        query = f"""
        SELECT 
            category,
            SUM(amount) as sales,
            COUNT(*) as transactions
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
            AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY category
        ORDER BY sales DESC
        LIMIT 5
        """
        
        results = list(self.client.query(query).result())
        categories = []
        for row in results:
            categories.append({
                'type': 'category',
                'category': row['category'],
                'sales': float(row['sales']),
                'transactions': int(row['transactions'])
            })
        return categories
    
    def _get_overview_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get general overview"""
        query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_revenue,
            COUNT(DISTINCT item_name) as unique_products,
            COUNT(DISTINCT category) as unique_categories,
            MIN(date) as first_date,
            MAX(date) as last_date
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = '{user_id}'
        """
        
        results = list(self.client.query(query).result())
        if results and results[0]['total_transactions']:
            row = results[0]
            return [{
                'type': 'overview',
                'total_transactions': int(row['total_transactions']),
                'total_revenue': float(row['total_revenue']),
                'unique_products': int(row['unique_products']),
                'unique_categories': int(row['unique_categories']),
                'first_transaction': row['first_date'].isoformat(),
                'last_transaction': row['last_date'].isoformat()
            }]
        return []


# Global instance
bigquery_context = BigQueryContextRetriever()
