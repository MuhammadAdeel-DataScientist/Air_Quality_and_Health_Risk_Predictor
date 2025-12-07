"""
IMPROVED Script to fix AQI values in collected data
This version properly detects and fixes the 1-5 scale issue
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


def calculate_aqi_from_pm25(pm25):
    """
    Calculate AQI from PM2.5 using US EPA standard
    
    Args:
        pm25: PM2.5 concentration in µg/m³
        
    Returns:
        AQI value (0-500)
    """
    if pd.isna(pm25) or pm25 < 0:
        return np.nan
    
    # AQI breakpoints for PM2.5 (US EPA standard)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= pm25 <= c_high:
            # Linear interpolation
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return round(aqi)
    
    # If PM2.5 > 500.4, return max AQI
    return 500


def detect_wrong_aqi_scale(df):
    """
    Detect if AQI is on wrong scale by checking multiple indicators
    
    Args:
        df: DataFrame with AQI and PM2.5 data
        
    Returns:
        bool: True if AQI scale is wrong
    """
    if 'aqi' not in df.columns or 'pm25' not in df.columns:
        return False
    
    # Remove NaN values
    valid_data = df[['aqi', 'pm25']].dropna()
    
    if len(valid_data) < 10:
        return False
    
    # Calculate expected AQI from PM2.5
    valid_data['expected_aqi'] = valid_data['pm25'].apply(calculate_aqi_from_pm25)
    
    # Check correlation between actual and expected
    correlation = valid_data['aqi'].corr(valid_data['expected_aqi'])
    
    # Check if most AQI values are very low
    low_aqi_pct = (valid_data['aqi'] <= 10).sum() / len(valid_data)
    
    # Check mean AQI vs mean expected AQI
    mean_aqi = valid_data['aqi'].mean()
    mean_expected = valid_data['expected_aqi'].mean()
    ratio = mean_aqi / mean_expected if mean_expected > 0 else 0
    
    print(f"\n🔍 AQI Scale Detection:")
    print(f"   Current AQI mean: {mean_aqi:.2f}")
    print(f"   Expected AQI mean (from PM2.5): {mean_expected:.2f}")
    print(f"   Ratio: {ratio:.3f}")
    print(f"   Correlation: {correlation:.3f}")
    print(f"   % of AQI values <= 10: {low_aqi_pct*100:.1f}%")
    
    # Decision criteria
    wrong_scale = (
        (correlation < 0.7) or  # Poor correlation
        (low_aqi_pct > 0.7) or  # Most values very low
        (ratio < 0.2)  # Mean is way too low
    )
    
    if wrong_scale:
        print("   ❌ AQI scale appears to be WRONG (likely 1-5 scale)")
    else:
        print("   ✓ AQI scale appears correct")
    
    return wrong_scale


def fix_aqi_values(df, force_recalculate=False):
    """
    Fix AQI values in dataframe
    
    Args:
        df: DataFrame with air quality data
        force_recalculate: Force recalculation even if scale seems correct
        
    Returns:
        DataFrame with corrected AQI values
    """
    df = df.copy()
    
    print("\n" + "=" * 70)
    print("Analyzing AQI values...")
    print(f"Current AQI statistics:")
    print(f"  Mean: {df['aqi'].mean():.2f}")
    print(f"  Median: {df['aqi'].median():.2f}")
    print(f"  Min: {df['aqi'].min():.2f}")
    print(f"  Max: {df['aqi'].max():.2f}")
    
    # Detect if scale is wrong
    needs_fix = detect_wrong_aqi_scale(df) or force_recalculate
    
    if needs_fix:
        print("\n🔧 Recalculating AQI from PM2.5 values...")
        
        # Save original AQI for comparison
        df['aqi_original'] = df['aqi']
        
        # Recalculate AQI from PM2.5
        df['aqi'] = df['pm25'].apply(calculate_aqi_from_pm25)
        
        # Count how many were recalculated
        recalculated = df['aqi'].notna().sum()
        
        print(f"\n✅ AQI RECALCULATED!")
        print(f"   Records recalculated: {recalculated:,}")
        print(f"\nNew AQI statistics:")
        print(f"  Mean: {df['aqi'].mean():.2f}")
        print(f"  Median: {df['aqi'].median():.2f}")
        print(f"  Min: {df['aqi'].min():.2f}")
        print(f"  Max: {df['aqi'].max():.2f}")
        
        # Show comparison
        comparison = pd.DataFrame({
            'Original': df['aqi_original'].describe(),
            'Corrected': df['aqi'].describe()
        })
        print("\n📊 Before vs After Comparison:")
        print(comparison)
        
    else:
        print("\n✓ AQI values appear correct, no changes needed")
    
    return df, needs_fix


def add_aqi_category(df):
    """Add AQI category column based on US EPA standards"""
    def categorize_aqi(aqi):
        if pd.isna(aqi):
            return 'Unknown'
        elif aqi <= 50:
            return 'Good'
        elif aqi <= 100:
            return 'Moderate'
        elif aqi <= 150:
            return 'Unhealthy for Sensitive Groups'
        elif aqi <= 200:
            return 'Unhealthy'
        elif aqi <= 300:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    df['aqi_category'] = df['aqi'].apply(categorize_aqi)
    
    # Show distribution
    print("\n📊 AQI Category Distribution:")
    category_counts = df['aqi_category'].value_counts()
    category_pct = (category_counts / len(df) * 100).round(1)
    
    for category, count in category_counts.items():
        pct = category_pct[category]
        print(f"   {category:.<40} {count:>6,} ({pct:>5.1f}%)")
    
    return df


def validate_correction(df):
    """Validate that the correction was successful"""
    print("\n" + "=" * 70)
    print("🔍 VALIDATION")
    print("=" * 70)
    
    if 'aqi' not in df.columns or 'pm25' not in df.columns:
        print("❌ Cannot validate: missing required columns")
        return False
    
    valid_data = df[['aqi', 'pm25']].dropna()
    
    if len(valid_data) < 10:
        print("❌ Cannot validate: insufficient data")
        return False
    
    # Recalculate expected AQI
    valid_data['expected_aqi'] = valid_data['pm25'].apply(calculate_aqi_from_pm25)
    
    # Check correlation
    correlation = valid_data['aqi'].corr(valid_data['expected_aqi'])
    
    # Check mean difference
    mean_diff = abs(valid_data['aqi'].mean() - valid_data['expected_aqi'].mean())
    mean_diff_pct = (mean_diff / valid_data['expected_aqi'].mean()) * 100
    
    print(f"✓ AQI vs PM2.5 correlation: {correlation:.3f}")
    print(f"✓ Mean AQI difference: {mean_diff:.2f} ({mean_diff_pct:.1f}%)")
    
    is_valid = correlation > 0.85 and mean_diff_pct < 15
    
    if is_valid:
        print("\n✅ VALIDATION PASSED - AQI values are now correct!")
    else:
        print("\n⚠️  VALIDATION WARNING - There may still be issues")
        if correlation < 0.85:
            print(f"   - Correlation too low: {correlation:.3f} (should be > 0.85)")
        if mean_diff_pct > 15:
            print(f"   - Mean difference too high: {mean_diff_pct:.1f}% (should be < 15%)")
    
    return is_valid


def main():
    print("=" * 70)
    print("IMPROVED AQI VALUE CORRECTION SCRIPT")
    print("=" * 70)
    
    # Find data files
    data_dir = Path('data/raw')
    csv_files = list(data_dir.glob('air_quality_*.csv'))
    
    if not csv_files:
        print("❌ No data files found in data/raw/")
        return
    
    print(f"\nFound {len(csv_files)} data files:")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {f.name}")
    
    # Process each file
    for file_path in csv_files:
        print("\n" + "=" * 70)
        print(f"Processing: {file_path.name}")
        print("=" * 70)
        
        # Load data
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        print(f"✓ Loaded {len(df):,} records")
        
        # Fix AQI (force recalculation if needed)
        df_fixed, was_fixed = fix_aqi_values(df, force_recalculate=False)
        
        # Add categories
        df_fixed = add_aqi_category(df_fixed)
        
        # Validate
        if was_fixed:
            validate_correction(df_fixed)
        
        # Save corrected data
        output_dir = Path('data/processed')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"corrected_{file_path.name}"
        
        df_fixed.to_csv(output_path, index=False)
        print(f"\n💾 Saved corrected data to: {output_path}")
    
    print("\n" + "=" * 70)
    print("✅ ALL FILES PROCESSED!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Check data/processed/ for corrected files")
    print("2. Re-run notebooks using corrected data")
    print("3. Verify AQI values make sense for each city")


if __name__ == "__main__":
    main()