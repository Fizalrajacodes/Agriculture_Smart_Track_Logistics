"""
=============================================================================
LAYER 4: SURVIVAL MARGIN OPTIMIZER
=============================================================================

This engine calculates survival margins for multiple destinations and
determines the optimal routing strategy.

For each destination:
- Original
- Center A
- Center B

Calculate:
SurvivalMargin = Days_Left - Travel_Time

Rules:
- If road_condition == "Blocked": Travel_Time = Infinity
- If capacity > 90%: mark center as HIGH RISK
- If all SurvivalMargins < 0: Destination = "DUMP"
- Else: Choose center with highest SurvivalMargin

Returns explanation string showing reasoning.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, List, Tuple, Optional
import math

class SurvivalMarginOptimizer:
    """
    Survival Margin Optimizer for Route Selection
    
    Calculates survival margins for all possible destinations
    and recommends the optimal route based on available time.
    """
    
    # Configuration
    CAPACITY_HIGH_RISK_THRESHOLD = 90  # Percentage
    MARGIN_CRITICAL_THRESHOLD = 2      # Hours
    
    def __init__(self):
        """Initialize the optimizer"""
        pass
    
    def calculate_travel_time(self, distance_km, road_condition):
        """
        Calculate travel time based on distance and road condition
        
        Args:
            distance_km: Distance in kilometers
            road_condition: Road condition string ('Good', 'Moderate', 'Poor', 'Blocked')
            
        Returns:
            Travel time in hours (or infinity if blocked)
        """
        if road_condition == 'Blocked':
            return float('inf')
        
        # Base speed varies by road condition
        base_speeds = {
            'Good': 60,      # km/h
            'Moderate': 45,
            'Poor': 30,
            'Blocked': 0     # Handled above
        }
        
        base_speed = base_speeds.get(road_condition, 60)
        travel_time = distance_km / base_speed
        
        return travel_time
    
    def calculate_survival_margin(self, days_left, travel_time_hours):
        """
        Calculate Survival Margin
        
        Formula: SM = Days_Left - Travel_Time (in days)
        
        Note: Convert hours to days (24 hours = 1 day)
        
        Args:
            days_left: Remaining shelf life in days
            travel_time_hours: Travel time in hours
            
        Returns:
            Survival margin in days
        """
        if travel_time_hours == float('inf'):
            return float('-inf')
        
        travel_time_days = travel_time_hours / 24
        return days_left - travel_time_days
    
    def assess_destination(self, name, distance, capacity, road_condition, days_left):
        """
        Assess a single destination
        
        Args:
            name: Destination name
            distance: Distance in km
            capacity: Capacity percentage (0-100)
            road_condition: Road condition
            days_left: Remaining shelf life in days
            
        Returns:
            Dictionary with destination assessment
        """
        travel_time = self.calculate_travel_time(distance, road_condition)
        survival_margin = self.calculate_survival_margin(days_left, travel_time)
        
        # Determine risk level
        if capacity > self.CAPACITY_HIGH_RISK_THRESHOLD:
            risk_level = 'HIGH'
        elif capacity > 70:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'destination': name,
            'distance_km': distance,
            'capacity_percent': capacity,
            'road_condition': road_condition,
            'travel_time_hours': round(travel_time, 2) if travel_time != float('inf') else 'INF',
            'survival_margin_days': round(survival_margin, 2) if survival_margin != float('-inf') else '-INF',
            'survival_margin_hours': round(survival_margin * 24, 2) if survival_margin != float('-inf') else '-INF',
            'risk_level': risk_level,
            'is_viable': travel_time != float('inf') and capacity <= 100
        }
    
    def optimize(self, destinations: Dict, days_left: float) -> Dict:
        """
        Optimize route selection across multiple destinations
        
        Args:
            destinations: Dictionary of {name: {distance, capacity, road_condition}}
            days_left: Remaining shelf life in days
            
        Returns:
            Dictionary with optimal route and reasoning
        """
        assessments = []
        
        # Assess each destination
        for name, data in destinations.items():
            assessment = self.assess_destination(
                name=name,
                distance=data.get('distance', 0),
                capacity=data.get('capacity', 0),
                road_condition=data.get('road_condition', 'Good'),
                days_left=days_left
            )
            assessments.append(assessment)
        
        # Filter viable destinations
        viable = [a for a in assessments if a['is_viable']]
        
        # Sort by survival margin (highest first)
        viable_sorted = sorted(
            viable, 
            key=lambda x: x['survival_margin_days'] if x['survival_margin_days'] != '-INF' else float('-inf'),
            reverse=True
        )
        
        # Determine result
        if not viable_sorted:
            # All destinations are blocked or over capacity
            result = {
                'destination': 'DUMP',
                'reason': 'All destinations are blocked or at full capacity',
                'explanation': 'No viable routes available - all destinations either have blocked roads or exceed capacity limits.',
                'candidates': assessments,
                'action_required': 'CONTACT_DISPATCH'
            }
        elif viable_sorted[0]['survival_margin_days'] < 0:
            # Best option has negative survival margin
            result = {
                'destination': 'DUMP',
                'reason': f'Best survival margin is negative: {viable_sorted[0]["survival_margin_hours"]} hours',
                'explanation': f'Even the best route ({viable_sorted[0]["destination"]}) would result in spoilage en route. Survival margin: {viable_sorted[0]["survival_margin_hours"]} hours.',
                'candidates': assessments,
                'action_required': 'DUMP_PRODUCT'
            }
        else:
            # Valid route found
            best = viable_sorted[0]
            
            # Generate explanation
            other_margins = []
            for a in viable_sorted[1:]:
                margin_diff = best['survival_margin_hours'] - a['survival_margin_hours']
                other_margins.append(f'{a["destination"]} ({a["survival_margin_hours"]:+g} hrs)')
            
            explanation = f"Rerouted to {best['destination']} because Survival Margin is {best['survival_margin_hours']:+g} hrs"
            if other_margins:
                explanation += f" vs {', '.join(other_margins)} at other centers"
            
            result = {
                'destination': best['destination'],
                'reason': f'Highest survival margin: {best["survival_margin_hours"]} hours',
                'explanation': explanation,
                'travel_time_hours': best['travel_time_hours'],
                'distance_km': best['distance_km'],
                'candidates': assessments,
                'action_required': 'PROCEED_AS_PLANNED' if best['survival_margin_hours'] >= self.MARGIN_CRITICAL_THRESHOLD else 'URGENT_DELIVERY'
            }
        
        # Add risk assessment
        result['overall_risk'] = self._assess_overall_risk(assessments)
        
        return result
    
    def _assess_overall_risk(self, assessments: List[Dict]) -> Dict:
        """
        Assess overall transport risk
        
        Args:
            assessments: List of destination assessments
            
        Returns:
            Risk assessment dictionary
        """
        high_risk_count = sum(1 for a in assessments if a['risk_level'] == 'HIGH')
        blocked_count = sum(1 for a in assessments if a['road_condition'] == 'Blocked')
        
        if blocked_count >= len(assessments):
            return {
                'level': 'CRITICAL',
                'message': 'All routes blocked - emergency protocol required'
            }
        elif high_risk_count > 0:
            return {
                'level': 'HIGH',
                'message': f'{high_risk_count} destination(s) at high capacity'
            }
        else:
            return {
                'level': 'NORMAL',
                'message': 'Routes available with acceptable margins'
            }
    
    def get_alternative_routes(self, current_recommendation: Dict, days_left: float) -> List[Dict]:
        """
        Get alternative routing options if current route fails
        
        Args:
            current_recommendation: Current route recommendation
            days_left: Remaining shelf life
            
        Returns:
            List of alternative routes sorted by viability
        """
        if 'candidates' not in current_recommendation:
            return []
        
        alternatives = [
            c for c in current_recommendation['candidates'] 
            if c['is_viable'] and c['destination'] != current_recommendation.get('destination')
        ]
        
        return sorted(
            alternatives,
            key=lambda x: x['survival_margin_days'] if x['survival_margin_days'] != '-INF' else float('-inf'),
            reverse=True
        )


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_survival_optimizer():
    """Demo function to test the survival margin optimizer"""
    optimizer = SurvivalMarginOptimizer()
    
    # Test case 1: Normal scenario
    print("\n" + "="*60)
    print("TEST 1: Normal delivery scenario")
    print("="*60)
    
    days_left = 8.0  # 8 days shelf life
    destinations = {
        'Original': {'distance': 30, 'capacity': 60, 'road_condition': 'Good'},
        'Center_A': {'distance': 45, 'capacity': 75, 'road_condition': 'Good'},
        'Center_B': {'distance': 60, 'capacity': 85, 'road_condition': 'Good'},
    }
    
    result = optimizer.optimize(destinations, days_left)
    print(f"Days Left: {days_left}")
    print(f"\nDestination Assessments:")
    for c in result['candidates']:
        print(f"  {c['destination']:12} | Distance: {c['distance_km']:3}km | "
              f"Capacity: {c['capacity_percent']:3}% | SM: {c['survival_margin_hours']:>6} hrs | "
              f"Risk: {c['risk_level']}")
    
    print(f"\n✓ RECOMMENDED: {result['destination']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Explanation: {result['explanation']}")
    print(f"  Action: {result['action_required']}")
    
    # Test case 2: High capacity scenario
    print("\n" + "="*60)
    print("TEST 2: High capacity at some centers")
    print("="*60)
    
    days_left = 5.0
    destinations = {
        'Original': {'distance': 25, 'capacity': 50, 'road_condition': 'Good'},
        'Center_A': {'distance': 40, 'capacity': 95, 'road_condition': 'Good'},
        'Center_B': {'distance': 50, 'capacity': 70, 'road_condition': 'Good'},
    }
    
    result = optimizer.optimize(destinations, days_left)
    print(f"Days Left: {days_left}")
    print(f"\n✓ RECOMMENDED: {result['destination']}")
    print(f"  Explanation: {result['explanation']}")
    print(f"  Risk Assessment: {result['overall_risk']['level']} - {result['overall_risk']['message']}")
    
    # Test case 3: Blocked roads
    print("\n" + "="*60)
    print("TEST 3: Blocked roads scenario")
    print("="*60)
    
    days_left = 6.0
    destinations = {
        'Original': {'distance': 30, 'capacity': 60, 'road_condition': 'Blocked'},
        'Center_A': {'distance': 45, 'capacity': 75, 'road_condition': 'Blocked'},
        'Center_B': {'distance': 60, 'capacity': 85, 'road_condition': 'Good'},
    }
    
    result = optimizer.optimize(destinations, days_left)
    print(f"Days Left: {days_left}")
    print(f"\n✓ RECOMMENDED: {result['destination']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Explanation: {result['explanation']}")
    print(f"  Action: {result['action_required']}")
    
    # Test case 4: All margins negative
    print("\n" + "="*60)
    print("TEST 4: Negative margins - time too short")
    print("="*60)
    
    days_left = 2.0
    destinations = {
        'Original': {'distance': 80, 'capacity': 60, 'road_condition': 'Good'},
        'Center_A': {'distance': 60, 'capacity': 75, 'road_condition': 'Good'},
        'Center_B': {'distance': 50, 'capacity': 85, 'road_condition': 'Good'},
    }
    
    result = optimizer.optimize(destinations, days_left)
    print(f"Days Left: {days_left}")
    print(f"\n✓ RECOMMENDED: {result['destination']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Explanation: {result['explanation']}")
    print(f"  Action: {result['action_required']}")


if __name__ == '__main__':
    demo_survival_optimizer()
