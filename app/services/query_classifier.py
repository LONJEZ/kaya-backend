"""Classify user queries for better context retrieval"""

from typing import Dict, Any
from enum import Enum


class QueryType(Enum):
    TOP_PRODUCTS = "top_products"
    REVENUE = "revenue"
    CATEGORIES = "categories"
    PAYMENT_METHODS = "payment_methods"
    TRENDS = "trends"
    COMPARISON = "comparison"
    OVERVIEW = "overview"
    UNKNOWN = "unknown"


class QueryClassifier:
    """Classify natural language queries"""
    
    KEYWORDS = {
        QueryType.TOP_PRODUCTS: ['top', 'best', 'popular', 'selling', 'highest', 'most sold'],
        QueryType.REVENUE: ['revenue', 'sales', 'money', 'earned', 'income', 'profit'],
        QueryType.CATEGORIES: ['category', 'categories', 'type', 'types', 'breakdown'],
        QueryType.PAYMENT_METHODS: ['payment', 'mpesa', 'cash', 'card', 'method', 'how paid'],
        QueryType.TRENDS: ['trend', 'over time', 'monthly', 'growth', 'change'],
        QueryType.COMPARISON: ['compare', 'vs', 'versus', 'difference', 'last month', 'last quarter'],
        QueryType.OVERVIEW: ['overview', 'summary', 'overall', 'general', 'everything'],
    }
    
    def classify(self, query: str) -> QueryType:
        """Classify query type"""
        query_lower = query.lower()
        
        # Score each type
        scores = {}
        for query_type, keywords in self.KEYWORDS.items():
            scores[query_type] = sum(1 for keyword in keywords if keyword in query_lower)
        
        # Get highest score
        max_type = max(scores, key=scores.get)
        
        if scores[max_type] > 0:
            return max_type
        
        return QueryType.UNKNOWN
    
    def extract_time_period(self, query: str) -> Dict[str, Any]:
        """Extract time period from query"""
        query_lower = query.lower()
        
        if 'today' in query_lower:
            return {'period': 'today', 'days': 1}
        elif 'week' in query_lower or 'last 7 days' in query_lower:
            return {'period': 'week', 'days': 7}
        elif 'month' in query_lower or 'last 30 days' in query_lower:
            return {'period': 'month', 'days': 30}
        elif 'quarter' in query_lower:
            return {'period': 'quarter', 'days': 90}
        elif 'year' in query_lower:
            return {'period': 'year', 'days': 365}
        else:
            return {'period': 'default', 'days': 30}


query_classifier = QueryClassifier()

