from fastapi import APIRouter, Depends, HTTPException
import asyncio
import time
import logging

from app.models.schemas import ChatQuery, ChatResponse
from app.auth import verify_token
from app.config import settings
from app.services.bigquery_context import bigquery_context
from app.services.gemini_service import gemini_service
from app.services.chat_fallback import chat_fallback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    token: dict = Depends(verify_token)
):
    """Process natural language query with BigQuery data and Gemini AI"""
    start_time = time.time()
    user_id = token.get("sub")
    
    try:
        # Retrieve context from BigQuery
        logger.info(f"Fetching BigQuery context for user: {user_id}")
        context = await asyncio.to_thread(
            bigquery_context.retrieve_context,
            user_id=user_id,
            query=query.query,
            top_k=settings.MAX_CONTEXT_CHUNKS
        )
        
        logger.info(f"Retrieved {len(context)} context chunks from BigQuery")
        
        # Check if we have data
        if not context or (len(context) == 1 and context[0].get('type') == 'error'):
            return ChatResponse(
                answer_text="I don't have any transaction data for your account yet. Once you start recording sales through the dashboard, I'll be able to provide insights and analysis!",
                confidence=1.0,
                visualization=None,
                structured={
                    'insights': [],
                    'recommendations': ['Upload your first transaction to get started', 'Use the dashboard to track your sales']
                },
                sources=[]
            )
        
        # Try Gemini AI with BigQuery context
        try:
            response = await asyncio.to_thread(
                gemini_service.generate_response,
                query=query.query,
                context=context,
                user_id=user_id
            )
            logger.info("✅ Gemini response generated successfully")
        except Exception as gemini_error:
            logger.warning(f"Gemini failed, using fallback: {gemini_error}")
            # Fallback to rule-based
            response = chat_fallback.generate_fallback_response(query.query, context)
        
        response['sources'] = [ctx.get('type') for ctx in context]
        
        elapsed = time.time() - start_time
        logger.info(f"Chat response generated in {elapsed:.2f}s with {len(context)} data points")
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        return ChatResponse(
            answer_text="I'm having trouble processing your question right now. Please try again in a moment.",
            confidence=0.0,
            visualization=None,
            structured={},
            sources=[]
        )
