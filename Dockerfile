# Production Dockerfile for SolisCloud Mock API System
FROM python:3.11-slim AS builder

WORKDIR /workspace

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in a virtual environment to make image lightweight
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-privileged system user and group for maximum runtime security
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser -d /app -s /sbin/nologin appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application package
COPY app/ ./app
COPY .env .

# Adjust ownership to prevent root writes
RUN chown -R appuser:appuser /app

# Switch to the secure non-root user
USER appuser

# Expose default uvicorn port
EXPOSE 8000

# Start Uvicorn pointing directly to the modular application entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
