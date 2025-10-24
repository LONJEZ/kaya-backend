"""Google AI Studio Gemini integration - Enhanced for BigQuery context"""

from typing import Dict, Any, List
import json
import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Generate conversational responses using Google AI Studio Gemini API"""
    
    def __init__(self):
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.api_url = f"{self.base_url}/models/{self.model}:generateContent"
        self.api_key = settings.GEMINI_API_KEY
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Chat will use fallback responses.")
        else:
            logger.info(f"✅ Gemini API initialized with model: {self.model}")
    
    def generate_response(
        self, 
        query: str, 
        context: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate AI response using Google AI Studio Gemini with BigQuery data"""
        
        if not self.api_key:
            raise Exception("Gemini API key not configured")
        
        try:
            # Build enhanced prompt with BigQuery context
            prompt = self._build_enhanced_prompt(query, context)
            
            logger.info(f"🤖 Calling Gemini API: {self.model}")
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2048,
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise Exception(f"Gemini API returned {response.status_code}")
            
            result = response.json()
            
            # Extract response text
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']
                answer_text = content['parts'][0]['text']
                
                # Parse structured response
                structured_response = self._parse_response(answer_text, context)
                
                return {
                    'answer_text': structured_response['answer'],
                    'confidence': structured_response['confidence'],
                    'visualization': structured_response['visualization'],
                    'structured': structured_response['structured']
                }
            else:
                raise Exception("No response from Gemini")
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout")
            raise Exception("Gemini API timeout")
        except Exception as e:
            logger.error(f"Gemini service error: {str(e)}")
            raise
    
    def _build_enhanced_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Build enhanced prompt with properly formatted BigQuery context"""
        
        # Format the BigQuery data into readable text
        context_text = self._format_bigquery_context(context)
        
        prompt = f"""You are Kaya AI, an intelligent business analytics assistant for small business owners in Africa.

USER QUESTION: {query}

BUSINESS DATA FROM DATABASE:
{context_text}

INSTRUCTIONS:
1. Answer the question directly using the specific data provided above
2. Use exact numbers from the data (format with commas: 125,000)
3. Use KES for currency formatting
4. Be conversational and encouraging
5. Provide actionable insights based on the actual data
6. If data shows growth, celebrate it; if declining, suggest improvements
7. Keep responses concise but informative (2-4 sentences)

IMPORTANT:
- Only use data that is actually provided above
- If no data is available for something, say so honestly
- Be specific about time periods mentioned in the data
- Highlight the most important insight first

Your response:"""
        
        return prompt
    
    def _format_bigquery_context(self, context: List[Dict[str, Any]]) -> str:
        """Format BigQuery context data into readable text for Gemini"""
        
        if not context:
            return "No business data available yet."
        
        formatted_sections = []
        
        for ctx in context:
            ctx_type = ctx.get('type', 'unknown')
            data = ctx.get('data', {})
            
            if ctx_type == 'overview':
                total_trans = data.get('total_transactions', 0)
                total_rev = data.get('total_revenue', 0)
                avg_trans = data.get('avg_transaction', 0)
                unique_prods = data.get('unique_products', 0)
                
                formatted_sections.append(f"""
BUSINESS OVERVIEW (Last 30 days):
- Total Transactions: {total_trans:,}
- Total Revenue: KES {total_rev:,.2f}
- Average Transaction: KES {avg_trans:,.2f}
- Unique Products: {unique_prods}""")
            
            elif ctx_type == 'revenue':
                period = ctx.get('period', 'period')
                revenue = data.get('revenue', 0)
                prev_revenue = data.get('prev_revenue', 0)
                growth = data.get('growth_percent', 0)
                
                formatted_sections.append(f"""
REVENUE ANALYSIS ({period.replace('_', ' ').title()}):
- Current Period Revenue: KES {revenue:,.2f}
- Previous Period Revenue: KES {prev_revenue:,.2f}
- Growth Rate: {growth:+.1f}%""")
            
            elif ctx_type == 'top_products':
                formatted_sections.append("\nTOP SELLING PRODUCTS:")
                for i, product in enumerate(data[:5], 1):
                    name = product.get('item_name', 'Unknown')
                    category = product.get('category', 'N/A')
                    sales = product.get('total_sales', 0)
                    count = product.get('transaction_count', 0)
                    formatted_sections.append(f"  {i}. {name} ({category}) - KES {sales:,.2f} from {count} sales")
            
            elif ctx_type == 'categories':
                formatted_sections.append("\nSALES BY CATEGORY:")
                for i, cat in enumerate(data[:5], 1):
                    category = cat.get('category', 'Unknown')
                    sales = cat.get('sales', 0)
                    trans = cat.get('transactions', 0)
                    formatted_sections.append(f"  {i}. {category}: KES {sales:,.2f} ({trans} transactions)")
            
            elif ctx_type == 'payment_methods':
                formatted_sections.append("\nPAYMENT METHODS:")
                for method in data:
                    pm = method.get('payment_method', 'Unknown')
                    count = method.get('count', 0)
                    total = method.get('total', 0)
                    formatted_sections.append(f"  - {pm}: {count} transactions, KES {total:,.2f}")
            
            elif ctx_type == 'trends':
                if len(data) >= 2:
                    formatted_sections.append("\nMONTHLY REVENUE TRENDS:")
                    for month_data in data[-6:]:  # Last 6 months
                        month = month_data.get('month', 'Unknown')
                        revenue = month_data.get('revenue', 0)
                        formatted_sections.append(f"  - {month}: KES {revenue:,.2f}")
        
        if not formatted_sections:
            return "Limited business data available."
        
        return "\n".join(formatted_sections)
    
    def _parse_response(self, answer_text: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse response and generate visualization if appropriate"""
        
        visualization = None
        query_lower = answer_text.lower()
        
        # Generate visualization from context data
        if context:
            viz_data = self._generate_visualization(context)
            if viz_data:
                visualization = viz_data
        
        # Extract insights and recommendations
        insights = []
        recommendations = []
        
        lines = answer_text.split('\n')
        for line in lines:
            line_clean = line.strip('- •*').strip()
            if not line_clean:
                continue
            
            line_lower = line.lower()
            if any(word in line_lower for word in ['increased', 'growing', 'improved', 'higher', 'up by', 'growth']):
                insights.append(line_clean)
            if any(word in line_lower for word in ['should', 'consider', 'recommend', 'try', 'focus', 'could', 'suggest']):
                recommendations.append(line_clean)
        
        return {
            'answer': answer_text,
            'confidence': 0.9,  # High confidence with real BigQuery data
            'visualization': visualization,
            'structured': {
                'insights': insights[:3] if insights else [],
                'recommendations': recommendations[:3] if recommendations else []
            }
        }
    
    def _generate_visualization(self, context: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        """Generate visualization from BigQuery context data"""
        
        for ctx in context:
            ctx_type = ctx.get('type')
            data = ctx.get('data', [])
            
            # Top products chart
            if ctx_type == 'top_products' and isinstance(data, list) and len(data) >= 2:
                chart_data = []
                for product in data[:5]:
                    chart_data.append({
                        'name': product.get('item_name', 'Unknown'),
                        'value': float(product.get('total_sales', 0))
                    })
                return {
                    'type': 'bar_chart',
                    'title': 'Top Products by Sales',
                    'data': chart_data
                }
            
            # Category breakdown
            elif ctx_type == 'categories' and isinstance(data, list) and len(data) >= 2:
                chart_data = []
                for category in data:
                    chart_data.append({
                        'name': category.get('category', 'Unknown'),
                        'value': float(category.get('sales', 0))
                    })
                return {
                    'type': 'pie_chart',
                    'title': 'Sales by Category',
                    'data': chart_data
                }
            
            # Revenue trends
            elif ctx_type == 'trends' and isinstance(data, list) and len(data) >= 2:
                chart_data = []
                for month in data:
                    chart_data.append({
                        'month': month.get('month', 'Unknown'),
                        'revenue': float(month.get('revenue', 0))
                    })
                return {
                    'type': 'line_chart',
                    'title': 'Revenue Trends',
                    'data': chart_data
                }
        
        return None


# Global instance
gemini_service = GeminiService()