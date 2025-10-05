"""Vertex AI Gemini integration for chat"""

from typing import Dict, Any, List
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Generate conversational responses using Gemini"""
    
    def __init__(self):
        vertexai.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
        self.model = GenerativeModel(settings.VERTEX_AI_MODEL)
    
    def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate structured response from query and context
        
        Returns:
            {
                "answer_text": str,
                "confidence": float,
                "visualization": dict,
                "structured": dict
            }
        """
        
        # Build prompt
        prompt = self._build_prompt(query, context)
        
        # Generate with structured output
        generation_config = GenerationConfig(
            temperature=0.2,
            max_output_tokens=1024,
            response_mime_type="application/json"
        )
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Parse response
            result = json.loads(response.text)
            
            # Add visualization config based on context type
            result['visualization'] = self._generate_visualization_config(context, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return {
                "answer_text": "I apologize, but I encountered an error processing your question. Please try rephrasing it.",
                "confidence": 0.0,
                "visualization": None,
                "structured": {}
            }
    
    def _build_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Build prompt with context"""
        
        context_str = json.dumps(context, indent=2, default=str)
        
        prompt = f"""You are Kaya AI, a business analytics assistant for African SMEs.

User Question: {query}

Business Data Context:
{context_str}

Generate a JSON response with these fields:
{{
    "answer_text": "Natural language answer (2-3 sentences, friendly tone)",
    "confidence": 0.0-1.0,
    "structured": {{
        "key_metrics": {{}},
        "insights": [],
        "recommendations": []
    }}
}}

Guidelines:
- Be concise and actionable
- Use Kenyan context (KES currency, M-Pesa references)
- Highlight key insights from the data
- Provide 1-2 practical recommendations
- If data shows growth, celebrate it!
- If data shows decline, suggest improvements

Response:"""
        
        return prompt
    
    def _generate_visualization_config(
        self,
        context: List[Dict[str, Any]],
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualization configuration based on context type"""
        
        if not context:
            return None
        
        context_type = context[0].get('type')
        data = context[0].get('data', {})
        
        if context_type == 'top_products' and isinstance(data, list):
            return {
                "type": "bar_chart",
                "title": "Top Products",
                "data": [
                    {"name": item['item_name'], "value": float(item['total_sales'])}
                    for item in data[:5]
                ]
            }
        
        elif context_type == 'categories' and isinstance(data, list):
            return {
                "type": "pie_chart",
                "title": "Sales by Category",
                "data": [
                    {"name": item['category'], "value": float(item['sales'])}
                    for item in data
                ]
            }
        
        elif context_type == 'trends' and isinstance(data, list):
            return {
                "type": "line_chart",
                "title": "Revenue Trend",
                "data": [
                    {"month": item['month'], "revenue": float(item['revenue'])}
                    for item in data
                ]
            }
        
        elif context_type == 'revenue':
            revenue = float(data.get('revenue', 0))
            growth = float(data.get('growth_percent', 0))
            
            return {
                "type": "metric_card",
                "metrics": [
                    {"label": "Revenue", "value": f"KES {revenue:,.0f}"},
                    {"label": "Growth", "value": f"{growth:+.1f}%"}
                ]
            }
        
        return None


gemini_service = GeminiService()