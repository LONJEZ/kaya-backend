"""🔥 Complete System Benchmark — Enhanced Version"""

import requests
import time
import statistics
from typing import List, Dict
from colorama import Fore, Style, init

# Initialize colored output
init(autoreset=True)

BASE_URL = "http://localhost:8007"


def get_demo_token():
    """Generate a demo token for testing"""
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo"})


def benchmark_endpoint(name: str, method: str, endpoint: str, token: str, data=None) -> Dict:
    """Benchmark a single API endpoint and return timing metrics"""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    times = []
    errors = 0

    for i in range(5):
        start = time.time()

        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=10)

            duration = time.time() - start

            if response.status_code == 200:
                times.append(duration)
            else:
                errors += 1
                print(f"{Fore.YELLOW}⚠️  {name}: Received status {response.status_code}")

        except requests.exceptions.Timeout:
            errors += 1
            print(f"{Fore.RED}⏱️  Timeout on {name}")
        except Exception as e:
            errors += 1
            print(f"{Fore.RED}❌ Error on {name}: {e}")

        time.sleep(0.2)

    if not times:
        return {"name": name, "avg_ms": 0, "min_ms": 0, "max_ms": 0, "passes_3s": False, "errors": errors}

    return {
        "name": name,
        "avg_ms": statistics.mean(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "passes_3s": max(times) < 3.0,
        "errors": errors
    }


def main():
    print("=" * 70)
    print("⚡ Complete System Benchmark")
    print("=" * 70)
    print()

    token = get_demo_token()

    tests = [
        ("Analytics Overview", "GET", "/api/analytics/overview", None),
        ("Revenue Trends", "GET", "/api/analytics/revenue-trends", None),
        ("Top Products", "GET", "/api/analytics/top-products", None),
        ("Growth Metrics", "GET", "/api/analytics/advanced/growth-metrics", None),
        ("Chat Query", "POST", "/api/chat/query",
         {"query": "What are my top products?", "user_id": "demo-user-001"}),
    ]

    results = []

    for name, method, endpoint, data in tests:
        print(f"Testing {Fore.CYAN}{name}{Style.RESET_ALL}...")
        result = benchmark_endpoint(name, method, endpoint, token, data)
        results.append(result)

    print("\n" + "=" * 70)
    print(f"{Fore.MAGENTA}📊 Benchmark Results{Style.RESET_ALL}")
    print("=" * 70)
    print(f"{'Endpoint':<30} {'Avg':<10} {'Min':<10} {'Max':<10} {'< 3s':<6} {'Errors':<8}")
    print("-" * 70)

    for r in results:
        status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if r['passes_3s'] else f"{Fore.RED}❌{Style.RESET_ALL}"
        err_color = f"{Fore.RED}" if r['errors'] > 0 else f"{Fore.GREEN}"
        print(f"{r['name']:<30} {r['avg_ms']:>8.0f}ms {r['min_ms']:>8.0f}ms {r['max_ms']:>8.0f}ms {status:<6} {err_color}{r['errors']}{Style.RESET_ALL}")

    print("=" * 70)
    all_pass = all(r['passes_3s'] and r['errors'] == 0 for r in results)

    if all_pass:
        print(f"{Fore.GREEN}✅ All endpoints meet < 3s requirement and returned 200 OK")
    else:
        print(f"{Fore.YELLOW}⚠️  Some endpoints are slow or returned errors")

    print()


if __name__ == "__main__":
    main()
