FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Create a startup script with better error handling
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Decoding GCP credentials..."\n\
if [ -z "$GCP_CREDENTIALS_BASE64" ]; then\n\
    echo "ERROR: GCP_CREDENTIALS_BASE64 environment variable is not set!"\n\
    exit 1\n\
fi\n\
echo "$GCP_CREDENTIALS_BASE64" | base64 -d > /app/credentials.json\n\
if [ ! -f /app/credentials.json ]; then\n\
    echo "ERROR: Failed to create credentials.json"\n\
    exit 1\n\
fi\n\
echo "Credentials file created successfully"\n\
ls -lh /app/credentials.json\n\
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
