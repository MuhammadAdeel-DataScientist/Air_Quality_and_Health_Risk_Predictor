"""
API endpoint tests
Tests all FastAPI REST endpoints for correct responses
"""
import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns welcome message"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'status' in data
        assert data['status'] == 'running'
        print("✓ Root endpoint working")
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'model_loaded' in data
        assert 'features_count' in data
        assert data['model_loaded'] == True
        print(f"✓ Health check passed (features: {data['features_count']})")
    
    def test_predict_endpoint(self, test_client, sample_features):
        """Test prediction endpoint with valid features"""
        response = test_client.post("/api/predict", json={
            "features": sample_features,
            "city": "TestCity"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'aqi_predicted' in data
        assert 'aqi_category' in data
        assert 'risk_level' in data
        assert 'timestamp' in data
        assert isinstance(data['aqi_predicted'], (int, float))
        print(f"✓ Prediction endpoint working (AQI: {data['aqi_predicted']})")
    
    def test_predict_endpoint_without_city(self, test_client, sample_features):
        """Test prediction endpoint without city parameter"""
        response = test_client.post("/api/predict", json={
            "features": sample_features
        })
        assert response.status_code == 200
        data = response.json()
        assert 'aqi_predicted' in data
        print("✓ Prediction works without city parameter")
    
    def test_health_risk_endpoint(self, test_client):
        """Test health risk assessment endpoint"""
        response = test_client.post("/api/health-risk", json={
            "aqi": 75.0,
            "vulnerable_groups": ["children", "elderly"]
        })
        assert response.status_code == 200
        data = response.json()
        assert 'health_message' in data
        assert 'recommendations' in data
        assert 'vulnerable_group_warnings' in data
        assert 'outdoor_activity_level' in data
        assert 'mask_recommendation' in data
        assert len(data['recommendations']) > 0
        print(f"✓ Health risk endpoint working ({len(data['recommendations'])} recommendations)")
    
    def test_health_risk_without_vulnerable_groups(self, test_client):
        """Test health risk endpoint without vulnerable groups"""
        response = test_client.post("/api/health-risk", json={
            "aqi": 100.0
        })
        assert response.status_code == 200
        data = response.json()
        assert 'health_message' in data
        print("✓ Health risk works without vulnerable groups")
    
    def test_cities_endpoint(self, test_client):
        """Test cities list endpoint"""
        response = test_client.get("/api/cities")
        assert response.status_code == 200
        data = response.json()
        assert 'cities' in data
        assert 'count' in data
        assert len(data['cities']) > 0
        assert data['count'] == len(data['cities'])
        print(f"✓ Cities endpoint working ({data['count']} cities)")
    
    def test_current_aqi_endpoint(self, test_client):
        """Test current AQI endpoint for a valid city"""
        # First get list of cities
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            city = cities[0]
            response = test_client.get(f"/api/current/{city.lower()}")
            assert response.status_code == 200
            data = response.json()
            assert 'aqi' in data
            assert 'category' in data
            assert 'city' in data
            assert 'health_message' in data
            print(f"✓ Current AQI endpoint working for {city}")
        else:
            pytest.skip("No cities available")
    
    def test_forecast_endpoint(self, test_client):
        """Test forecast endpoint"""
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            city = cities[0]
            response = test_client.get(f"/api/forecast/{city.lower()}?hours=12")
            assert response.status_code == 200
            data = response.json()
            assert 'forecast' in data
            assert 'best_hour' in data
            assert 'worst_hour' in data
            assert len(data['forecast']) > 0
            assert len(data['forecast']) <= 12
            print(f"✓ Forecast endpoint working ({len(data['forecast'])} hours)")
        else:
            pytest.skip("No cities available")
    
    def test_forecast_default_hours(self, test_client):
        """Test forecast endpoint with default hours parameter"""
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            city = cities[0]
            response = test_client.get(f"/api/forecast/{city.lower()}")
            assert response.status_code == 200
            data = response.json()
            assert len(data['forecast']) > 0
            print("✓ Forecast works with default hours")
        else:
            pytest.skip("No cities available")
    
    def test_stats_endpoint(self, test_client):
        """Test statistics endpoint"""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'average_aqi' in data
        assert 'total_predictions' in data
        assert 'median_aqi' in data
        assert 'max_aqi' in data
        assert 'min_aqi' in data
        assert 'cities_count' in data
        print(f"✓ Stats endpoint working ({data['total_predictions']} predictions)")
    
    def test_vulnerable_groups_endpoint(self, test_client):
        """Test vulnerable groups endpoint"""
        response = test_client.get("/api/vulnerable-groups")
        assert response.status_code == 200
        data = response.json()
        assert 'vulnerable_groups' in data
        assert 'descriptions' in data
        assert len(data['vulnerable_groups']) > 0
        print(f"✓ Vulnerable groups endpoint working ({len(data['vulnerable_groups'])} groups)")
    
    def test_feature_importance_endpoint(self, test_client):
        """Test feature importance endpoint"""
        response = test_client.get("/api/explainability/feature-importance?top_n=10")
        
        if response.status_code == 200:
            data = response.json()
            assert 'features' in data
            assert 'importance' in data
            assert 'importance_pct' in data
            assert len(data['features']) <= 10
            print(f"✓ Feature importance endpoint working ({len(data['features'])} features)")
        elif response.status_code == 503:
            print("⚠ Feature importance not available (run generate_shap_values.py)")
            pytest.skip("Explainability not available")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_explain_endpoint(self, test_client):
        """Test explanation endpoint for a city"""
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            city = cities[0]
            response = test_client.get(f"/api/explainability/explain/{city.lower()}")
            
            if response.status_code == 200:
                data = response.json()
                assert 'prediction' in data
                assert 'top_features' in data
                assert 'aqi_category' in data
                print(f"✓ Explanation endpoint working for {city}")
            elif response.status_code == 503:
                pytest.skip("Explainability not available")
        else:
            pytest.skip("No cities available")
    
    def test_explainability_metadata_endpoint(self, test_client):
        """Test explainability metadata endpoint"""
        response = test_client.get("/api/explainability/metadata")
        
        if response.status_code == 200:
            data = response.json()
            assert 'metadata' in data
            print("✓ Explainability metadata endpoint working")
        elif response.status_code == 503:
            pytest.skip("Explainability not available")
    
    def test_top_features_endpoint(self, test_client):
        """Test top features endpoint"""
        response = test_client.get("/api/explainability/top-features?n=10")
        
        if response.status_code == 200:
            data = response.json()
            assert 'top_features' in data
            assert len(data['top_features']) <= 10
            print(f"✓ Top features endpoint working ({len(data['top_features'])} features)")
        elif response.status_code == 503:
            pytest.skip("Explainability not available")
    
    def test_invalid_city_404(self, test_client):
        """Test invalid city returns 404"""
        response = test_client.get("/api/current/invalidcityname12345")
        assert response.status_code == 404
        print("✓ Invalid city correctly returns 404")
    
    def test_invalid_aqi_value_422(self, test_client):
        """Test invalid AQI value returns 422"""
        response = test_client.post("/api/health-risk", json={
            "aqi": -50,  # Invalid negative AQI
            "vulnerable_groups": None
        })
        assert response.status_code == 422
        print("✓ Invalid AQI correctly returns 422")
    
    def test_invalid_aqi_value_high(self, test_client):
        """Test very high AQI value returns 422"""
        response = test_client.post("/api/health-risk", json={
            "aqi": 1000,  # Invalid too high AQI
            "vulnerable_groups": None
        })
        assert response.status_code == 422
        print("✓ Too high AQI correctly returns 422")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])