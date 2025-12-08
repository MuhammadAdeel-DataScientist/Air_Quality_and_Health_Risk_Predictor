"""
SHAP Explainer Module
Provides interpretable explanations for AQI predictions
"""
import numpy as np
import pandas as pd
import shap
import pickle
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class SHAPExplainer:
    """
    SHAP-based explainability for AQI predictions
    """
    
    def __init__(self, model, feature_names: List[str], background_data: np.ndarray = None):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained XGBoost model
            feature_names: List of feature names
            background_data: Background dataset for SHAP (optional)
        """
        self.model = model
        self.feature_names = feature_names
        self.background_data = background_data
        self.explainer = None
        self.base_value = None
        
        # Initialize explainer
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP TreeExplainer"""
        try:
            # For tree-based models, TreeExplainer is fastest
            self.explainer = shap.TreeExplainer(self.model)
            
            # Get base value (average prediction)
            if self.background_data is not None:
                self.base_value = self.explainer.expected_value
            else:
                self.base_value = self.explainer.expected_value
                
            print(f"✓ SHAP explainer initialized (base value: {self.base_value:.2f})")
            
        except Exception as e:
            print(f"⚠️ TreeExplainer failed, using KernelExplainer: {e}")
            
            # Fallback to KernelExplainer (slower but works with any model)
            if self.background_data is not None:
                background = shap.sample(self.background_data, 100)
            else:
                # Use model's training data if available
                background = None
            
            self.explainer = shap.KernelExplainer(
                self.model.predict, 
                background
            )
            self.base_value = background.mean() if background is not None else 0
    
    def explain_prediction(self, X: np.ndarray, feature_names: List[str] = None) -> Dict:
        """
        Generate SHAP explanation for a single prediction
        
        Args:
            X: Input features (1D or 2D array)
            feature_names: Optional custom feature names
        
        Returns:
            Dictionary with explanation data
        """
        # Ensure 2D input
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # Get prediction
        prediction = float(self.model.predict(X)[0])
        
        # Use provided feature names or default
        features = feature_names if feature_names else self.feature_names
        
        # Create explanation dictionary
        explanation = {
            'prediction': prediction,
            'base_value': float(self.base_value),
            'shap_values': {},
            'feature_contributions': {},
            'top_positive_features': [],
            'top_negative_features': []
        }
        
        # Extract SHAP values for features
        shap_vals = shap_values[0] if len(shap_values.shape) > 1 else shap_values
        
        for i, feature in enumerate(features):
            shap_val = float(shap_vals[i])
            feature_val = float(X[0, i])
            
            explanation['shap_values'][feature] = shap_val
            explanation['feature_contributions'][feature] = {
                'value': feature_val,
                'shap_value': shap_val,
                'contribution': 'positive' if shap_val > 0 else 'negative',
                'impact': abs(shap_val)
            }
        
        # Sort by absolute SHAP value
        sorted_features = sorted(
            explanation['feature_contributions'].items(),
            key=lambda x: abs(x[1]['shap_value']),
            reverse=True
        )
        
        # Get top positive and negative contributors
        for feature, data in sorted_features:
            if data['shap_value'] > 0:
                explanation['top_positive_features'].append({
                    'feature': feature,
                    'shap_value': data['shap_value'],
                    'feature_value': data['value']
                })
            else:
                explanation['top_negative_features'].append({
                    'feature': feature,
                    'shap_value': data['shap_value'],
                    'feature_value': data['value']
                })
        
        # Limit to top 5 each
        explanation['top_positive_features'] = explanation['top_positive_features'][:5]
        explanation['top_negative_features'] = explanation['top_negative_features'][:5]
        
        return explanation
    
    def get_global_feature_importance(self, X: np.ndarray, max_samples: int = 1000) -> pd.DataFrame:
        """
        Calculate global feature importance using SHAP
        
        Args:
            X: Input data (2D array)
            max_samples: Maximum samples to use for calculation
        
        Returns:
            DataFrame with feature importance
        """
        # Limit samples for performance
        if len(X) > max_samples:
            indices = np.random.choice(len(X), max_samples, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X
        
        print(f"Calculating SHAP values for {len(X_sample)} samples...")
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X_sample)
        
        # Calculate mean absolute SHAP value for each feature
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': mean_abs_shap
        }).sort_values('importance', ascending=False)
        
        # Add percentage
        importance_df['importance_pct'] = (
            importance_df['importance'] / importance_df['importance'].sum() * 100
        )
        
        return importance_df
    
    def explain_multiple(self, X: np.ndarray, n_samples: int = None) -> Dict:
        """
        Generate SHAP values for multiple samples
        
        Args:
            X: Input data (2D array)
            n_samples: Number of samples to explain (None = all)
        
        Returns:
            Dictionary with SHAP values and summary statistics
        """
        if n_samples:
            X = X[:n_samples]
        
        print(f"Generating SHAP values for {len(X)} samples...")
        shap_values = self.explainer.shap_values(X)
        
        return {
            'shap_values': shap_values,
            'base_value': self.base_value,
            'feature_names': self.feature_names,
            'n_samples': len(X)
        }
    
    def get_waterfall_data(self, X: np.ndarray, max_features: int = 10) -> Dict:
        """
        Get data for waterfall plot (API-friendly format)
        
        Args:
            X: Single sample (1D or 2D array)
            max_features: Maximum features to include
        
        Returns:
            Dictionary with waterfall plot data
        """
        explanation = self.explain_prediction(X)
        
        # Sort all features by absolute SHAP value
        all_features = []
        for feature, data in explanation['feature_contributions'].items():
            all_features.append({
                'feature': feature,
                'shap_value': data['shap_value'],
                'feature_value': data['value']
            })
        
        all_features.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        # Take top features
        top_features = all_features[:max_features]
        
        # Calculate cumulative values for waterfall
        waterfall_data = {
            'base_value': explanation['base_value'],
            'prediction': explanation['prediction'],
            'features': []
        }
        
        cumulative = explanation['base_value']
        
        for item in top_features:
            waterfall_data['features'].append({
                'name': item['feature'],
                'value': item['feature_value'],
                'shap_value': item['shap_value'],
                'cumulative_before': cumulative,
                'cumulative_after': cumulative + item['shap_value']
            })
            cumulative += item['shap_value']
        
        # Add "other features" if needed
        other_shap = explanation['prediction'] - cumulative
        if abs(other_shap) > 0.01:
            waterfall_data['features'].append({
                'name': 'Other features',
                'value': None,
                'shap_value': other_shap,
                'cumulative_before': cumulative,
                'cumulative_after': cumulative + other_shap
            })
        
        return waterfall_data
    
    def save(self, save_path: Path):
        """Save explainer to disk"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        explainer_data = {
            'feature_names': self.feature_names,
            'base_value': self.base_value,
            'background_data': self.background_data
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(explainer_data, f)
        
        print(f"✓ SHAP explainer saved to {save_path}")
    
    @classmethod
    def load(cls, load_path: Path, model):
        """Load explainer from disk"""
        load_path = Path(load_path)
        
        with open(load_path, 'rb') as f:
            explainer_data = pickle.load(f)
        
        return cls(
            model=model,
            feature_names=explainer_data['feature_names'],
            background_data=explainer_data.get('background_data')
        )


def create_feature_importance_chart_data(importance_df: pd.DataFrame, top_n: int = 15) -> Dict:
    """
    Create chart-ready data for feature importance
    
    Args:
        importance_df: Feature importance dataframe
        top_n: Number of top features to include
    
    Returns:
        Dictionary with chart data
    """
    top_features = importance_df.head(top_n)
    
    return {
        'features': top_features['feature'].tolist(),
        'importance': top_features['importance'].tolist(),
        'importance_pct': top_features['importance_pct'].tolist()
    }


def explain_aqi_category(aqi_value: float, shap_explanation: Dict) -> str:
    """
    Generate human-readable explanation of AQI prediction
    
    Args:
        aqi_value: Predicted AQI value
        shap_explanation: SHAP explanation dictionary
    
    Returns:
        Human-readable explanation string
    """
    # Determine category
    if aqi_value <= 50:
        category = "Good"
        emoji = "✅"
    elif aqi_value <= 100:
        category = "Moderate"
        emoji = "⚠️"
    elif aqi_value <= 150:
        category = "Unhealthy for Sensitive Groups"
        emoji = "🟠"
    elif aqi_value <= 200:
        category = "Unhealthy"
        emoji = "🔴"
    elif aqi_value <= 300:
        category = "Very Unhealthy"
        emoji = "🟣"
    else:
        category = "Hazardous"
        emoji = "⚫"
    
    # Get top contributors
    top_pos = shap_explanation['top_positive_features'][:3]
    top_neg = shap_explanation['top_negative_features'][:3]
    
    explanation = f"{emoji} The model predicts an AQI of {aqi_value:.1f} ({category}).\n\n"
    
    if top_pos:
        explanation += "**Factors increasing AQI:**\n"
        for feat in top_pos:
            explanation += f"• {feat['feature'].replace('_', ' ').title()}: {feat['feature_value']:.2f} (+{feat['shap_value']:.2f})\n"
        explanation += "\n"
    
    if top_neg:
        explanation += "**Factors decreasing AQI:**\n"
        for feat in top_neg:
            explanation += f"• {feat['feature'].replace('_', ' ').title()}: {feat['feature_value']:.2f} ({feat['shap_value']:.2f})\n"
    
    return explanation