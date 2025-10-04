"""Benchmark analytics endpoint performance"""

import requests
import time
import statistics
from typing import List

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def benchmark_endpoint(endpoint: str, token: str, iterations: int = 10) -> dict:
    """Benchmark an endpoint"""
    headers = {'Authorization': f'Bearer {token}'}
    response_times = []
    
    for i in range(iterations):
        start = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        duration = time.time() - start
        
        if response.status_code == 200:
            response_times.append(duration)
        
        # Brief pause between requests
        time.sleep(0.1)
    
    if not response_times:
        return {"error": "All requests failed"}
    
    return {
        "endpoint": endpoint,
        "iterations": len(response_times),
        "avg_time": statistics.mean(response_times),
        "min_time": min(response_times),
        "max_time": max(response_times),
        "median_time": statistics.median(response_times),
        "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
    }


def main():
    print("="*70)
    print("⚡ Kaya AI Analytics Performance Benchmark")
    print("="*70)
    print()
    
    token = get_demo_token()
    
    endpoints = [
        "/api/analytics/overview",
        "/api/analytics/revenue-trends",
        "/api/analytics/top-products",
        "/api/analytics/category-sales",
        "/api/analytics/transactions?limit=50",
        "/api/analytics/advanced/growth-metrics",
        "/api/analytics/advanced/customer-insights",
        "/api/analytics/advanced/profit-analysis",
    ]
    
    print("Running 10 iterations per endpoint...\n")
    
    results = []
    for endpoint in endpoints:
        print(f"Benchmarking {endpoint}...")
        result = benchmark_endpoint(endpoint, token, iterations=10)
        results.append(result)
        
        if "error" not in result:
            print(f"  Avg: {result['avg_time']*1000:.0f}ms | "
                  f"Min: {result['min_time']*1000:.0f}ms | "
                  f"Max: {result['max_time']*1000:.0f}ms")
        else:
            print(f"  ❌ {result['error']}")
        print()
    
    # Summary
    print("="*70)
    print("📊 Performance Summary")
    print("="*70)
    
    valid_results = [r for r in results if "error" not in r]
    
    if valid_results:
        avg_times = [r['avg_time'] for r in valid_results]
        print(f"\nOverall Average Response Time: {statistics.mean(avg_times)*1000:.0f}ms")
        print(f"Fastest Endpoint: {min(valid_results, key=lambda x: x['avg_time'])['endpoint']}")
        print(f"Slowest Endpoint: {max(valid_results, key=lambda x: x['avg_time'])['endpoint']}")
        
        # Check if under 3s requirement
        max_time = max(r['max_time'] for r in valid_results)
        if max_time < 3.0:
            print(f"\n✅ All endpoints under 3s requirement (max: {max_time*1000:.0f}ms)")
        else:
            print(f"\n⚠️  Some endpoints exceed 3s (max: {max_time*1000:.0f}ms)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

