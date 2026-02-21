"""
=============================================================================
LAYER 9: LIABILITY ENGINE
=============================================================================

This engine tracks spoilage contribution and assigns liability.

Calculates percentage damage caused by:
- High Temperature exposure
- High Vibration exposure  
- Transit delay

Returns:
{
  temperature_damage_percent,
  vibration_damage_percent,
  delay_damage_percent
}

Generates Spoilage Responsibility Report.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta

class LiabilityEngine:
    """
    Liability Engine for Spoilage Attribution
    
    Tracks and calculates the percentage of spoilage attributable
    to different factors: temperature, vibration, and delays.
    """
    
    # Thresholds for damage attribution
    TEMP_DAMAGE_THRESHOLD = 8       # °C above which damage occurs
    TEMP_CRITICAL = 15              # °C critical damage threshold
    VIBRATION_DAMAGE_THRESHOLD = 0.5  # G above which damage occurs
    VIBRATION_CRITICAL = 0.8        # G critical damage threshold
    
    # Damage weights (sum to 1.0)
    DAMAGE_WEIGHTS = {
        'temperature': 0.5,     # 50% weight for temperature
        'vibration': 0.3,      # 30% weight for vibration
        'delay': 0.2           # 20% weight for delays
    }
    
    def __init__(self):
        """Initialize the liability engine"""
        self.exposure_history = []
        self.max_history = 1000
        
    def calculate_damage_attribution(self, telemetry_history: List[Dict], 
                                     transit_delay_hours: float = 0,
                                     initial_quality: float = 100) -> Dict:
        """
        Calculate damage attribution from all factors
        
        Args:
            telemetry_history: List of telemetry readings over time
            transit_delay_hours: Additional delay in transit
            initial_quality: Initial quality percentage (100 = perfect)
            
        Returns:
            Dictionary with damage percentages and responsibility
        """
        # Calculate temperature damage
        temp_damage = self._calculate_temperature_damage(telemetry_history)
        
        # Calculate vibration damage
        vib_damage = self._calculate_vibration_damage(telemetry_history)
        
        # Calculate delay damage
        delay_damage = self._calculate_delay_damage(transit_delay_hours)
        
        # Normalize to percentages
        total_damage = temp_damage + vib_damage + delay_damage
        
        # Calculate percentages
        if total_damage > 0:
            temp_percent = (temp_damage / total_damage) * 100
            vib_percent = (vib_damage / total_damage) * 100
            delay_percent = (delay_damage / total_damage) * 100
        else:
            temp_percent = 0
            vib_percent = 0
            delay_percent = 0
        
        return {
            'temperature_damage_percent': round(temp_percent, 1),
            'vibration_damage_percent': round(vib_percent, 1),
            'delay_damage_percent': round(delay_percent, 1),
            'total_damage_percent': round(min(100, total_damage), 1),
            'contribution_factors': {
                'temperature': {
                    'raw_damage': round(temp_damage, 2),
                    'percent': round(temp_percent, 1),
                    'exposure_hours': self._count_damaging_readings(telemetry_history, 'temperature')
                },
                'vibration': {
                    'raw_damage': round(vib_damage, 2),
                    'percent': round(vib_percent, 1),
                    'exposure_events': self._count_damaging_readings(telemetry_history, 'vibration')
                },
                'delay': {
                    'raw_damage': round(delay_damage, 2),
                    'percent': round(delay_percent, 1),
                    'delay_hours': transit_delay_hours
                }
            }
        }
    
    def _calculate_temperature_damage(self, history: List[Dict]) -> float:
        """Calculate damage from temperature exposure"""
        if not history:
            return 0.0
            
        total_damage = 0.0
        for reading in history:
            temp = reading.get('temperature', 4)
            
            if temp > self.TEMP_CRITICAL:
                # Critical damage
                total_damage += (temp - self.TEMP_CRITICAL) * 5 + (self.TEMP_CRITICAL - self.TEMP_DAMAGE_THRESHOLD) * 2
            elif temp > self.TEMP_DAMAGE_THRESHOLD:
                # Moderate damage
                total_damage += (temp - self.TEMP_DAMAGE_THRESHOLD) * 2
                
        return total_damage
    
    def _calculate_vibration_damage(self, history: List[Dict]) -> float:
        """Calculate damage from vibration exposure"""
        if not history:
            return 0.0
            
        total_damage = 0.0
        for reading in history:
            vib = reading.get('vibration', 0)
            
            if vib > self.VIBRATION_CRITICAL:
                # Critical damage
                total_damage += (vib - self.VIBRATION_CRITICAL) * 50 + 15
            elif vib > self.VIBRATION_DAMAGE_THRESHOLD:
                # Moderate damage
                total_damage += (vib - self.VIBRATION_DAMAGE_THRESHOLD) * 30
                
        return total_damage
    
    def _calculate_delay_damage(self, delay_hours: float) -> float:
        """Calculate damage from transit delay"""
        if delay_hours <= 0:
            return 0.0
            
        # Damage increases exponentially with delay
        damage = delay_hours * 2  # Base damage
        if delay_hours > 4:
            damage += (delay_hours - 4) * 3  # Extra penalty for long delays
            
        return damage
    
    def _count_damaging_readings(self, history: List[Dict], factor: str) -> int:
        """Count readings that caused damage"""
        count = 0
        for reading in history:
            if factor == 'temperature':
                if reading.get('temperature', 4) > self.TEMP_DAMAGE_THRESHOLD:
                    count += 1
            elif factor == 'vibration':
                if reading.get('vibration', 0) > self.VIBRATION_DAMAGE_THRESHOLD:
                    count += 1
        return count
    
    def generate_responsibility_report(self, damage_data: Dict,
                                       parties: Optional[Dict] = None) -> Dict:
        """
        Generate spoilage responsibility report
        
        Args:
            damage_data: Damage attribution data
            parties: Optional dictionary of parties involved
            
        Returns:
            Responsibility report dictionary
        """
        temp_percent = damage_data['temperature_damage_percent']
        vib_percent = damage_data['vibration_damage_percent']
        delay_percent = damage_data['delay_damage_percent']
        
        # Determine primary cause
        causes = [
            ('Temperature', temp_percent),
            ('Vibration', vib_percent),
            ('Delay', delay_percent)
        ]
        primary_cause = max(causes, key=lambda x: x[1])
        
        # Generate recommendations
        recommendations = []
        
        if temp_percent > 30:
            recommendations.append({
                'cause': 'Temperature',
                'action': 'Investigate refrigeration system',
                'priority': 'HIGH' if temp_percent > 50 else 'MEDIUM'
            })
            
        if vib_percent > 20:
            recommendations.append({
                'cause': 'Vibration',
                'action': 'Review loading procedures and vehicle suspension',
                'priority': 'HIGH' if vib_percent > 40 else 'MEDIUM'
            })
            
        if delay_percent > 15:
            recommendations.append({
                'cause': 'Delay',
                'action': 'Review route planning and scheduling',
                'priority': 'MEDIUM'
            })
        
        report = {
            'report_type': 'Spoilage Responsibility Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_damage_percent': damage_data['total_damage_percent'],
                'primary_cause': primary_cause[0],
                'primary_cause_percent': primary_cause[1]
            },
            'attribution': {
                'temperature': {
                    'percent': temp_percent,
                    'description': f'Temperature excursions above {self.TEMP_DAMAGE_THRESHOLD}°C'
                },
                'vibration': {
                    'percent': vib_percent,
                    'description': f'Vibration above {self.VIBRATION_DAMAGE_THRESHOLD}G'
                },
                'delay': {
                    'percent': delay_percent,
                    'description': 'Transit delays and extended travel time'
                }
            },
            'recommendations': recommendations
        }
        
        # Add party responsibility if provided
        if parties:
            report['party_responsibility'] = self._calculate_party_responsibility(
                parties, damage_data
            )
        
        return report
    
    def _calculate_party_responsibility(self, parties: Dict, damage_data: Dict) -> Dict:
        """Calculate responsibility per party"""
        responsibility = {}
        
        for party_name, party_type in parties.items():
            if party_type == 'CARRIER':
                # Carrier responsible for vibration and delays
                responsibility[party_name] = {
                    'percent': damage_data['vibration_damage_percent'] + damage_data['delay_damage_percent'],
                    'factors': ['Vibration', 'Transit Delays']
                }
            elif party_type == 'SHIPPER':
                # Shipper responsible for pre-transit conditions
                responsibility[party_name] = {
                    'percent': damage_data['temperature_damage_percent'] * 0.5,
                    'factors': ['Pre-transit Temperature']
                }
            elif party_type == 'REFRIGERATION':
                # Refrigeration responsible for temperature
                responsibility[party_name] = {
                    'percent': damage_data['temperature_damage_percent'],
                    'factors': ['Temperature Control']
                }
                
        return responsibility
    
    def add_exposure(self, telemetry: Dict):
        """
        Add telemetry reading to exposure history
        
        Args:
            telemetry: Telemetry data
        """
        self.exposure_history.append(telemetry)
        
        if len(self.exposure_history) > self.max_history:
            self.exposure_history.pop(0)
    
    def get_exposure_summary(self) -> Dict:
        """Get summary of exposure history"""
        if not self.exposure_history:
            return {'status': 'NO_DATA'}
            
        temps = [r.get('temperature', 4) for r in self.exposure_history]
        vibes = [r.get('vibration', 0) for r in self.exposure_history]
        
        temp_damaging = sum(1 for t in temps if t > self.TEMP_DAMAGE_THRESHOLD)
        vib_damaging = sum(1 for v in vibes if v > self.VIBRATION_DAMAGE_THRESHOLD)
        
        return {
            'total_readings': len(self.exposure_history),
            'temperature': {
                'avg': round(np.mean(temps), 2),
                'max': round(max(temps), 2),
                'damaging_readings': temp_damaging,
                'damaging_percent': round((temp_damaging / len(temps)) * 100, 1)
            },
            'vibration': {
                'avg': round(np.mean(vibes), 3),
                'max': round(max(vibes), 3),
                'damaging_readings': vib_damaging,
                'damaging_percent': round((vib_damaging / len(vibes)) * 100, 1)
            }
        }


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_liability_engine():
    """Demo function to test the liability engine"""
    engine = LiabilityEngine()
    
    # Test case 1: Temperature damage dominant
    print("\n" + "="*60)
    print("TEST 1: Temperature damage dominant")
    print("="*60)
    
    # Simulate history with high temperature
    history = [
        {'temperature': 15 + (i % 5), 'vibration': 0.2, 'timestamp': i}
        for i in range(20)
    ]
    
    damage = engine.calculate_damage_attribution(history, transit_delay_hours=1)
    
    print(f"History: 20 readings with high temperatures")
    print(f"Transit Delay: 1 hour")
    print(f"\nDamage Attribution:")
    print(f"  Temperature: {damage['temperature_damage_percent']}%")
    print(f"  Vibration:   {damage['vibration_damage_percent']}%")
    print(f"  Delay:       {damage['delay_damage_percent']}%")
    print(f"  TOTAL:       {damage['total_damage_percent']}%")
    
    report = engine.generate_responsibility_report(damage)
    print(f"\nPrimary Cause: {report['summary']['primary_cause']} ({report['summary']['primary_cause_percent']}%)")
    
    # Test case 2: Vibration damage dominant
    print("\n" + "="*60)
    print("TEST 2: Vibration damage dominant")
    print("="*60)
    
    history = [
        {'temperature': 4, 'vibration': 0.8 + (i % 3) * 0.2, 'timestamp': i}
        for i in range(20)
    ]
    
    damage = engine.calculate_damage_attribution(history, transit_delay_hours=2)
    
    print(f"History: 20 readings with high vibration")
    print(f"Transit Delay: 2 hours")
    print(f"\nDamage Attribution:")
    print(f"  Temperature: {damage['temperature_damage_percent']}%")
    print(f"  Vibration:   {damage['vibration_damage_percent']}%")
    print(f"  Delay:       {damage['delay_damage_percent']}%")
    print(f"  TOTAL:       {damage['total_damage_percent']}%")
    
    # Test case 3: Delay damage dominant
    print("\n" + "="*60)
    print("TEST 3: Delay damage dominant")
    print("="*60)
    
    history = [
        {'temperature': 4, 'vibration': 0.2, 'timestamp': i}
        for i in range(10)
    ]
    
    damage = engine.calculate_damage_attribution(history, transit_delay_hours=12)
    
    print(f"History: 10 readings with good conditions")
    print(f"Transit Delay: 12 hours (major delay)")
    print(f"\nDamage Attribution:")
    print(f"  Temperature: {damage['temperature_damage_percent']}%")
    print(f"  Vibration:   {damage['vibration_damage_percent']}%")
    print(f"  Delay:       {damage['delay_damage_percent']}%")
    print(f"  TOTAL:       {damage['total_damage_percent']}%")
    
    # Test case 4: Full responsibility report
    print("\n" + "="*60)
    print("TEST 4: Full responsibility report")
    print("="*60)
    
    history = [
        {'temperature': 12, 'vibration': 0.6, 'timestamp': i}
        for i in range(20)
    ]
    
    damage = engine.calculate_damage_attribution(history, transit_delay_hours=5)
    
    parties = {
        'CoolTemp Logistics': 'CARRIER',
        'FreshFarm Shippers': 'SHIPPER',
        'Arctic Cool Systems': 'REFRIGERATION'
    }
    
    report = engine.generate_responsibility_report(damage, parties)
    
    print(f"Report Type: {report['report_type']}")
    print(f"Generated: {report['generated_at']}")
    print(f"\nSummary:")
    print(f"  Total Damage: {report['summary']['total_damage_percent']}%")
    print(f"  Primary Cause: {report['summary']['primary_cause']}")
    
    print(f"\nAttribution:")
    for factor, data in report['attribution'].items():
        print(f"  {factor}: {data['percent']}% - {data['description']}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  [{rec['priority']}] {rec['cause']}: {rec['action']}")
    
    print(f"\nParty Responsibility:")
    for party, resp in report.get('party_responsibility', {}).items():
        print(f"  {party}: {resp['percent']:.1f}% ({', '.join(resp['factors'])})")


if __name__ == '__main__':
    demo_liability_engine()
