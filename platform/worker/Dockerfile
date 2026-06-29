FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by some ML packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker application code
COPY app/ ./app/

# SupportRAG is bind-mounted at /supportrag in docker-compose.yml
# (./SupportRAG:/supportrag:ro) — no COPY needed here.
# The processor auto-detects /supportrag at runtime.

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the worker
CMD ["python", "-m", "app.main"]
