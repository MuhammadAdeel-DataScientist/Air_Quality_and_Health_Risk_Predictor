FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY data/ ./data/

# Create logs directory
RUN mkdir -p logs

# Start BOTH services properly for Render
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
