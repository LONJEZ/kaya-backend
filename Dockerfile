FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Decode credentials at runtime from environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

CMD echo "$GCP_CREDENTIALS_BASE64" | base64 -d > /app/credentials.json && \
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
