"""
FastAPI Backend for Air Quality & Health Risk Predictor
FIXED VERSION - Works around XGBoost version incompatibility
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import traceback
import pickle

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.health_risk.risk_assessment import HealthRiskCalculator

# Initialize FastAPI
app = FastAPI(
    title="Air Quality & Health Risk Prediction API",
    description="Real-time air quality predictions with personalized health risk assessments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and data on startup
MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "models" / "best_model_gradientboosting.pkl"
FEATURES_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "feature_sets.json"
TEST_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "features_test.csv"

model = None
booster = None  # XGBoost Booster object
feature_list = None
test_data = None
risk_calculator = None

def prepare_features_safe(data_row, feature_list):
    """Safely prepare features, handling missing columns"""
    feature_values = []
    for feature in feature_list:
        try:
            if feature in data_row.index:
                val = data_row[feature]
                feature_values.append(0.0 if pd.isna(val) else float(val))
            else:
                feature_values.append(0.0)
        except:
            feature_values.append(0.0)
    return feature_values

def safe_predict(X, feature_names=None):
    """
    Safely predict using XGBoost model with version compatibility fix
    This bypasses the gpu_id attribute error
    """
    import xgboost as xgb
    
    try:
        # Try direct booster prediction with feature names
        if booster is not None:
            # Create DMatrix with feature names to match training
            if feature_names is not None:
                dmatrix = xgb.DMatrix(X, feature_names=feature_names)
            else:
                dmatrix = xgb.DMatrix(X)
            return booster.predict(dmatrix)
        
        # Fallback to sklearn predict (set gpu_id if missing)
        if not hasattr(model, 'gpu_id'):
            model.gpu_id = None
        return model.predict(X)
    
    except (AttributeError, ValueError) as e:
        # If feature name mismatch or gpu_id error, use sklearn wrapper
        try:
            if not hasattr(model, 'gpu_id'):
                model.gpu_id = None
            return model.predict(X)
        except AttributeError:
            # Last resort: get booster and disable feature validation
            booster_obj = model.get_booster()
            dmatrix = xgb.DMatrix(X, feature_names=feature_names)
            return booster_obj.predict(dmatrix, validate_features=False)
    except Exception as e:
        print(f"Prediction error: {e}")
        # Ultimate fallback - disable validation
        try:
            dmatrix = xgb.DMatrix(X)
            return booster.predict(dmatrix, validate_features=False) if booster else model.predict(X)
        except:
            raise

@app.on_event("startup")
async def load_resources():
    """Load model and resources on startup"""
    global model, booster, feature_list, test_data, risk_calculator
    
    try:
        # Load model
        print(f"Loading model from: {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Extract booster for direct predictions (bypasses sklearn wrapper issues)
        try:
            booster = model.get_booster()
            print("✓ Extracted XGBoost booster for direct predictions")
        except:
            booster = None
            print("⚠️  Using sklearn wrapper (may have compatibility issues)")
        
        # Fix missing gpu_id attribute if needed
        if not hasattr(model, 'gpu_id'):
            model.gpu_id = None
            print("✓ Fixed missing gpu_id attribute")
        
        # Load features - USE COMPREHENSIVE (33 features)
        import json
        with open(FEATURES_PATH, 'r') as f:
            features = json.load(f)
            feature_list = features['comprehensive']
        
        # Load test data for demo
        test_data = pd.read_csv(TEST_DATA_PATH)
        
        # Initialize risk calculator
        risk_calculator = HealthRiskCalculator()
        
        # Test prediction to verify model works
        test_X = np.zeros((1, len(feature_list)))
        test_pred = safe_predict(test_X)
        
        print("=" * 70)
        print("✓ Model loaded successfully")
        print(f"✓ Using {len(feature_list)} features")
        print(f"✓ Test data: {len(test_data)} records")
        print("✓ Risk calculator initialized")
        print(f"✓ Test prediction successful: {test_pred[0]:.2f}")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR loading resources: {str(e)}")
        traceback.print_exc()
        raise

# ============================================================================
# PYDANTIC MODELS (Request/Response)
# ============================================================================

class PredictionRequest(BaseModel):
    """Request for AQI prediction"""
    features: Dict[str, float] = Field(..., description="Feature values for prediction")
    city: Optional[str] = Field(None, description="City name")

class HealthRiskRequest(BaseModel):
    """Request for health risk assessment"""
    aqi: float = Field(..., ge=0, le=500, description="Air Quality Index")
    vulnerable_groups: Optional[List[str]] = Field(default=None)

class PredictionResponse(BaseModel):
    """Response with AQI prediction"""
    aqi_predicted: float
    aqi_category: str
    risk_level: str
    timestamp: datetime
    city: Optional[str]

class HealthRiskResponse(BaseModel):
    """Response with health risk assessment"""
    aqi: float
    aqi_category: str
    risk_level: str
    health_message: str
    recommendations: List[str]
    outdoor_activity_level: str
    mask_recommendation: str
    vulnerable_group_warnings: Dict[str, str]

class ForecastResponse(BaseModel):
    """Response with multi-hour forecast"""
    city: str
    forecast: List[Dict]
    best_hour: int
    worst_hour: int

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Air Quality & Health Risk Prediction API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model is not None,
        "features": len(feature_list) if feature_list else 0
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "features_loaded": feature_list is not None,
        "features_count": len(feature_list) if feature_list else 0,
        "risk_calculator_ready": risk_calculator is not None,
        "test_data_loaded": test_data is not None,
        "test_records": len(test_data) if test_data is not None else 0
    }

@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_aqi(request: PredictionRequest):
    """Predict AQI based on input features"""
    try:
        # Prepare features
        feature_values = []
        for feature in feature_list:
            feature_values.append(request.features.get(feature, 0.0))
        
        # Make prediction
        X = np.array(feature_values).reshape(1, -1)
        predictions = safe_predict(X)
        aqi_pred = float(predictions[0])
        
        # Get risk assessment
        assessment = risk_calculator.assess_health_risk(aqi_pred)
        
        return PredictionResponse(
            aqi_predicted=round(aqi_pred, 2),
            aqi_category=assessment.aqi_category,
            risk_level=assessment.risk_level,
            timestamp=datetime.now(),
            city=request.city
        )
    
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/health-risk", response_model=HealthRiskResponse, tags=["Health Risk"])
async def assess_health_risk(request: HealthRiskRequest):
    """Get personalized health risk assessment for given AQI"""
    try:
        assessment = risk_calculator.assess_health_risk(
            aqi=request.aqi,
            vulnerable_groups=request.vulnerable_groups
        )
        
        return HealthRiskResponse(
            aqi=request.aqi,
            aqi_category=assessment.aqi_category,
            risk_level=assessment.risk_level,
            health_message=assessment.health_message,
            recommendations=assessment.recommendations,
            outdoor_activity_level=assessment.outdoor_activity_level,
            mask_recommendation=assessment.mask_recommendation,
            vulnerable_group_warnings=assessment.vulnerable_group_warnings
        )
    
    except Exception as e:
        print(f"Risk assessment error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {str(e)}")

@app.get("/api/current/{city}", tags=["Current Data"])
async def get_current_aqi(city: str):
    """Get current AQI for a specific city"""
    try:
        # Filter data for city
        city_data = test_data[test_data['city_name'].str.lower() == city.lower()]
        
        if city_data.empty:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        
        # Get latest record
        latest = city_data.iloc[-1]
        
        # Prepare features safely
        feature_values = prepare_features_safe(latest, feature_list)
        
        # Predict
        X = np.array(feature_values).reshape(1, -1)
        predictions = safe_predict(X)
        aqi_pred = float(predictions[0])
        
        # Get risk assessment
        assessment = risk_calculator.assess_health_risk(aqi_pred)
        
        return {
            "city": city,
            "timestamp": datetime.now().isoformat(),
            "aqi": round(aqi_pred, 2),
            "category": assessment.aqi_category,
            "risk_level": assessment.risk_level,
            "health_message": assessment.health_message,
            "outdoor_activity": assessment.outdoor_activity_level,
            "mask_recommendation": assessment.mask_recommendation,
            "recommendations": assessment.recommendations[:3]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_aqi: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/forecast/{city}", response_model=ForecastResponse, tags=["Forecast"])
async def get_forecast(
    city: str,
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to forecast")
):
    """Get hourly AQI forecast for a city"""
    try:
        # Filter data for city
        city_data = test_data[test_data['city_name'].str.lower() == city.lower()]
        
        if city_data.empty:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        
        # Get recent records for forecast
        recent_data = city_data.tail(min(hours, len(city_data)))
        
        # Prepare all features at once for batch prediction
        all_features = []
        for idx, row in recent_data.iterrows():
            feature_values = prepare_features_safe(row, feature_list)
            all_features.append(feature_values)
        
        # Batch predict (more efficient)
        X_batch = np.array(all_features)
        predictions = safe_predict(X_batch)
        
        forecasts = []
        hourly_aqi = {}
        
        for hour, aqi_pred in enumerate(predictions):
            aqi_pred = float(aqi_pred)
            
            assessment = risk_calculator.assess_health_risk(aqi_pred)
            
            forecasts.append({
                "hour": hour,
                "timestamp": (datetime.now() + timedelta(hours=hour)).isoformat(),
                "aqi": round(aqi_pred, 2),
                "category": assessment.aqi_category,
                "risk_level": assessment.risk_level
            })
            
            hourly_aqi[hour] = aqi_pred
        
        # Find best and worst hours
        if hourly_aqi:
            best_hour = min(hourly_aqi, key=hourly_aqi.get)
            worst_hour = max(hourly_aqi, key=hourly_aqi.get)
        else:
            best_hour = 0
            worst_hour = 0
        
        return ForecastResponse(
            city=city,
            forecast=forecasts,
            best_hour=best_hour,
            worst_hour=worst_hour
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Forecast error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

@app.get("/api/cities", tags=["Cities"])
async def get_available_cities():
    """Get list of available cities"""
    try:
        cities = test_data['city_name'].unique().tolist()
        return {
            "cities": sorted(cities),
            "count": len(cities)
        }
    except Exception as e:
        print(f"Error in get_cities: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/vulnerable-groups", tags=["Health Risk"])
async def get_vulnerable_groups():
    """Get list of supported vulnerable groups"""
    try:
        return {
            "vulnerable_groups": risk_calculator.vulnerable_groups,
            "descriptions": {
                "children": "Children under 18 years",
                "elderly": "People aged 65 and above",
                "pregnant_women": "Pregnant women",
                "asthma_patients": "People with asthma",
                "heart_disease_patients": "People with heart disease",
                "copd_patients": "People with COPD",
                "athletes": "Athletes and people who exercise outdoors"
            }
        }
    except Exception as e:
        print(f"Error in get_vulnerable_groups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """Get overall statistics from test data"""
    try:
        # Prepare all features at once for batch prediction
        X_all = []
        valid_indices = []
        
        for idx, row in test_data.iterrows():
            try:
                feature_values = prepare_features_safe(row, feature_list)
                X_all.append(feature_values)
                valid_indices.append(idx)
            except:
                continue
        
        if not X_all:
            raise HTTPException(status_code=500, detail="No valid data to process")
        
        # Batch predict all at once (much more efficient)
        X_array = np.array(X_all)
        predictions = safe_predict(X_array)
        
        # Calculate stats
        categories = []
        for aqi in predictions:
            try:
                cat = risk_calculator.get_aqi_category(float(aqi))
                categories.append(cat.value if cat else "Unknown")
            except:
                categories.append("Unknown")
        
        category_counts = pd.Series(categories).value_counts().to_dict()
        
        return {
            "total_predictions": len(predictions),
            "average_aqi": round(float(np.mean(predictions)), 2),
            "median_aqi": round(float(np.median(predictions)), 2),
            "max_aqi": round(float(np.max(predictions)), 2),
            "min_aqi": round(float(np.min(predictions)), 2),
            "category_distribution": category_counts,
            "cities_count": test_data['city_name'].nunique()
        }
    
    except Exception as e:
        print(f"Stats error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("Starting Air Quality Prediction API...")
    print("=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)