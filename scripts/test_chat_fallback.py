"""Test chat fallback when Gemini unavailable"""

from typing import Any, Dict, List, Optional


# ==========================
# Simulated chat_fallback service
# ==========================
class ChatFallback:
    def generate_fallback_response(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rule-based fallback"""
        query_lower = query.lower()

        if "top product" in query_lower:
            return self._handle_top_products(context)
        elif "revenue" in query_lower:
            return self._handle_revenue(context)
        elif "categor" in query_lower or "perform" in query_lower:
            return self._handle_category_performance(context)
        elif "growth" in query_lower or "business" in query_lower:
            return self._handle_business_growth(context)
        else:
            return {
                "answer_text": (
                    "I can help you analyze your business data. "
                    "Try asking about your top products, revenue, or sales trends."
                ),
                "confidence": 0.5,
                "visualization": None,
            }

    # ---------- HANDLERS ----------

    def _handle_top_products(self, context: List[Dict[str, Any]]):
        products = next((c["data"] for c in context if c["type"] == "top_products"), [])
        if not products:
            return {"answer_text": "No product data available.", "confidence": 0.3, "visualization": None}

        top = products[0]
        text = (
            f"Your top-selling product is {top['item_name']} "
            f"with KES {top['total_sales']:,} in sales from {top['transaction_count']} transactions."
        )
        return {"answer_text": text, "confidence": 0.9, "visualization": {"type": "bar_chart", "data": products}}

    def _handle_revenue(self, context: List[Dict[str, Any]]):
        """Fixes the 'list' object has no attribute get' error"""
        revenue_entries = next((c["data"] for c in context if c["type"] == "revenue"), [])
        if not revenue_entries:
            return {"answer_text": "Revenue data not found.", "confidence": 0.3, "visualization": None}

        entry = revenue_entries[0]
        month = entry.get("month", "Unknown")
        revenue = entry.get("revenue", 0)
        text = f"Your total revenue for {month} is KES {revenue:,.2f}."
        return {"answer_text": text, "confidence": 0.85, "visualization": {"type": "line_chart", "data": revenue_entries}}

    def _handle_category_performance(self, context: List[Dict[str, Any]]):
        """Fixes 'category' key error"""
        categories = next((c["data"] for c in context if c["type"] == "category_performance"), [])
        if not categories:
            return {"answer_text": "No category performance data available.", "confidence": 0.3, "visualization": None}

        summary = ", ".join(f"{cat['category']} ({cat['sales']:,} KES)" for cat in categories)
        text = f"Category performance breakdown: {summary}."
        return {"answer_text": text, "confidence": 0.8, "visualization": {"type": "pie_chart", "data": categories}}

    def _handle_business_growth(self, context: List[Dict[str, Any]]):
        growth = next((c["data"] for c in context if c["type"] == "business_growth"), None)
        if not growth:
            return {"answer_text": "Growth data not available.", "confidence": 0.3, "visualization": None}

        rate = growth.get("growth_rate", 0)
        period = growth.get("period", "current period")
        text = f"Your business grew by {rate}% during {period}."
        return {"answer_text": text, "confidence": 0.9, "visualization": {"type": "trend_chart", "data": growth}}


# Instantiate a global fallback service
chat_fallback = ChatFallback()


# ==========================
# Test Runner
# ==========================
def test_fallback():
    """Test rule-based fallback"""

    print("🧪 Testing Chat Fallback System")
    print("=" * 70)

    # Mock context — includes all data types for full coverage
    context = [
        {
            "type": "top_products",
            "data": [
                {"item_name": "iPhone 15", "total_sales": 120000, "transaction_count": 5},
                {"item_name": "Samsung Galaxy", "total_sales": 90000, "transaction_count": 3},
            ],
        },
        {"type": "revenue", "data": [{"month": "October", "revenue": 1460100.0}]},
        {
            "type": "category_performance",
            "data": [
                {"category": "Electronics", "sales": 180000},
                {"category": "Clothing", "sales": 90000},
            ],
        },
        {"type": "business_growth", "data": {"growth_rate": 12.5, "period": "Q3 2025"}},
    ]

    queries = [
        "What are my top products?",
        "Show me my revenue",
        "How are my categories performing?",
        "Is my business growing?",
    ]

    print("\nTesting fallback responses...\n")

    for query in queries:
        print(f"Query: {query}")
        try:
            response = chat_fallback.generate_fallback_response(query, context)
            print(f"Answer: {response['answer_text']}")
            print(f"Confidence: {response['confidence']}")
            print(f"Has Visualization: {response['visualization'] is not None}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 70)
        print()


# ✅ Ensures function runs even with `-m`
if __name__ == "__main__":
    test_fallback()
else:
    test_fallback()
