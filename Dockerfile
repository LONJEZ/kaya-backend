FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Use shell form to ensure proper execution
CMD echo "Decoding GCP credentials..." && \
    if [ -z "$GCP_CREDENTIALS_BASE64" ]; then \
        echo "ERROR: GCP_CREDENTIALS_BASE64 environment variable is not set!"; \
        exit 1; \
    fi && \
    echo "$GCP_CREDENTIALS_BASE64" | base64 -d > /app/credentials.json && \
    if [ ! -f /app/credentials.json ]; then \
        echo "ERROR: Failed to create credentials.json"; \
        exit 1; \
    fi && \
    echo "Credentials file created successfully" && \
    ls -lh /app/credentials.json && \
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
