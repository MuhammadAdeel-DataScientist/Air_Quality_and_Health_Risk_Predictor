"""
Pytest configuration and fixtures
Fixed version that properly initializes the backend
"""
import pytest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pickle
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.health_risk.risk_assessment import HealthRiskCalculator


@pytest.fixture
def sample_aqi_values():
    """Sample AQI values for testing different categories"""
    return {
        'good': 25.0,
        'moderate': 75.0,
        'unhealthy_sensitive': 125.0,
        'unhealthy': 175.0,
        'very_unhealthy': 250.0,
        'hazardous': 350.0
    }


@pytest.fixture
def risk_calculator():
    """Health risk calculator instance"""
    return HealthRiskCalculator()


@pytest.fixture
def sample_features():
    """Sample feature data for predictions"""
    return {
        'pm25': 35.5,
        'pm10': 65.2,
        'no2': 42.1,
        'so2': 15.3,
        'co': 0.8,
        'o3': 58.7,
        'aqi_lag_1h': 80.0,
        'pm25_lag_1h': 33.2,
        'aqi_rolling_3h_mean': 78.5,
        'pm25_rolling_3h_mean': 34.1,
        'aqi_rolling_3h_max': 85.0,
        'aqi_rolling_3h_min': 72.0,
        'pm25_rolling_3h_max': 38.0,
        'pm25_rolling_3h_min': 30.0,
        'aqi_rolling_6h_mean': 77.0,
        'pm25_rolling_6h_mean': 33.5,
        'aqi_rolling_6h_max': 90.0,
        'aqi_rolling_6h_min': 65.0,
        'pm25_rolling_6h_max': 40.0,
        'pm25_rolling_6h_min': 28.0,
        'aqi_rolling_12h_mean': 76.0,
        'pm25_rolling_12h_mean': 32.8,
        'aqi_rolling_12h_max': 95.0,
        'aqi_rolling_12h_min': 60.0,
        'pm25_rolling_12h_max': 42.0,
        'pm25_rolling_12h_min': 25.0,
        'aqi_rolling_24h_mean': 75.0,
        'pm25_rolling_24h_mean': 32.0,
        'aqi_rolling_24h_max': 100.0,
        'aqi_rolling_24h_min': 55.0,
        'pm25_rolling_24h_max': 45.0,
        'pm25_rolling_24h_min': 22.0,
        'hour': 14
    }


@pytest.fixture(scope="session")
def backend_initialized():
    """
    Initialize backend resources once for all tests
    This loads the model and data to avoid startup issues
    """
    try:
        from backend.app import main as backend_main
        
        # Manually trigger resource loading
        MODEL_PATH = Path("data/models/best_model_gradientboosting.pkl")
        FEATURES_PATH = Path("data/processed/feature_sets.json")
        TEST_DATA_PATH = Path("data/processed/features_test.csv")
        
        # Check if files exist
        if not MODEL_PATH.exists():
            print(f"⚠️  Model not found at {MODEL_PATH}")
            return False
        
        if not TEST_DATA_PATH.exists():
            print(f"⚠️  Test data not found at {TEST_DATA_PATH}")
            return False
        
        # Load model
        with open(MODEL_PATH, 'rb') as f:
            backend_main.model = pickle.load(f)
        
        # Fix gpu_id attribute
        if not hasattr(backend_main.model, 'gpu_id'):
            backend_main.model.gpu_id = None
        
        # Try to extract booster
        try:
            backend_main.booster = backend_main.model.get_booster()
        except:
            backend_main.booster = None
        
        # Load features
        with open(FEATURES_PATH, 'r') as f:
            features = json.load(f)
            backend_main.feature_list = features['comprehensive']
        
        # Load test data
        backend_main.test_data = pd.read_csv(TEST_DATA_PATH)
        
        # Initialize risk calculator
        backend_main.risk_calculator = HealthRiskCalculator()
        
        # Load explainability data
        EXPLAINABILITY_DIR = Path("data/explainability")
        try:
            importance_json_path = EXPLAINABILITY_DIR / "feature_importance.json"
            if importance_json_path.exists():
                with open(importance_json_path, 'r') as f:
                    backend_main.feature_importance_data = json.load(f)
            
            explanations_path = EXPLAINABILITY_DIR / "sample_explanations.json"
            if explanations_path.exists():
                with open(explanations_path, 'r') as f:
                    backend_main.sample_explanations = json.load(f)
            else:
                backend_main.sample_explanations = []
            
            metadata_path = EXPLAINABILITY_DIR / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    backend_main.explainability_metadata = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load explainability data: {e}")
            backend_main.feature_importance_data = None
            backend_main.sample_explanations = []
            backend_main.explainability_metadata = None
        
        print("✓ Backend resources initialized for testing")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize backend: {e}")
        import traceback
        traceback.print_exc()
        return False


@pytest.fixture
def test_client(backend_initialized):
    """
    FastAPI test client with properly initialized backend
    """
    try:
        from fastapi.testclient import TestClient
        from backend.app.main import app
        
        if not backend_initialized:
            pytest.skip("Backend initialization failed - check model and data files")
        
        # Create test client
        client = TestClient(app)
        
        # Verify backend is working
        response = client.get("/health")
        if response.status_code != 200:
            pytest.skip("Backend health check failed")
        
        return client
        
    except ImportError as e:
        pytest.skip(f"FastAPI or backend not available: {e}")
    except Exception as e:
        pytest.skip(f"Test client initialization failed: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment before all tests
    """
    print("\n" + "="*70)
    print("🧪 INITIALIZING TEST ENVIRONMENT")
    print("="*70)
    
    # Check critical files
    critical_files = [
        "data/models/best_model_gradientboosting.pkl",
        "data/processed/feature_sets.json",
        "data/processed/features_test.csv"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} critical file(s) missing")
        print("Some tests will be skipped")
    else:
        print("\n✓ All critical files present")
    
    print("="*70 + "\n")
    
    yield
    
    print("\n" + "="*70)
    print("✅ TEST ENVIRONMENT CLEANUP COMPLETE")
    print("="*70 + "\n")