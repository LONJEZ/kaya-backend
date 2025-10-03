#!/bin/bash
# Complete Phase 2 demo script

echo "🎬 Kaya AI Phase 2 Demo"
echo "======================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8007/health > /dev/null; then
    echo "❌ Backend is not running"
    echo "   Start it with: uvicorn app.main:app --reload"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Upload sample data
echo "📤 Step 1: Uploading sample data..."
python3 scripts/upload_sample_data.py

echo ""
echo "⏳ Step 2: Waiting for processing..."
sleep 5

echo ""
echo "🔍 Step 3: Verifying data in BigQuery..."
python3 scripts/verify_bigquery_data.py

echo ""
echo "🎉 Phase 2 Demo Complete!"
echo ""
echo "Try these API endpoints:"
echo "  GET  /api/analytics/overview"
echo "  GET  /api/analytics/transactions"
echo "  POST /api/ingestion/upload/csv"
echo ""
echo "View API docs: http://localhost:8007/docs"