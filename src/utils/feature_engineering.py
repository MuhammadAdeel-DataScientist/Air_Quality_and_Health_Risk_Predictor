"""
Feature engineering utilities for air quality prediction
Reusable functions for creating features
"""
import pandas as pd
import numpy as np
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AirQualityFeatureEngineer:
    """Feature engineering for air quality data"""
    
    def __init__(self):
        self.lag_hours = [1, 3, 6, 12, 24, 48, 72, 168]
        self.rolling_windows = [3, 6, 12, 24, 48, 72]
        self.change_periods = [1, 3, 6, 12, 24]
        
    def create_lag_features(self, df: pd.DataFrame, 
                           features: List[str],
                           lag_hours: List[int] = None,
                           group_col: str = 'city_name') -> pd.DataFrame:
        """
        Create lag features for time series
        
        Args:
            df: DataFrame with time series data
            features: List of column names to create lags for
            lag_hours: List of lag periods in hours
            group_col: Column to group by (e.g., city_name)
            
        Returns:
            DataFrame with lag features added
        """
        if lag_hours is None:
            lag_hours = self.lag_hours
        
        df = df.copy()
        
        for feature in features:
            if feature not in df.columns:
                logger.warning(f"Feature {feature} not found in DataFrame")
                continue
                
            for lag in lag_hours:
                col_name = f'{feature}_lag_{lag}h'
                df[col_name] = df.groupby(group_col)[feature].shift(lag)
        
        logger.info(f"Created {len(features) * len(lag_hours)} lag features")
        return df
    
    def create_rolling_features(self, df: pd.DataFrame,
                               features: List[str],
                               windows: List[int] = None,
                               stats: List[str] = None,
                               group_col: str = 'city_name') -> pd.DataFrame:
        """
        Create rolling window statistics
        
        Args:
            df: DataFrame with time series data
            features: List of column names
            windows: List of window sizes in hours
            stats: List of statistics to calculate
            group_col: Column to group by
            
        Returns:
            DataFrame with rolling features added
        """
        if windows is None:
            windows = self.rolling_windows
        
        if stats is None:
            stats = ['mean', 'std', 'min', 'max']
        
        df = df.copy()
        
        for feature in features:
            if feature not in df.columns:
                continue
                
            for window in windows:
                for stat in stats:
                    col_name = f'{feature}_rolling_{window}h_{stat}'
                    
                    if stat == 'mean':
                        df[col_name] = df.groupby(group_col)[feature].transform(
                            lambda x: x.rolling(window=window, min_periods=1).mean()
                        )
                    elif stat == 'std':
                        df[col_name] = df.groupby(group_col)[feature].transform(
                            lambda x: x.rolling(window=window, min_periods=1).std()
                        )
                    elif stat == 'min':
                        df[col_name] = df.groupby(group_col)[feature].transform(
                            lambda x: x.rolling(window=window, min_periods=1).min()
                        )
                    elif stat == 'max':
                        df[col_name] = df.groupby(group_col)[feature].transform(
                            lambda x: x.rolling(window=window, min_periods=1).max()
                        )
        
        logger.info(f"Created rolling statistics features")
        return df
    
    def create_change_features(self, df: pd.DataFrame,
                              features: List[str],
                              periods: List[int] = None,
                              group_col: str = 'city_name') -> pd.DataFrame:
        """
        Create rate of change features
        
        Args:
            df: DataFrame
            features: List of column names
            periods: List of periods for change calculation
            group_col: Column to group by
            
        Returns:
            DataFrame with change features added
        """
        if periods is None:
            periods = self.change_periods
        
        df = df.copy()
        
        for feature in features:
            if feature not in df.columns:
                continue
                
            for period in periods:
                # Absolute change
                col_name = f'{feature}_change_{period}h'
                df[col_name] = df.groupby(group_col)[feature].diff(period)
                
                # Percentage change
                col_name_pct = f'{feature}_pct_change_{period}h'
                df[col_name_pct] = df.groupby(group_col)[feature].pct_change(period) * 100
        
        logger.info(f"Created rate of change features")
        return df
    
    def create_temporal_features(self, df: pd.DataFrame,
                                timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """
        Create temporal features including cyclical encoding
        
        Args:
            df: DataFrame with timestamp column
            timestamp_col: Name of timestamp column
            
        Returns:
            DataFrame with temporal features added
        """
        df = df.copy()
        
        # Ensure timestamp is datetime
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        # Extract components
        df['hour'] = df[timestamp_col].dt.hour
        df['day_of_week'] = df[timestamp_col].dt.dayofweek
        df['month'] = df[timestamp_col].dt.month
        df['day_of_year'] = df[timestamp_col].dt.dayofyear
        df['week_of_year'] = df[timestamp_col].dt.isocalendar().week
        
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        df['month_sin'] = np.sin(2 * np.pi * (df['month'] - 1) / 12)
        df['month_cos'] = np.cos(2 * np.pi * (df['month'] - 1) / 12)
        
        df['day_of_year_sin'] = np.sin(2 * np.pi * (df['day_of_year'] - 1) / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * (df['day_of_year'] - 1) / 365)
        
        # Categorical temporal features
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_rush_hour'] = df['hour'].isin([7, 8, 9, 17, 18, 19, 20]).astype(int)
        df['is_night'] = df['hour'].isin(range(0, 6)).astype(int)
        df['is_peak_pollution'] = df['hour'].isin([19, 20, 21]).astype(int)
        
        # Season (Northern Hemisphere)
        df['season'] = df['month'].apply(lambda x: 
            1 if x in [12, 1, 2] else  # Winter
            2 if x in [3, 4, 5] else    # Spring
            3 if x in [6, 7, 8] else    # Summer
            4                            # Fall
        )
        
        logger.info("Created temporal features")
        return df
    
    def create_weather_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create weather interaction features
        
        Args:
            df: DataFrame with weather features
            
        Returns:
            DataFrame with interaction features added
        """
        df = df.copy()
        
        weather_features = {
            'temperature': 'temperature',
            'humidity': 'humidity',
            'pressure': 'pressure',
            'wind_speed': 'wind_speed'
        }
        
        # Check which features exist
        available = {k: v for k, v in weather_features.items() if v in df.columns}
        
        if 'temperature' in available and 'humidity' in available:
            df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
            df['comfort_index'] = df['temperature'] + (0.4 * df['humidity'])
        
        if 'temperature' in available:
            df['temperature_squared'] = df['temperature'] ** 2
        
        if 'humidity' in available:
            df['humidity_squared'] = df['humidity'] ** 2
        
        if 'temperature' in available and 'wind_speed' in available:
            df['wind_chill'] = df['temperature'] - (df['wind_speed'] * 0.5)
        
        if 'pressure' in available:
            df['pressure_change_3h'] = df.groupby('city_name')['pressure'].diff(3)
        
        logger.info("Created weather interaction features")
        return df
    
    def create_pollutant_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create pollutant ratio features
        
        Args:
            df: DataFrame with pollutant features
            
        Returns:
            DataFrame with ratio features added
        """
        df = df.copy()
        
        if 'pm25' in df.columns and 'pm10' in df.columns:
            df['pm25_pm10_ratio'] = df['pm25'] / (df['pm10'] + 1e-6)
            df['total_pm'] = df['pm25'] + df['pm10']
        
        if 'no2' in df.columns and 'o3' in df.columns:
            df['no2_o3_ratio'] = df['no2'] / (df['o3'] + 1e-6)
        
        if 'so2' in df.columns and 'no2' in df.columns:
            df['so2_no2_ratio'] = df['so2'] / (df['no2'] + 1e-6)
        
        logger.info("Created pollutant ratio features")
        return df
    
    def engineer_all_features(self, df: pd.DataFrame,
                             lag_features: List[str] = None,
                             rolling_features: List[str] = None,
                             change_features: List[str] = None) -> pd.DataFrame:
        """
        Apply all feature engineering steps
        
        Args:
            df: Input DataFrame
            lag_features: Features to create lags for
            rolling_features: Features for rolling statistics
            change_features: Features for rate of change
            
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Starting comprehensive feature engineering...")
        
        # Default features
        if lag_features is None:
            lag_features = ['aqi', 'pm25', 'pm10', 'temperature', 'humidity']
        
        if rolling_features is None:
            rolling_features = ['aqi', 'pm25', 'pm10']
        
        if change_features is None:
            change_features = ['aqi', 'pm25', 'temperature', 'pressure']
        
        # Sort data
        df = df.sort_values(['city_name', 'timestamp']).reset_index(drop=True)
        
        # Create features
        df = self.create_temporal_features(df)
        df = self.create_lag_features(df, lag_features)
        df = self.create_rolling_features(df, rolling_features)
        df = self.create_change_features(df, change_features)
        df = self.create_weather_interactions(df)
        df = self.create_pollutant_ratios(df)
        
        logger.info(f"Feature engineering complete. Total columns: {len(df.columns)}")
        
        return df


def load_and_engineer_features(data_path: str, 
                               save_path: str = None) -> pd.DataFrame:
    """
    Convenience function to load data and engineer all features
    
    Args:
        data_path: Path to input CSV
        save_path: Optional path to save engineered features
        
    Returns:
        DataFrame with engineered features
    """
    # Load data
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    logger.info(f"Loaded {len(df):,} records from {data_path}")
    
    # Engineer features
    engineer = AirQualityFeatureEngineer()
    df_engineered = engineer.engineer_all_features(df)
    
    # Save if path provided
    if save_path:
        df_engineered.to_csv(save_path, index=False)
        logger.info(f"Saved engineered features to {save_path}")
    
    return df_engineered


if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python feature_engineering.py <input_csv> [output_csv]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    df_engineered = load_and_engineer_features(input_path, output_path)
    
    print(f"\n✅ Feature engineering complete!")
    print(f"   Input records: {len(df_engineered):,}")
    print(f"   Output features: {len(df_engineered.columns)}")