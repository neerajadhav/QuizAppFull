FROM python:3.12-slim AS builder

# --- Builder Stage ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir\
    -r requirements.txt

# --- Runtime Stage ---
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PORT=8000 \
    APP_ENV=dev

WORKDIR /app

# Create non-root user
RUN useradd -u 10001 -s /usr/sbin/nologin appuser && \
    mkdir -p /app && chown -R appuser:appuser /app

COPY --from=builder /venv /venv

COPY app/ /app/

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
