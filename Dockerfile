FROM python:3.10-slim

# Create a non-root user (Hugging Face Spaces runs as user ID 1000)
RUN useradd -m -u 1000 user

WORKDIR /app

# Set necessary environment variables
# HF_HOME ensures Hugging Face models are cached in a writable directory
ENV HOME=/home/user \
    PYTHONPATH=/app \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/app/data/hf_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership to 'user'
COPY --chown=user:user . .

# Create necessary runtime directories and give explicit permissions
RUN mkdir -p data/vector_store logs data/hf_cache && \
    chmod -R 777 /app/data /app/logs

# Switch to the non-root user to respect Hugging Face Spaces security
USER user

# Expose Hugging Face Space port (Requires 7860)
EXPOSE 7860

# Run the application
# - Using Gunicorn to manage Uvicorn workers for production stability
# - 1 worker ensures ML models don't load twice and cause memory crashes
# - High timeout (300s) because PyTorch embedding models take time to load
CMD ["gunicorn", "src.api.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "1", "--bind", "0.0.0.0:7860", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-"]
