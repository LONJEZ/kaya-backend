"""Fallback mechanisms when Gemini/Elastic unavailable"""

from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)


class ChatFallback:
    """Rule-based fallback for chat when AI services unavailable"""
    
    def generate_fallback_response(
        self,
        query: str,
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate response using templates"""
        
        query_lower = query.lower()
        
        # Top products query
        if any(word in query_lower for word in ['top', 'best', 'popular']):
            return self._handle_top_products(context)
        
        # Revenue query
        elif any(word in query_lower for word in ['revenue', 'sales', 'earned']):
            return self._handle_revenue(context)
        
        # Category query
        elif 'category' in query_lower or 'categories' in query_lower:
            return self._handle_categories(context)
        
        # Growth/comparison query
        elif any(word in query_lower for word in ['growth', 'change', 'compare']):
            return self._handle_growth(context)
        
        # Default
        else:
            return self._handle_default(context)
    
    def _handle_top_products(self, context: List[Dict]) -> Dict[str, Any]:
        """Handle top products query"""
        if not context or not context[0].get('data'):
            return self._empty_response()
        
        data = context[0]['data']
        if not isinstance(data, list) or not data:
            return self._empty_response()
        
        top_item = data[0]
        answer = f"Your top-selling product is {top_item['item_name']} with KES {top_item['total_sales']:,.0f} in sales from {top_item['transaction_count']} transactions."
        
        return {
            "answer_text": answer,
            "confidence": 0.9,
            "visualization": {
                "type": "bar_chart",
                "data": [{"name": item['item_name'], "value": float(item['total_sales'])} for item in data[:5]]
            },
            "structured": {
                "top_product": top_item['item_name'],
                "total_sales": float(top_item['total_sales'])
            }
        }
    
    def _handle_revenue(self, context: List[Dict]) -> Dict[str, Any]:
        """Handle revenue query"""
        if not context or not context[0].get('data'):
            return self._empty_response()
        
        data = context[0]['data']
        revenue = float(data.get('revenue', 0))
        growth = float(data.get('growth_percent', 0))
        
        trend = "up" if growth > 0 else "down"
        answer = f"Your revenue is KES {revenue:,.0f}, {trend} {abs(growth):.1f}% from the previous period."
        
        return {
            "answer_text": answer,
            "confidence": 0.95,
            "visualization": {
                "type": "metric_card",
                "metrics": [
                    {"label": "Revenue", "value": f"KES {revenue:,.0f}"},
                    {"label": "Growth", "value": f"{growth:+.1f}%"}
                ]
            },
            "structured": {
                "revenue": revenue,
                "growth_percent": growth
            }
        }
    
    def _handle_categories(self, context: List[Dict]) -> Dict[str, Any]:
        """Handle category query"""
        if not context or not context[0].get('data'):
            return self._empty_response()
        
        data = context[0]['data']
        if not isinstance(data, list):
            return self._empty_response()
        
        top_cat = data[0] if data else {}
        answer = f"Your top category is {top_cat.get('category', 'N/A')} with KES {float(top_cat.get('sales', 0)):,.0f} in sales."
        
        return {
            "answer_text": answer,
            "confidence": 0.9,
            "visualization": {
                "type": "pie_chart",
                "data": [{"name": item['category'], "value": float(item['sales'])} for item in data]
            },
            "structured": {"categories": data}
        }
    
    def _handle_growth(self, context: List[Dict]) -> Dict[str, Any]:
        """Handle growth/trend query"""
        if not context or not context[0].get('data'):
            return self._empty_response()
        
        data = context[0]['data']
        
        if isinstance(data, list) and data:
            answer = f"Your revenue has been trending over the past {len(data)} months. Latest month shows KES {float(data[-1].get('revenue', 0)):,.0f}."
        else:
            growth = float(data.get('growth_percent', 0))
            answer = f"Your business has grown {growth:+.1f}% compared to the previous period."
        
        return {
            "answer_text": answer,
            "confidence": 0.85,
            "visualization": None,
            "structured": {"data": data}
        }
    
    def _handle_default(self, context: List[Dict]) -> Dict[str, Any]:
        """Default response"""
        return {
            "answer_text": "I can help you analyze your business data. Try asking about your top products, revenue, or sales trends.",
            "confidence": 0.5,
            "visualization": None,
            "structured": {}
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        """Response when no data available"""
        return {
            "answer_text": "I don't have enough data to answer that question yet. Please upload your transaction data first.",
            "confidence": 0.3,
            "visualization": None,
            "structured": {}
        }


chat_fallback = ChatFallback()
