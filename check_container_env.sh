#!/bin/bash
# check_container_env.sh - Verify what the container sees

echo "🔍 Checking Container Environment"
echo "=================================="
echo ""

echo "1️⃣ Environment variables in container:"
echo ""
docker-compose exec -T kaya-backend env | grep -E "GEMINI|GCP" | while read line; do
    KEY=$(echo "$line" | cut -d= -f1)
    VALUE=$(echo "$line" | cut -d= -f2)
    
    if [ ! -z "$VALUE" ]; then
        # Mask sensitive data
        if [ ${#VALUE} -gt 20 ]; then
            echo "  $KEY=${VALUE:0:20}...${VALUE: -4}"
        else
            echo "  $KEY=$VALUE"
        fi
    else
        echo "  $KEY=(empty) ❌"
    fi
done

echo ""
echo "2️⃣ What config.py sees inside container:"
echo ""
docker-compose exec -T kaya-backend python3 -c "
from app.config import settings
print(f'  GEMINI_API_KEY: {settings.GEMINI_API_KEY[:20] + \"...\" if settings.GEMINI_API_KEY else \"(empty)\"}')
print(f'  GEMINI_MODEL: {settings.GEMINI_MODEL}')
print(f'  GCP_PROJECT_ID: {settings.GCP_PROJECT_ID}')
" 2>&1

echo ""
echo "3️⃣ What gemini_service.py is actually using:"
echo ""
docker-compose exec -T kaya-backend python3 -c "
from app.services.gemini_service import gemini_service
print(f'  API URL: {gemini_service.api_url}')
print(f'  Model: {gemini_service.model}')
print(f'  Has API key: {\"Yes\" if gemini_service.api_key else \"No\"} ({len(gemini_service.api_key) if gemini_service.api_key else 0} chars)')
" 2>&1

echo ""
echo "4️⃣ Checking .env file on host:"
echo ""
if [ -f .env ]; then
    echo "  Found .env file ✅"
    echo ""
    if grep -q "GEMINI_API_KEY=AIzaSy" .env; then
        KEY=$(grep GEMINI_API_KEY .env | cut -d= -f2)
        echo "  GEMINI_API_KEY: ${KEY:0:20}...${KEY: -4}"
    else
        echo "  GEMINI_API_KEY: ❌ Not found or invalid format"
    fi
    
    if grep -q "GEMINI_MODEL=" .env; then
        echo "  GEMINI_MODEL: $(grep GEMINI_MODEL .env | cut -d= -f2)"
    else
        echo "  GEMINI_MODEL: ❌ Not set"
    fi
else
    echo "  ❌ .env file not found!"
fi

echo ""
echo "5️⃣ Checking docker-compose.yml:"
echo ""
if grep -q "GEMINI_API_KEY" docker-compose.yml; then
    echo "  ✅ GEMINI_API_KEY is passed to container"
else
    echo "  ❌ GEMINI_API_KEY NOT in docker-compose.yml!"
    echo ""
    echo "  FIX: Add to docker-compose.yml under 'environment:':"
    echo "    - GEMINI_API_KEY=\${GEMINI_API_KEY}"
fi

if grep -q "GEMINI_MODEL" docker-compose.yml; then
    echo "  ✅ GEMINI_MODEL is passed to container"
else
    echo "  ⚠️  GEMINI_MODEL NOT in docker-compose.yml"
    echo "     (Will use default from config.py)"
fi

echo ""
echo "📋 Diagnosis:"
echo "============"
echo ""

# Get the actual values
HOST_KEY=$(grep GEMINI_API_KEY .env 2>/dev/null | cut -d= -f2 | tr -d ' ')
CONTAINER_KEY=$(docker-compose exec -T kaya-backend env 2>/dev/null | grep GEMINI_API_KEY | cut -d= -f2 | tr -d ' ')

if [ -z "$HOST_KEY" ]; then
    echo "❌ PROBLEM: No API key in .env file"
    echo "   Fix: Add GEMINI_API_KEY=your_key to .env"
elif [ -z "$CONTAINER_KEY" ]; then
    echo "❌ PROBLEM: API key in .env but not reaching container"
    echo "   Fix: Add to docker-compose.yml:"
    echo "        - GEMINI_API_KEY=\${GEMINI_API_KEY}"
    echo "   Then: docker-compose down && docker-compose up -d"
elif [ "$HOST_KEY" != "$CONTAINER_KEY" ]; then
    echo "⚠️  WARNING: API key in container differs from .env"
    echo "   Container needs restart to pick up changes"
    echo "   Fix: docker-compose restart kaya-backend"
else
    echo "✅ API key is properly configured"
    echo ""
    echo "   But you're still getting 404, which means:"
    echo "   1. The API key might be invalid/expired"
    echo "   2. The model name is wrong for your API key"
    echo "   3. There's a network/firewall issue"
    echo ""
    echo "   Run: ./verify_api_key.sh to test the key"
fi

echo ""