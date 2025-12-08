"""
Generate SHAP Values and Feature Importance
Run this script ONCE to pre-compute SHAP values for the test dataset
FIXED: Handles XGBoost version compatibility issues
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import pickle
import json
import numpy as np
import pandas as pd
import shap
from src.explainability import create_feature_importance_chart_data

# Paths
MODEL_PATHS = [
    project_root / "data" / "models" / "xgboost_tuned.pkl",
    project_root / "data" / "models" / "best_model_xgboost_tuned.pkl",
    project_root / "data" / "models" / "best_model_gradientboosting.pkl",
]
TEST_DATA_PATH = project_root / "data" / "processed" / "features_test.csv"
FEATURES_PATH = project_root / "data" / "processed" / "feature_sets.json"
OUTPUT_DIR = project_root / "data" / "explainability"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("🔍 GENERATING SHAP EXPLANATIONS")
print("=" * 70)

# Load model - try all possible paths
model = None
model_path = None

print(f"\n1. Looking for model...")
for path in MODEL_PATHS:
    if path.exists():
        print(f"   ✓ Found model at: {path}")
        try:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            
            # Fix missing gpu_id attribute
            if not hasattr(model, 'gpu_id'):
                model.gpu_id = None
            
            model_path = path
            print(f"   ✓ Model loaded: {type(model)}")
            break
        except Exception as e:
            print(f"   ⚠️ Could not load {path}: {e}")
            continue

if model is None:
    print(f"\n   ❌ No model found in any of these locations:")
    for path in MODEL_PATHS:
        print(f"      • {path}")
    sys.exit(1)

# Load features
print(f"\n2. Loading feature configuration...")
with open(FEATURES_PATH, 'r') as f:
    feature_sets = json.load(f)

# Use comprehensive features (33 features - matches backend)
feature_names = feature_sets['comprehensive']
print(f"   ✓ Using {len(feature_names)} features")

# Load test data
print(f"\n3. Loading test data from {TEST_DATA_PATH}...")
df_test = pd.read_csv(TEST_DATA_PATH)
print(f"   ✓ Loaded {len(df_test):,} test samples")

# Prepare features
print(f"\n4. Preparing features...")
available_features = [f for f in feature_names if f in df_test.columns]
print(f"   ✓ {len(available_features)}/{len(feature_names)} features available")

if len(available_features) < len(feature_names):
    missing = set(feature_names) - set(available_features)
    print(f"   ⚠️  Missing features: {list(missing)[:5]}...")

X_test = df_test[available_features].copy()
X_test = X_test.fillna(X_test.median())

# Sample background data
print(f"\n5. Sampling background data...")
n_background = min(100, len(X_test))
background_indices = np.random.choice(len(X_test), n_background, replace=False)
X_background = X_test.iloc[background_indices].values

print(f"   ✓ Background data: {n_background} samples")

# Initialize SHAP explainer with compatibility fixes
print(f"\n6. Initializing SHAP explainer (this may take a minute)...")

explainer = None
base_value = 0
use_shap = False

try:
    # Try TreeExplainer first (fastest for tree models)
    # Convert to booster format to avoid compatibility issues
    if hasattr(model, 'get_booster'):
        booster = model.get_booster()
        explainer = shap.TreeExplainer(booster)
    else:
        explainer = shap.TreeExplainer(model)
    
    base_value = explainer.expected_value
    
    # Handle array base values
    if isinstance(base_value, np.ndarray):
        base_value = float(base_value[0]) if len(base_value) > 0 else float(base_value)
    
    # Test with a small sample to verify it works
    test_sample = X_test.head(1).values
    test_shap = explainer.shap_values(test_sample)
    
    print(f"   ✓ TreeExplainer initialized (base value: {base_value:.2f})")
    use_shap = True
    
except Exception as e:
    print(f"   ⚠️ TreeExplainer failed: {str(e)[:150]}")
    print(f"   ℹ️  Falling back to model's built-in feature importance...")
    
    explainer = None
    use_shap = False
    
    # Get model's feature importance as fallback
    if hasattr(model, 'feature_importances_'):
        importance_values = model.feature_importances_
        print(f"   ✓ Using model.feature_importances_")
    elif hasattr(model, 'coef_'):
        importance_values = np.abs(model.coef_)
        print(f"   ✓ Using model.coef_")
    else:
        print("   ❌ Cannot extract feature importance from model")
        sys.exit(1)

# Generate global feature importance
print(f"\n7. Computing global feature importance...")

if use_shap and explainer is not None:
    try:
        # Use smaller sample to avoid memory issues
        n_sample = min(200, len(X_test))
        X_sample = X_test.head(n_sample).values
        print(f"   Calculating SHAP values for {len(X_sample)} samples...")
        
        shap_values = explainer.shap_values(X_sample)
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Ensure correct shape
        if len(shap_values.shape) == 1:
            shap_values = shap_values.reshape(1, -1)
        
        # Calculate mean absolute SHAP values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        # Verify length matches features
        if len(mean_abs_shap) != len(available_features):
            print(f"   ⚠️ Shape mismatch: {len(mean_abs_shap)} SHAP values vs {len(available_features)} features")
            raise ValueError("Feature count mismatch")
        
        importance_df = pd.DataFrame({
            'feature': available_features,
            'importance': mean_abs_shap
        }).sort_values('importance', ascending=False)
        
        print(f"   ✓ SHAP-based importance calculated")
        
    except Exception as e:
        print(f"   ⚠️ SHAP calculation failed: {str(e)[:150]}")
        print(f"   Using model's built-in feature importance...")
        use_shap = False
        
        # Fallback to model's feature importance
        if hasattr(model, 'feature_importances_'):
            importance_values = model.feature_importances_
        
        # Verify lengths match
        if len(importance_values) != len(available_features):
            print(f"   ⚠️ Feature importance length mismatch")
            print(f"      Model importance: {len(importance_values)}")
            print(f"      Available features: {len(available_features)}")
            # Truncate or pad to match
            if len(importance_values) > len(available_features):
                importance_values = importance_values[:len(available_features)]
            else:
                importance_values = np.pad(
                    importance_values, 
                    (0, len(available_features) - len(importance_values)),
                    'constant'
                )
        
        importance_df = pd.DataFrame({
            'feature': available_features,
            'importance': importance_values
        }).sort_values('importance', ascending=False)

else:
    # Use model's built-in importance (no SHAP)
    print(f"   Using model's built-in feature importance...")
    
    # Verify lengths match
    if len(importance_values) != len(available_features):
        print(f"   ⚠️ Feature importance length mismatch")
        print(f"      Model importance: {len(importance_values)}")
        print(f"      Available features: {len(available_features)}")
        
        # Truncate or pad to match
        if len(importance_values) > len(available_features):
            importance_values = importance_values[:len(available_features)]
        else:
            importance_values = np.pad(
                importance_values, 
                (0, len(available_features) - len(importance_values)),
                'constant'
            )
    
    importance_df = pd.DataFrame({
        'feature': available_features,
        'importance': importance_values
    }).sort_values('importance', ascending=False)

# Add percentage
importance_df['importance_pct'] = (
    importance_df['importance'] / importance_df['importance'].sum() * 100
)

print(f"\n   📊 Top 10 Most Important Features:")
print(importance_df.head(10).to_string(index=False))

# Save feature importance
importance_path = OUTPUT_DIR / "feature_importance.csv"
importance_df.to_csv(importance_path, index=False)
print(f"\n   ✓ Saved to: {importance_path}")

# Create JSON version for API
importance_json = create_feature_importance_chart_data(importance_df, top_n=20)
importance_json_path = OUTPUT_DIR / "feature_importance.json"
with open(importance_json_path, 'w') as f:
    json.dump(importance_json, f, indent=2)
print(f"   ✓ Saved JSON to: {importance_json_path}")

# Generate sample explanations (only if SHAP works)
sample_explanations = []

if use_shap and explainer is not None:
    print(f"\n8. Generating sample explanations...")
    n_samples = min(30, len(X_test))  # Reduced for speed and stability
    sample_indices = np.random.choice(len(X_test), n_samples, replace=False)
    
    for i, idx in enumerate(sample_indices):
        if i % 10 == 0:
            print(f"   Progress: {i}/{n_samples} samples...")
        
        try:
            X_sample = X_test.iloc[idx].values.reshape(1, -1)
            
            # Get SHAP values
            shap_vals = explainer.shap_values(X_sample)
            
            # Handle different formats
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[0]
            if len(shap_vals.shape) > 1:
                shap_vals = shap_vals[0]
            
            # Verify length
            if len(shap_vals) != len(available_features):
                if i == 0:
                    print(f"   ⚠️ SHAP values length mismatch, skipping samples")
                break
            
            # Get prediction
            prediction = float(model.predict(X_sample)[0])
            
            # Build explanation
            explanation = {
                'prediction': prediction,
                'base_value': float(base_value),
                'sample_index': int(idx)
            }
            
            # Add city and timestamp if available
            if 'city_name' in df_test.columns:
                explanation['city'] = str(df_test.iloc[idx]['city_name'])
            if 'timestamp' in df_test.columns:
                explanation['timestamp'] = str(df_test.iloc[idx]['timestamp'])
            
            # Top features
            feature_impacts = []
            for j, feature in enumerate(available_features):
                feature_impacts.append({
                    'feature': feature,
                    'value': float(X_sample[0, j]),
                    'shap_value': float(shap_vals[j])
                })
            
            # Sort by absolute SHAP value
            feature_impacts.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            explanation['top_features'] = feature_impacts[:10]
            explanation['top_positive'] = [f for f in feature_impacts if f['shap_value'] > 0][:5]
            explanation['top_negative'] = [f for f in feature_impacts if f['shap_value'] < 0][:5]
            
            sample_explanations.append(explanation)
            
        except Exception as e:
            if i == 0:  # Only print first error
                print(f"   ⚠️ Error on sample {idx}: {str(e)[:150]}")
            continue
    
    if sample_explanations:
        print(f"   ✓ Generated {len(sample_explanations)} explanations")
        
        # Save sample explanations
        explanations_path = OUTPUT_DIR / "sample_explanations.json"
        with open(explanations_path, 'w') as f:
            json.dump(sample_explanations, f, indent=2)
        print(f"   ✓ Saved to: {explanations_path}")
    else:
        print(f"   ⚠️ Could not generate sample explanations")
else:
    print(f"\n8. Skipping sample explanations (SHAP not available)")

# Create metadata
print(f"\n9. Saving metadata...")

metadata = {
    'model_path': str(model_path),
    'model_type': str(type(model).__name__),
    'features': available_features,
    'n_features': len(available_features),
    'test_samples': len(df_test),
    'shap_samples': len(sample_explanations),
    'base_value': float(base_value) if use_shap else 0.0,
    'top_features': importance_df.head(10)['feature'].tolist(),
    'explainer_type': 'SHAP' if use_shap else 'ModelImportance',
    'shap_available': use_shap
}

metadata_path = OUTPUT_DIR / "metadata.json"
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✓ Saved metadata to: {metadata_path}")

print("\n" + "=" * 70)
print("✅ SHAP GENERATION COMPLETE!")
print("=" * 70)

print(f"\n📁 Generated files in {OUTPUT_DIR}:")
print(f"   • feature_importance.csv ({len(importance_df)} features)")
print(f"   • feature_importance.json")
if sample_explanations:
    print(f"   • sample_explanations.json ({len(sample_explanations)} samples)")
print(f"   • metadata.json")

print(f"\n🚀 Next steps:")
print(f"   1. Backend: Add SHAP endpoints to API")
print(f"   2. Frontend: Add Explainability page")
print(f"   3. Test: View explanations in web interface")

print("\n" + "=" * 70)