"""Service tests"""

import pytest
from app.services.context_retriever import ContextRetriever
from app.services.chat_fallback import ChatFallback


def test_context_retriever():
    """Test context retrieval"""
    retriever = ContextRetriever()
    
    # Test query classification
    context = retriever.retrieve_context(
        user_id="test-user",
        query="What are my top products?"
    )
    
    assert len(context) > 0
    assert context[0]["type"] == "top_products"


def test_chat_fallback():
    """Test fallback system"""
    fallback = ChatFallback()
    
    mock_context = [{
        "type": "top_products",
        "data": [
            {"item_name": "Product A", "total_sales": 1000, "transaction_count": 5}
        ]
    }]
    
    response = fallback.generate_fallback_response(
        "What are my top products?",
        mock_context
    )
    
    assert response["answer_text"]
    assert response["confidence"] > 0
    assert response["visualization"] is not None

