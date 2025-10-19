#!/bin/bash
# Quick update script for authentication

echo "🔐 Updating Authentication System"
echo "=================================="
echo ""

# 1. Update users table schema
echo "1. Updating BigQuery users table..."
python3 scripts/update_users_table.py
echo ""

# 2. Restart Docker container
echo "2. Restarting backend..."
docker-compose restart kaya-backend
echo ""

# Wait for startup
echo "Waiting for backend to start..."
sleep 5

# 3. Test authentication
echo "3. Testing authentication..."
python3 scripts/test_auth.py
echo ""

echo "✅ Authentication update complete!"