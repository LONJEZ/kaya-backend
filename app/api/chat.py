from fastapi import APIRouter, Depends, HTTPException
import asyncio
import time

from app.models.schemas import ChatQuery, ChatResponse
from app.auth import verify_token
from app.config import settings

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    token: dict = Depends(verify_token)
):
    """
    Process natural language query and return structured answer
    
    Flow:
    1. Embed query
    2. Retrieve top-K context from Elastic/BigQuery
    3. Build prompt + call Vertex AI Gemini
    4. Return structured response
    """
    start_time = time.time()
    user_id = token.get("sub")
    
    try:
        # TODO: Implement RAG flow in Phase 4
        # For now, return mock response
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        response = ChatResponse(
            answer_text=f"Based on your data, here's what I found regarding: '{query.query}'",
            confidence=0.85,
            visualization=None,
            structured={
                "query_type": "analytics",
                "time_period": "last_30_days",
                "metrics": ["revenue", "profit"]
            },
            sources=["transactions_table", "products_table"]
        )
        
        elapsed = time.time() - start_time
        if elapsed > settings.CHAT_TIMEOUT_SECONDS:
            raise HTTPException(status_code=504, detail="Query timeout")
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
