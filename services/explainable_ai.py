"""
=============================================================================
LAYER 10: EXPLAINABLE AI ENGINE
=============================================================================

This engine provides transparent, human-readable explanations for all
AI decisions made by the system.

Returns structured explainable JSON for:
- Why rerouted
- Why dumping
- Why recommending
- How much profit saved

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, List, Optional, Any

class ExplainableAI:
    """
    Explainable AI Engine for Transparent Decision Making
    
    Provides clear, structured explanations for all AI decisions
    to help human operators understand and trust the system.
    """
    
    def __init__(self):
        """Initialize the explainable AI engine"""
        self.decision_history = []
        
    def explain_reroute(self, route_decision: Dict, telemetry: Dict, 
                         days_left: float) -> Dict:
        """
        Explain why a reroute decision was made
        
        Args:
            route_decision: Route optimization result
            telemetry: Current telemetry data
            days_left: Remaining shelf life
            
        Returns:
            Structured explanation dictionary
        """
        explanation = {
            'decision_type': 'REROUTE',
            'decision': route_decision.get('destination', 'UNKNOWN'),
            'timestamp': telemetry.get('timestamp', 0),
            
            'why': [],
            'factors': [],
            'confidence': 'HIGH',
            'alternatives_considered': []
        }
        
        # Add survival margin explanation
        sm = route_decision.get('candidates', [])
        if sm:
            best = sm[0] if sm else {}
            explanation['why'].append({
                'reason': f"Selected {best.get('destination')} with survival margin of {best.get('survival_margin_hours')} hours",
                'priority': 1
            })
            explanation['factors'].append({
                'factor': 'Survival Margin',
                'value': f"{best.get('survival_margin_hours')} hours",
                'impact': 'POSITIVE' if best.get('survival_margin_days', 0) > 0 else 'NEGATIVE'
            })
            
            # Document alternatives
            for alt in sm[1:]:
                explanation['alternatives_considered'].append({
                    'destination': alt.get('destination'),
                    'survival_margin': alt.get('survival_margin_hours'),
                    'rejected_reason': 'Lower survival margin' if alt.get('survival_margin_hours', 0) < best.get('survival_margin_hours', 0) else 'Higher risk'
                })
        
        # Add telemetry factors
        if telemetry.get('temperature', 0) > 8:
            explanation['why'].append({
                'reason': f"Temperature {telemetry['temperature']}°C is dangerously high - accelerating spoilage",
                'priority': 1
            })
            explanation['factors'].append({
                'factor': 'Temperature',
                'value': f"{telemetry['temperature']}°C",
                'impact': 'NEGATIVE'
            })
            
        if telemetry.get('vibration', 0) > 0.5:
            explanation['why'].append({
                'reason': f"Vibration {telemetry['vibration']}G causing mechanical damage",
                'priority': 2
            })
            explanation['factors'].append({
                'factor': 'Vibration',
                'value': f"{telemetry['vibration']}G",
                'impact': 'NEGATIVE'
            })
        
        # Add time pressure
        if days_left < 5:
            explanation['why'].append({
                'reason': f"Critical time pressure: only {days_left} days of shelf life remaining",
                'priority': 1
            })
            explanation['factors'].append({
                'factor': 'Time Pressure',
                'value': f"{days_left} days",
                'impact': 'CRITICAL'
            })
        
        # Sort reasons by priority
        explanation['why'].sort(key=lambda x: x['priority'])
        
        return explanation
    
    def explain_dump_decision(self, route_decision: Dict, telemetry: Dict,
                              days_left: float) -> Dict:
        """
        Explain why a dump decision was made
        
        Args:
            route_decision: Route optimization result
            telemetry: Current telemetry data
            days_left: Remaining shelf life
            
        Returns:
            Structured explanation dictionary
        """
        explanation = {
            'decision_type': 'DUMP',
            'decision': 'DUMP',
            'timestamp': telemetry.get('timestamp', 0),
            'severity': 'CRITICAL',
            
            'why': [],
            'reasons': [],
            'economic_impact': {},
            'alternatives_attempted': []
        }
        
        # Add all candidate failures
        candidates = route_decision.get('candidates', [])
        for candidate in candidates:
            explanation['alternatives_attempted'].append({
                'destination': candidate.get('destination'),
                'survival_margin': candidate.get('survival_margin_hours'),
                'status': 'BLOCKED' if candidate.get('road_condition') == 'Blocked' else ('OVER_CAPACITY' if candidate.get('capacity_percent', 0) > 90 else 'INSUFFICIENT_TIME')
            })
            
            reason = candidate.get('survival_margin_hours', 0)
            if candidate.get('road_condition') == 'Blocked':
                explanation['why'].append({
                    'reason': f"Road to {candidate['destination']} is blocked",
                    'type': 'INFRASTRUCTURE'
                })
            elif candidate.get('capacity_percent', 0) > 90:
                explanation['why'].append({
                    'reason': f"Center {candidate['destination']} at {candidate['capacity_percent']}% capacity (HIGH RISK)",
                    'type': 'CAPACITY'
                })
            elif reason < 0:
                explanation['why'].append({
                    'reason': f"Travel time to {candidate['destination']} exceeds shelf life by {abs(reason)} hours",
                    'type': 'TIME'
                })
        
        # Calculate economic impact
        food_value = 10000  # Default, would be passed in
        lost_value = food_value * (days_left / 14)  # Assuming 14 day max shelf life
        explanation['economic_impact'] = {
            'lost_value': round(lost_value, 2),
            'waste_reason': f'Spoilage inevitable - shelf life insufficient for any route',
            'recommendation': 'Contact dispatch for emergency disposal protocol'
        }
        
        return explanation
    
    def explain_recommendation(self, recommendations: List[Dict],
                               telemetry: Dict) -> Dict:
        """
        Explain driver recommendations
        
        Args:
            recommendations: List of recommendations
            telemetry: Current telemetry data
            
        Returns:
            Structured explanation dictionary
        """
        explanation = {
            'decision_type': 'RECOMMENDATION',
            'total_recommendations': len(recommendations),
            'critical_count': sum(1 for r in recommendations if r.get('priority') == 'CRITICAL'),
            'warning_count': sum(1 for r in recommendations if r.get('priority') == 'WARNING'),
            
            'recommendations': [],
            'summary': '',
            'immediate_actions': []
        }
        
        # Add each recommendation with explanation
        for rec in recommendations:
            explanation['recommendations'].append({
                'type': rec.get('type'),
                'priority': rec.get('priority'),
                'message': rec.get('message'),
                'reason': rec.get('reason'),
                'action': rec.get('action')
            })
            
            if rec.get('priority') == 'CRITICAL':
                explanation['immediate_actions'].append({
                    'action': rec.get('action'),
                    'reason': rec.get('reason')
                })
        
        # Generate summary
        if explanation['critical_count'] > 0:
            explanation['summary'] = f"{explanation['critical_count']} CRITICAL action(s) required immediately"
        elif explanation['warning_count'] > 0:
            explanation['summary'] = f"{explanation['warning_count']} warning(s) - monitor closely"
        else:
            explanation['summary'] = "All conditions normal - no action required"
            
        return explanation
    
    def explain_profit_saved(self, profit_data: Dict, route_decision: Dict,
                            original_days: float, optimized_days: float) -> Dict:
        """
        Explain profit saved from optimization
        
        Args:
            profit_data: Profit calculation data
            route_decision: Route optimization result
            original_days: Days left without optimization
            optimized_days: Days left with optimization
            
        Returns:
            Structured explanation dictionary
        """
        improvement = optimized_days - original_days
        
        explanation = {
            'decision_type': 'PROFIT_SAVINGS',
            'improvement_days': round(improvement, 2),
            'improvement_percent': round((improvement / original_days * 100) if original_days > 0 else 0, 1),
            
            'financial': {
                'profit_saved': profit_data.get('profit_saved', 0),
                'profit_saved_formatted': profit_data.get('profit_saved_formatted', '$0.00'),
                'food_value': profit_data.get('food_value', 0),
                'remaining_percent': profit_data.get('remaining_percent', 0)
            },
            
            'routing_impact': {
                'original_route': 'Standard' if not route_decision.get('destination') else route_decision.get('destination'),
                'optimized_route': route_decision.get('destination', 'Unknown'),
                'survival_margin': route_decision.get('survival_margin', {}),
                'explanation': route_decision.get('explanation', '')
            },
            
            'why': []
        }
        
        # Add explanation for savings
        if improvement > 0:
            explanation['why'].append({
                'reason': f"Rerouting saved {improvement:.1f} days of shelf life",
                'impact': f"+{profit_data.get('profit_saved_formatted', '$0')}"
            })
            
        if profit_data.get('remaining_percent', 0) > 50:
            explanation['why'].append({
                'reason': f"Product retains {profit_data.get('remaining_percent', 0)}% of original value",
                'impact': 'PREMIUM_QUALITY'
            })
            
        return explanation
    
    def explain_trust_score(self, trust_data: Dict, telemetry: Dict) -> Dict:
        """
        Explain trust score calculation
        
        Args:
            trust_data: Trust score data
            telemetry: Current telemetry data
            
        Returns:
            Structured explanation dictionary
        """
        explanation = {
            'decision_type': 'TRUST_SCORE',
            'trust_score': trust_data.get('trust_score', 0),
            'grade': trust_data.get('grade', 'N/A'),
            
            'factors': [],
            'recommendations': []
        }
        
        # Add penalty explanations
        for penalty in trust_data.get('penalties', []):
            explanation['factors'].append({
                'type': penalty.get('type'),
                'penalty': penalty.get('penalty'),
                'reason': self._get_penalty_explanation(penalty.get('type'), telemetry)
            })
            
        # Add recommendations based on score
        if trust_data.get('trust_score', 0) < 50:
            explanation['recommendations'].append({
                'priority': 'CRITICAL',
                'action': 'IMMEDIATE_INSPECTION',
                'reason': 'Trust score below 50% - requires immediate attention'
            })
        elif trust_data.get('trust_score', 0) < 70:
            explanation['recommendations'].append({
                'priority': 'WARNING',
                'action': 'MONITOR_CLOSELY',
                'reason': 'Trust score below 70% - conditions should be monitored'
            })
            
        return explanation
    
    def _get_penalty_explanation(self, penalty_type: str, telemetry: Dict) -> str:
        """Get human-readable explanation for penalty type"""
        explanations = {
            'TEMPERATURE': f"Current temperature {telemetry.get('temperature', 0)}°C deviates from optimal 2-4°C range",
            'TEMP_VARIANCE': "Temperature fluctuations indicate unstable refrigeration",
            'VIBRATION': f"Current vibration {telemetry.get('vibration', 0)}G exceeds recommended levels",
            'HUMIDITY': f"Current humidity {telemetry.get('humidity', 50)}% outside optimal range",
            'CHAOS_EVENTS': "Recent chaos events have impacted transport quality"
        }
        return explanations.get(penalty_type, 'Condition outside optimal parameters')
    
    def generate_full_explanation(self, all_data: Dict) -> Dict:
        """
        Generate comprehensive explanation combining all decision factors
        
        Args:
            all_data: Dictionary with all engine outputs
            
        Returns:
            Comprehensive explainable AI report
        """
        report = {
            'report_type': 'Comprehensive AI Decision Explanation',
            'summary': {},
            'layers': {}
        }
        
        # Add layer-by-layer explanations
        if 'hybrid' in all_data:
            report['layers']['hybrid_engine'] = {
                'description': 'Physics + ML prediction',
                'physics_prediction': all_data['hybrid'].get('physics_prediction'),
                'ml_prediction': all_data['hybrid'].get('ml_prediction'),
                'final_prediction': all_data['hybrid'].get('final_days_left'),
                'weights': all_data['hybrid'].get('weights')
            }
            
        if 'future' in all_data:
            report['layers']['future_prediction'] = {
                'description': 'Short-term forecasting',
                'now': all_data['future'].get('now'),
                'after_1h': all_data['future'].get('after_1h'),
                'after_2h': all_data['future'].get('after_2h'),
                'after_4h': all_data['future'].get('after_4h'),
                'trend': all_data['future'].get('trend', {}).get('severity')
            }
            
        if 'route' in all_data:
            report['layers']['route_optimization'] = {
                'description': 'Destination selection',
                'destination': all_data['route'].get('destination'),
                'reason': all_data['route'].get('reason'),
                'explanation': all_data['route'].get('explanation')
            }
            
        if 'profit' in all_data:
            report['layers']['profit_optimization'] = {
                'description': 'Value preservation',
                'saved': all_data['profit'].get('profit_saved_formatted'),
                'remaining': all_data['profit'].get('remaining_percent')
            }
            
        # Generate executive summary
        report['summary'] = self._generate_executive_summary(all_data)
        
        return report
    
    def _generate_executive_summary(self, all_data: Dict) -> Dict:
        """Generate executive summary of all decisions"""
        summary = {
            'overall_status': 'OPTIMAL',
            'key_decisions': [],
            'actions_required': []
        }
        
        # Determine overall status
        if 'hybrid' in all_data:
            days_left = all_data['hybrid'].get('final_days_left', 0)
            if days_left < 2:
                summary['overall_status'] = 'CRITICAL'
            elif days_left < 5:
                summary['overall_status'] = 'WARNING'
                
        # Add key decisions
        if 'route' in all_data:
            summary['key_decisions'].append(f"Destination: {all_data['route'].get('destination')}")
            
        if 'recommendations' in all_data:
            for rec in all_data['recommendations']:
                if rec.get('priority') == 'CRITICAL':
                    summary['actions_required'].append(rec.get('message'))
                    
        return summary
    
    def add_to_history(self, explanation: Dict):
        """Add explanation to decision history"""
        self.decision_history.append(explanation)
        
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)
    
    def get_decision_history(self) -> List[Dict]:
        """Get decision history"""
        return self.decision_history


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_explainable_ai():
    """Demo function to test the explainable AI"""
    xai = ExplainableAI()
    
    # Test case 1: Reroute explanation
    print("\n" + "="*60)
    print("TEST 1: Reroute Explanation")
    print("="*60)
    
    route_decision = {
        'destination': 'Center_B',
        'reason': 'Highest survival margin: 4.5 hours',
        'explanation': 'Rerouted to Center B because Survival Margin is +4.5 hrs vs -2.1 hrs at Center A',
        'candidates': [
            {'destination': 'Center_B', 'survival_margin_hours': 4.5, 'capacity_percent': 75, 'road_condition': 'Good'},
            {'destination': 'Center_A', 'survival_margin_hours': -2.1, 'capacity_percent': 85, 'road_condition': 'Good'},
            {'destination': 'Original', 'survival_margin_hours': 1.2, 'capacity_percent': 60, 'road_condition': 'Blocked'}
        ]
    }
    
    telemetry = {
        'temperature': 12,
        'humidity': 60,
        'vibration': 0.6,
        'timestamp': 1234567890
    }
    
    explanation = xai.explain_reroute(route_decision, telemetry, days_left=5.5)
    
    print(f"Decision: {explanation['decision']}")
    print(f"\nWhy:")
    for why in explanation['why']:
        print(f"  • {why['reason']}")
    
    print(f"\nFactors:")
    for factor in explanation['factors']:
        print(f"  • {factor['factor']}: {factor['value']} ({factor['impact']})")
    
    print(f"\nAlternatives Considered:")
    for alt in explanation['alternatives_considered']:
        print(f"  • {alt['destination']}: {alt['survival_margin']} hrs - {alt['rejected_reason']}")
    
    # Test case 2: Dump explanation
    print("\n" + "="*60)
    print("TEST 2: Dump Decision Explanation")
    print("="*60)
    
    dump_decision = {
        'destination': 'Dump',
        'reason': 'All survival margins negative',
        'candidates': [
            {'destination': 'Center_A', 'survival_margin_hours': -5.2, 'capacity_percent': 75, 'road_condition': 'Good'},
            {'destination': 'Center_B', 'survival_margin_hours': -8.1, 'capacity_percent': 95, 'road_condition': 'Good'},
            {'destination': 'Original', 'survival_margin_hours': -3.5, 'capacity_percent': 60, 'road_condition': 'Blocked'}
        ]
    }
    
    explanation = xai.explain_dump_decision(dump_decision, telemetry, days_left=2)
    
    print(f"Decision: {explanation['decision']}")
    print(f"Severity: {explanation['severity']}")
    print(f"\nWhy:")
    for why in explanation['why']:
        print(f"  • {why['reason']} ({why['type']})")
    
    print(f"\nEconomic Impact:")
    print(f"  Lost Value: ${explanation['economic_impact']['lost_value']}")
    print(f"  Reason: {explanation['economic_impact']['waste_reason']}")
    
    # Test case 3: Recommendation explanation
    print("\n" + "="*60)
    print("TEST 3: Driver Recommendations Explanation")
    print("="*60)
    
    recommendations = [
        {'type': 'TEMPERATURE', 'priority': 'CRITICAL', 'message': 'Reduce temperature to 3°C immediately', 'reason': 'Temperature too high', 'action': 'REDUCE_TEMPERATURE'},
        {'type': 'VIBRATION', 'priority': 'WARNING', 'message': 'Reduce speed to avoid damage', 'reason': 'High vibration', 'action': 'REDUCE_SPEED'},
        {'type': 'ROUTING', 'priority': 'CRITICAL', 'message': 'Immediate rerouting required', 'reason': 'Survival margin critical', 'action': 'REROUTE'}
    ]
    
    explanation = xai.explain_recommendation(recommendations, telemetry)
    
    print(f"Total Recommendations: {explanation['total_recommendations']}")
    print(f"Critical: {explanation['critical_count']}, Warning: {explanation['warning_count']}")
    print(f"\nSummary: {explanation['summary']}")
    print(f"\nImmediate Actions:")
    for action in explanation['immediate_actions']:
        print(f"  • {action['action']}: {action['reason']}")
    
    # Test case 4: Full explanation
    print("\n" + "="*60)
    print("TEST 4: Full System Explanation")
    print("="*60)
    
    all_data = {
        'hybrid': {
            'physics_prediction': 6.5,
            'ml_prediction': 7.2,
            'final_days_left': 6.9,
            'weights': {'physics': 0.4, 'ml': 0.6}
        },
        'future': {
            'now': 6.9,
            'after_1h': 6.7,
            'after_2h': 6.5,
            'after_4h': 6.1,
            'trend': {'severity': 'NORMAL'}
        },
        'route': {
            'destination': 'Center_B',
            'reason': 'Best survival margin',
            'explanation': 'Rerouted to Center B'
        },
        'profit': {
            'profit_saved': 4500,
            'profit_saved_formatted': '$4,500.00',
            'remaining_percent': 65
        },
        'recommendations': recommendations
    }
    
    full_report = xai.generate_full_explanation(all_data)
    
    print(f"Report Type: {full_report['report_type']}")
    print(f"Overall Status: {full_report['summary']['overall_status']}")
    print(f"\nKey Decisions:")
    for decision in full_report['summary']['key_decisions']:
        print(f"  • {decision}")
    print(f"\nActions Required: {len(full_report['summary']['actions_required'])}")
    for action in full_report['summary']['actions_required']:
        print(f"  ⚠️  {action}")


if __name__ == '__main__':
    demo_explainable_ai()
