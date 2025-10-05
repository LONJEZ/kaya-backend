"""Test chat endpoint with various queries"""

import requests
import json
import time

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def test_chat_query(query: str, token: str):
    """Test a single chat query"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "query": query,
        "user_id": "demo-user-001"
    }
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/chat/query",
        headers=headers,
        json=data
    )
    duration = time.time() - start
    
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    print(f"Response Time: {duration*1000:.0f}ms")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nAnswer: {result['answer_text']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        if result.get('visualization'):
            print(f"\nVisualization: {result['visualization']['type']}")
        
        if result.get('sources'):
            print(f"Sources: {', '.join(result['sources'])}")
        
        if result.get('structured'):
            print(f"\nStructured Data:")
            print(json.dumps(result['structured'], indent=2, default=str))
    else:
        print(f"Error: {response.text}")
    
    return duration


def main():
    print("🤖 Testing Kaya AI Chat Engine")
    print("="*70)
    
    token = get_demo_token()
    
    # Test queries
    queries = [
        "What were my top-selling products last month?",
        "How much revenue did I make?",
        "Show me sales by category",
        "Which payment method is most popular?",
        "How did my sales change compared to last quarter?",
        "What are my best performing products?",
        "Tell me about my business performance",
    ]
    
    times = []
    
    for query in queries:
        duration = test_chat_query(query, token)
        times.append(duration)
        time.sleep(1)  # Brief pause between queries
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Chat Performance Summary")
    print(f"{'='*70}")
    print(f"Queries tested: {len(times)}")
    print(f"Average response time: {sum(times)/len(times)*1000:.0f}ms")
    print(f"Fastest: {min(times)*1000:.0f}ms")
    print(f"Slowest: {max(times)*1000:.0f}ms")
    
    # Check < 3s requirement
    max_time = max(times)
    if max_time < 3.0:
        print(f"\n✅ All queries under 3s requirement (max: {max_time*1000:.0f}ms)")
    else:
        print(f"\n⚠️ Some queries exceed 3s (max: {max_time*1000:.0f}ms)")


if __name__ == "__main__":
    main()

