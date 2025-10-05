#!/bin/bash
# Deploy Kaya AI Backend to Google Cloud Run

set -e

echo "🚀 Deploying Kaya AI Backend to Cloud Run"
echo "=========================================="

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"kaya-ai-demo"}
REGION="us-central1"
SERVICE_NAME="kaya-backend"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Build container
echo "📦 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Push to Container Registry
echo "⬆️  Pushing to Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,BIGQUERY_DATASET=kaya_data,ENVIRONMENT=production" \
  --set-secrets "JWT_SECRET_KEY=jwt-secret:latest" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 60 \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
