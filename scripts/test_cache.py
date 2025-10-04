"""Test caching functionality"""

import requests
import time

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def test_cache_performance():
    """Test that cache improves performance"""
    token = get_demo_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoint = f"{BASE_URL}/api/analytics/overview"
    
    print("="*60)
    print("🧪 Testing Cache Performance")
    print("="*60)
    print()
    
    # First request (cold - no cache)
    print("1️⃣ First request (cold)...")
    start = time.time()
    response1 = requests.get(endpoint, headers=headers)
    time1 = time.time() - start
    
    process_time1 = float(response1.headers.get('X-Process-Time', 0))
    print(f"   Response time: {time1*1000:.0f}ms")
    print(f"   Server process time: {process_time1*1000:.0f}ms")
    print(f"   Status: {response1.status_code}")
    print()
    
    # Second request (should be cached)
    print("2️⃣ Second request (should be cached)...")
    start = time.time()
    response2 = requests.get(endpoint, headers=headers)
    time2 = time.time() - start
    
    process_time2 = float(response2.headers.get('X-Process-Time', 0))
    print(f"   Response time: {time2*1000:.0f}ms")
    print(f"   Server process time: {process_time2*1000:.0f}ms")
    print(f"   Status: {response2.status_code}")
    print()
    
    # Check cache stats
    print("3️⃣ Cache statistics...")
    stats_response = requests.get(f"{BASE_URL}/api/cache/stats", headers=headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   Total cached entries: {stats['total_entries']}")
        print(f"   Cache TTL: {stats['ttl_seconds']}s")
        print()
    
    # Clear cache
    print("4️⃣ Clearing cache...")
    clear_response = requests.post(f"{BASE_URL}/api/cache/clear", headers=headers)
    print(f"   Status: {clear_response.status_code}")
    print()
    
    # Third request (cold again after clear)
    print("5️⃣ Third request (cold after cache clear)...")
    start = time.time()
    response3 = requests.get(endpoint, headers=headers)
    time3 = time.time() - start
    
    process_time3 = float(response3.headers.get('X-Process-Time', 0))
    print(f"   Response time: {time3*1000:.0f}ms")
    print(f"   Server process time: {process_time3*1000:.0f}ms")
    print()
    
    # Analysis
    print("="*60)
    print("📊 Analysis")
    print("="*60)
    
    speedup = ((time1 - time2) / time1) * 100
    print(f"Cache speedup: {speedup:.1f}%")
    
    if time2 < time1:
        print("✅ Cache is working! Second request was faster.")
    else:
        print("⚠️ Cache may not be working as expected.")
    
    print()


if __name__ == "__main__":
    test_cache_performance()
