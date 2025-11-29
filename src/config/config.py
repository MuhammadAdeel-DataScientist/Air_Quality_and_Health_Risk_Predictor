"""
Configuration file for Air Quality Predictor
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly set .env location to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Root folder
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"Warning: .env file not found at {ENV_PATH}")

# Base directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# API Configuration
class APIConfig:
    """API keys and endpoints"""
    
    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_AIR_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    # IQAir API
    IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")
    IQAIR_BASE_URL = "https://api.airvisual.com/v2"
    
    # OpenAQ API - Now requires authentication for v3
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")  # NEW: Add API key
    OPENAQ_BASE_URL = "https://api.openaq.org/v3"  # Updated to v3
    
    # WAQI (World Air Quality Index) API
    WAQI_API_KEY = os.getenv("WAQI_API_KEY")
    WAQI_BASE_URL = "https://api.waqi.info"


# Database Configuration
class DatabaseConfig:
    """Database connection settings"""
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "air_quality_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    
    # SQLAlchemy connection string
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Alternative: SQLite for development
    SQLITE_URL = f"sqlite:///{DATA_DIR}/air_quality.db"


# Model Configuration
class ModelConfig:
    """Machine learning model parameters"""
    
    # LSTM Model
    LSTM_SEQUENCE_LENGTH = 168  # 1 week of hourly data
    LSTM_FORECAST_HORIZON = 24  # Predict next 24 hours
    LSTM_UNITS = [128, 64]
    LSTM_DROPOUT = 0.2
    LSTM_BATCH_SIZE = 32
    LSTM_EPOCHS = 50
    LSTM_LEARNING_RATE = 0.001
    
    # Prophet Model
    PROPHET_CHANGEPOINT_PRIOR_SCALE = 0.05
    PROPHET_SEASONALITY_PRIOR_SCALE = 10
    PROPHET_HOLIDAYS_PRIOR_SCALE = 10
    
    # XGBoost Model
    XGB_N_ESTIMATORS = 1000
    XGB_MAX_DEPTH = 7
    XGB_LEARNING_RATE = 0.01
    XGB_SUBSAMPLE = 0.8
    
    # Random Forest
    RF_N_ESTIMATORS = 500
    RF_MAX_DEPTH = 20
    RF_MIN_SAMPLES_SPLIT = 5
    
    # Train/Test split
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42


# Feature Engineering Configuration
class FeatureConfig:
    """Feature engineering parameters"""
    
    # Lag features (in hours)
    LAG_FEATURES = [1, 3, 6, 12, 24, 48, 72, 168]  # 1hr to 1 week
    
    # Rolling window features (in hours)
    ROLLING_WINDOWS = [3, 6, 12, 24, 48, 72]
    
    # Pollutants to track
    POLLUTANTS = ['pm25', 'pm10', 'no2', 'so2', 'o3', 'co']
    
    # Weather features
    WEATHER_FEATURES = ['temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction']
    
    # Temporal features
    TEMPORAL_FEATURES = ['hour', 'day_of_week', 'month', 'season', 'is_weekend', 'is_holiday']


# Health Risk Configuration
class HealthConfig:
    """Health risk assessment thresholds and categories"""
    
    # AQI Breakpoints (US EPA standard)
    AQI_BREAKPOINTS = {
        'Good': (0, 50),
        'Moderate': (51, 100),
        'Unhealthy for Sensitive Groups': (101, 150),
        'Unhealthy': (151, 200),
        'Very Unhealthy': (201, 300),
        'Hazardous': (301, 500)
    }
    
    # Color codes for AQI levels
    AQI_COLORS = {
        'Good': '#00E400',
        'Moderate': '#FFFF00',
        'Unhealthy for Sensitive Groups': '#FF7E00',
        'Unhealthy': '#FF0000',
        'Very Unhealthy': '#8F3F97',
        'Hazardous': '#7E0023'
    }
    
    # Vulnerable groups
    VULNERABLE_GROUPS = [
        'children',
        'elderly',
        'pregnant_women',
        'asthma_patients',
        'heart_disease_patients',
        'athletes'
    ]
    
    # Risk thresholds for vulnerable groups (lower than general population)
    VULNERABLE_AQI_THRESHOLD = 100


# Data Collection Configuration
class DataCollectionConfig:
    """Data collection parameters"""
    
    # Cities to collect data for (can be expanded)
    MAJOR_CITIES = [
        {'name': 'Delhi', 'country': 'IN', 'lat': 28.7041, 'lon': 77.1025},
        {'name': 'Mumbai', 'country': 'IN', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Beijing', 'country': 'CN', 'lat': 39.9042, 'lon': 116.4074},
        {'name': 'London', 'country': 'GB', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'New York', 'country': 'US', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'Los Angeles', 'country': 'US', 'lat': 34.0522, 'lon': -118.2437},
        {'name': 'Tokyo', 'country': 'JP', 'lat': 35.6762, 'lon': 139.6503},
        {'name': 'São Paulo', 'country': 'BR', 'lat': -23.5505, 'lon': -46.6333},
        {'name': 'Mexico City', 'country': 'MX', 'lat': 19.4326, 'lon': -99.1332},
        {'name': 'Cairo', 'country': 'EG', 'lat': 30.0444, 'lon': 31.2357}
    ]
    
    # Data collection frequency
    COLLECTION_INTERVAL_HOURS = 1
    
    # Historical data range
    HISTORICAL_YEARS = 3  # Collect last 3 years
    
    # Request timeout
    REQUEST_TIMEOUT = 30  # seconds
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds


# Logging Configuration
class LoggingConfig:
    """Logging settings"""
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "air_quality.log"


# Application Configuration
class AppConfig:
    """General application settings"""
    
    APP_NAME = "Air Quality & Health Risk Predictor"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # API rate limiting
    RATE_LIMIT_CALLS = 100
    RATE_LIMIT_PERIOD = 3600  # 1 hour in seconds
    
    # Caching
    CACHE_EXPIRY_SECONDS = 3600  # 1 hour
    
    # Timezone
    TIMEZONE = "UTC"


# Export all configs
class Config:
    """Main configuration class"""
    api = APIConfig
    database = DatabaseConfig
    model = ModelConfig
    feature = FeatureConfig
    health = HealthConfig
    data_collection = DataCollectionConfig
    logging = LoggingConfig
    app = AppConfig
    
    # Paths
    base_dir = BASE_DIR
    data_dir = DATA_DIR
    raw_data_dir = RAW_DATA_DIR
    processed_data_dir = PROCESSED_DATA_DIR
    models_dir = MODELS_DIR
    logs_dir = LOGS_DIR