#!/bin/bash
# ============================================================================
# FILE: install_phase6.sh
# ============================================================================
# Complete installation script for Phase 6

set -e

echo "🚀 Kaya AI Backend - Phase 6 Installation"
echo "=========================================="
echo ""

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo "--------------------------------"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found"
    exit 1
fi
echo "✅ pip3 found"

# Step 2: Create virtual environment
echo ""
echo "Step 2: Setting up virtual environment..."
echo "----------------------------------------"

if [ -d "venv" ]; then
    echo "⚠️  venv already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate
source venv/bin/activate
echo "✅ Virtual environment activated"

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
echo "----------------------------------"

pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 4: Create environment file
echo ""
echo "Step 4: Setting up environment..."
echo "--------------------------------"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo "⚠️  Please edit .env with your credentials:"
    echo "   - GCP_PROJECT_ID"
    echo "   - GOOGLE_APPLICATION_CREDENTIALS"
    echo "   - JWT_SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

# Step 5: Create necessary directories
echo ""
echo "Step 5: Creating directories..."
echo "-------------------------------"

mkdir -p logs
mkdir -p scripts
mkdir -p tests
mkdir -p k8s
mkdir -p sample_data
echo "✅ Directories created"

# Step 6: Test imports
echo ""
echo "Step 6: Testing imports..."
echo "-------------------------"

python3 << 'EOF'
import sys
try:
    # Test basic imports
    from app.main import app
    from app.config import settings
    from app.auth import create_access_token
    
    # Test Phase 6 imports
    from app.services.observability import StructuredLogger
    from app.services.feature_flags import feature_flags, Feature
    from app.services.data_quality import data_quality_checker
    from app.services.monitoring import metrics_collector
    
    # Test API imports
    from app.api import admin, data_quality, monitoring
    
    print("✅ All imports successful")
    print(f"✅ Version: {settings.VERSION}")
    print(f"✅ Environment: {settings.ENVIRONMENT}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

# Step 7: Initialize BigQuery (optional)
echo ""
echo "Step 7: BigQuery initialization..."
echo "----------------------------------"
echo "Do you want to initialize BigQuery tables now? (y/n)"
read -p "> " init_bq

if [ "$init_bq" = "y" ]; then
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo "⚠️  GCP_PROJECT_ID not set. Skipping BigQuery initialization."
    else
        python3 scripts/init_bigquery.py
        echo "✅ BigQuery tables initialized"
    fi
else
    echo "⏭️  Skipping BigQuery initialization"
fi

# Step 8: Summary
echo ""
echo "=========================================="
echo "✅ Phase 6 Installation Complete!"
echo "=========================================="
echo ""
echo "Installation Summary:"
echo "  ✅ Virtual environment created"
echo "  ✅ Dependencies installed"
echo "  ✅ Environment file ready"
echo "  ✅ Directories created"
echo "  ✅ Imports verified"
echo ""
echo "Next Steps:"
echo "  1. Edit .env with your GCP credentials"
echo "  2. Start server: make run"
echo "  3. Test: make test-phase6"
echo "  4. View docs: http://localhost:8007/docs"
echo ""
echo "Quick Commands:"
echo "  make run          - Start development server"
echo "  make test         - Run all tests"
echo "  make health       - Check system health"
echo "  make deploy       - Deploy to production"
echo ""

