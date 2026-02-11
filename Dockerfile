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
COPY data/models/ ./data/models/
COPY data/processed/ ./data/processed/
COPY data/explainability/ ./data/explainability/

# Create logs directory
RUN mkdir -p logs

# Expose Streamlit port (NOT 8000!)
EXPOSE 8501

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Create startup script that runs BOTH services
RUN echo '#!/bin/bash\n\
echo "Starting backend API on port 8000..."\n\
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &\n\
echo "Waiting for backend to start..."\n\
sleep 10\n\
echo "Starting Streamlit frontend on port 8501..."\n\
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start both services
CMD ["/bin/bash", "/app/start.sh"]