# Backend Dockerfile

FROM python:3.10.13-slim

WORKDIR /app

# Install system dependencies (needed for numpy, xgboost, shap)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements only
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend + src only
COPY backend/ ./backend/
COPY src/ ./src/
COPY data/ ./data/

# Render provides $PORT — MUST use it
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]
