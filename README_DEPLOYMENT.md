# Kaya AI Backend - Deployment Guide

## Prerequisites

1. **Google Cloud Platform**
   - Project created
   - Billing enabled
   - APIs enabled: BigQuery, Vertex AI, Cloud Run, Secret Manager

2. **Local Setup**
   - Docker installed
   - gcloud CLI configured
   - Python 3.11+

## Quick Deploy to Cloud Run

```bash
# 1. Set project
export GCP_PROJECT_ID=your-project-id
gcloud config set project $GCP_PROJECT_ID

# 2. Enable APIs
gcloud services enable \
    bigquery.googleapis.com \
    aiplatform.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com

# 3. Create secrets
echo -n "your-jwt-secret" | gcloud secrets create jwt-secret --data-file=-

# 4. Build and deploy
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh
```

## Environment Variables

```bash
# Required
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=kaya_data
JWT_SECRET_KEY=your-secret-key

# Optional
VERTEX_AI_LOCATION=us-central1
ENABLE_CACHE=true
CACHE_TTL_SECONDS=300
```

## Local Development

```bash
# Start with docker-compose
docker-compose up -d

# Or run directly
uvicorn app.main:app --reload --port 8000
```

## Testing Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe kaya-backend \
    --region us-central1 \
    --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test with token
curl -H "Authorization: Bearer $TOKEN" \
    $SERVICE_URL/api/analytics/overview
```

## Monitoring

### Cloud Run Metrics
- Request count
- Request latency
- Error rate
- Container instance count

### Custom Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Custom metric", extra={"user_id": user_id})
```

## Scaling Configuration

```yaml
# cloud-run-config.yaml
minInstances: 1
maxInstances: 10
concurrency: 80
cpu: 2
memory: 2Gi
timeout: 60s
```

## Cost Optimization

1. **BigQuery**: Use partitioned tables
2. **Caching**: Enable 5-min TTL
3. **Cloud Run**: Set min instances = 1
4. **Vertex AI**: Batch embeddings when possible

## Security

1. **JWT Tokens**: Store secret in Secret Manager
2. **IAM**: Least privilege access
3. **VPC**: Optional private networking
4. **CORS**: Configure allowed origins

## Troubleshooting

### Common Issues

**Cold Starts**
```bash
# Set min instances
gcloud run services update kaya-backend --min-instances 1
```

**Memory Issues**
```bash
# Increase memory
gcloud run services update kaya-backend --memory 4Gi
```

**Timeout**
```bash
# Increase timeout
gcloud run services update kaya-backend --timeout 120
```

## Production Checklist

- [ ] JWT secret in Secret Manager
- [ ] BigQuery tables created and partitioned
- [ ] Vertex AI enabled
- [ ] CORS configured
- [ ] Monitoring enabled
- [ ] Error logging configured
- [ ] Health checks passing
- [ ] Load testing complete
- [ ] Backup strategy defined
- [ ] Documentation updated