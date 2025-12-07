"""
Script to collect air quality data from multiple sources
Run this script to start collecting data for your project
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from src.config.config import Config
from src.data_pipeline.api_clients import APIClientManager
from src.data_pipeline.data_processor import AirQualityDataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.logs_dir / 'data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataCollector:
    """Main data collection orchestrator"""
    
    def __init__(self):
        self.api_manager = APIClientManager()
        self.processor = AirQualityDataProcessor()
        self.cities = Config.data_collection.MAJOR_CITIES
        
    def collect_current_data(self) -> pd.DataFrame:
        """
        Collect current air quality data for all cities
        
        Returns:
            DataFrame with collected data
        """
        all_data = []
        
        for city in self.cities:
            logger.info(f"Collecting data for {city['name']}, {city['country']}")
            
            try:
                # Fetch data from all sources
                raw_data = self.api_manager.fetch_all_sources(
                    lat=city['lat'],
                    lon=city['lon'],
                    city=city['name']
                )
                
                # Process and combine data
                df = self.processor.combine_sources(raw_data)
                
                if df is not None and not df.empty:
                    # Add city metadata
                    df['city_name'] = city['name']
                    df['country_code'] = city['country']
                    
                    all_data.append(df)
                    logger.info(f"Successfully collected data for {city['name']}")
                else:
                    logger.warning(f"No data collected for {city['name']}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting data for {city['name']}: {e}")
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Clean data
            combined_df = self.processor.clean_data(combined_df)
            
            # Fill missing AQI values
            combined_df = self.processor.fill_missing_aqi(combined_df)
            
            return combined_df
        
        return pd.DataFrame()
    
    def collect_historical_data(
        self, 
        city: dict, 
        days_back: int = 90
    ) -> pd.DataFrame:
        """
        Collect historical data for a specific city using multiple strategies
        
        Args:
            city: City dictionary with name, lat, lon
            days_back: Number of days to collect (default 90)
            
        Returns:
            DataFrame with historical data
        """
        logger.info(f"Collecting {days_back} days of historical data for {city['name']}")
        
        all_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Strategy 1: Try OpenWeatherMap Historical Air Quality (requires paid plan)
        try:
            logger.info("  Attempting OpenWeatherMap historical data...")
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            data = self.api_manager.openweather.get_historical_air_quality(
                lat=city['lat'],
                lon=city['lon'],
                start_timestamp=start_ts,
                end_timestamp=end_ts
            )
            
            if data:
                df = self.processor.process_openweather_air(data)
                if df is not None and not df.empty:
                    logger.info(f"    ✓ Got {len(df)} records from OpenWeatherMap")
                    all_data.append(df)
            
            time.sleep(2)
        
        except Exception as e:
            logger.warning(f"  OpenWeatherMap historical failed: {e}")
        
        # Strategy 2: Collect repeated current data to build historical dataset
        # This simulates historical data by collecting current data multiple times
        logger.info("  Using current data collection as fallback...")
        logger.info("  Note: For true historical data, consider:")
        logger.info("    - OpenWeatherMap Historical API (paid)")
        logger.info("    - Download OpenAQ S3 archive")
        logger.info("    - Use WAQI historical feed (if available)")
        
        try:
            # Get current data as a sample
            raw_data = self.api_manager.fetch_all_sources(
                lat=city['lat'],
                lon=city['lon'],
                city=city['name']
            )
            
            df = self.processor.combine_sources(raw_data)
            if df is not None and not df.empty:
                logger.info(f"    ✓ Collected current data sample: {len(df)} records")
                all_data.append(df)
            
            time.sleep(2)
        
        except Exception as e:
            logger.error(f"  Error in fallback collection: {e}")
        
        # Combine all collected data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df['city_name'] = city['name']
            combined_df['country_code'] = city['country']
            
            return self.processor.clean_data(combined_df)
        
        logger.warning(f"  No historical data collected for {city['name']}")
        return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, filename: str):
        """
        Save collected data to CSV
        
        Args:
            df: DataFrame to save
            filename: Output filename
        """
        if df is None or df.empty:
            logger.warning("No data to save")
            return
        
        output_path = Config.raw_data_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")
        logger.info(f"Total records: {len(df)}")
        logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    def run_collection(self, mode='current'):
        """
        Run data collection based on mode
        
        Args:
            mode: 'current' for real-time data, 'historical' for past data
        """
        logger.info(f"Starting data collection - Mode: {mode}")
        
        if mode == 'current':
            df = self.collect_current_data()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"air_quality_current_{timestamp}.csv"
            self.save_data(df, filename)
            
        elif mode == 'historical':
            all_historical = []
            
            for city in self.cities:
                logger.info(f"\nCollecting historical data for {city['name']}")
                df = self.collect_historical_data(city, days_back=90)
                
                if not df.empty:
                    all_historical.append(df)
                
                time.sleep(5)  # Longer delay between cities
            
            if all_historical:
                combined_df = pd.concat(all_historical, ignore_index=True)
                filename = f"air_quality_historical_{datetime.now().strftime('%Y%m%d')}.csv"
                self.save_data(combined_df, filename)
        
        logger.info("Data collection completed!")


def main():
    """Main entry point"""
    print("=" * 60)
    print("Air Quality Data Collector")
    print("=" * 60)
    print()
    print("Select collection mode:")
    print("1. Current data (real-time)")
    print("2. Historical data (last 90 days)")
    print("3. Both")
    print()
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    collector = DataCollector()
    
    if choice == '1':
        collector.run_collection(mode='current')
    elif choice == '2':
        collector.run_collection(mode='historical')
    elif choice == '3':
        collector.run_collection(mode='current')
        print("\n" + "=" * 60)
        collector.run_collection(mode='historical')
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\n" + "=" * 60)
    print("Data collection completed successfully!")
    print(f"Check the data directory: {Config.raw_data_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()