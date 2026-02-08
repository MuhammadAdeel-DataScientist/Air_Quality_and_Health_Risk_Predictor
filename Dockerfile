FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY data/models/ ./data/models/
COPY data/processed/ ./data/processed/
COPY data/explainability/ ./data/explainability/
COPY frontend/ ./frontend/
# Create necessary directories
RUN mkdir -p logs

# Expose port
EXPOSE 8501

# Health check
# Update health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run as non-root user (security best practice)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# With these lines:
RUN echo '#!/bin/bash\n\
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &\n\
sleep 5\n\
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start both services
CMD ["/app/start.sh"]