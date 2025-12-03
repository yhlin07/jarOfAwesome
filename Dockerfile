# Jar of Awesome - Production Dockerfile for Cloud Run
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies including gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code and data
COPY src/ ./src/
COPY affirmations_pregenerated.json .
COPY jar-of-awesome.md .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080
ENV RUN_MODE=http

# Cloud Run will set PORT dynamically
EXPOSE 8080

# Use gunicorn as production WSGI server (2025 best practices)
# --workers 1: Single worker to minimize memory and cold start
# --threads 8: Handle concurrent requests efficiently
# --timeout 0: Disable timeout (Cloud Run handles this)
# --bind :$PORT: Listen on Cloud Run's assigned port
# --access-logfile -: Log to stdout for Cloud Logging
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --access-logfile - --error-logfile - src.http_server:app
