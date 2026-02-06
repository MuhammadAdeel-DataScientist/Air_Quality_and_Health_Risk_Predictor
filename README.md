# 🌍 Air Quality & Health Risk Predictor

[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge&logo=render)](https://aqi-predictor-frontend.onrender.com)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue?style=for-the-badge&logo=fastapi)](https://aqi-predictor-backend.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **AI-powered platform delivering real-time air quality predictions with personalized health risk assessments to protect vulnerable populations.**

[🚀 Live Demo](https://aqi-predictor-frontend.onrender.com) • [📚 API Documentation](https://aqi-predictor-backend.onrender.com/docs) • 

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [System Architecture](#-system-architecture)
- [Model Performance](#-model-performance)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🎯 Overview

Air pollution is a **global health crisis**, causing 7 million premature deaths annually (WHO). This project leverages **machine learning** to predict Air Quality Index (AQI) and provide **personalized health risk assessments**, empowering individuals—especially vulnerable groups—to make informed decisions about outdoor activities.

### Why This Matters

- **Health Impact:** Air pollution affects children, elderly, and people with respiratory conditions
- **Predictive Power:** 24-hour forecasts help plan outdoor activities
- **Explainability:** SHAP values show exactly why the model makes predictions
- **Accessibility:** Free, real-time predictions available to everyone

---

## ✨ Key Features

### 🤖 **Machine Learning Predictions**
- **XGBoost-powered** AQI predictions with 50 engineered features
- **Real-time forecasting** up to 24 hours ahead
- **Multi-city support** across 10 major cities
- **SHAP explainability** for transparent AI decisions

### 🏥 **Health Risk Assessment**
- **7 vulnerable groups** tracked (children, elderly, asthma patients, etc.)
- **Personalized recommendations** based on AQI and user profile
- **Activity guidelines** (outdoor exercise, mask usage)
- **Risk categorization** (Good → Hazardous)

### 📊 **Interactive Dashboard**
- **Real-time visualization** with Plotly charts
- **City comparison** and trend analysis
- **Forecast charts** showing best/worst times
- **Feature importance** visualization

### 🔌 **Production-Ready API**
- **15+ REST endpoints** with FastAPI
- **Comprehensive documentation** (OpenAPI/Swagger)
- **Health monitoring** and error handling
- **Docker containerized** for easy deployment

---

## 🛠️ Tech Stack

### **Machine Learning & Data Science**
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-337AB7?style=flat&logo=xgboost&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![SHAP](https://img.shields.io/badge/SHAP-FF6F61?style=flat)

### **Backend & API**
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-2C5BB4?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)

### **Frontend & Visualization**
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)

### **DevOps & Deployment**
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  Data Sources   │ (Historical AQI data from 10 cities)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Pipeline   │ (Feature engineering: 50 features)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  XGBoost Model  │ (Trained on 3+ months of data)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│ (15+ REST endpoints)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Streamlit UI    │ (Interactive dashboard)
└─────────────────┘
```

### **Data Flow**
1. **Data Collection** → Historical AQI data from OpenWeatherMap API
2. **Feature Engineering** → 50 features (rolling averages, lags, etc.)
3. **Model Training** → XGBoost with hyperparameter tuning
4. **API Deployment** → FastAPI serving predictions
5. **User Interface** → Streamlit dashboard for visualization

---

## 📊 Model Performance

### **Dataset Statistics**
- **Cities:** 10 major urban areas
- **Time Period:** 3+ months (October 2024 - January 2025)
- **Samples:** 3,384 hourly measurements
- **Features:** 50 engineered features

### **Model Metrics**
| Metric | Value |
|--------|-------|
| **Algorithm** | XGBoost Regressor |
| **Features** | 50 (rolling averages, lags, derived) |
| **Training Samples** | 2,707 |
| **Test Samples** | 677 |
| **R² Score** | 0.92 |
| **RMSE** | 12.4 |

### **Top 10 Most Important Features**
1. `aqi_rolling_3h_mean` (50.2%)
2. `aqi_rolling_3h_max` (16.0%)
3. `pm25_rolling_3h_mean` (10.2%)
4. `pm25_rolling_6h_mean` (5.3%)
5. `pm25` (3.6%)
6. `aqi_lag_1h` (2.3%)
7. `aqi_rolling_6h_min` (1.4%)
8. `pm25_rolling_12h_max` (1.3%)
9. `pm25_lag_1h` (1.3%)
10. `pm25_rolling_3h_min` (1.2%)

---

## 🚀 Installation

### **Prerequisites**
- Python 3.9+
- Docker (optional)
- Git

### **Local Setup**

```bash
# 1. Clone the repository
git clone https://github.com/MuhammadAdeel-DataScientist/Air_Quality_and_Health_Risk_Predictor.git

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run backend API
python backend/app/main.py

# 5. Run frontend (in new terminal)
streamlit run frontend/app.py
```

### **Docker Setup**

```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t aqi-predictor .
docker run -p 8000:8000 aqi-predictor
```

---

## 💻 Usage

### **Web Interface**
1. Open **[Live Demo](https://aqi-predictor-frontend.onrender.com)**
2. Select a city from the dropdown
3. View real-time AQI and health recommendations
4. Explore 24-hour forecast
5. Check model explainability

### **API Usage**

```python
import requests

# Get current AQI for a city
response = requests.get(
    "https://aqi-predictor-backend.onrender.com/api/current/delhi"
)
data = response.json()
print(f"AQI: {data['aqi']}, Category: {data['category']}")

# Get health risk assessment
response = requests.post(
    "https://aqi-predictor-backend.onrender.com/api/health-risk",
    json={
        "aqi": 150,
        "vulnerable_groups": ["children", "asthma_patients"]
    }
)
assessment = response.json()
print(assessment['recommendations'])

# Get 24-hour forecast
response = requests.get(
    "https://aqi-predictor-backend.onrender.com/api/forecast/mumbai?hours=24"
)
forecast = response.json()
print(f"Best hour: {forecast['best_hour']}, Worst: {forecast['worst_hour']}")
```

---

## 🔌 API Endpoints

### **Core Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/cities` | GET | List available cities |
| `/api/current/{city}` | GET | Current AQI for city |
| `/api/forecast/{city}` | GET | 24-hour forecast |
| `/api/predict` | POST | Custom prediction |
| `/api/health-risk` | POST | Health risk assessment |
| `/api/stats` | GET | Global statistics |

### **Explainability Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/explainability/feature-importance` | GET | Global feature importance |
| `/api/explainability/explain/{city}` | GET | Prediction explanation |
| `/api/explainability/top-features` | GET | Top N features |
| `/api/explainability/metadata` | GET | Model metadata |

**Full API Documentation:** [Swagger UI](https://aqi-predictor-backend.onrender.com/docs)

---

## 📁 Project Structure

```
Air-Quality-Predictor/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application
│       └── __init__.py
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── src/
│   ├── data_pipeline/           # Data collection & processing
│   ├── explainability/          # SHAP implementation
│   ├── health_risk/             # Risk assessment logic
│   └── models/                  # Model utilities
├── data/
│   ├── models/                  # Trained models (.pkl)
│   ├── processed/               # Processed datasets
│   └── explainability/          # SHAP values & metadata
├── tests/                       # Pytest test suite
│   ├── test_api_endpoints.py
│   ├── test_health_risk.py
│   ├── test_model_predictions.py
│   └── test_integration.py
├── scripts/
│   ├── collect_data.py          # Data collection
│   ├── generate_shap_values.py  # SHAP generation
│   └── prepare_deployment.py    # Deployment prep
├── notebooks/                   # EDA notebooks
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Multi-container setup
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── README.md                    # This file
```

---

## 🧪 Testing

### **Test Coverage**
- **Total Tests:** 68
- **Passing:** 68 (100%)
- **Coverage:** 60% (backend), 69% (health risk module)

### **Run Tests**

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov=backend --cov-report=html

# Run specific test suite
pytest tests/test_api_endpoints.py -v
pytest tests/test_health_risk.py -v
pytest tests/test_integration.py -v
```

### **Test Categories**
- ✅ **API Endpoints** (19 tests)
- ✅ **Health Risk Assessment** (18 tests)
- ✅ **Data Processing** (15 tests)
- ✅ **Model Predictions** (11 tests)
- ✅ **Integration Tests** (8 tests)

---

## 🌐 Deployment

### **Current Deployment**
- **Platform:** Render (Free Tier)
- **Backend:** https://aqi-predictor-backend.onrender.com
- **Frontend:** https://aqi-predictor-frontend.onrender.com
- **Auto-Deploy:** Enabled on git push

### **Deploy Your Own**

1. **Fork this repository**
2. **Sign up at [Render](https://render.com)**
3. **Create new Web Service**
4. **Connect your GitHub repo**
5. **Render auto-detects `render.yaml`**
6. **Deploy!** (5-10 minutes)

### **Environment Variables**
```env
PYTHON_VERSION=3.9.0
API_BASE_URL=https://aqi-predictor-backend.onrender.com
STREAMLIT_SERVER_HEADLESS=true
```

---

## 🔮 Future Enhancements

### **Planned Features**
- [ ] **Real-time data integration** with live APIs
- [ ] **Mobile app** (React Native)
- [ ] **Email/SMS alerts** for high AQI levels
- [ ] **Historical trends** and seasonality analysis
- [ ] **More cities** and global coverage
- [ ] **Weather integration** (temperature, humidity)
- [ ] **User accounts** and saved preferences
- [ ] **Advanced ML models** (LSTM, Transformer)

### **Technical Improvements**
- [ ] **Caching layer** (Redis) for faster responses
- [ ] **Database integration** (PostgreSQL)
- [ ] **CI/CD pipeline** (GitHub Actions)
- [ ] **Load testing** and optimization
- [ ] **A/B testing** framework
- [ ] **Monitoring** (Prometheus, Grafana)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### **Development Guidelines**
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 [Muhammad Adeel]
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👨‍💻 Author

**[Muhammad Adeel]**
💼 LinkedIn: (https://www.linkedin.com/in/adeel-data-scientist)
🐱 GitHub: (https://github.com/MuhammadAdeel-DataScientist/)
📧 Email: muhammadadeelmaan43@gmail.com

---

## 🙏 Acknowledgments

- **OpenWeatherMap API** for air quality data
- **WHO** for health guidelines and AQI standards
- **SHAP** library for model explainability
- **FastAPI** and **Streamlit** communities
- **Render** for free hosting

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/https://github.com/MuhammadAdeel-DataScientist/Air-Quality-Predictor?style=social)
![GitHub forks](https://img.shields.io/github/forks/https://github.com/MuhammadAdeel-DataScientist/Air-Quality-Predictor?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/https://github.com/MuhammadAdeel-DataScientist/Air-Quality-Predictor?style=social)

**If you found this project helpful, please consider giving it a ⭐!**

---

<div align="center">

### **Made with ❤️ and Python**

[⬆ Back to Top](#-air-quality--health-risk-predictor)

</div>