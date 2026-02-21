"""
=============================================================================
LAYER 6: DRIVER RECOMMENDATION ENGINE
=============================================================================

This engine generates smart, actionable recommendations for drivers
based on real-time telemetry and analytics.

Rules:
- If Temp > 8°C: "Reduce temperature to 3°C immediately."
- If vibration > 0.5: "Reduce speed to avoid spoilage from mechanical stress."
- If SurvivalMargin < 2 hours: "Immediate rerouting required."

Returns array of recommendations.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, List, Optional

class DriverRecommender:
    """
    Driver Recommendation Engine for Real-Time Guidance
    
    Generates smart recommendations based on telemetry data
    and survival margin analysis.
    """
    
    # Thresholds
    TEMP_THRESHOLD_CRITICAL = 8      # °C
    TEMP_THRESHOLD_WARNING = 6       # °C
    TEMP_IDEAL_MIN = 2                # °C
    TEMP_IDEAL_MAX = 4                # °C
    
    VIBRATION_THRESHOLD_CRITICAL = 0.5  # G
    VIBRATION_THRESHOLD_WARNING = 0.3  # G
    
    HUMIDITY_THRESHOLD_HIGH = 70     # %
    HUMIDITY_THRESHOLD_LOW = 40      # %
    
    SURVIVAL_MARGIN_CRITICAL = 2     # hours
    SURVIVAL_MARGIN_WARNING = 5       # hours
    
    def __init__(self):
        """Initialize the driver recommender"""
        self.recommendation_history = []
        
    def generate_recommendations(self, telemetry: Dict, survival_margin: Optional[float] = None) -> List[Dict]:
        """
        Generate recommendations based on telemetry data
        
        Args:
            telemetry: Dictionary with temperature, humidity, vibration
            survival_margin: Optional survival margin in hours
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Temperature recommendations
        temp_recs = self._check_temperature(telemetry.get('temperature', 0))
        recommendations.extend(temp_recs)
        
        # Vibration recommendations
        vib_recs = self._check_vibration(telemetry.get('vibration', 0))
        recommendations.extend(vib_recs)
        
        # Humidity recommendations
        humid_recs = self._check_humidity(telemetry.get('humidity', 0))
        recommendations.extend(humid_recs)
        
        # Survival margin recommendations
        if survival_margin is not None:
            sm_recs = self._check_survival_margin(survival_margin)
            recommendations.extend(sm_recs)
        
        # Sort by priority (critical first)
        recommendations.sort(key=lambda x: self._priority_score(x['priority']), reverse=True)
        
        # Store in history
        self.recommendation_history.append({
            'timestamp': telemetry.get('timestamp', 0),
            'recommendations': recommendations
        })
        
        return recommendations
    
    def _check_temperature(self, temperature: float) -> List[Dict]:
        """Check temperature and generate recommendations"""
        recs = []
        
        if temperature > self.TEMP_THRESHOLD_CRITICAL:
            recs.append({
                'type': 'TEMPERATURE',
                'priority': 'CRITICAL',
                'message': 'CRITICAL: Reduce temperature to 3°C immediately!',
                'current': f'{temperature}°C',
                'target': '3°C',
                'action': 'REDUCE_TEMPERATURE',
                'reason': f'Temperature {temperature}°C is dangerously high - rapid spoilage occurring'
            })
        elif temperature > self.TEMP_THRESHOLD_WARNING:
            recs.append({
                'type': 'TEMPERATURE',
                'priority': 'WARNING',
                'message': f'Warning: Temperature at {temperature}°C - aim for 2-4°C range',
                'current': f'{temperature}°C',
                'target': '2-4°C',
                'action': 'ADJUST_TEMPERATURE',
                'reason': 'Temperature above optimal range - increased decay rate'
            })
        elif temperature < 0:
            recs.append({
                'type': 'TEMPERATURE',
                'priority': 'WARNING',
                'message': 'Warning: Temperature near freezing - prevent product freezing',
                'current': f'{temperature}°C',
                'target': '>0°C',
                'action': 'INCREASE_TEMPERATURE',
                'reason': 'Risk of freezing damage to produce'
            })
            
        return recs
    
    def _check_vibration(self, vibration: float) -> List[Dict]:
        """Check vibration and generate recommendations"""
        recs = []
        
        if vibration > self.VIBRATION_THRESHOLD_CRITICAL:
            recs.append({
                'type': 'VIBRATION',
                'priority': 'CRITICAL',
                'message': 'CRITICAL: Reduce speed immediately! Vibration causing mechanical damage.',
                'current': f'{vibration}G',
                'target': '<0.3G',
                'action': 'REDUCE_SPEED',
                'reason': f'Vibration {vibration}G exceeds damage threshold - accelerating spoilage'
            })
        elif vibration > self.VIBRATION_THRESHOLD_WARNING:
            recs.append({
                'type': 'VIBRATION',
                'priority': 'WARNING',
                'message': f'Warning: High vibration detected ({vibration}G) - reduce speed for safety',
                'current': f'{vibration}G',
                'target': '<0.3G',
                'action': 'REDUCE_SPEED',
                'reason': 'Elevated vibration increases mechanical stress on produce'
            })
            
        return recs
    
    def _check_humidity(self, humidity: float) -> List[Dict]:
        """Check humidity and generate recommendations"""
        recs = []
        
        if humidity > self.HUMIDITY_THRESHOLD_HIGH:
            recs.append({
                'type': 'HUMIDITY',
                'priority': 'INFO',
                'message': f'High humidity ({humidity}%) - monitor for mold growth',
                'current': f'{humidity}%',
                'target': '40-60%',
                'action': 'MONITOR',
                'reason': 'High humidity can promote bacterial growth'
            })
        elif humidity < self.HUMIDITY_THRESHOLD_LOW:
            recs.append({
                'type': 'HUMIDITY',
                'priority': 'INFO',
                'message': f'Low humidity ({humidity}%) - produce may dry out',
                'current': f'{humidity}%',
                'target': '40-60%',
                'action': 'MONITOR',
                'reason': 'Low humidity can cause dehydration of fresh produce'
            })
            
        return recs
    
    def _check_survival_margin(self, survival_margin: float) -> List[Dict]:
        """Check survival margin and generate recommendations"""
        recs = []
        
        if survival_margin < 0:
            recs.append({
                'type': 'ROUTING',
                'priority': 'CRITICAL',
                'message': 'IMMEDIATE ACTION: Product will spoil before reaching destination!',
                'current': f'{survival_margin:.1f} hrs',
                'target': '>0 hrs',
                'action': 'DUMP_OR_REROUTE',
                'reason': f'Negative survival margin of {survival_margin:.1f} hours - spoilage inevitable'
            })
        elif survival_margin < self.SURVIVAL_MARGIN_CRITICAL:
            recs.append({
                'type': 'ROUTING',
                'priority': 'CRITICAL',
                'message': 'IMMEDIATE REROUTING REQUIRED: Less than 2 hours margin!',
                'current': f'{survival_margin:.1f} hrs',
                'target': f'>{self.SURVIVAL_MARGIN_CRITICAL} hrs',
                'action': 'REROUTE',
                'reason': f'Survival margin of {survival_margin:.1f} hours is critically low'
            })
        elif survival_margin < self.SURVIVAL_MARGIN_WARNING:
            recs.append({
                'type': 'ROUTING',
                'priority': 'WARNING',
                'message': f'Warning: Survival margin low ({survival_margin:.1f} hrs) - consider faster route',
                'current': f'{survival_margin:.1f} hrs',
                'target': f'>{self.SURVIVAL_MARGIN_WARNING} hrs',
                'action': 'CONSIDER_REROUTE',
                'reason': 'Limited buffer for delays - recommend alternative route'
            })
            
        return recs
    
    def _priority_score(self, priority: str) -> int:
        """Get numeric score for priority"""
        scores = {
            'CRITICAL': 3,
            'WARNING': 2,
            'INFO': 1
        }
        return scores.get(priority, 0)
    
    def get_summary(self, recommendations: List[Dict]) -> Dict:
        """
        Get summary of recommendations
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Summary dictionary
        """
        critical = sum(1 for r in recommendations if r['priority'] == 'CRITICAL')
        warning = sum(1 for r in recommendations if r['priority'] == 'WARNING')
        info = sum(1 for r in recommendations if r['priority'] == 'INFO')
        
        return {
            'total': len(recommendations),
            'critical': critical,
            'warning': warning,
            'info': info,
            'has_critical': critical > 0,
            'action_required': critical > 0 or warning > 0
        }
    
    def format_for_display(self, recommendations: List[Dict]) -> str:
        """
        Format recommendations for display
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Formatted string
        """
        if not recommendations:
            return "✓ All systems normal - no action required"
        
        lines = []
        for rec in recommendations:
            icon = '🔴' if rec['priority'] == 'CRITICAL' else ('🟡' if rec['priority'] == 'WARNING' else '🔵')
            lines.append(f"{icon} {rec['message']}")
            
        return '\n'.join(lines)


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_driver_recommender():
    """Demo function to test the driver recommender"""
    recommender = DriverRecommender()
    
    # Test case 1: Normal conditions
    print("\n" + "="*60)
    print("TEST 1: Normal operating conditions")
    print("="*60)
    
    telemetry = {
        'temperature': 3.5,
        'humidity': 50,
        'vibration': 0.2,
        'timestamp': 1234567890
    }
    
    recommendations = recommender.generate_recommendations(telemetry, survival_margin=10)
    
    print(f"Telemetry: {telemetry}")
    print(f"\n{recommender.format_for_display(recommendations)}")
    
    summary = recommender.get_summary(recommendations)
    print(f"\nSummary: {summary['total']} recommendations ({summary['critical']} critical, {summary['warning']} warning)")
    
    # Test case 2: High temperature
    print("\n" + "="*60)
    print("TEST 2: High temperature alert")
    print("="*60)
    
    telemetry = {
        'temperature': 12,
        'humidity': 55,
        'vibration': 0.3,
        'timestamp': 1234567890
    }
    
    recommendations = recommender.generate_recommendations(telemetry, survival_margin=8)
    print(f"{recommender.format_for_display(recommendations)}")
    
    # Test case 3: High vibration
    print("\n" + "="*60)
    print("TEST 3: High vibration alert")
    print("="*60)
    
    telemetry = {
        'temperature': 4,
        'humidity': 45,
        'vibration': 0.8,
        'timestamp': 1234567890
    }
    
    recommendations = recommender.generate_recommendations(telemetry, survival_margin=6)
    print(f"{recommender.format_for_display(recommendations)}")
    
    # Test case 4: Critical survival margin
    print("\n" + "="*60)
    print("TEST 4: Critical survival margin")
    print("="*60)
    
    telemetry = {
        'temperature': 5,
        'humidity': 60,
        'vibration': 0.4,
        'timestamp': 1234567890
    }
    
    recommendations = recommender.generate_recommendations(telemetry, survival_margin=1.5)
    print(f"{recommender.format_for_display(recommendations)}")
    
    # Test case 5: Multiple issues
    print("\n" + "="*60)
    print("TEST 5: Multiple critical issues")
    print("="*60)
    
    telemetry = {
        'temperature': 25,
        'humidity': 85,
        'vibration': 1.2,
        'timestamp': 1234567890
    }
    
    recommendations = recommender.generate_recommendations(telemetry, survival_margin=0.5)
    print(f"{recommender.format_for_display(recommendations)}")
    
    summary = recommender.get_summary(recommendations)
    print(f"\n⚠️  ACTION REQUIRED: {summary['critical']} critical, {summary['warning']} warning")


if __name__ == '__main__':
    demo_driver_recommender()
