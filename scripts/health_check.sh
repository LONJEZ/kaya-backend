#!/bin/bash
# Health check script for monitoring

BASE_URL=${1:-"http://localhost:8007"}

echo "🏥 Kaya AI Health Check"
echo "======================="
echo "URL: $BASE_URL"
echo ""

# Basic health
echo "1. Basic Health..."
HEALTH=$(curl -s "$BASE_URL/health")
STATUS=$(echo $HEALTH | jq -r '.status')
echo "   Status: $STATUS"

if [ "$STATUS" != "healthy" ]; then
    echo "   ❌ Health check failed"
    exit 1
fi
echo "   ✅ Healthy"
echo ""

# Detailed health
echo "2. Detailed Health..."
DETAILED=$(curl -s "$BASE_URL/api/monitoring/health/detailed")
echo $DETAILED | jq '.'
echo ""

# Readiness
echo "3. Readiness..."
READINESS=$(curl -s "$BASE_URL/api/monitoring/health/readiness")
READY_STATUS=$(echo $READINESS | jq -r '.status')
echo "   Status: $READY_STATUS"

if [ "$READY_STATUS" != "ready" ]; then
    echo "   ⚠️  Not ready"
else
    echo "   ✅ Ready"
fi
echo ""

# Metrics (requires auth)
if [ -n "$TOKEN" ]; then
    echo "4. Metrics..."
    METRICS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/monitoring/metrics")
    echo $METRICS | jq '.'
fi

echo ""
echo "✅ Health check complete"

