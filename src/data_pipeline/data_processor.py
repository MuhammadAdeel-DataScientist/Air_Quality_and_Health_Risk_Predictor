"""
Data processor to clean and standardize air quality data from multiple sources
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AirQualityDataProcessor:
    """Process and standardize air quality data from different sources"""
    
    def __init__(self):
        self.pollutant_mapping = {
            'pm2.5': 'pm25',
            'pm25': 'pm25',
            'pm10': 'pm10',
            'no2': 'no2',
            'so2': 'so2',
            'o3': 'o3',
            'co': 'co'
        }
    
    def normalize_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize timestamps to remove timezone information
        
        Args:
            df: DataFrame with timestamp column
            
        Returns:
            DataFrame with normalized timestamps
        """
        if df is None or df.empty or 'timestamp' not in df.columns:
            return df
        
        df = df.copy()
        
        # Convert to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Remove timezone info to make all tz-naive
        if hasattr(df['timestamp'].dtype, 'tz') and df['timestamp'].dt.tz is not None:
            # All timestamps are tz-aware
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        else:
            # Mixed tz-aware and tz-naive - normalize each row
            def remove_tz(ts):
                if pd.isna(ts):
                    return ts
                if hasattr(ts, 'tzinfo') and ts.tzinfo is not None:
                    return ts.tz_localize(None)
                return ts
            
            df['timestamp'] = df['timestamp'].apply(remove_tz)
        
        return df
    
    def process_openweather_air(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Process OpenWeatherMap air quality data
        
        Args:
            data: Raw API response
            
        Returns:
            Processed DataFrame
        """
        try:
            if not data or 'list' not in data:
                return None
            
            records = []
            for item in data['list']:
                record = {
                    'timestamp': datetime.fromtimestamp(item['dt']),
                    'source': 'openweather',
                    'aqi': item.get('main', {}).get('aqi'),
                }
                
                # Extract pollutant components
                components = item.get('components', {})
                record['pm25'] = components.get('pm2_5')
                record['pm10'] = components.get('pm10')
                record['no2'] = components.get('no2')
                record['so2'] = components.get('so2')
                record['o3'] = components.get('o3')
                record['co'] = components.get('co')
                
                records.append(record)
            
            return pd.DataFrame(records)
        
        except Exception as e:
            logger.error(f"Error processing OpenWeather air data: {e}")
            return None
    
    def process_openweather_weather(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Process OpenWeatherMap weather data
        
        Args:
            data: Raw API response
            
        Returns:
            Processed DataFrame
        """
        try:
            if not data:
                return None
            
            record = {
                'timestamp': datetime.fromtimestamp(data['dt']),
                'source': 'openweather',
                'temperature': data.get('main', {}).get('temp'),
                'humidity': data.get('main', {}).get('humidity'),
                'pressure': data.get('main', {}).get('pressure'),
                'wind_speed': data.get('wind', {}).get('speed'),
                'wind_direction': data.get('wind', {}).get('deg'),
            }
            
            return pd.DataFrame([record])
        
        except Exception as e:
            logger.error(f"Error processing OpenWeather weather data: {e}")
            return None
    
    def process_openaq_data(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Process OpenAQ data
        
        Args:
            data: Raw API response
            
        Returns:
            Processed DataFrame
        """
        try:
            if not data or 'results' not in data:
                return None
            
            records = []
            for item in data['results']:
                # OpenAQ v3 format
                record = {
                    'timestamp': pd.to_datetime(item.get('lastUpdated') or item.get('dateUpdated')),
                    'source': 'openaq',
                    'location': item.get('name') or item.get('location'),
                    'city': item.get('city', {}).get('name') if isinstance(item.get('city'), dict) else item.get('city'),
                    'country': item.get('country', {}).get('name') if isinstance(item.get('country'), dict) else item.get('country'),
                }
                
                # Try to get parameter data
                parameters = item.get('parameters', []) or item.get('measurements', [])
                for param in parameters:
                    param_name = self.pollutant_mapping.get(
                        param.get('parameter', '').lower()
                    )
                    if param_name:
                        record[param_name] = param.get('lastValue') or param.get('value')
                
                records.append(record)
            
            if records:
                return pd.DataFrame(records)
            
            return None
        
        except Exception as e:
            logger.error(f"Error processing OpenAQ data: {e}")
            return None
    
    def process_waqi_data(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Process WAQI (World Air Quality Index) data
        
        Args:
            data: Raw API response
            
        Returns:
            Processed DataFrame
        """
        try:
            if not data or data.get('status') != 'ok':
                return None
            
            result_data = data.get('data', {})
            
            record = {
                'timestamp': pd.to_datetime(result_data.get('time', {}).get('s')),
                'source': 'waqi',
                'aqi': result_data.get('aqi'),
                'city': result_data.get('city', {}).get('name'),
            }
            
            # Extract pollutant data
            iaqi = result_data.get('iaqi', {})
            if 'pm25' in iaqi:
                record['pm25'] = iaqi['pm25'].get('v')
            if 'pm10' in iaqi:
                record['pm10'] = iaqi['pm10'].get('v')
            if 'no2' in iaqi:
                record['no2'] = iaqi['no2'].get('v')
            if 'so2' in iaqi:
                record['so2'] = iaqi['so2'].get('v')
            if 'o3' in iaqi:
                record['o3'] = iaqi['o3'].get('v')
            if 'co' in iaqi:
                record['co'] = iaqi['co'].get('v')
            
            # Extract weather data
            if 't' in iaqi:
                record['temperature'] = iaqi['t'].get('v')
            if 'h' in iaqi:
                record['humidity'] = iaqi['h'].get('v')
            if 'p' in iaqi:
                record['pressure'] = iaqi['p'].get('v')
            if 'w' in iaqi:
                record['wind_speed'] = iaqi['w'].get('v')
            
            return pd.DataFrame([record])
        
        except Exception as e:
            logger.error(f"Error processing WAQI data: {e}")
            return None
    
    def process_iqair_data(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Process IQAir data
        
        Args:
            data: Raw API response
            
        Returns:
            Processed DataFrame
        """
        try:
            if not data or data.get('status') != 'success':
                return None
            
            result_data = data.get('data', {})
            current = result_data.get('current', {})
            pollution = current.get('pollution', {})
            weather = current.get('weather', {})
            
            record = {
                'timestamp': pd.to_datetime(pollution.get('ts')),
                'source': 'iqair',
                'aqi': pollution.get('aqius'),
                'city': result_data.get('city'),
                'state': result_data.get('state'),
                'country': result_data.get('country'),
                'pm25': pollution.get('p2'),  # Main pollutant
                'temperature': weather.get('tp'),
                'humidity': weather.get('hu'),
                'pressure': weather.get('pr'),
                'wind_speed': weather.get('ws'),
                'wind_direction': weather.get('wd'),
            }
            
            return pd.DataFrame([record])
        
        except Exception as e:
            logger.error(f"Error processing IQAir data: {e}")
            return None
    
    def combine_sources(self, data_dict: Dict) -> Optional[pd.DataFrame]:
        """
        Combine data from all sources into a single DataFrame
        
        Args:
            data_dict: Dictionary with data from different sources
            
        Returns:
            Combined DataFrame
        """
        dfs = []
        
        # Process each source
        if 'openweather_air' in data_dict:
            df = self.process_openweather_air(data_dict['openweather_air'])
            if df is not None and not df.empty:
                df = self.normalize_timestamps(df)
                dfs.append(df)
        
        if 'openweather_weather' in data_dict:
            df = self.process_openweather_weather(data_dict['openweather_weather'])
            if df is not None and not df.empty:
                df = self.normalize_timestamps(df)
                dfs.append(df)
        
        if 'openaq' in data_dict:
            df = self.process_openaq_data(data_dict['openaq'])
            if df is not None and not df.empty:
                df = self.normalize_timestamps(df)
                dfs.append(df)
        
        if 'waqi' in data_dict:
            df = self.process_waqi_data(data_dict['waqi'])
            if df is not None and not df.empty:
                df = self.normalize_timestamps(df)
                dfs.append(df)
        
        if 'iqair' in data_dict:
            df = self.process_iqair_data(data_dict['iqair'])
            if df is not None and not df.empty:
                df = self.normalize_timestamps(df)
                dfs.append(df)
        
        # Combine all dataframes
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Add location metadata
            if 'location' in data_dict:
                combined_df['latitude'] = data_dict['location']['lat']
                combined_df['longitude'] = data_dict['location']['lon']
            
            return combined_df
        
        return None
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the data
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df is None or df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Normalize timestamps
        if 'timestamp' in df.columns:
            df = self.normalize_timestamps(df)
        
        # Remove duplicates
        if 'source' in df.columns:
            df = df.drop_duplicates(subset=['timestamp', 'source'], keep='first')
        else:
            df = df.drop_duplicates(subset=['timestamp'], keep='first')
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Remove rows with missing critical values
        critical_cols = ['pm25', 'aqi', 'timestamp']
        existing_critical = [col for col in critical_cols if col in df.columns]
        
        if existing_critical:
            # Keep rows where at least one critical column has data
            mask = df[existing_critical].notna().any(axis=1)
            df = df[mask]
        
        # Fill missing numeric values with forward fill then backward fill
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def fill_missing_aqi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate AQI if missing, based on PM2.5 values
        
        Args:
            df: DataFrame with air quality data
            
        Returns:
            DataFrame with filled AQI values
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Calculate AQI from PM2.5 if AQI is missing but PM2.5 is available
        if 'aqi' in df.columns and 'pm25' in df.columns:
            missing_aqi = df['aqi'].isna() & df['pm25'].notna()
            
            if missing_aqi.any():
                # Simple AQI calculation from PM2.5 (US EPA standard)
                df.loc[missing_aqi, 'aqi'] = df.loc[missing_aqi, 'pm25'].apply(
                    lambda x: self._calculate_aqi_from_pm25(x)
                )
        
        return df
    
    def _calculate_aqi_from_pm25(self, pm25: float) -> int:
        """
        Calculate AQI from PM2.5 concentration (US EPA standard)
        
        Args:
            pm25: PM2.5 concentration in µg/m³
            
        Returns:
            AQI value
        """
        if pd.isna(pm25):
            return None
        
        # US EPA AQI breakpoints for PM2.5
        breakpoints = [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ]
        
        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
            if bp_lo <= pm25 <= bp_hi:
                aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
                return int(round(aqi))
        
        # If PM2.5 is beyond the scale
        if pm25 > 500.4:
            return 500
        
        return None