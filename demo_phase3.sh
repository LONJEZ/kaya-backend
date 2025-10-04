#!/bin/bash
# ============================================================================
# FILE: demo_phase3.sh
# ============================================================================
# Complete Phase 3 demo for judges

set -e

echo "🎬 Kaya AI Backend - Phase 3 Demo"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo "🔍 Checking backend status..."
if ! curl -s http://localhost:8007/health > /dev/null; then
    echo -e "${YELLOW}⚠️  Backend not running. Starting it...${NC}"
    uvicorn app.main:app --reload &
    sleep 5
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Generate token
echo "🔑 Generating authentication token..."
TOKEN=$(python3 -c "from app.auth import create_access_token; print(create_access_token({'sub': 'demo-user-001', 'business_name': 'Demo Electronics'}))")
echo -e "${GREEN}✅ Token generated${NC}"
echo ""

# Function to make API call and display results
make_api_call() {
    local name=$1
    local endpoint=$2
    local method=${3:-GET}
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 ${name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nTIME_TOTAL:%{time_total}" \
            -H "Authorization: Bearer $TOKEN" \
            "http://localhost:8007${endpoint}")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nTIME_TOTAL:%{time_total}" \
            -X POST \
            -H "Authorization: Bearer $TOKEN" \
            "http://localhost:8007${endpoint}")
    fi
    
    # Parse response
    body=$(echo "$response" | sed -e '/HTTP_STATUS/,$d')
    status=$(echo "$response" | grep HTTP_STATUS | cut -d: -f2)
    time=$(echo "$response" | grep TIME_TOTAL | cut -d: -f2)
    
    # Display formatted response
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    echo ""
    echo -e "Status: ${GREEN}${status}${NC} | Response Time: ${GREEN}${time}s${NC}"
    echo ""
}

# Demo Sequence
echo -e "${YELLOW}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          Phase 3: Real Analytics Demo             ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Overview
make_api_call "Business Overview (Last 30 Days)" "/api/analytics/overview?days=30"

# 2. Revenue Trends
make_api_call "Revenue Trends (6 Months)" "/api/analytics/revenue-trends?months=6"

# 3. Top Products
make_api_call "Top 5 Products" "/api/analytics/top-products?limit=5"

# 4. Category Sales
make_api_call "Sales by Category" "/api/analytics/category-sales"

# 5. Recent Transactions
make_api_call "Recent 10 Transactions" "/api/analytics/transactions?limit=10"

# 6. Payment Methods
make_api_call "Payment Methods Breakdown" "/api/analytics/payment-methods"

echo -e "${YELLOW}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║        Advanced Analytics Demo                     ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 7. Growth Metrics
make_api_call "Growth Metrics (MoM & YoY)" "/api/analytics/advanced/growth-metrics"

# 8. Customer Insights
make_api_call "Customer Behavior Insights" "/api/analytics/advanced/customer-insights"

# 9. Profit Analysis
make_api_call "Profit Analysis by Category" "/api/analytics/advanced/profit-analysis"

echo -e "${YELLOW}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          Cache Performance Demo                    ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 10. Cache Stats
make_api_call "Cache Statistics" "/api/cache/stats"

# 11. Clear Cache
make_api_call "Clear Cache" "/api/cache/clear" "POST"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Phase 3 Demo Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📚 Key Features Demonstrated:"
echo "  ✅ Real BigQuery analytics queries"
echo "  ✅ Caching layer (5-min TTL)"
echo "  ✅ Advanced metrics (growth, insights, profit)"
echo "  ✅ Sub-second response times (cached)"
echo "  ✅ Partition-optimized queries"
echo ""
echo "📖 View API Documentation: http://localhost:8000/docs"
echo ""
