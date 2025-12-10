"""
Data processing and feature engineering tests
Tests data transformations and feature creation
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestDataProcessing:
    """Test suite for data processing and feature engineering"""
    
    def test_feature_engineering_rolling_mean(self):
        """Test rolling mean feature creation"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'aqi': np.random.uniform(20, 150, 100)
        })
        
        # Create 3-hour rolling mean
        df['aqi_rolling_3h_mean'] = df['aqi'].rolling(window=3, min_periods=1).mean()
        
        assert 'aqi_rolling_3h_mean' in df.columns
        assert not df['aqi_rolling_3h_mean'].isna().all()
        assert len(df['aqi_rolling_3h_mean']) == len(df['aqi'])
        print("✓ Rolling mean feature created successfully")
    
    def test_feature_engineering_rolling_max(self):
        """Test rolling max feature creation"""
        df = pd.DataFrame({
            'pm25': [30, 40, 50, 35, 45]
        })
        
        df['pm25_rolling_3h_max'] = df['pm25'].rolling(window=3, min_periods=1).max()
        
        assert df['pm25_rolling_3h_max'].iloc[2] == 50  # Max of [30, 40, 50]
        assert df['pm25_rolling_3h_max'].iloc[4] == 50  # Max of [50, 35, 45]
        print("✓ Rolling max feature created successfully")
    
    def test_feature_engineering_rolling_min(self):
        """Test rolling min feature creation"""
        df = pd.DataFrame({
            'pm25': [30, 40, 50, 35, 45]
        })
        
        df['pm25_rolling_3h_min'] = df['pm25'].rolling(window=3, min_periods=1).min()
        
        assert df['pm25_rolling_3h_min'].iloc[2] == 30  # Min of [30, 40, 50]
        assert df['pm25_rolling_3h_min'].iloc[4] == 35  # Min of [50, 35, 45]
        print("✓ Rolling min feature created successfully")
    
    def test_lag_features_1h(self):
        """Test 1-hour lag feature creation"""
        df = pd.DataFrame({
            'aqi': [50, 60, 70, 80, 90]
        })
        
        df['aqi_lag_1h'] = df['aqi'].shift(1)
        
        assert pd.isna(df['aqi_lag_1h'].iloc[0])  # First value should be NaN
        assert df['aqi_lag_1h'].iloc[1] == 50
        assert df['aqi_lag_1h'].iloc[2] == 60
        assert df['aqi_lag_1h'].iloc[4] == 80
        print("✓ Lag features created successfully")
    
    def test_lag_features_multiple_hours(self):
        """Test multiple hour lag features"""
        df = pd.DataFrame({
            'pm25': [30, 35, 40, 45, 50, 55]
        })
        
        df['pm25_lag_1h'] = df['pm25'].shift(1)
        df['pm25_lag_3h'] = df['pm25'].shift(3)
        
        assert df['pm25_lag_1h'].iloc[2] == 35
        assert df['pm25_lag_3h'].iloc[4] == 35
        print("✓ Multiple lag features created successfully")
    
    def test_missing_value_handling_median(self):
        """Test missing value handling with median imputation"""
        df = pd.DataFrame({
            'pm25': [35.5, np.nan, 42.1, 38.9, np.nan, 40.0],
            'aqi': [75, 80, np.nan, 85, 90, 88]
        })
        
        # Fill with median
        df_filled = df.fillna(df.median())
        
        assert not df_filled.isna().any().any()
        assert df_filled['pm25'].iloc[1] == df['pm25'].median()
        print("✓ Missing values filled with median")
    
    def test_missing_value_handling_forward_fill(self):
        """Test missing value handling with forward fill"""
        df = pd.DataFrame({
            'aqi': [50, 60, np.nan, np.nan, 70]
        })
        
        df_filled = df.fillna(method='ffill')
        
        assert not df_filled.isna().any().any()
        assert df_filled['aqi'].iloc[2] == 60
        assert df_filled['aqi'].iloc[3] == 60
        print("✓ Missing values forward filled")
    
    def test_datetime_feature_extraction(self):
        """Test datetime feature extraction (hour, day, month)"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=24, freq='H')
        })
        
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        assert df['hour'].min() == 0
        assert df['hour'].max() == 23
        assert df['day'].iloc[0] == 1
        assert df['month'].iloc[0] == 1
        print("✓ Datetime features extracted successfully")
    
    def test_data_normalization(self):
        """Test data normalization"""
        df = pd.DataFrame({
            'pm25': [10, 20, 30, 40, 50]
        })
        
        # Min-max normalization
        df['pm25_normalized'] = (df['pm25'] - df['pm25'].min()) / (df['pm25'].max() - df['pm25'].min())
        
        assert df['pm25_normalized'].min() == 0
        assert df['pm25_normalized'].max() == 1
        print("✓ Data normalized successfully")
    
    def test_outlier_detection(self):
        """Test outlier detection using IQR method"""
        df = pd.DataFrame({
            'aqi': [50, 55, 60, 58, 62, 500, 54, 56]  # 500 is outlier
        })
        
        Q1 = df['aqi'].quantile(0.25)
        Q3 = df['aqi'].quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = df[(df['aqi'] < (Q1 - 1.5 * IQR)) | (df['aqi'] > (Q3 + 1.5 * IQR))]
        
        assert len(outliers) > 0
        assert 500 in outliers['aqi'].values
        print(f"✓ Outliers detected: {len(outliers)}")
    
    def test_feature_correlation(self):
        """Test feature correlation calculation"""
        df = pd.DataFrame({
            'pm25': np.random.uniform(20, 100, 100),
            'pm10': np.random.uniform(30, 150, 100),
            'aqi': np.random.uniform(30, 120, 100)
        })
        
        correlation = df.corr()
        
        assert correlation.shape == (3, 3)
        assert correlation.loc['pm25', 'pm25'] == 1.0
        print("✓ Feature correlation calculated")
    
    def test_data_aggregation(self):
        """Test data aggregation by time periods"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=72, freq='H'),
            'aqi': np.random.uniform(30, 100, 72)
        })
        
        df['date'] = df['timestamp'].dt.date
        daily_avg = df.groupby('date')['aqi'].mean()
        
        assert len(daily_avg) == 3  # 72 hours = 3 days
        print(f"✓ Data aggregated to {len(daily_avg)} days")
    
    def test_feature_set_loading(self):
        """Test loading feature sets from JSON"""
        import json
        feature_sets_path = Path("data/processed/feature_sets.json")
        
        if feature_sets_path.exists():
            with open(feature_sets_path, 'r') as f:
                feature_sets = json.load(f)
            
            assert 'comprehensive' in feature_sets
            assert isinstance(feature_sets['comprehensive'], list)
            assert len(feature_sets['comprehensive']) > 0
            print(f"✓ Feature sets loaded ({len(feature_sets['comprehensive'])} features)")
        else:
            pytest.skip("Feature sets file not found")
    
    def test_data_type_validation(self):
        """Test data type validation"""
        df = pd.DataFrame({
            'pm25': [35.5, 42.1, 38.9],
            'city_name': ['Delhi', 'Mumbai', 'Kolkata'],
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='H')
        })
        
        assert df['pm25'].dtype in [np.float64, np.float32]
        assert df['city_name'].dtype == object
        assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])
        print("✓ Data types validated")
    
    def test_duplicate_removal(self):
        """Test duplicate row removal"""
        df = pd.DataFrame({
            'timestamp': ['2024-01-01 00:00', '2024-01-01 01:00', '2024-01-01 00:00'],
            'aqi': [50, 60, 50]
        })
        
        df_unique = df.drop_duplicates()
        
        assert len(df_unique) == 2
        print(f"✓ Duplicates removed ({len(df)} -> {len(df_unique)})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])