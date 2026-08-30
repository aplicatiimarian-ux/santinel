# Multi-stage Dockerfile for SANTINEL Production
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels for faster installation
RUN pip install --user --no-cache-dir --compile \
    -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

LABEL maintainer="SANTINEL Team <dev@santinel.ai>"
LABEL version="1.0"
LABEL description="SANTINEL AI Coaching Assistant - Production"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use local pip packages
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy application code
COPY backend/ /app/backend/
COPY core/ /app/core/
COPY module/ /app/module/
COPY anonimizare/ /app/anonimizare/
COPY bridge/ /app/bridge/
COPY monitoring/ /app/monitoring/
COPY schema.sql /app/

# Copy configuration templates
COPY .env.example /app/.env.production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/api/v1/health || exit 1

# Expose port
EXPOSE 8002

# Non-root user for security
RUN useradd -m -u 1000 santinel && \
    chown -R santinel:santinel /app

USER santinel

# Startup script
CMD ["python", "-u", "backend/fastapi_backend.py"]
