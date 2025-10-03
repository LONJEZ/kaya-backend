"""
Test script for Kaya AI Backend API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def get_demo_token():
    """Generate a demo JWT token"""
    from app.auth import create_access_token
    token = create_access_token({
        "sub": "demo-user-001",
        "business_name": "Demo Electronics Kenya"
    })
    return token


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_analytics_overview(token):
    """Test analytics overview endpoint"""
    print("\n📊 Testing analytics overview...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_revenue_trends(token):
    """Test revenue trends endpoint"""
    print("\n📈 Testing revenue trends...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/revenue-trends", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_top_products(token):
    """Test top products endpoint"""
    print("\n🏆 Testing top products...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/top-products", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_chat_query(token):
    """Test chat query endpoint"""
    print("\n💬 Testing chat query...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "query": "What were my top-selling products last month?",
        "user_id": "demo-user-001"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat/query",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_settings(token):
    """Test settings endpoint"""
    print("\n⚙️ Testing settings...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/settings", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("="*60)
    print("🧪 Kaya AI Backend API Tests")
    print("="*60)
    
    # Generate token
    print("\n🔑 Generating demo token...")
    token = get_demo_token()
    print(f"Token: {token[:50]}...")
    
    # Run tests
    results = {
        "health": test_health(),
        "analytics_overview": test_analytics_overview(token),
        "revenue_trends": test_revenue_trends(token),
        "top_products": test_top_products(token),
        "chat_query": test_chat_query(token),
        "settings": test_settings(token),
    }
    
    # Print summary
    print("\n" + "="*60)
    print("📋 Test Results Summary")
    print("="*60)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Score: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total

