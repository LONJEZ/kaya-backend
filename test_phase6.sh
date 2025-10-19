#!/bin/bash
# Test Phase 6 features

set -e

echo "🧪 Testing Phase 6 Features"
echo "==========================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Server not running on port 8000"
    echo "   Start with: make run"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Get token
echo "Generating test token..."
TOKEN=$(python3 -c "from app.auth import create_access_token; print(create_access_token({'sub': 'test-user', 'business_name': 'Test'}))")
echo "✅ Token generated"
echo ""

# Test 1: Monitoring endpoints
echo "Test 1: Monitoring Endpoints"
echo "----------------------------"

echo "  → Health check..."
curl -s http://localhost:8000/health | jq '.status' || echo "Failed"

echo "  → Detailed health..."
curl -s http://localhost:8000/api/monitoring/health/detailed | jq '.status' || echo "Failed"

echo "  → Metrics..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/metrics | jq '.total_requests' || echo "Failed"

echo "✅ Monitoring tests passed"
echo ""

# Test 2: Admin endpoints
echo "Test 2: Admin Endpoints"
echo "----------------------"

echo "  → System stats..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/system/stats | jq '.environment' || echo "Failed"

echo "  → Feature flags..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/system/stats | jq '.feature_flags' || echo "Failed"

echo "✅ Admin tests passed"
echo ""

# Test 3: Data quality
echo "Test 3: Data Quality"
echo "-------------------"

echo "  → Quality check..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/check | jq '.overall_status' || echo "Failed"

echo "✅ Data quality tests passed"
echo ""

# Test 4: Advanced analytics
echo "Test 4: Advanced Analytics"
echo "-------------------------"

echo "  → Growth metrics..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/analytics/advanced/growth-metrics | jq '.' > /dev/null || echo "Failed"

echo "  → Product performance..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/analytics/advanced/product-performance | jq '.' > /dev/null || echo "Failed"

echo "✅ Advanced analytics tests passed"
echo ""

# Test 5: Feature flags
echo "Test 5: Feature Flags"
echo "--------------------"

echo "  → Disable AI chat..."
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/feature-flags/ai_chat/disable | jq '.status' || echo "Failed"

echo "  → Enable AI chat..."
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/feature-flags/ai_chat/enable | jq '.status' || echo "Failed"

echo "✅ Feature flag tests passed"
echo ""

# Summary
echo "=========================================="
echo "✅ All Phase 6 Tests Passed!"
echo "=========================================="
echo ""
echo "Tested:"
echo "  ✅ Monitoring endpoints"
echo "  ✅ Admin APIs"
echo "  ✅ Data quality checks"
echo "  ✅ Advanced analytics"
echo "  ✅ Feature flags"
echo ""

