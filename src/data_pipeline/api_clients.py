"""
API clients for fetching air quality and weather data
"""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from src.config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenWeatherMapClient:
    """Client for OpenWeatherMap API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.api.OPENWEATHER_API_KEY
        self.base_url = Config.api.OPENWEATHER_BASE_URL
        self.air_url = Config.api.OPENWEATHER_AIR_URL
        
    def get_current_air_quality(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current air quality data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with air quality data
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            response = requests.get(
                f"{self.air_url}/forecast",
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return None
    
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with weather data
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(
                f"{self.base_url}/weather",
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def get_historical_air_quality(
        self, 
        lat: float, 
        lon: float, 
        start_timestamp: int, 
        end_timestamp: int
    ) -> Optional[Dict]:
        """
        Get historical air quality data
        
        Args:
            lat: Latitude
            lon: Longitude
            start_timestamp: Unix timestamp for start date
            end_timestamp: Unix timestamp for end date
            
        Returns:
            Dictionary with historical air quality data
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'start': start_timestamp,
                'end': end_timestamp,
                'appid': self.api_key
            }
            response = requests.get(
                f"{self.air_url}/history",
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching historical air quality: {e}")
            return None


class IQAirClient:
    """Client for IQAir API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.api.IQAIR_API_KEY
        self.base_url = Config.api.IQAIR_BASE_URL
        
    def get_city_data(self, city: str, state: str, country: str) -> Optional[Dict]:
        """
        Get air quality data for a specific city
        
        Args:
            city: City name
            state: State name
            country: Country code (e.g., 'US', 'IN')
            
        Returns:
            Dictionary with air quality data
        """
        try:
            params = {
                'city': city,
                'state': state,
                'country': country,
                'key': self.api_key
            }
            response = requests.get(
                f"{self.base_url}/city",
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching IQAir data for {city}: {e}")
            return None
    
    def get_nearest_city(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get air quality data for nearest city to coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with air quality data
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'key': self.api_key
            }
            response = requests.get(
                f"{self.base_url}/nearest_city",
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching nearest city data: {e}")
            return None


class OpenAQClient:
    """Client for OpenAQ API v3 (requires API key)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.api.OPENAQ_API_KEY
        self.base_url = Config.api.OPENAQ_BASE_URL

    def _get_headers(self):
        """Get request headers with API key"""
        if self.api_key:
            return {"X-API-Key": self.api_key}
        return {}

    def get_latest_measurements(
        self,
        city: str = None,
        country: str = None,
        coordinates: tuple = None,
        radius: int = 10000,
        parameter: str = "pm25",
        limit: int = 100
    ) -> Optional[Dict]:
        """
        Fetch the latest air quality measurements using v3 API.
        
        Note: OpenAQ v3 uses latitude,longitude format (not lon,lat)
        """
        try:
            params = {
                "limit": limit,
                "parameters_id": 2  # PM2.5 parameter ID in v3
            }

            if coordinates:
                # v3 format: latitude,longitude (reversed from typical lon,lat)
                lat, lon = coordinates
                params["coordinates"] = f"{lat},{lon}"
                params["radius"] = radius

            if country:
                params["countries_id"] = country

            response = requests.get(
                f"{self.base_url}/locations",
                params=params,
                headers=self._get_headers(),
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching OpenAQ v3 data: {e}")
            return None

    def get_measurements(
        self,
        city: str = None,
        country: str = None,
        date_from: str = None,
        date_to: str = None,
        parameter: str = 'pm25',
        coordinates: tuple = None,
        radius: int = 25000
    ) -> Optional[Dict]:
        """
        Get measurements using OpenAQ v3 API
        
        Args:
            city: City name
            country: Country code
            date_from: Start date in ISO format
            date_to: End date in ISO format
            parameter: Pollutant parameter (default: pm25)
            coordinates: Tuple of (lat, lon)
            radius: Search radius in meters
            
        Returns:
            Dictionary with measurement data
        """
        try:
            # Map parameter names to v3 IDs
            param_map = {
                'pm25': 2,
                'pm10': 1,
                'o3': 5,
                'no2': 3,
                'so2': 4,
                'co': 6
            }
            
            params = {
                'limit': 1000,
                'parameters_id': param_map.get(parameter.lower(), 2)
            }

            if coordinates:
                # v3 format: latitude,longitude
                lat, lon = coordinates
                params['coordinates'] = f"{lat},{lon}"
                params['radius'] = radius
            
            # Note: v3 locations endpoint doesn't support date filtering
            # For historical data, would need to use sensors endpoint instead
            
            response = requests.get(
                f"{self.base_url}/locations",
                params=params,
                headers=self._get_headers(),
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            # Transform v3 response to match expected format
            if data and 'results' in data:
                return data
            else:
                return {'results': []}

        except Exception as e:
            logger.error(f"Error fetching measurements from v3: {e}")
            return None


class WAQIClient:
    """Client for World Air Quality Index API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.api.WAQI_API_KEY
        self.base_url = Config.api.WAQI_BASE_URL
        
    def get_city_feed(self, city: str) -> Optional[Dict]:
        """
        Get air quality feed for a city
        
        Args:
            city: City name
            
        Returns:
            Dictionary with air quality data
        """
        try:
            url = f"{self.base_url}/feed/{city}/"
            params = {'token': self.api_key}
            
            response = requests.get(
                url,
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching WAQI data for {city}: {e}")
            return None
    
    def get_geo_feed(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get air quality feed for coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with air quality data
        """
        try:
            url = f"{self.base_url}/feed/geo:{lat};{lon}/"
            params = {'token': self.api_key}
            
            response = requests.get(
                url,
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching WAQI geo data: {e}")
            return None
    
    def search_stations(self, keyword: str) -> Optional[Dict]:
        """
        Search for monitoring stations
        
        Args:
            keyword: Search keyword (city name, etc.)
            
        Returns:
            Dictionary with station data
        """
        try:
            url = f"{self.base_url}/search/"
            params = {
                'token': self.api_key,
                'keyword': keyword
            }
            
            response = requests.get(
                url,
                params=params,
                timeout=Config.data_collection.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching stations: {e}")
            return None


class APIClientManager:
    """Manager class to coordinate all API clients"""
    
    def __init__(self):
        self.openweather = OpenWeatherMapClient()
        self.iqair = IQAirClient()
        self.openaq = OpenAQClient()
        self.waqi = WAQIClient()
        
    def fetch_all_sources(self, lat: float, lon: float, city: str = None) -> Dict:
        """
        Fetch data from all available sources
        
        Args:
            lat: Latitude
            lon: Longitude
            city: City name (optional)
            
        Returns:
            Dictionary with data from all sources
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'location': {'lat': lat, 'lon': lon, 'city': city}
        }
        
        # Fetch from OpenWeatherMap
        logger.info("Fetching from OpenWeatherMap...")
        data['openweather_air'] = self.openweather.get_current_air_quality(lat, lon)
        data['openweather_weather'] = self.openweather.get_weather_data(lat, lon)
        time.sleep(1)  # Rate limiting
        
        # Fetch from OpenAQ
        logger.info("Fetching from OpenAQ...")
        data['openaq'] = self.openaq.get_latest_measurements(coordinates=(lat, lon))
        time.sleep(1)
        
        # Fetch from WAQI
        logger.info("Fetching from WAQI...")
        data['waqi'] = self.waqi.get_geo_feed(lat, lon)
        time.sleep(1)
        
        # Fetch from IQAir (if city provided)
        if city:
            logger.info("Fetching from IQAir...")
            data['iqair'] = self.iqair.get_nearest_city(lat, lon)
            time.sleep(1)
        
        return data