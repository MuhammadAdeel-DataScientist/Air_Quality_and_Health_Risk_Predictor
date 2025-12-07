"""
Data validation utilities for air quality data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validate air quality data for quality and consistency"""
    
    def __init__(self):
        # Define valid ranges for each metric
        self.valid_ranges = {
            'aqi': (0, 500),
            'pm25': (0, 500),
            'pm10': (0, 600),
            'no2': (0, 2000),
            'so2': (0, 1000),
            'o3': (0, 500),
            'co': (0, 50000),
            'temperature': (-50, 60),
            'humidity': (0, 100),
            'pressure': (900, 1100),
            'wind_speed': (0, 150)
        }
        
        self.required_columns = ['timestamp']
        self.validation_results = {}
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """
        Run complete validation on dataframe
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Starting data validation...")
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check 1: Required columns
        missing_cols = self.check_required_columns(df)
        if missing_cols:
            results['errors'].append(f"Missing required columns: {missing_cols}")
            results['valid'] = False
        
        # Check 2: Data types
        dtype_issues = self.check_data_types(df)
        if dtype_issues:
            results['warnings'].extend(dtype_issues)
        
        # Check 3: Value ranges
        range_issues = self.check_value_ranges(df)
        if range_issues:
            results['warnings'].extend(range_issues)
        
        # Check 4: Missing data
        missing_stats = self.check_missing_data(df)
        results['statistics']['missing_data'] = missing_stats
        
        # Check 5: Duplicates
        duplicate_count = self.check_duplicates(df)
        results['statistics']['duplicates'] = duplicate_count
        if duplicate_count > 0:
            results['warnings'].append(f"Found {duplicate_count} duplicate records")
        
        # Check 6: Temporal consistency
        temporal_issues = self.check_temporal_consistency(df)
        if temporal_issues:
            results['warnings'].extend(temporal_issues)
        
        # Check 7: Statistical outliers
        outlier_stats = self.detect_outliers(df)
        results['statistics']['outliers'] = outlier_stats
        
        # Summary
        results['total_records'] = len(df)
        results['columns'] = list(df.columns)
        
        logger.info(f"Validation complete. Valid: {results['valid']}")
        logger.info(f"Errors: {len(results['errors'])}, Warnings: {len(results['warnings'])}")
        
        return results
    
    def check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check if required columns exist"""
        missing = [col for col in self.required_columns if col not in df.columns]
        return missing
    
    def check_data_types(self, df: pd.DataFrame) -> List[str]:
        """Check if data types are appropriate"""
        issues = []
        
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                issues.append("'timestamp' column should be datetime type")
        
        numeric_cols = ['aqi', 'pm25', 'pm10', 'no2', 'so2', 'o3', 'co',
                       'temperature', 'humidity', 'pressure', 'wind_speed']
        
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"'{col}' column should be numeric type")
        
        return issues
    
    def check_value_ranges(self, df: pd.DataFrame) -> List[str]:
        """Check if values are within valid ranges"""
        issues = []
        
        for col, (min_val, max_val) in self.valid_ranges.items():
            if col in df.columns:
                invalid_low = (df[col] < min_val).sum()
                invalid_high = (df[col] > max_val).sum()
                
                if invalid_low > 0:
                    pct = (invalid_low / len(df)) * 100
                    issues.append(
                        f"{col}: {invalid_low} values ({pct:.2f}%) below valid range ({min_val})"
                    )
                
                if invalid_high > 0:
                    pct = (invalid_high / len(df)) * 100
                    issues.append(
                        f"{col}: {invalid_high} values ({pct:.2f}%) above valid range ({max_val})"
                    )
        
        return issues
    
    def check_missing_data(self, df: pd.DataFrame) -> Dict:
        """Analyze missing data patterns"""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        
        missing_stats = {
            'by_column': missing[missing > 0].to_dict(),
            'percentage_by_column': missing_pct[missing > 0].to_dict(),
            'total_missing': missing.sum(),
            'total_percentage': (missing.sum() / (len(df) * len(df.columns)) * 100).round(2)
        }
        
        return missing_stats
    
    def check_duplicates(self, df: pd.DataFrame) -> int:
        """Check for duplicate records"""
        if 'timestamp' in df.columns and 'source' in df.columns:
            duplicates = df.duplicated(subset=['timestamp', 'source']).sum()
        else:
            duplicates = df.duplicated().sum()
        
        return int(duplicates)
    
    def check_temporal_consistency(self, df: pd.DataFrame) -> List[str]:
        """Check temporal data consistency"""
        issues = []
        
        if 'timestamp' not in df.columns:
            return issues
        
        # Check for future dates
        future_dates = (df['timestamp'] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            issues.append(f"Found {future_dates} records with future timestamps")
        
        # Check for very old dates (> 10 years)
        old_dates = (df['timestamp'] < pd.Timestamp.now() - pd.Timedelta(days=3650)).sum()
        if old_dates > 0:
            issues.append(f"Found {old_dates} records older than 10 years")
        
        # Check for gaps in time series
        df_sorted = df.sort_values('timestamp')
        time_diffs = df_sorted['timestamp'].diff()
        large_gaps = (time_diffs > pd.Timedelta(days=7)).sum()
        if large_gaps > 0:
            issues.append(f"Found {large_gaps} time gaps larger than 7 days")
        
        return issues
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict:
        """Detect statistical outliers using IQR method"""
        outlier_stats = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in self.valid_ranges:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                if len(outliers) > 0:
                    outlier_stats[col] = {
                        'count': len(outliers),
                        'percentage': round((len(outliers) / len(df)) * 100, 2),
                        'lower_bound': round(lower_bound, 2),
                        'upper_bound': round(upper_bound, 2)
                    }
        
        return outlier_stats
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply automatic cleaning based on validation results
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        logger.info("Starting data cleaning...")
        
        # Remove duplicates
        initial_len = len(df_clean)
        if 'timestamp' in df_clean.columns and 'source' in df_clean.columns:
            df_clean = df_clean.drop_duplicates(subset=['timestamp', 'source'], keep='last')
        else:
            df_clean = df_clean.drop_duplicates(keep='last')
        logger.info(f"Removed {initial_len - len(df_clean)} duplicate records")
        
        # Remove values outside valid ranges
        for col, (min_val, max_val) in self.valid_ranges.items():
            if col in df_clean.columns:
                before = df_clean[col].notna().sum()
                df_clean.loc[(df_clean[col] < min_val) | (df_clean[col] > max_val), col] = np.nan
                after = df_clean[col].notna().sum()
                if before != after:
                    logger.info(f"Set {before - after} out-of-range values to NaN in {col}")
        
        # Remove records with future timestamps
        if 'timestamp' in df_clean.columns:
            future_mask = df_clean['timestamp'] > pd.Timestamp.now()
            if future_mask.sum() > 0:
                df_clean = df_clean[~future_mask]
                logger.info(f"Removed {future_mask.sum()} records with future timestamps")
        
        # Sort by timestamp
        if 'timestamp' in df_clean.columns:
            df_clean = df_clean.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"Cleaning complete. Final records: {len(df_clean)}")
        
        return df_clean
    
    def generate_validation_report(self, results: Dict) -> str:
        """
        Generate a readable validation report
        
        Args:
            results: Validation results dictionary
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Overall status
        status = "✅ PASSED" if results['valid'] else "❌ FAILED"
        report.append(f"Status: {status}")
        report.append(f"Total Records: {results['total_records']:,}")
        report.append(f"Total Columns: {len(results['columns'])}")
        report.append("")
        
        # Errors
        if results['errors']:
            report.append("ERRORS:")
            report.append("-" * 70)
            for error in results['errors']:
                report.append(f"  ❌ {error}")
            report.append("")
        
        # Warnings
        if results['warnings']:
            report.append("WARNINGS:")
            report.append("-" * 70)
            for warning in results['warnings']:
                report.append(f"  ⚠️  {warning}")
            report.append("")
        
        # Statistics
        report.append("STATISTICS:")
        report.append("-" * 70)
        
        # Missing data
        if 'missing_data' in results['statistics']:
            missing = results['statistics']['missing_data']
            report.append(f"  Total Missing Values: {missing['total_missing']:,} ({missing['total_percentage']}%)")
            if missing['by_column']:
                report.append("  Missing by Column:")
                for col, count in sorted(missing['by_column'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                    pct = missing['percentage_by_column'][col]
                    report.append(f"    - {col}: {count:,} ({pct}%)")
        
        # Duplicates
        if 'duplicates' in results['statistics']:
            dup_count = results['statistics']['duplicates']
            report.append(f"  Duplicate Records: {dup_count:,}")
        
        # Outliers
        if 'outliers' in results['statistics'] and results['statistics']['outliers']:
            report.append("  Outliers Detected:")
            for col, stats in results['statistics']['outliers'].items():
                report.append(f"    - {col}: {stats['count']:,} ({stats['percentage']}%)")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def validate_and_clean(input_path: str, output_path: str = None) -> pd.DataFrame:
    """
    Convenience function to validate and clean a CSV file
    
    Args:
        input_path: Path to input CSV
        output_path: Optional path to save cleaned data
        
    Returns:
        Cleaned DataFrame
    """
    # Load data
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df):,} records from {input_path}")
    
    # Convert timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Validate
    validator = DataValidator()
    results = validator.validate_dataframe(df)
    
    # Print report
    report = validator.generate_validation_report(results)
    print(report)
    
    # Clean
    df_clean = validator.clean_data(df)
    
    # Save if output path provided
    if output_path:
        df_clean.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned data to {output_path}")
    
    return df_clean


if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python data_validator.py <input_csv> [output_csv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    df_clean = validate_and_clean(input_file, output_file)
    print(f"\n✅ Validation and cleaning complete!")
    print(f"   Original records: {pd.read_csv(input_file).shape[0]:,}")
    print(f"   Cleaned records: {len(df_clean):,}")