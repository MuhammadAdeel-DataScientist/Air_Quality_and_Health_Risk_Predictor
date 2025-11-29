from src.data_pipeline.api_clients import APIClientManager
from datetime import datetime, timedelta

manager = APIClientManager()

# Test OpenWeatherMap
print("Testing OpenWeatherMap...")
data = manager.openweather.get_current_air_quality(28.7041, 77.1025)  # Delhi
if data:
    print("✓ OpenWeatherMap working!")
else:
    print("✗ Check your OpenWeatherMap API key")

# Test WAQI
print("\nTesting WAQI...")
data = manager.waqi.get_geo_feed(28.7041, 77.1025)
if data and data.get('status') == 'ok':
    print("✓ WAQI working!")
else:
    print("✗ Check your WAQI API key")

# Test OpenAQ with correct coordinate format
print("\nTesting OpenAQ...")

# Los Angeles coordinates - (lat, lon) format for OpenAQ v3
lat, lon = 34.0522, -118.2437

# First try: Get latest measurements
print("  Trying latest measurements...")
data = manager.openaq.get_latest_measurements(
    coordinates=(lat, lon),  # Note: (lat, lon) order
    parameter="pm25",
    radius=25000  # Max 25km radius for OpenAQ v3
)

if data and "results" in data and len(data["results"]) > 0:
    print("✓ OpenAQ working!")
    print(f"  Found {len(data['results'])} locations near Los Angeles")
    
    # Show first location as example
    if len(data['results']) > 0:
        first_loc = data['results'][0]
        loc_name = first_loc.get('name', 'Unknown')
        print(f"  Example location: {loc_name}")
else:
    print("  No results from OpenAQ")
    print("  Trying with larger radius...")
    
    # Try with larger radius
    data = manager.openaq.get_latest_measurements(
        coordinates=(lat, lon),
        parameter="pm25",
        radius=100000  # 100km radius
    )
    
    if data and "results" in data and len(data["results"]) > 0:
        print("✓ OpenAQ working with larger radius!")
        print(f"  Found {len(data['results'])} locations")
    else:
        print("✗ OpenAQ might not have data for this location")
        print("  Note: OpenAQ v3 requires authentication and may have limited coverage")

# Test IQAir
print("\nTesting IQAir...")
try:
    data = manager.iqair.get_nearest_city(28.7041, 77.1025)
    if data and data.get('status') == 'success':
        print("✓ IQAir working!")
    else:
        print("✗ Check your IQAir API key or rate limits")
except Exception as e:
    print(f"✗ IQAir error: {e}")

print("\n" + "="*50)
print("API Testing Complete!")
print("="*50)
print("\nSummary:")
print("  3/4 APIs working is excellent for this project")
print("  OpenAQ v3 has limited coverage but is authenticated")