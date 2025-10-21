#!/bin/bash
# verify_api_key.sh - Check if Gemini API key is valid

echo "🔍 Verifying Gemini API Key"
echo "==========================="
echo ""

# Get API key from .env
if [ -f .env ]; then
    GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2 | tr -d ' ')
    
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "❌ GEMINI_API_KEY is empty in .env!"
        echo ""
        echo "Fix: Add your API key to .env:"
        echo "GEMINI_API_KEY=AIzaSyBswilasKs4bCGbBggNEBPNQWPDxF_tJw0"
        echo ""
        echo "Get key from: https://aistudio.google.com/app/apikey"
        exit 1
    fi
    
    echo "✅ Found API key: ${GEMINI_API_KEY:0:20}..."
    echo ""
    
    # Test 1: List available models
    echo "1️⃣ Testing API key by listing models..."
    echo ""
    
    RESPONSE=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY")
    
    # Check if response contains error
    if echo "$RESPONSE" | grep -q '"error"'; then
        echo "❌ API Key Error:"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        echo "🔧 Fixes:"
        echo "1. Get a new API key: https://aistudio.google.com/app/apikey"
        echo "2. Make sure you copied the ENTIRE key"
        echo "3. Check if key has been revoked in AI Studio"
        exit 1
    fi
    
    echo "✅ API key is valid!"
    echo ""
    
    # Test 2: Show available models
    echo "2️⃣ Available models for your API key:"
    echo ""
    
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'models' in data:
    print('Model Name | Supports generateContent')
    print('-' * 50)
    for model in data['models']:
        name = model.get('name', '').replace('models/', '')
        methods = model.get('supportedGenerationMethods', [])
        supports = '✅' if 'generateContent' in methods else '❌'
        print(f'{name:30} | {supports}')
" 2>/dev/null
    
    echo ""
    
    # Test 3: Try generating content with gemini-1.5-flash
    echo "3️⃣ Testing gemini-1.5-flash content generation..."
    echo ""
    
    TEST_RESPONSE=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{"contents":[{"parts":[{"text":"Say hi"}]}]}')
    
    if echo "$TEST_RESPONSE" | grep -q '"error"'; then
        echo "❌ generateContent test failed:"
        echo "$TEST_RESPONSE" | python3 -m json.tool
        echo ""
        
        # Try alternate model names
        echo "🔄 Trying alternate model names..."
        echo ""
        
        for model in "gemini-1.5-flash-001" "gemini-1.5-flash-latest" "gemini-pro"; do
            echo "   Testing: $model"
            ALT_RESPONSE=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$GEMINI_API_KEY" \
              -H 'Content-Type: application/json' \
              -d '{"contents":[{"parts":[{"text":"Hi"}]}]}' | head -c 200)
            
            if ! echo "$ALT_RESPONSE" | grep -q '"error"'; then
                echo "   ✅ $model WORKS!"
                echo ""
                echo "💡 Use this model: $model"
                echo ""
                echo "Update your .env:"
                echo "GEMINI_MODEL=$model"
                exit 0
            else
                echo "   ❌ $model failed"
            fi
        done
    else
        echo "✅ gemini-1.5-flash works perfectly!"
        echo ""
        echo "Response preview:"
        echo "$TEST_RESPONSE" | python3 -m json.tool | head -20
    fi
    
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "🎯 Summary:"
echo "==========="
echo ""
echo "If you got here with errors, your API key might be:"
echo "1. Invalid or expired"
echo "2. From wrong service (Vertex AI vs AI Studio)"
echo "3. Restricted/rate-limited"
echo ""
echo "Get a fresh key: https://aistudio.google.com/app/apikey"