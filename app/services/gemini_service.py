"""Google AI Studio Gemini integration - FREE, no billing required!"""

from typing import Dict, Any, List
import json
import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Generate conversational responses using Google AI Studio Gemini API"""
    
    def __init__(self):
        # Get model from settings (defaults to gemini-1.5-pro)
        self.model = settings.GEMINI_MODEL
        
        # Build API URL dynamically using the model from settings
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
        """Generate AI response using Google AI Studio Gemini"""
        
        if not self.api_key:
            raise Exception("Gemini API key not configured")
        
        try:
            # Build prompt with context
            prompt = self._build_prompt(query, context)
            
            # Call Gemini API
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
                        "maxOutputTokens": 1024,
                    }
                },
                timeout=10
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
    
    def _build_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Build prompt with business context"""
        
        # Format context data
        context_str = self._format_context(context)
        
        prompt = f"""You are Kaya AI, a business intelligence assistant for African SMEs. 
Analyze the user's question and provide helpful insights based on their business data.

USER QUESTION: {query}

BUSINESS DATA CONTEXT:
{context_str}

INSTRUCTIONS:
1. Answer the question directly and conversationally
2. Use specific numbers from the data when available
3. Provide actionable insights
4. Be concise but informative
5. If asking about trends, mention specific patterns
6. Always be encouraging and supportive

IMPORTANT: 
- Format numbers with commas (e.g., 125,000)
- Use KES for currency
- Be specific about time periods
- Highlight key insights

Your response:"""
        
        return prompt
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context data for prompt"""
        if not context:
            return "No specific business data available yet. Encourage user to upload data."
        
        formatted = []
        for idx, ctx in enumerate(context[:5], 1):  # Top 5 most relevant
            if ctx.get('type') == 'revenue':
                formatted.append(f"- Total Revenue: KES {ctx.get('value', 0):,.0f}")
            elif ctx.get('type') == 'transaction':
                formatted.append(f"- Recent transaction: {ctx.get('item', 'N/A')} - KES {ctx.get('amount', 0):,.0f}")
            elif ctx.get('type') == 'product':
                formatted.append(f"- Top product: {ctx.get('name', 'N/A')} with {ctx.get('sales', 0):,.0f} in sales")
            elif ctx.get('type') == 'category':
                formatted.append(f"- Category {ctx.get('category', 'N/A')}: KES {ctx.get('sales', 0):,.0f}")
        
        return "\n".join(formatted) if formatted else "Limited data available"
    
    def _parse_response(self, answer_text: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse response and generate visualization if appropriate"""
        
        # Determine if visualization is needed
        visualization = None
        query_lower = answer_text.lower()
        
        # Check for chart keywords
        if any(word in query_lower for word in ['revenue', 'sales', 'trend', 'growth']):
            # Generate simple visualization from context
            if context and len(context) > 0:
                viz_data = self._generate_visualization(context)
                if viz_data:
                    visualization = viz_data
        
        # Extract insights and recommendations
        insights = []
        recommendations = []
        
        # Simple keyword-based extraction
        lines = answer_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['increased', 'growing', 'improved', 'higher']):
                insights.append(line.strip('- •'))
            if any(word in line_lower for word in ['should', 'consider', 'recommend', 'try', 'focus']):
                recommendations.append(line.strip('- •'))
        
        return {
            'answer': answer_text,
            'confidence': 0.85,  # Good confidence for Gemini responses
            'visualization': visualization,
            'structured': {
                'insights': insights[:3] if insights else [],
                'recommendations': recommendations[:3] if recommendations else []
            }
        }
    
    def _generate_visualization(self, context: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        """Generate visualization from context data"""
        
        # Try to create a bar chart from context
        chart_data = []
        
        for ctx in context[:5]:
            if ctx.get('type') in ['product', 'category']:
                chart_data.append({
                    'name': ctx.get('name') or ctx.get('category', 'Unknown'),
                    'value': ctx.get('sales') or ctx.get('value', 0)
                })
        
        if len(chart_data) >= 2:
            return {
                'type': 'bar_chart',
                'title': 'Top Performance',
                'data': chart_data
            }
        
        return None


# Global instance
gemini_service = GeminiService()