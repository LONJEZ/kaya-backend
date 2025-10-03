# Kaya AI Backend

Smart Business Assistant API for African SMEs. Powers analytics, data ingestion, and AI-driven insights.

## 🎯 Quick Start (For Judges)

```bash
# 1. Clone and navigate
git clone <repo-url>
cd kaya-backend

# 2. Set up environment
cp .env.example .env
# Edit .env with your GCP credentials

# 3. Run demo script
chmod +x demo.sh
./demo.sh
```

The backend will start at `http://localhost:8000` with interactive API docs at `/docs`.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│  FastAPI     │─────▶│  BigQuery   │
│  (Next.js)  │      │  Backend     │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Vertex AI   │
                     │  (Gemini)    │
                     └──────────────┘
```

## 📋 Phase 1: Core Setup (Current)

### What's Included
- ✅ FastAPI application with async support
- ✅ JWT authentication
- ✅ BigQuery schema (transactions, products, users)
- ✅ Partitioned tables for cost optimization
- ✅ CORS middleware for frontend integration
- ✅ Docker containerization
- ✅ Health check endpoints
- ✅ Structured logging

### API Endpoints

#### Public
- `GET /` - Service info
- `GET /health` - Health check

#### Authenticated (requires JWT token)
- `GET /api/analytics/overview` - Dashboard metrics
- `GET /api/analytics/revenue-trends` - Revenue over time
- `GET /api/analytics/top-products` - Best sellers
- `GET /api/analytics/transactions` - Recent transactions
- `POST /api/chat/query` - AI chat interface
- `GET /api/settings` - User preferences
- `PUT /api/settings` - Update preferences

## 🔧 Environment Variables

```bash
# Required
GCP_PROJECT_ID=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
JWT_SECRET_KEY=your-secret-key

# Optional
BIGQUERY_DATASET=kaya_data
VERTEX_AI_LOCATION=us-central1
ENVIRONMENT=development
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t kaya-backend .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🧪 Testing

```bash
# Get JWT token
TOKEN=$(cat demo_token.txt)

# Test health endpoint
curl http://localhost:8000/health

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/analytics/overview

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What were my top products last month?", "user_id": "demo-user"}'
```

## 📊 BigQuery Schema

### Transactions Table (partitioned by date)
- `id`, `user_id`, `source`, `amount`, `currency`
- `date`, `timestamp`, `category`, `item_name`
- `payment_method`, `status`, `metadata`

### Products Table
- `id`, `user_id`, `name`, `category`
- `price`, `cost`, `margin`, `stock_quantity`

### Users Table
- `id`, `email`, `business_name`, `full_name`
- `currency`, `language`, `refresh_frequency`, `settings`

## 🚀 Next Steps (Phases 2-4)

### Phase 2: Data Ingestion
- [ ] Fivetran Connector SDK for Google Sheets
- [ ] CSV upload and parsing
- [ ] Mock M-Pesa/POS connectors
- [ ] Incremental sync with idempotency

### Phase 3: Real Analytics
- [ ] BigQuery query optimization
- [ ] Caching layer (Redis/in-memory)
- [ ] Real aggregations for dashboard

### Phase 4: AI Chat
- [ ] Elastic Search integration
- [ ] Vertex AI Gemini API
- [ ] RAG flow (embed → retrieve → generate)
- [ ] Structured JSON responses (<3s)

## 📝 License

MIT

## 👥 Authors

Kaya AI Team - Hackathon 2025