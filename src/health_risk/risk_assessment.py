"""
Health Risk Assessment Module
Provides personalized health risk assessments based on AQI
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass


class AQICategory(Enum):
    """AQI categories based on US EPA standards"""
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class RiskLevel(Enum):
    """Health risk levels"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"
    EXTREME = "Extreme"


@dataclass
class HealthRiskAssessment:
    """Health risk assessment result"""
    aqi: float
    aqi_category: str
    risk_level: str
    health_message: str
    recommendations: List[str]
    vulnerable_group_warnings: Dict[str, str]
    outdoor_activity_level: str
    mask_recommendation: str


class HealthRiskCalculator:
    """Calculate health risks based on AQI and demographics"""
    
    def __init__(self):
        # AQI breakpoints (US EPA)
        self.aqi_breakpoints = {
            AQICategory.GOOD: (0, 50),
            AQICategory.MODERATE: (51, 100),
            AQICategory.UNHEALTHY_SENSITIVE: (101, 150),
            AQICategory.UNHEALTHY: (151, 200),
            AQICategory.VERY_UNHEALTHY: (201, 300),
            AQICategory.HAZARDOUS: (301, 500)
        }
        
        # Color codes for visualization
        self.aqi_colors = {
            AQICategory.GOOD: "#00E400",
            AQICategory.MODERATE: "#FFFF00",
            AQICategory.UNHEALTHY_SENSITIVE: "#FF7E00",
            AQICategory.UNHEALTHY: "#FF0000",
            AQICategory.VERY_UNHEALTHY: "#8F3F97",
            AQICategory.HAZARDOUS: "#7E0023"
        }
        
        # Vulnerable groups
        self.vulnerable_groups = [
            'children',
            'elderly',
            'pregnant_women',
            'asthma_patients',
            'heart_disease_patients',
            'copd_patients',
            'athletes'
        ]
    
    def get_aqi_category(self, aqi: float) -> AQICategory:
        """Get AQI category from AQI value"""
        if pd.isna(aqi):
            return None
        
        for category, (low, high) in self.aqi_breakpoints.items():
            if low <= aqi <= high:
                return category
        
        # If AQI > 500, still hazardous
        if aqi > 500:
            return AQICategory.HAZARDOUS
        
        return None
    
    def get_risk_level(self, aqi: float, is_vulnerable: bool = False) -> RiskLevel:
        """Calculate risk level based on AQI and vulnerability"""
        category = self.get_aqi_category(aqi)
        
        if category == AQICategory.GOOD:
            return RiskLevel.LOW
        elif category == AQICategory.MODERATE:
            return RiskLevel.MODERATE if is_vulnerable else RiskLevel.LOW
        elif category == AQICategory.UNHEALTHY_SENSITIVE:
            return RiskLevel.HIGH if is_vulnerable else RiskLevel.MODERATE
        elif category == AQICategory.UNHEALTHY:
            return RiskLevel.VERY_HIGH if is_vulnerable else RiskLevel.HIGH
        elif category == AQICategory.VERY_UNHEALTHY:
            return RiskLevel.EXTREME if is_vulnerable else RiskLevel.VERY_HIGH
        else:  # HAZARDOUS
            return RiskLevel.EXTREME
    
    def get_health_message(self, aqi: float) -> str:
        """Get general health message for AQI level"""
        category = self.get_aqi_category(aqi)
        
        messages = {
            AQICategory.GOOD: "Air quality is satisfactory, and air pollution poses little or no risk.",
            AQICategory.MODERATE: "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
            AQICategory.UNHEALTHY_SENSITIVE: "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
            AQICategory.UNHEALTHY: "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
            AQICategory.VERY_UNHEALTHY: "Health alert: The risk of health effects is increased for everyone.",
            AQICategory.HAZARDOUS: "Health warning of emergency conditions: everyone is more likely to be affected."
        }
        
        return messages.get(category, "Unable to determine health impact.")
    
    def get_recommendations(self, aqi: float, is_vulnerable: bool = False) -> List[str]:
        """Get personalized recommendations based on AQI"""
        category = self.get_aqi_category(aqi)
        recommendations = []
        
        if category == AQICategory.GOOD:
            recommendations.append("Enjoy outdoor activities!")
            recommendations.append("No precautions needed")
        
        elif category == AQICategory.MODERATE:
            if is_vulnerable:
                recommendations.append("Consider reducing prolonged outdoor exertion")
                recommendations.append("Watch for symptoms like coughing or shortness of breath")
            else:
                recommendations.append("Outdoor activities are generally safe")
                recommendations.append("Sensitive individuals should watch for symptoms")
        
        elif category == AQICategory.UNHEALTHY_SENSITIVE:
            recommendations.append("Sensitive groups should reduce prolonged outdoor exertion")
            recommendations.append("Keep windows closed to reduce indoor pollution")
            if is_vulnerable:
                recommendations.append("Consider moving activities indoors")
                recommendations.append("Have quick-relief medication readily available (if applicable)")
        
        elif category == AQICategory.UNHEALTHY:
            recommendations.append("Everyone should reduce prolonged outdoor exertion")
            recommendations.append("Sensitive groups should avoid prolonged outdoor exertion")
            recommendations.append("Keep windows closed")
            recommendations.append("Use air purifiers indoors if available")
            if is_vulnerable:
                recommendations.append("Stay indoors as much as possible")
        
        elif category == AQICategory.VERY_UNHEALTHY:
            recommendations.append("Everyone should avoid prolonged outdoor exertion")
            recommendations.append("Sensitive groups should remain indoors")
            recommendations.append("Keep windows and doors closed")
            recommendations.append("Use HEPA air purifiers")
            recommendations.append("Postpone outdoor activities")
        
        else:  # HAZARDOUS
            recommendations.append("STAY INDOORS - Emergency conditions")
            recommendations.append("Keep all windows and doors closed")
            recommendations.append("Run air purifiers continuously")
            recommendations.append("Avoid all outdoor activities")
            recommendations.append("Vulnerable individuals should seek medical advice")
            recommendations.append("Use N95/N99 masks if you must go outside")
        
        return recommendations
    
    def get_outdoor_activity_level(self, aqi: float, is_vulnerable: bool = False) -> str:
        """Get outdoor activity recommendation"""
        category = self.get_aqi_category(aqi)
        
        if category == AQICategory.GOOD:
            return "Unrestricted"
        elif category == AQICategory.MODERATE:
            return "Generally Safe" if not is_vulnerable else "Reduce Prolonged Exertion"
        elif category == AQICategory.UNHEALTHY_SENSITIVE:
            return "Reduce Prolonged Exertion" if not is_vulnerable else "Avoid Prolonged Exertion"
        elif category == AQICategory.UNHEALTHY:
            return "Avoid Prolonged Exertion" if not is_vulnerable else "Minimize Outdoor Activity"
        elif category == AQICategory.VERY_UNHEALTHY:
            return "Minimize Outdoor Activity" if not is_vulnerable else "Stay Indoors"
        else:  # HAZARDOUS
            return "Stay Indoors - Emergency"
    
    def get_mask_recommendation(self, aqi: float) -> str:
        """Get mask wearing recommendation"""
        category = self.get_aqi_category(aqi)
        
        if category in [AQICategory.GOOD, AQICategory.MODERATE]:
            return "Not necessary"
        elif category == AQICategory.UNHEALTHY_SENSITIVE:
            return "Recommended for sensitive groups"
        elif category == AQICategory.UNHEALTHY:
            return "N95 mask recommended for everyone outdoors"
        else:  # VERY_UNHEALTHY or HAZARDOUS
            return "N95/N99 mask required if going outdoors"
    
    def get_vulnerable_group_warnings(self, aqi: float) -> Dict[str, str]:
        """Get warnings for specific vulnerable groups"""
        category = self.get_aqi_category(aqi)
        warnings = {}
        
        if category in [AQICategory.GOOD, AQICategory.MODERATE]:
            return warnings  # No special warnings needed
        
        # Children
        warnings['children'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Children should reduce prolonged outdoor play. Watch for symptoms.",
            AQICategory.UNHEALTHY: "Children should avoid prolonged outdoor activities. Indoor play recommended.",
            AQICategory.VERY_UNHEALTHY: "Keep children indoors. Close schools may consider closure.",
            AQICategory.HAZARDOUS: "CRITICAL: Keep children indoors at all times. Schools should close."
        }.get(category, "")
        
        # Elderly
        warnings['elderly'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Seniors should limit time outdoors and reduce exertion.",
            AQICategory.UNHEALTHY: "Seniors should stay indoors and minimize physical activity.",
            AQICategory.VERY_UNHEALTHY: "Seniors must stay indoors. Monitor for chest pain or breathing difficulty.",
            AQICategory.HAZARDOUS: "CRITICAL: Seniors should remain indoors. Seek medical help if needed."
        }.get(category, "")
        
        # Pregnant women
        warnings['pregnant_women'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Limit outdoor exposure to protect fetal health.",
            AQICategory.UNHEALTHY: "Avoid outdoor activities. Indoor rest recommended.",
            AQICategory.VERY_UNHEALTHY: "Stay indoors. High pollution may affect pregnancy.",
            AQICategory.HAZARDOUS: "CRITICAL: Remain indoors. Consult doctor if experiencing symptoms."
        }.get(category, "")
        
        # Asthma patients
        warnings['asthma_patients'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Have quick-relief inhaler ready. Reduce outdoor activities.",
            AQICategory.UNHEALTHY: "High risk of asthma attacks. Stay indoors. Keep medication close.",
            AQICategory.VERY_UNHEALTHY: "SEVERE RISK: Stay indoors. Monitor symptoms closely. Have emergency plan ready.",
            AQICategory.HAZARDOUS: "CRITICAL: Extreme asthma risk. Stay indoors. Seek emergency care if symptoms worsen."
        }.get(category, "")
        
        # Heart disease patients
        warnings['heart_disease_patients'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Reduce physical exertion. Monitor for chest discomfort.",
            AQICategory.UNHEALTHY: "Avoid all outdoor activities. Rest indoors. Watch for symptoms.",
            AQICategory.VERY_UNHEALTHY: "HIGH RISK: Stay indoors. Seek medical attention if experiencing chest pain.",
            AQICategory.HAZARDOUS: "CRITICAL: Cardiovascular emergency risk. Stay indoors. Call doctor if symptoms appear."
        }.get(category, "")
        
        # COPD patients
        warnings['copd_patients'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Use medications as prescribed. Limit outdoor exposure.",
            AQICategory.UNHEALTHY: "High risk of exacerbation. Stay indoors. Keep oxygen therapy ready if applicable.",
            AQICategory.VERY_UNHEALTHY: "SEVERE RISK: Stay indoors. Monitor oxygen levels. Have emergency plan.",
            AQICategory.HAZARDOUS: "CRITICAL: Extreme risk of respiratory failure. Stay indoors. Seek immediate care if worsening."
        }.get(category, "")
        
        # Athletes
        warnings['athletes'] = {
            AQICategory.UNHEALTHY_SENSITIVE: "Reduce intensity and duration of outdoor training.",
            AQICategory.UNHEALTHY: "Move training indoors. High-intensity exercise is risky.",
            AQICategory.VERY_UNHEALTHY: "Cancel outdoor training. Indoor low-intensity only.",
            AQICategory.HAZARDOUS: "CRITICAL: No training. Rest and recovery mode."
        }.get(category, "")
        
        return warnings
    
    def assess_health_risk(self, 
                          aqi: float,
                          vulnerable_groups: List[str] = None) -> HealthRiskAssessment:
        """
        Complete health risk assessment
        
        Args:
            aqi: Air Quality Index value
            vulnerable_groups: List of applicable vulnerable groups
            
        Returns:
            HealthRiskAssessment object with complete assessment
        """
        is_vulnerable = bool(vulnerable_groups)
        
        category = self.get_aqi_category(aqi)
        risk_level = self.get_risk_level(aqi, is_vulnerable)
        
        assessment = HealthRiskAssessment(
            aqi=aqi,
            aqi_category=category.value if category else "Unknown",
            risk_level=risk_level.value if risk_level else "Unknown",
            health_message=self.get_health_message(aqi),
            recommendations=self.get_recommendations(aqi, is_vulnerable),
            vulnerable_group_warnings=self.get_vulnerable_group_warnings(aqi),
            outdoor_activity_level=self.get_outdoor_activity_level(aqi, is_vulnerable),
            mask_recommendation=self.get_mask_recommendation(aqi)
        )
        
        return assessment
    
    def get_best_time_for_outdoor(self, 
                                  hourly_aqi: Dict[int, float],
                                  duration_hours: int = 2) -> Tuple[int, float]:
        """
        Find best time window for outdoor activities
        
        Args:
            hourly_aqi: Dictionary of hour -> AQI values
            duration_hours: Required duration of activity
            
        Returns:
            Tuple of (best_start_hour, average_aqi_during_window)
        """
        if not hourly_aqi or duration_hours < 1:
            return None, None
        
        hours = sorted(hourly_aqi.keys())
        best_hour = None
        best_avg_aqi = float('inf')
        
        for start_hour in hours:
            # Get window
            window_hours = [h for h in hours 
                          if start_hour <= h < start_hour + duration_hours]
            
            if len(window_hours) == duration_hours:
                avg_aqi = np.mean([hourly_aqi[h] for h in window_hours])
                
                if avg_aqi < best_avg_aqi:
                    best_avg_aqi = avg_aqi
                    best_hour = start_hour
        
        return best_hour, best_avg_aqi
    
    def calculate_daily_exposure(self,
                                hourly_aqi: Dict[int, float],
                                outdoor_hours: List[int]) -> Dict[str, float]:
        """
        Calculate daily pollution exposure
        
        Args:
            hourly_aqi: Hour -> AQI mapping
            outdoor_hours: Hours spent outdoors
            
        Returns:
            Dictionary with exposure metrics
        """
        if not outdoor_hours:
            return {
                'total_exposure': 0,
                'average_exposure': 0,
                'peak_exposure': 0,
                'exposure_category': 'Minimal'
            }
        
        exposure_values = [hourly_aqi.get(h, 0) for h in outdoor_hours]
        
        total_exposure = sum(exposure_values)
        avg_exposure = np.mean(exposure_values)
        peak_exposure = max(exposure_values)
        
        # Categorize exposure
        if avg_exposure <= 50:
            category = 'Low'
        elif avg_exposure <= 100:
            category = 'Moderate'
        elif avg_exposure <= 150:
            category = 'High'
        else:
            category = 'Very High'
        
        return {
            'total_exposure': round(total_exposure, 2),
            'average_exposure': round(avg_exposure, 2),
            'peak_exposure': round(peak_exposure, 2),
            'exposure_category': category,
            'hours_outdoors': len(outdoor_hours)
        }


def format_assessment_report(assessment: HealthRiskAssessment) -> str:
    """Format assessment as readable report"""
    report = []
    report.append("=" * 60)
    report.append("HEALTH RISK ASSESSMENT REPORT")
    report.append("=" * 60)
    report.append(f"\nAir Quality Index: {assessment.aqi:.0f}")
    report.append(f"Category: {assessment.aqi_category}")
    report.append(f"Risk Level: {assessment.risk_level}")
    report.append(f"\nHealth Message:")
    report.append(f"{assessment.health_message}")
    report.append(f"\nOutdoor Activity Level: {assessment.outdoor_activity_level}")
    report.append(f"Mask Recommendation: {assessment.mask_recommendation}")
    
    report.append(f"\nRecommendations:")
    for i, rec in enumerate(assessment.recommendations, 1):
        report.append(f"  {i}. {rec}")
    
    if assessment.vulnerable_group_warnings:
        report.append(f"\nVulnerable Group Warnings:")
        for group, warning in assessment.vulnerable_group_warnings.items():
            if warning:
                report.append(f"\n  {group.replace('_', ' ').title()}:")
                report.append(f"  {warning}")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    calculator = HealthRiskCalculator()
    
    # Example 1: General population, moderate AQI
    print("Example 1: General Population, AQI = 75")
    assessment1 = calculator.assess_health_risk(aqi=75)
    print(format_assessment_report(assessment1))
    
    # Example 2: Asthma patient, unhealthy AQI
    print("\n\nExample 2: Asthma Patient, AQI = 165")
    assessment2 = calculator.assess_health_risk(
        aqi=165, 
        vulnerable_groups=['asthma_patients']
    )
    print(format_assessment_report(assessment2))
    
    # Example 3: Best time for outdoor activity
    print("\n\nExample 3: Finding Best Time for Outdoor Activity")
    hourly_forecast = {
        6: 45, 7: 52, 8: 68, 9: 85, 10: 92,
        11: 98, 12: 105, 13: 112, 14: 108, 15: 95,
        16: 87, 17: 78, 18: 65, 19: 55, 20: 48
    }
    
    best_hour, avg_aqi = calculator.get_best_time_for_outdoor(
        hourly_forecast, duration_hours=2
    )
    
    print(f"Best time for 2-hour outdoor activity:")
    print(f"  Start at: {best_hour}:00")
    print(f"  Average AQI: {avg_aqi:.1f}")
    print(f"  Category: {calculator.get_aqi_category(avg_aqi).value}")