"""
Integration tests
Tests complete workflows and end-to-end functionality
"""
import pytest


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_end_to_end_prediction_workflow(self, test_client):
        """Test complete prediction workflow from city selection to health assessment"""
        # Step 1: Get available cities
        cities_response = test_client.get("/api/cities")
        assert cities_response.status_code == 200
        cities_data = cities_response.json()
        assert 'cities' in cities_data
        cities = cities_data['cities']
        assert len(cities) > 0
        print(f"✓ Step 1: Found {len(cities)} cities")
        
        # Step 2: Get current AQI for first city
        city = cities[0]
        current_response = test_client.get(f"/api/current/{city.lower()}")
        assert current_response.status_code == 200
        current_data = current_response.json()
        assert 'aqi' in current_data
        aqi = current_data['aqi']
        print(f"✓ Step 2: Current AQI for {city}: {aqi}")
        
        # Step 3: Get health risk assessment
        risk_response = test_client.post("/api/health-risk", json={
            "aqi": aqi,
            "vulnerable_groups": ["children", "elderly"]
        })
        assert risk_response.status_code == 200
        risk_data = risk_response.json()
        assert 'recommendations' in risk_data
        assert 'health_message' in risk_data
        assert len(risk_data['recommendations']) > 0
        print(f"✓ Step 3: Health assessment complete ({len(risk_data['recommendations'])} recommendations)")
        
        print("✅ End-to-end prediction workflow successful")
    
    def test_forecast_to_health_workflow(self, test_client):
        """Test forecast workflow with health assessment"""
        # Get cities
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if not cities:
            pytest.skip("No cities available")
        
        city = cities[0]
        
        # Get forecast
        forecast_response = test_client.get(f"/api/forecast/{city.lower()}?hours=12")
        assert forecast_response.status_code == 200
        forecast_data = forecast_response.json()
        
        assert 'best_hour' in forecast_data
        assert 'worst_hour' in forecast_data
        assert len(forecast_data['forecast']) > 0
        
        best_hour = forecast_data['best_hour']
        worst_hour = forecast_data['worst_hour']
        
        best_aqi = forecast_data['forecast'][best_hour]['aqi']
        worst_aqi = forecast_data['forecast'][worst_hour]['aqi']
        
        print(f"✓ Forecast: Best hour {best_hour} (AQI: {best_aqi}), Worst hour {worst_hour} (AQI: {worst_aqi})")
        
        # Get health assessment for worst hour
        risk_response = test_client.post("/api/health-risk", json={
            "aqi": worst_aqi,
            "vulnerable_groups": ["children"]
        })
        assert risk_response.status_code == 200
        
        print("✅ Forecast to health workflow successful")
    
    def test_explainability_workflow(self, test_client):
        """Test complete explainability workflow"""
        # Check if explainability is available
        metadata_response = test_client.get("/api/explainability/metadata")
        
        if metadata_response.status_code == 503:
            pytest.skip("Explainability not available")
        
        assert metadata_response.status_code == 200
        print("✓ Explainability metadata available")
        
        # Get feature importance
        importance_response = test_client.get("/api/explainability/feature-importance?top_n=10")
        assert importance_response.status_code == 200
        importance_data = importance_response.json()
        assert 'features' in importance_data
        print(f"✓ Feature importance loaded ({len(importance_data['features'])} features)")
        
        # Get top features with descriptions
        top_features_response = test_client.get("/api/explainability/top-features?n=5")
        assert top_features_response.status_code == 200
        top_data = top_features_response.json()
        assert 'top_features' in top_data
        print(f"✓ Top features loaded ({len(top_data['top_features'])} features)")
        
        # Get city explanation
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            city = cities[0]
            explain_response = test_client.get(f"/api/explainability/explain/{city.lower()}")
            assert explain_response.status_code == 200
            explain_data = explain_response.json()
            assert 'prediction' in explain_data
            assert 'top_features' in explain_data
            print(f"✓ City explanation loaded for {city}")
        
        print("✅ Explainability workflow successful")
    
    def test_vulnerable_groups_workflow(self, test_client):
        """Test vulnerable groups integration"""
        # Get vulnerable groups
        groups_response = test_client.get("/api/vulnerable-groups")
        assert groups_response.status_code == 200
        groups_data = groups_response.json()
        all_groups = groups_data['vulnerable_groups']
        print(f"✓ Found {len(all_groups)} vulnerable groups")
        
        # Test health assessment with each group
        test_aqi = 150  # Unhealthy for sensitive groups
        
        for group in all_groups[:3]:  # Test first 3 groups
            risk_response = test_client.post("/api/health-risk", json={
                "aqi": test_aqi,
                "vulnerable_groups": [group]
            })
            assert risk_response.status_code == 200
            risk_data = risk_response.json()
            assert group in risk_data['vulnerable_group_warnings']
            print(f"✓ Health assessment for {group} successful")
        
        print("✅ Vulnerable groups workflow successful")
    
    def test_statistics_workflow(self, test_client):
        """Test statistics and analytics workflow"""
        # Get overall statistics
        stats_response = test_client.get("/api/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        
        assert 'average_aqi' in stats_data
        assert 'total_predictions' in stats_data
        assert 'category_distribution' in stats_data
        
        print(f"✓ Statistics: Avg AQI {stats_data['average_aqi']:.2f}")
        print(f"✓ Total predictions: {stats_data['total_predictions']}")
        
        # Verify category distribution
        categories = stats_data['category_distribution']
        total_count = sum(categories.values())
        assert total_count == stats_data['total_predictions']
        
        print("✅ Statistics workflow successful")
    
    def test_multi_city_comparison(self, test_client):
        """Test comparing AQI across multiple cities"""
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if len(cities) < 2:
            pytest.skip("Need at least 2 cities")
        
        city_aqi_data = []
        
        for city in cities[:5]:  # Compare first 5 cities
            response = test_client.get(f"/api/current/{city.lower()}")
            if response.status_code == 200:
                data = response.json()
                city_aqi_data.append({
                    'city': city,
                    'aqi': data['aqi'],
                    'category': data['category']
                })
        
        assert len(city_aqi_data) >= 2
        print(f"✓ Compared {len(city_aqi_data)} cities")
        
        # Sort by AQI
        city_aqi_data.sort(key=lambda x: x['aqi'])
        best_city = city_aqi_data[0]
        worst_city = city_aqi_data[-1]
        
        print(f"✓ Best: {best_city['city']} (AQI: {best_city['aqi']:.1f})")
        print(f"✓ Worst: {worst_city['city']} (AQI: {worst_city['aqi']:.1f})")
        
        print("✅ Multi-city comparison successful")
    
    def test_error_handling_integration(self, test_client):
        """Test error handling across different scenarios"""
        # Invalid city
        response = test_client.get("/api/current/invalidcity123")
        assert response.status_code == 404
        print("✓ Invalid city handled correctly")
        
        # Invalid AQI
        response = test_client.post("/api/health-risk", json={
            "aqi": -100
        })
        assert response.status_code == 422
        print("✓ Invalid AQI handled correctly")
        
        # Invalid forecast hours
        cities_response = test_client.get("/api/cities")
        cities = cities_response.json()['cities']
        
        if cities:
            response = test_client.get(f"/api/forecast/{cities[0].lower()}?hours=200")
            assert response.status_code in [200, 422]  # Either works with cap or rejects
            print("✓ Invalid forecast hours handled")
        
        print("✅ Error handling integration successful")
    
    def test_complete_user_journey(self, test_client):
        """Test complete user journey through the application"""
        print("\n🚀 Starting complete user journey test...")
        
        # 1. User opens app - check health
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        print("✓ App health check passed")
        
        # 2. User browses available cities
        cities_response = test_client.get("/api/cities")
        assert cities_response.status_code == 200
        cities = cities_response.json()['cities']
        print(f"✓ User sees {len(cities)} cities")
        
        # 3. User selects a city and views current AQI
        if cities:
            selected_city = cities[0]
            current_response = test_client.get(f"/api/current/{selected_city.lower()}")
            assert current_response.status_code == 200
            current_aqi = current_response.json()['aqi']
            print(f"✓ User views current AQI for {selected_city}: {current_aqi}")
            
            # 4. User checks forecast
            forecast_response = test_client.get(f"/api/forecast/{selected_city.lower()}?hours=24")
            assert forecast_response.status_code == 200
            print("✓ User views 24-hour forecast")
            
            # 5. User gets personalized health assessment
            risk_response = test_client.post("/api/health-risk", json={
                "aqi": current_aqi,
                "vulnerable_groups": ["children"]
            })
            assert risk_response.status_code == 200
            recommendations = risk_response.json()['recommendations']
            print(f"✓ User receives {len(recommendations)} health recommendations")
            
            # 6. User explores explainability
            explain_response = test_client.get(f"/api/explainability/explain/{selected_city.lower()}")
            if explain_response.status_code == 200:
                print("✓ User views prediction explanation")
            
            # 7. User checks overall statistics
            stats_response = test_client.get("/api/stats")
            assert stats_response.status_code == 200
            print("✓ User views overall statistics")
        
        print("✅ Complete user journey successful!\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])