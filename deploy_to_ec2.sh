#!/bin/bash

# Kaya Backend - EC2 Deployment Script
# Run this ON YOUR EC2 INSTANCE after SSH

set -e

echo "🚀 Kaya Backend EC2 Setup"
echo "=========================="
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
rm get-docker.sh

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo apt install -y docker-compose

# Install Git
echo "📦 Installing Git..."
sudo apt install -y git curl

echo ""
echo "✅ Prerequisites installed!"
echo ""
echo "⚠️  IMPORTANT: You need to log out and log back in for Docker permissions"
echo "   Run: exit"
echo "   Then reconnect with SSH"
echo ""
echo "After reconnecting, run:"
echo "  git clone https://github.com/YOUR_USERNAME/kaya-backend.git"
echo "  cd kaya-backend"
echo "  nano .env  # Add your credentials"
echo "  docker-compose up -d"
