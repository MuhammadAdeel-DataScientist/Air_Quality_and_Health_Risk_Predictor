# Air Quality & Health Risk Predictor

## Overview
An end-to-end data science project that predicts air quality and assesses health risks for different demographics using machine learning.

## Features
- Real-time AQI predictions for any location
- 7-day and 30-day forecasts using LSTM and Prophet models
- Health risk assessment for vulnerable groups
- Interactive pollution heatmaps
- Historical trend analysis

## Tech Stack
- **ML/DL**: TensorFlow, Keras, Prophet, Scikit-learn
- **Backend**: FastAPI, PostgreSQL
- **Frontend**: React.js / Streamlit
- **Deployment**: Heroku / AWS
- **APIs**: OpenWeatherMap, IQAir, OpenAQ

## Project Status
Work in Progress

## Getting Started

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd air-quality-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your API keys
3. Run data collection scripts

## Project Structure
```
air-quality-predictor/
├── data/              # Data storage
├── notebooks/         # Jupyter notebooks
├── src/              # Source code
├── frontend/         # Web interface
├── tests/            # Unit tests
└── docs/             # Documentation
```

## Results
Coming soon...

## Author
Muhammad Adeel 

## License
MIT License

