#!/bin/bash
# Demo Phase 6 features for judges

set -e

echo "🎬 Kaya AI Backend - Phase 6 Demo"
echo "===================================="
echo "Launch Readiness & Production Features"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check server
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}⚠️  Server not running. Please start it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server is operational${NC}"
echo ""

# Get token
TOKEN=$(python3 -c "from app.auth import create_access_token; print(create_access_token({'sub': 'demo-user', 'business_name': 'Demo Business'}))")

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  1. Advanced Observability                         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 System Statistics${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/system/stats | jq '{
    environment: .environment,
    version: .version,
    total_requests: .metrics.total_requests,
    total_errors: .metrics.total_errors,
    feature_flags: .feature_flags
  }'

echo ""
echo -e "${BLUE}🏥 Health Status${NC}"
curl -s http://localhost:8000/api/monitoring/health/detailed | jq '{
    status: .status,
    services: .services
  }'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  2. Data Quality Monitoring                        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}🔍 Data Quality Check${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/check | jq '{
    overall_status: .overall_status,
    checks: .checks | to_entries | map({
      check: .key,
      passed: .value.passed,
      message: .value.message
    })
  }'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  3. Feature Flags Demo                             ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}🎛️ Current Feature Flags${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/system/stats | jq '.feature_flags'

echo ""
echo -e "${BLUE}Disabling AI Chat feature...${NC}"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/feature-flags/ai_chat/disable | jq '.'

echo ""
echo -e "${BLUE}Re-enabling AI Chat feature...${NC}"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/feature-flags/ai_chat/enable | jq '.'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  4. Performance Metrics                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📈 Application Metrics${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/metrics | jq '.'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  5. Advanced Analytics Preview                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Growth Metrics${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/analytics/advanced/growth-metrics | jq '.'

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Phase 6 Demo Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Phase 6 Features Demonstrated:"
echo "  ✅ Advanced observability & monitoring"
echo "  ✅ Data quality checks"
echo "  ✅ Feature flags for safe rollout"
echo "  ✅ System health monitoring"
echo "  ✅ Performance metrics tracking"
echo ""
echo "📚 Full API Documentation: http://localhost:8007/docs"
echo ""