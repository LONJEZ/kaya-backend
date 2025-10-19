"""API tests"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import create_access_token

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Generate test token"""
    return create_access_token({"sub": "test-user", "business_name": "Test Business"})


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_analytics_overview_requires_auth():
    """Test analytics requires authentication"""
    response = client.get("/api/analytics/overview")
    assert response.status_code == 403


def test_analytics_overview_with_auth(auth_token):
    """Test analytics with valid token"""
    response = client.get(
        "/api/analytics/overview",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "profit_margin" in data


def test_chat_query(auth_token):
    """Test chat endpoint"""
    response = client.post(
        "/api/chat/query",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"query": "What are my top products?", "user_id": "test-user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer_text" in data
    assert "confidence" in data


def test_rate_limiting():
    """Test rate limiting"""
    token = create_access_token({"sub": "test-user"})
    
    # Make many requests
    responses = []
    for _ in range(70):  # Exceed 60/min limit
        response = client.get(
            "/api/analytics/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        responses.append(response.status_code)
    
    # Should have some 429 responses
    assert 429 in responses
