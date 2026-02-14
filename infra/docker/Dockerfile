# Multi-stage build for FastAPI RAG Gateway
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ensure requirements are available in final image and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python dependencies from builder (fallback for any user-installed assets)
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Install application in development mode (editable)
RUN cd /app && pip install -e .

# Copy and make startup script executable
COPY infra/docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set PATH for user-installed packages
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUSERBASE=/root

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run FastAPI with startup script
CMD ["/app/start.sh"]
