#!/bin/bash
# Setup script for Phase 6

set -e

echo "🔧 Setting up Phase 6: Launch Readiness"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p scripts
mkdir -p tests
mkdir -p k8s

# Check environment variables
echo ""
echo "Checking environment variables..."

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "⚠️  Warning: GCP_PROJECT_ID not set"
else
    echo "✅ GCP_PROJECT_ID: $GCP_PROJECT_ID"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️  Warning: JWT_SECRET_KEY not set (using default)"
else
    echo "✅ JWT_SECRET_KEY: Set"
fi

# Test imports
echo ""
echo "Testing imports..."
python3 -c "
try:
    from app.main import app
    from app.services.observability import StructuredLogger
    from app.services.feature_flags import feature_flags
    from app.services.data_quality import data_quality_checker
    print('✅ All Phase 6 imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Run pre-launch checks
echo ""
echo "Running basic health checks..."
python3 -c "
from app.config import settings
print(f'Environment: {settings.ENVIRONMENT}')
print(f'Version: {settings.VERSION}')
print(f'Rate Limit: {settings.RATE_LIMIT_PER_MINUTE}/min')
print(f'Cache Enabled: {settings.ENABLE_CACHE}')
print('✅ Configuration loaded successfully')
"

echo ""
echo "✅ Phase 6 setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the server: uvicorn app.main:app --reload --port 8000"
echo "  2. Test endpoints: python3 scripts/test_advanced_analytics.py"
echo "  3. Run pre-launch: python3 scripts/pre_launch_checklist.py"
echo "  4. Launch: ./launch.sh"
echo ""

