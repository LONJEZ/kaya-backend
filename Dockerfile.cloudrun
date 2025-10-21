FROM python:3.11-slim as builder
WORKDIR /app
# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ git \
    && rm -rf /var/lib/apt/lists/*
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
# Copy Python packages from builder
COPY --from=builder /usr/local /usr/local
# Copy application
COPY app/ ./app/
# Non-root user
RUN useradd -m -u 1000 kaya && chown -R kaya:kaya /app
USER kaya
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
