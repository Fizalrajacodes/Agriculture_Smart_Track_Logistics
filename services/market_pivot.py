"""
================================================================================
MARKET PIVOT ENGINE - Emergency Rescue Logic
================================================================================

This engine handles emergency triage when cargo is at risk of spoilage.
It finds the best secondary market to rescue the cargo before it spoils.

Features:
- Secondary Market Database (Juice Processor, Wholesale, Bio-Fuel)
- Emergency triage when shelf life < time to destination
- Rescue value recovery calculation
- Loss prevented calculation

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
================================================================================
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class MarketPivotEngine:
    """
    Market Pivot Engine for Emergency Cargo Rescue
    
    When remaining shelf life is insufficient to reach the original destination,
    this engine finds the best alternative market to maximize value recovery.
    """
    
    def __init__(self):
        """Initialize the Market Pivot Engine with secondary market database"""
        
        # Secondary Market Database
        self.secondary_markets = {
            'Plant_Alpha': {
                'name': 'Plant Alpha',
                'type': 'Juice Processor',
                'recovery_multiplier': 0.65,
                'description': 'Juice extraction plant - premium recovery',
                'travel_time_hrs': 0,
                'capacity_percent': 80
            },
            'Market_Beta': {
                'name': 'Market Beta',
                'type': 'Wholesale',
                'recovery_multiplier': 0.40,
                'description': 'Wholesale market - moderate recovery',
                'travel_time_hrs': 0,
                'capacity_percent': 60
            },
            'BioFuel_Gamma': {
                'name': 'Bio-Fuel Gamma',
                'type': 'Ethanol',
                'recovery_multiplier': 0.15,
                'description': 'Bio-fuel plant - minimum recovery',
                'travel_time_hrs': 0,
                'capacity_percent': 95
            }
        }
        
        # Default distances (in hours) - can be overridden
        self.default_travel_times = {
            'Plant_Alpha': 2.5,      # 2.5 hours away
            'Market_Beta': 1.5,       # 1.5 hours away
            'BioFuel_Gamma': 1.0,    # 1 hour away (closest)
            'Premium_Supermarket': 4.0  # Original destination: 4 hours
        }
        
        self.rescue_history = []
    
    def calculate_emergency_triage(self, 
                                   current_cargo_value: float,
                                   remaining_shelf_life_hrs: float,
                                   original_destination_eta_hrs: float,
                                   travel_times: Optional[Dict[str, float]] = None) -> Dict:
        """
        Calculate emergency triage - determine if pivot is needed
        
        Args:
            current_cargo_value: Value of cargo in Rupees
            remaining_shelf_life_hrs: Hours of shelf life remaining
            original_destination_eta_hrs: Hours to reach original destination
            travel_times: Optional dict of destination -> hours mapping
            
        Returns:
            Dictionary with triage decision and rescue plan
        """
        
        # Use provided travel times or defaults
        times = travel_times or self.default_travel_times
        
        # Determine if pivot is needed
        if remaining_shelf_life_hrs >= original_destination_eta_hrs:
            # No pivot needed - on track
            return {
                'status': 'ON_TRACK',
                'message': 'Cargo will reach original destination in time',
                'original_destination': 'Premium Supermarket',
                'eta_hrs': original_destination_eta_hrs,
                'remaining_shelf_life_hrs': remaining_shelf_life_hrs,
                'safety_margin_hrs': remaining_shelf_life_hrs - original_destination_eta_hrs,
                'current_cargo_value': current_cargo_value,
                'rescue_needed': False,
                'rescue_destination': None,
                'recovery_percent': 100,
                'loss_prevented': 0
            }
        
        # Pivot needed - find best rescue point
        return self.find_rescue_point(
            current_cargo_value=current_cargo_value,
            remaining_shelf_life_hrs=remaining_shelf_life_hrs,
            travel_times=times
        )
    
    def find_rescue_point(self,
                         current_cargo_value: float,
                         remaining_shelf_life_hrs: float,
                         travel_times: Dict[str, float]) -> Dict:
        """
        Find the best rescue point reachable within remaining shelf life
        
        Args:
            current_cargo_value: Value of cargo in Rupees
            remaining_shelf_life_hrs: Hours of shelf life remaining
            travel_times: Dictionary of destination -> travel time
            
        Returns:
            Dictionary with rescue destination and financial recovery stats
        """
        
        # Update travel times in market database
        for market_id, market_data in self.secondary_markets.items():
            if market_id in travel_times:
                market_data['travel_time_hrs'] = travel_times[market_id]
        
        # Find all reachable markets (travel_time < remaining_shelf_life)
        reachable_markets = []
        
        for market_id, market_data in self.secondary_markets.items():
            travel_time = travel_times.get(market_id, market_data['travel_time_hrs'])
            
            if travel_time < remaining_shelf_life_hrs:
                # Calculate recoverable value
                recoverable_value = current_cargo_value * market_data['recovery_multiplier']
                loss_prevented = recoverable_value
                
                reachable_markets.append({
                    'market_id': market_id,
                    'name': market_data['name'],
                    'type': market_data['type'],
                    'travel_time_hrs': travel_time,
                    'recovery_multiplier': market_data['recovery_multiplier'],
                    'recoverable_value': recoverable_value,
                    'loss_prevented': loss_prevented,
                    'recovery_percent': market_data['recovery_multiplier'] * 100,
                    'time_buffer_hrs': remaining_shelf_life_hrs - travel_time
                })
        
        if not reachable_markets:
            # No reachable markets - must dump to bio-fuel (minimum recovery)
            bio_fuel = self.secondary_markets['BioFuel_Gamma']
            travel_time = travel_times.get('BioFuel_Gamma', bio_fuel['travel_time_hrs'])
            
            recoverable_value = current_cargo_value * bio_fuel['recovery_multiplier']
            
            return {
                'status': 'EMERGENCY_DUMP',
                'message': 'Shelf life too short - emergency salvage to Bio-Fuel',
                'original_destination': 'Premium Supermarket',
                'original_eta_hrs': travel_times.get('Premium_Supermarket', 4.0),
                'remaining_shelf_life_hrs': remaining_shelf_life_hrs,
                'current_cargo_value': current_cargo_value,
                'rescue_needed': True,
                'severity': 'CRITICAL',
                'rescue_destination': {
                    'name': bio_fuel['name'],
                    'type': bio_fuel['type'],
                    'travel_time_hrs': travel_time,
                    'recovery_multiplier': bio_fuel['recovery_multiplier']
                },
                'recovery_percent': bio_fuel['recovery_multiplier'] * 100,
                'recoverable_value': recoverable_value,
                'loss_prevented': recoverable_value,
                'total_loss': current_cargo_value - recoverable_value,
                'reason': f'Even closest market (Beta) unreachable - {travel_times.get("Market_Beta", 1.5)}hrs > {remaining_shelf_life_hrs}hrs'
            }
        
        # Sort by recovery multiplier (highest first)
        reachable_markets.sort(key=lambda x: x['recovery_multiplier'], reverse=True)
        
        # Select best rescue point
        best_rescue = reachable_markets[0]
        
        # Determine severity
        if remaining_shelf_life_hrs < 2:
            severity = 'CRITICAL'
        elif remaining_shelf_life_hrs < best_rescue['travel_time_hrs'] * 1.5:
            severity = 'HIGH'
        else:
            severity = 'MEDIUM'
        
        result = {
            'status': 'RESCUE_REQUIRED',
            'message': f'Emergency pivot to {best_rescue["name"]}',
            'original_destination': 'Premium Supermarket',
            'original_eta_hrs': travel_times.get('Premium_Supermarket', 4.0),
            'remaining_shelf_life_hrs': remaining_shelf_life_hrs,
            'current_cargo_value': current_cargo_value,
            'rescue_needed': True,
            'severity': severity,
            'rescue_destination': {
                'name': best_rescue['name'],
                'type': best_rescue['type'],
                'travel_time_hrs': best_rescue['travel_time_hrs'],
                'recovery_multiplier': best_rescue['recovery_multiplier']
            },
            'recovery_percent': best_rescue['recovery_percent'],
            'recoverable_value': best_rescue['recoverable_value'],
            'loss_prevented': best_rescue['loss_prevented'],
            'total_loss': current_cargo_value - best_rescue['recoverable_value'],
            'time_buffer_hrs': best_rescue['time_buffer_hrs'],
            'alternatives': reachable_markets[1:] if len(reachable_markets) > 1 else []
        }
        
        # Add to history
        self.add_to_history(result)
        
        return result
    
    def get_market_options(self) -> List[Dict]:
        """Get list of all available secondary markets"""
        return [
            {
                'market_id': market_id,
                'name': data['name'],
                'type': data['type'],
                'recovery_multiplier': data['recovery_multiplier'],
                'description': data['description']
            }
            for market_id, data in self.secondary_markets.items()
        ]
    
    def update_travel_times(self, travel_times: Dict[str, float]):
        """Update travel times for markets"""
        for market_id, time in travel_times.items():
            if market_id in self.secondary_markets:
                self.secondary_markets[market_id]['travel_time_hrs'] = time
    
    def add_to_history(self, rescue_result: Dict):
        """Add rescue result to history"""
        rescue_result['timestamp'] = datetime.now().isoformat()
        self.rescue_history.append(rescue_result)
        
        # Keep only last 50 entries
        if len(self.rescue_history) > 50:
            self.rescue_history.pop(0)
    
    def get_history(self) -> List[Dict]:
        """Get rescue history"""
        return self.rescue_history


# =============================================================================
# DEMO FUNCTION
# =============================================================================

def demo_market_pivot_engine():
    """Demo function to test the Market Pivot Engine"""
    
    engine = MarketPivotEngine()
    
    # Scenario: Cooling system failure, cargo worth ₹7,00,000
    cargo_value = 700000  # ₹7 Lakhs
    remaining_shelf_life = 3.0  # Only 3 hours left
    original_eta = 4.0  # Original destination is 4 hours away
    
    # Travel times to different markets
    travel_times = {
        'Plant_Alpha': 2.5,      # 2.5 hours
        'Market_Beta': 1.5,       # 1.5 hours
        'BioFuel_Gamma': 1.0,    # 1 hour
        'Premium_Supermarket': 4.0
    }
    
    print("\n" + "="*60)
    print("MARKET PIVOT ENGINE - EMERGENCY TRIAGE DEMO")
    print("="*60)
    print(f"\n📦 Cargo Value: ₹{cargo_value:,}")
    print(f"⏰ Remaining Shelf Life: {remaining_shelf_life} hours")
    print(f"📍 Original Destination: Premium Supermarket (ETA: {original_eta} hrs)")
    print()
    
    # Calculate triage
    result = engine.calculate_emergency_triage(
        current_cargo_value=cargo_value,
        remaining_shelf_life_hrs=remaining_shelf_life,
        original_destination_eta_hrs=original_eta,
        travel_times=travel_times
    )
    
    print("-"*60)
    print(f"🚨 STATUS: {result['status']}")
    print(f"📋 Message: {result['message']}")
    print()
    
    if result['rescue_needed']:
        print(f"⚠️  SEVERITY: {result['severity']}")
        print(f"🔄 New Destination: {result['rescue_destination']['name']}")
        print(f"   Type: {result['rescue_destination']['type']}")
        print(f"   Travel Time: {result['rescue_destination']['travel_time_hrs']} hrs")
        print(f"   Time Buffer: {result['time_buffer_hrs']} hrs remaining")
        print()
        print(f"💰 FINANCIAL IMPACT:")
        print(f"   Original Cargo Value: ₹{result['current_cargo_value']:,}")
        print(f"   Recovery Rate: {result['recovery_percent']:.1f}%")
        print(f"   Recoverable Value: ₹{result['recoverable_value']:,.0f}")
        print(f"   Loss Prevented: ₹{result['loss_prevented']:,.0f}")
        print(f"   Total Loss: ₹{result['total_loss']:,.0f}")
        
        if result.get('alternatives'):
            print()
            print("📊 ALTERNATIVE OPTIONS:")
            for alt in result['alternatives']:
                print(f"   • {alt['name']}: {alt['recovery_percent']:.0f}% recovery (₹{alt['recoverable_value']:,.0f})")
    else:
        print(f"✅ Safety Margin: {result['safety_margin_hrs']} hours")
    
    print()
    print("-"*60)
    print("Available Markets:")
    for market in engine.get_market_options():
        print(f"   • {market['name']} ({market['type']}): {market['recovery_multiplier']*100:.0f}% recovery")


if __name__ == '__main__':
    demo_market_pivot_engine()
