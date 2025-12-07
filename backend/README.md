# Air Quality Prediction API

FastAPI backend for real-time air quality predictions and health risk assessments.

## 🚀 Quick Start

### 1. Setup

```bash
# Create backend directory structure
mkdir -p backend/app
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Server

```bash
# From project root
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:** http://localhost:8000

**Interactive Docs:** http://localhost:8000/docs

---

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API documentation |

### Prediction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Predict AQI from features |
| GET | `/api/current/{city}` | Get current AQI for city |
| GET | `/api/forecast/{city}` | Get hourly forecast |

### Health Risk Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/health-risk` | Get health risk assessment |
| GET | `/api/vulnerable-groups` | List vulnerable groups |

### Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities` | List available cities |
| GET | `/api/stats` | Overall statistics |

---

## 🔧 Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "features_loaded": true,
  "risk_calculator_ready": true
}
```

### 2. Get Current AQI for City

```bash
curl http://localhost:8000/api/current/delhi
```

**Response:**
```json
{
  "city": "delhi",
  "timestamp": "2024-01-15T10:30:00",
  "aqi": 156.4,
  "category": "Unhealthy",
  "risk_level": "High",
  "health_message": "Some members may experience health effects...",
  "outdoor_activity": "Avoid Prolonged Exertion",
  "mask_recommendation": "N95 mask recommended",
  "recommendations": [
    "Everyone should reduce prolonged outdoor exertion",
    "Keep windows closed",
    "Use air purifiers indoors"
  ]
}
```

### 3. Get Forecast

```bash
curl http://localhost:8000/api/forecast/delhi?hours=24
```

**Response:**
```json
{
  "city": "delhi",
  "forecast": [
    {
      "hour": 0,
      "timestamp": "2024-01-15T10:00:00",
      "aqi": 145.2,
      "category": "Unhealthy for Sensitive Groups",
      "risk_level": "Moderate"
    },
    ...
  ],
  "best_hour": 13,
  "worst_hour": 20
}
```

### 4. Health Risk Assessment

```bash
curl -X POST http://localhost:8000/api/health-risk \
  -H "Content-Type: application/json" \
  -d '{
    "aqi": 165,
    "vulnerable_groups": ["asthma_patients", "children"]
  }'
```

**Response:**
```json
{
  "aqi": 165,
  "aqi_category": "Unhealthy",
  "risk_level": "Very High",
  "health_message": "Some members of general public may experience...",
  "recommendations": [
    "Everyone should reduce prolonged outdoor exertion",
    "Sensitive groups should avoid prolonged outdoor exertion",
    "Keep windows closed"
  ],
  "outdoor_activity_level": "Minimize Outdoor Activity",
  "mask_recommendation": "N95 mask recommended for everyone outdoors",
  "vulnerable_group_warnings": {
    "asthma_patients": "High risk of asthma attacks...",
    "children": "Children should avoid prolonged outdoor activities..."
  }
}
```

### 5. List Available Cities

```bash
curl http://localhost:8000/api/cities
```

**Response:**
```json
{
  "cities": ["Beijing", "Cairo", "Delhi", "London", ...],
  "count": 10
}
```

### 6. Get Statistics

```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "total_predictions": 3384,
  "average_aqi": 64.8,
  "median_aqi": 39.0,
  "max_aqi": 500.0,
  "min_aqi": 2.0,
  "category_distribution": {
    "Good": 1334,
    "Moderate": 746,
    "Unhealthy": 605
  },
  "cities_count": 10
}
```

---

## 🧪 Testing

### Using cURL

```bash
# Test health check
curl http://localhost:8000/health

# Test current AQI
curl http://localhost:8000/api/current/london

# Test forecast
curl http://localhost:8000/api/forecast/beijing?hours=12
```

### Using Python

```python
import requests

# Get current AQI
response = requests.get("http://localhost:8000/api/current/delhi")
data = response.json()
print(f"AQI: {data['aqi']}, Category: {data['category']}")

# Health risk assessment
risk_response = requests.post(
    "http://localhost:8000/api/health-risk",
    json={"aqi": 150, "vulnerable_groups": ["children"]}
)
print(risk_response.json())
```

---

## 📦 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   └── main.py              # Main API application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🔒 Security Notes

- CORS is currently set to allow all origins (`*`) for development
- For production, restrict CORS to specific domains
- Add authentication for sensitive endpoints
- Use environment variables for secrets

---

## 🚀 Production Deployment

### Option 1: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 2: Cloud Platforms

- **Heroku:** `git push heroku main`
- **AWS:** Deploy to EC2/ECS/Lambda
- **Google Cloud:** Deploy to Cloud Run
- **Azure:** Deploy to App Service

---

## 📊 Performance

- **Prediction latency:** < 50ms
- **Concurrent requests:** 100+
- **Memory usage:** ~500MB (with model loaded)

---

## 🐛 Troubleshooting

### Model not loading
- Ensure model file exists at: `../data/models/best_model_gradientboosting.pkl`
- Check file paths are correct

### Import errors
- Install all requirements: `pip install -r requirements.txt`
- Ensure project structure is correct

### Port already in use
- Change port: `uvicorn app.main:app --port 8001`
- Or kill existing process

---

## 📝 API Documentation

Full interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🎯 Next Steps

1. ✅ Backend API (Current)
2. 🔄 Frontend Dashboard (Week 9-10)
3. ⏳ Deployment (Week 13)
4. ⏳ Monitoring & Scaling

---

**Built with:** FastAPI, Python, ML Models, Health Risk Assessment