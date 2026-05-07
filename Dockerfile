# ── Stage 1: Base ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Install deps in a separate layer for cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: App ─────────────────────────────────────────────────────────────
COPY . .

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

# Use gunicorn for production; 2 workers is sufficient for this app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
