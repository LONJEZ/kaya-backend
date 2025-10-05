from fastapi import APIRouter, Depends, HTTPException
import asyncio
import time
import logging

from app.models.schemas import ChatQuery, ChatResponse
from app.auth import verify_token
from app.config import settings
from app.services.context_retriever import context_retriever
from app.services.gemini_service import gemini_service
from app.services.chat_fallback import chat_fallback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    token: dict = Depends(verify_token)
):
    """Process natural language query with RAG and fallback"""
    start_time = time.time()
    user_id = token.get("sub")
    
    try:
        # Retrieve context
        context = await asyncio.to_thread(
            context_retriever.retrieve_context,
            user_id=user_id,
            query=query.query,
            top_k=settings.MAX_CONTEXT_CHUNKS
        )
        
        logger.info(f"Retrieved {len(context)} context chunks")
        
        # Try Gemini first
        try:
            response = await asyncio.to_thread(
                gemini_service.generate_response,
                query=query.query,
                context=context,
                user_id=user_id
            )
        except Exception as gemini_error:
            logger.warning(f"Gemini failed, using fallback: {gemini_error}")
            # Fallback to rule-based
            response = chat_fallback.generate_fallback_response(query.query, context)
        
        response['sources'] = [ctx.get('type') for ctx in context]
        
        elapsed = time.time() - start_time
        logger.info(f"Chat response generated in {elapsed:.2f}s")
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        # Return friendly error
        return ChatResponse(
            answer_text="I'm having trouble processing your question right now. Please try again in a moment.",
            confidence=0.0,
            visualization=None,
            structured={},
            sources=[]
        )

