#!/bin/bash

# Kaya AI Backend Demo Script
# This script sets up and runs the backend for judges

set -e

echo "🚀 Kaya AI Backend Demo Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your GCP credentials"
    echo "   Required: GCP_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS"
    read -p "Press enter when ready to continue..."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Initialize BigQuery tables
echo "🗄️  Initializing BigQuery tables..."
python3 -c "
from app.utils.bigquery_client import bq_client
bq_client.create_dataset()
bq_client.create_tables()
print('✅ BigQuery tables created successfully')
"

# Create demo JWT token
echo "🔑 Generating demo JWT token..."
python3 -c "
from app.auth import create_access_token
token = create_access_token({'sub': 'demo-user', 'business_name': 'Demo Electronics'})
print(f'\n📋 Demo JWT Token (valid for 24 hours):\n{token}\n')
" > demo_token.txt

echo "✅ Demo token saved to demo_token.txt"

# Start the server
echo ""
echo "🎯 Starting Kaya AI Backend..."
echo "================================"
echo "API Docs: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Use the token from demo_token.txt for authenticated requests"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000