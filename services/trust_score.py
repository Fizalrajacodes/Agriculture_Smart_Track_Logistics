"""
=============================================================================
LAYER 8: TRANSPORT TRUST SCORE
=============================================================================

This engine calculates a trust score for transport conditions based on:

- Temperature stability (variance)
- Vibration exposure time
- Chaos events

Score = 100 - penalty_points

Returns percentage score.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, List, Optional
import numpy as np

class TrustScoreEngine:
    """
    Transport Trust Score Engine
    
    Calculates a trust score (0-100%) based on transport conditions
    and adherence to optimal parameters.
    """
    
    # Penalty thresholds and values
    TEMP_IDEAL_MIN = 2     # °C
    TEMP_IDEAL_MAX = 4     # °C
    TEMP_VARIANCE_THRESHOLD = 2  # °C variance threshold
    
    VIBRATION_IDEAL_MAX = 0.3  # G
    VIBRATION_PENALTY_THRESHOLD = 0.5  # G
    
    HUMIDITY_IDEAL_MIN = 40   # %
    HUMIDITY_IDEAL_MAX = 60   # %
    
    # Penalty weights
    PENALTY_TEMP_DEVIATION = 10    # Per °C over threshold
    PENALTY_TEMP_VARIANCE = 5      # Per unit of variance
    PENALTY_VIBRATION = 15         # Per G over threshold
    PENALTY_VIBRATION_DURATION = 2 # Per minute over threshold
    PENALTY_CHAOS_EVENT = 20       # Per chaos event
    
    def __init__(self):
        """Initialize the trust score engine"""
        self.history = []
        self.chaos_events = []
        self.max_history = 1000
        
    def calculate_trust_score(self, telemetry: Dict, 
                              history_readings: Optional[List[Dict]] = None,
                              chaos_events: Optional[int] = None) -> Dict:
        """
        Calculate trust score based on current conditions and history
        
        Args:
            telemetry: Current telemetry data
            history_readings: Optional list of historical readings
            chaos_events: Optional number of chaos events
            
        Returns:
            Dictionary with trust score and breakdown
        """
        score = 100.0
        penalties = []
        
        # Temperature penalty
        temp_penalty = self._calculate_temp_penalty(telemetry.get('temperature', 4))
        if temp_penalty > 0:
            penalties.append({'type': 'TEMPERATURE', 'penalty': temp_penalty})
            score -= temp_penalty
        
        # Vibration penalty
        vib_penalty = self._calculate_vibration_penalty(telemetry.get('vibration', 0))
        if vib_penalty > 0:
            penalties.append({'type': 'VIBRATION', 'penalty': vib_penalty})
            score -= vib_penalty
        
        # Humidity penalty
        humid_penalty = self._calculate_humidity_penalty(telemetry.get('humidity', 50))
        if humid_penalty > 0:
            penalties.append({'type': 'HUMIDITY', 'penalty': humid_penalty})
            score -= humid_penalty
        
        # Historical temperature variance penalty
        if history_readings and len(history_readings) > 1:
            temp_variance = self._calculate_temp_variance(history_readings)
            var_penalty = self._calculate_variance_penalty(temp_variance)
            if var_penalty > 0:
                penalties.append({'type': 'TEMP_VARIANCE', 'penalty': var_penalty})
                score -= var_penalty
        
        # Chaos event penalty
        if chaos_events and chaos_events > 0:
            chaos_penalty = chaos_events * self.PENALTY_CHAOS_EVENT
            penalties.append({'type': 'CHAOS_EVENTS', 'penalty': min(chaos_penalty, 40)})
            score -= min(chaos_penalty, 40)  # Cap at 40
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return {
            'trust_score': round(score, 1),
            'trust_score_percent': f"{score:.1f}%",
            'grade': self._get_grade(score),
            'grade_color': self._get_grade_color(score),
            'penalties': penalties,
            'total_penalty': round(100 - score, 1),
            'is_healthy': score >= 70,
            'requires_attention': score < 50
        }
    
    def _calculate_temp_penalty(self, temperature: float) -> float:
        """Calculate penalty for temperature deviation"""
        penalty = 0.0
        
        if temperature > self.TEMP_IDEAL_MAX:
            deviation = temperature - self.TEMP_IDEAL_MAX
            penalty = deviation * self.PENALTY_TEMP_DEVIATION
        elif temperature < self.TEMP_IDEAL_MIN:
            deviation = self.TEMP_IDEAL_MIN - temperature
            penalty = deviation * self.PENALTY_TEMP_DEVIATION * 0.5  # Less penalty for too cold
            
        return min(penalty, 30)  # Cap at 30
    
    def _calculate_vibration_penalty(self, vibration: float) -> float:
        """Calculate penalty for vibration"""
        if vibration <= self.VIBRATION_IDEAL_MAX:
            return 0.0
            
        penalty = (vibration - self.VIBRATION_IDEAL_MAX) * self.PENALTY_VIBRATION * 10
        return min(penalty, 40)  # Cap at 40
    
    def _calculate_humidity_penalty(self, humidity: float) -> float:
        """Calculate penalty for humidity deviation"""
        penalty = 0.0
        
        if humidity > self.HUMIDITY_IDEAL_MAX:
            deviation = humidity - self.HUMIDITY_IDEAL_MAX
            penalty = deviation * 0.2
        elif humidity < self.HUMIDITY_IDEAL_MIN:
            deviation = self.HUMIDITY_IDEAL_MIN - humidity
            penalty = deviation * 0.2
            
        return min(penalty, 15)  # Cap at 15
    
    def _calculate_temp_variance(self, readings: List[Dict]) -> float:
        """Calculate temperature variance from readings"""
        temps = [r.get('temperature', 4) for r in readings]
        if not temps:
            return 0.0
        return np.var(temps)
    
    def _calculate_variance_penalty(self, variance: float) -> float:
        """Calculate penalty for temperature variance"""
        if variance < self.TEMP_VARIANCE_THRESHOLD:
            return 0.0
            
        penalty = (variance - self.TEMP_VARIANCE_THRESHOLD) * self.PENALTY_TEMP_VARIANCE
        return min(penalty, 20)  # Cap at 20
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade for score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_grade_color(self, score: float) -> str:
        """Get color for grade"""
        if score >= 80:
            return '#00cc66'
        elif score >= 60:
            return '#00d9ff'
        elif score >= 40:
            return '#ffaa00'
        else:
            return '#ff4444'
    
    def add_reading(self, telemetry: Dict):
        """
        Add a telemetry reading to history
        
        Args:
            telemetry: Telemetry data dictionary
        """
        self.history.append({
            'temperature': telemetry.get('temperature', 4),
            'humidity': telemetry.get('humidity', 50),
            'vibration': telemetry.get('vibration', 0),
            'timestamp': telemetry.get('timestamp', 0)
        })
        
        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def add_chaos_event(self, event_type: str = 'UNKNOWN'):
        """
        Record a chaos event
        
        Args:
            event_type: Type of chaos event
        """
        self.chaos_events.append({
            'type': event_type,
            'timestamp': self.history[-1].get('timestamp', 0) if self.history else 0
        })
    
    def get_statistics(self) -> Dict:
        """
        Get transport statistics from history
        
        Returns:
            Statistics dictionary
        """
        if not self.history:
            return {'status': 'NO_DATA'}
        
        temps = [r['temperature'] for r in self.history]
        vibes = [r['vibration'] for r in self.history]
        humids = [r['humidity'] for r in self.history]
        
        return {
            'readings_count': len(self.history),
            'temperature': {
                'mean': round(np.mean(temps), 2),
                'std': round(np.std(temps), 2),
                'min': round(min(temps), 2),
                'max': round(max(temps), 2),
                'variance': round(np.var(temps), 2)
            },
            'vibration': {
                'mean': round(np.mean(vibes), 3),
                'max': round(max(vibes), 3),
                'exposure_time': sum(1 for v in vibes if v > 0.5)  # Count high vibration
            },
            'humidity': {
                'mean': round(np.mean(humids), 2),
                'min': round(min(humids), 2),
                'max': round(max(humids), 2)
            },
            'chaos_events': len(self.chaos_events)
        }
    
    def get_trend(self) -> str:
        """
        Get trust score trend
        
        Returns:
            Trend string
        """
        if len(self.history) < 10:
            return 'INSUFFICIENT_DATA'
        
        # Compare recent readings to earlier ones
        recent = self.history[-10:]
        earlier = self.history[-20:-10] if len(self.history) >= 20 else self.history[:10]
        
        if not earlier:
            return 'STABLE'
            
        recent_avg_temp = np.mean([r['temperature'] for r in recent])
        earlier_avg_temp = np.mean([r['temperature'] for r in earlier])
        
        if recent_avg_temp < earlier_avg_temp - 1:
            return 'IMPROVING'
        elif recent_avg_temp > earlier_avg_temp + 1:
            return 'DEGRADING'
        else:
            return 'STABLE'


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_trust_score():
    """Demo function to test the trust score engine"""
    engine = TrustScoreEngine()
    
    # Test case 1: Perfect conditions
    print("\n" + "="*60)
    print("TEST 1: Perfect transport conditions")
    print("="*60)
    
    telemetry = {
        'temperature': 3.5,
        'humidity': 50,
        'vibration': 0.1,
        'timestamp': 1234567890
    }
    
    result = engine.calculate_trust_score(telemetry)
    print(f"Telemetry: {telemetry}")
    print(f"\n✓ Trust Score: {result['trust_score']}% (Grade: {result['grade']})")
    print(f"  Status: {'Healthy' if result['is_healthy'] else 'Requires Attention'}")
    if result['penalties']:
        print(f"  Penalties: {result['penalties']}")
    else:
        print(f"  Penalties: None - optimal conditions")
    
    # Test case 2: High temperature
    print("\n" + "="*60)
    print("TEST 2: High temperature conditions")
    print("="*60)
    
    telemetry = {
        'temperature': 15,
        'humidity': 55,
        'vibration': 0.2,
        'timestamp': 1234567890
    }
    
    result = engine.calculate_trust_score(telemetry)
    print(f"Telemetry: {telemetry}")
    print(f"\n✓ Trust Score: {result['trust_score']}% (Grade: {result['grade']})")
    print(f"  Penalties Applied:")
    for p in result['penalties']:
        print(f"    - {p['type']}: -{p['penalty']}")
    
    # Test case 3: With history
    print("\n" + "="*60)
    print("TEST 3: With temperature variance")
    print("="*60)
    
    # Simulate varying temperatures
    history = [
        {'temperature': 3 + (i % 5), 'humidity': 50, 'vibration': 0.1, 'timestamp': i}
        for i in range(20)
    ]
    
    telemetry = {'temperature': 7, 'humidity': 55, 'vibration': 0.2, 'timestamp': 20}
    result = engine.calculate_trust_score(telemetry, history)
    
    print(f"Current: {telemetry}")
    print(f"History: 20 readings with varying temps")
    print(f"\n✓ Trust Score: {result['trust_score']}% (Grade: {result['grade']})")
    print(f"  Penalties Applied:")
    for p in result['penalties']:
        print(f"    - {p['type']}: -{p['penalty']}")
    
    # Test case 4: Chaos events
    print("\n" + "="*60)
    print("TEST 4: With chaos events")
    print("="*60)
    
    telemetry = {'temperature': 5, 'humidity': 60, 'vibration': 0.3, 'timestamp': 100}
    result = engine.calculate_trust_score(telemetry, chaos_events=2)
    
    print(f"Telemetry: {telemetry}")
    print(f"Chaos Events: 2")
    print(f"\n✓ Trust Score: {result['trust_score']}% (Grade: {result['grade']})")
    print(f"  Penalties Applied:")
    for p in result['penalties']:
        print(f"    - {p['type']}: -{p['penalty']}")
    
    # Test case 5: Statistics
    print("\n" + "="*60)
    print("TEST 5: Historical statistics")
    print("="*60)
    
    # Add some readings
    for i in range(30):
        engine.add_reading({
            'temperature': 3 + (i % 4),
            'humidity': 45 + (i % 20),
            'vibration': 0.1 + (i % 3) * 0.1,
            'timestamp': i
        })
    
    stats = engine.get_statistics()
    print(f"Total Readings: {stats['readings_count']}")
    print(f"\nTemperature:")
    print(f"  Mean: {stats['temperature']['mean']}°C")
    print(f"  Variance: {stats['temperature']['variance']}")
    print(f"  Range: {stats['temperature']['min']} - {stats['temperature']['max']}°C")
    print(f"\nVibration:")
    print(f"  Mean: {stats['vibration']['mean']}G")
    print(f"  Max: {stats['vibration']['max']}G")
    print(f"\nTrust Score Trend: {engine.get_trend()}")


if __name__ == '__main__':
    demo_trust_score()
