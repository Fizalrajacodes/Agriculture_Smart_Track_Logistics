"""
=============================================================================
Aegis Harvest - Spoilage Shield 2.0
=============================================================================

Flask Backend API with Advanced Intelligent Logistics Features:

LAYER 2:  Physics + ML Hybrid Engine
LAYER 3:  Future Prediction Engine  
LAYER 4:  Survival Margin Optimizer
LAYER 5:  Profit Optimization Engine
LAYER 6:  Driver Recommendation Engine
LAYER 7:  Countdown Timer Service
LAYER 8:  Transport Trust Score
LAYER 9:  Liability Engine
LAYER 10: Explainable AI Engine

This upgrade adds modular AI services without breaking existing functionality.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd
import random
import time

# Import new intelligent services
from services.hybrid_engine import HybridEngine
from services.future_prediction import FuturePredictionEngine
from services.survival_optimizer import SurvivalMarginOptimizer
from services.profit_optimizer import ProfitOptimizer
from services.driver_recommender import DriverRecommender
from services.countdown_timer import CountdownTimer
from services.trust_score import TrustScoreEngine
from services.liability_engine import LiabilityEngine
from services.explainable_ai import ExplainableAI
from services.market_pivot import MarketPivotEngine

app = Flask(__name__, template_folder='templates')

# =============================================================================
# INITIALIZE ALL INTELLIGENT ENGINES
# =============================================================================

# Global state for chaos mode
is_chaos_mode = False

# Load ML model and scaler
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print(">>> ML Model loaded successfully!")
except:
    print("WARNING: ML Model not found. Using physics-only mode.")
    model = None
    scaler = None

# Initialize all intelligent engines
hybrid_engine = HybridEngine(model_path='model.pkl', scaler_path='scaler.pkl')
future_engine = FuturePredictionEngine()
survival_optimizer = SurvivalMarginOptimizer()
profit_optimizer = ProfitOptimizer(currency='USD', max_shelf_life=14)
driver_recommender = DriverRecommender()
countdown_timer = CountdownTimer()
trust_engine = TrustScoreEngine()
liability_engine = LiabilityEngine()
explainable_ai = ExplainableAI()
market_pivot_engine = MarketPivotEngine()

# =============================================================================
# CONFIGURATION
# =============================================================================

NORMAL_TELEMETRY = {
    'temperature': (2, 8),
    'humidity': (40, 60),
    'vibration': (0.1, 0.3),
}

CRISIS_TELEMETRY = {
    'temperature': (30, 45),
    'humidity': (70, 95),
    'vibration': (0.8, 1.5),
}

DEFAULT_FACILITIES = {
    'Center_A': {'distance': 45, 'capacity': 75, 'road_condition': 'Good'},
    'Center_B': {'distance': 60, 'capacity': 85, 'road_condition': 'Good'},
    'Original': {'distance': 30, 'capacity': 60, 'road_condition': 'Good'},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_telemetry():
    """Generate mock telemetry data based on chaos mode"""
    global is_chaos_mode
    
    if is_chaos_mode:
        ranges = CRISIS_TELEMETRY
    else:
        ranges = NORMAL_TELEMETRY
    
    telemetry = {
        'temperature': round(random.uniform(*ranges['temperature']), 1),
        'humidity': round(random.uniform(*ranges['humidity']), 1),
        'vibration': round(random.uniform(*ranges['vibration']), 2),
        'timestamp': int(time.time()),
        'chaos_mode': is_chaos_mode
    }
    
    # Add to trust engine history
    trust_engine.add_reading(telemetry)
    
    # Add to liability engine
    liability_engine.add_exposure(telemetry)
    
    return telemetry

def get_facilities():
    """Get facility data with varied conditions"""
    return {
        'Center_A': {
            'distance': random.randint(30, 80),
            'capacity': random.randint(40, 95),
            'road_condition': 'Blocked' if random.random() < 0.1 else 'Good'
        },
        'Center_B': {
            'distance': random.randint(40, 100),
            'capacity': random.randint(40, 95),
            'road_condition': 'Blocked' if random.random() < 0.1 else 'Good'
        },
        'Original': {
            'distance': random.randint(20, 50),
            'capacity': random.randint(40, 95),
            'road_condition': 'Good'
        }
    }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    """
    Get comprehensive telemetry with all AI analytics
    
    Returns:
    - Basic telemetry (temperature, humidity, vibration)
    - Hybrid engine prediction (Layer 2)
    - Future predictions (Layer 3)
    - Countdown timer (Layer 7)
    - Trust score (Layer 8)
    """
    telemetry = generate_telemetry()
    
    # LAYER 2: Hybrid Physics + ML Prediction
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    
    days_left = hybrid_result['final_days_left']
    
    # LAYER 3: Future Predictions
    decay_rate = hybrid_result['physics_details']['decay_rate']
    future_predictions = future_engine.predict(days_left, decay_rate)
    
    # Add to history
    future_engine.add_reading(days_left, decay_rate)
    
    # LAYER 7: Countdown Timer
    countdown = countdown_timer.format_countdown_components(days_left)
    
    # LAYER 8: Trust Score
    trust_result = trust_engine.calculate_trust_score(telemetry)
    
    # Determine status
    if days_left < 2:
        status = 'CRITICAL'
        status_color = '#ff4444'
    elif days_left < 5:
        status = 'WARNING'
        status_color = '#ffaa00'
    else:
        status = 'NORMAL'
        status_color = '#00cc66'
    
    response = {
        # Basic telemetry
        'temperature': telemetry['temperature'],
        'humidity': telemetry['humidity'],
        'vibration': telemetry['vibration'],
        'timestamp': telemetry['timestamp'],
        'chaos_mode': is_chaos_mode,
        
        # LAYER 2: Hybrid Engine Results
        'days_left': round(days_left, 1),
        'physics_prediction': hybrid_result['physics_prediction'],
        'ml_prediction': hybrid_result['ml_prediction'],
        'hybrid_prediction': hybrid_result['final_days_left'],
        'decay_rate': hybrid_result['physics_details']['decay_rate'],
        
        # LAYER 3: Future Predictions
        'future_1h': future_predictions['after_1h'],
        'future_2h': future_predictions['after_2h'],
        'future_4h': future_predictions['after_4h'],
        'decay_trend': future_predictions['trend']['severity'],
        
        # LAYER 7: Countdown Timer
        'countdown_display': countdown['display'],
        'countdown_verbose': countdown['display_verbose'],
        'countdown_seconds': countdown['total_seconds'],
        'urgency': countdown['urgency'],
        
        # LAYER 8: Trust Score
        'trust_score': trust_result['trust_score'],
        'trust_grade': trust_result['grade'],
        
        # Status
        'status': status,
        'status_color': status_color
    }
    
    return jsonify(response)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Get comprehensive analytics including all layers
    
    Returns:
    - Route optimization (Layer 4)
    - Profit optimization (Layer 5)
    - Driver recommendations (Layer 6)
    - Liability analysis (Layer 9)
    - Explainable AI (Layer 10)
    """
    telemetry = generate_telemetry()
    facilities = get_facilities()
    
    # LAYER 2: Get days left
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    days_left = hybrid_result['final_days_left']
    
    # LAYER 4: Survival Margin Optimization
    route_result = survival_optimizer.optimize(facilities, days_left)
    
    # LAYER 5: Profit Optimization
    food_value = 10000  # Default value
    profit_result = profit_optimizer.calculate_profit_saved(
        food_value=food_value,
        remaining_shelf_life=days_left,
        max_shelf_life=14
    )
    
    # Calculate survival margin for recommendations
    survival_margin = None
    if route_result.get('travel_time_hours') and route_result['travel_time_hours'] != 'INF':
        survival_margin = days_left * 24 - route_result['travel_time_hours']
    
    # LAYER 6: Driver Recommendations
    recommendations = driver_recommender.generate_recommendations(telemetry, survival_margin)
    recommendation_summary = driver_recommender.get_summary(recommendations)
    
    # LAYER 9: Liability Analysis
    damage_attribution = liability_engine.calculate_damage_attribution(
        liability_engine.exposure_history,
        transit_delay_hours=route_result.get('travel_time_hours', 0) if isinstance(route_result.get('travel_time_hours'), (int, float)) else 0
    )
    liability_report = liability_engine.generate_responsibility_report(damage_attribution)
    
    # LAYER 10: Explainable AI
    explainable = explainable_ai.explain_reroute(route_result, telemetry, days_left)
    explainable_profit = explainable_ai.explain_profit_saved(
        profit_result, route_result, 
        original_days=days_left * 0.7,  # Simulated original
        optimized_days=days_left
    )
    
    response = {
        # Telemetry
        'telemetry': telemetry,
        'days_left': round(days_left, 1),
        
        # LAYER 4: Route Optimization
        'route': {
            'destination': route_result['destination'],
            'reason': route_result['reason'],
            'explanation': route_result['explanation'],
            'travel_time_hours': route_result.get('travel_time_hours'),
            'candidates': route_result.get('candidates', []),
            'risk_level': route_result.get('overall_risk', {}).get('level', 'NORMAL')
        },
        
        # LAYER 5: Profit Optimization
        'profit': {
            'profit_saved': profit_result['profit_saved'],
            'profit_saved_formatted': profit_result['profit_saved_formatted'],
            'remaining_percent': profit_result['remaining_percent'],
            'food_value': profit_result['food_value'],
            'quality_grade': profit_optimizer.get_grade(profit_result['remaining_percent'])
        },
        
        # LAYER 6: Driver Recommendations
        'recommendations': {
            'messages': [r['message'] for r in recommendations],
            'summary': recommendation_summary,
            'critical_count': recommendation_summary['critical'],
            'has_critical': recommendation_summary['has_critical']
        },
        
        # LAYER 9: Liability
        'liability': {
            'damage_attribution': damage_attribution,
            'responsibility_report': liability_report
        },
        
        # LAYER 10: Explainable AI
        'explainable': {
            'reroute_reason': explainable.get('why', []),
            'profit_explanation': explainable_profit.get('why', [])
        }
    }
    
    return jsonify(response)


@app.route('/api/reroute', methods=['GET'])
def get_reroute():
    """
    Get smart reroute recommendation (Legacy endpoint with enhancements)
    
    Returns route decision with full explanation
    """
    telemetry = generate_telemetry()
    facilities = get_facilities()
    
    # Get hybrid prediction
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    days_left = hybrid_result['final_days_left']
    
    # Get route optimization
    route_result = survival_optimizer.optimize(facilities, days_left)
    
    response = {
        'destination': route_result['destination'],
        'reason': route_result['reason'],
        'explanation': route_result['explanation'],
        'days_left': round(days_left, 1),
        
        # Enhanced data
        'physics_prediction': hybrid_result['physics_prediction'],
        'ml_prediction': hybrid_result['ml_prediction'],
        'travel_time': route_result.get('travel_time_hours'),
        'candidates': route_result.get('candidates', []),
        
        # Trust score
        'trust_score': trust_engine.calculate_trust_score(telemetry)['trust_score'],
        
        'telemetry': telemetry
    }
    
    return jsonify(response)


@app.route('/api/future', methods=['GET'])
def get_future_predictions():
    """
    Get future shelf-life predictions (Layer 3)
    
    Returns predictions for +1h, +2h, +4h
    """
    telemetry = generate_telemetry()
    
    # Get current prediction
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    days_left = hybrid_result['final_days_left']
    decay_rate = hybrid_result['physics_details']['decay_rate']
    
    # Get future predictions
    predictions = future_engine.predict(days_left, decay_rate)
    
    # Generate curve for charting
    curve = future_engine.generate_curve(days_left, decay_rate, hours=24, points=50)
    
    response = {
        'now': predictions['now'],
        'after_1h': predictions['after_1h'],
        'after_2h': predictions['after_2h'],
        'after_4h': predictions['after_4h'],
        'decay_rate_per_hour': predictions['decay_rate_per_hour'],
        'trend': predictions['trend'],
        'curve': curve,
        'days_left': days_left
    }
    
    return jsonify(response)


@app.route('/api/profit', methods=['GET'])
def get_profit():
    """
    Get profit optimization data (Layer 5)
    
    Returns profit calculations
    """
    telemetry = generate_telemetry()
    
    # Get current prediction
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    days_left = hybrid_result['final_days_left']
    
    # Calculate profit
    food_value = 10000  # Default
    profit = profit_optimizer.calculate_profit_saved(food_value, days_left)
    
    # Get daily value
    daily = profit_optimizer.estimate_daily_value(food_value, 14)
    
    # Get quality grade
    grade = profit_optimizer.get_grade(profit['remaining_percent'])
    
    response = {
        'profit_saved': profit['profit_saved'],
        'profit_saved_formatted': profit['profit_saved_formatted'],
        'remaining_percent': profit['remaining_percent'],
        'remaining_days': profit['remaining_days'],
        'food_value': profit['food_value'],
        'daily_value': daily['daily_value_formatted'],
        'hourly_value': daily['hourly_value_formatted'],
        'quality_grade': grade,
        'days_left': days_left
    }
    
    return jsonify(response)


@app.route('/api/trust', methods=['GET'])
def get_trust_score():
    """
    Get transport trust score (Layer 8)
    
    Returns trust score and breakdown
    """
    telemetry = generate_telemetry()
    
    # Get trust score
    trust = trust_engine.calculate_trust_score(
        telemetry,
        trust_engine.history,
        len(trust_engine.chaos_events) if is_chaos_mode else 0
    )
    
    # Get statistics
    stats = trust_engine.get_statistics()
    trend = trust_engine.get_trend()
    
    response = {
        'trust_score': trust['trust_score'],
        'trust_score_percent': trust['trust_score_percent'],
        'grade': trust['grade'],
        'grade_color': trust['grade_color'],
        'penalties': trust['penalties'],
        'total_penalty': trust['total_penalty'],
        'is_healthy': trust['is_healthy'],
        'statistics': stats,
        'trend': trend
    }
    
    return jsonify(response)


@app.route('/api/liability', methods=['GET'])
def get_liability():
    """
    Get liability analysis (Layer 9)
    
    Returns damage attribution and responsibility report
    """
    # Get current telemetry
    telemetry = generate_telemetry()
    
    # Calculate damage attribution
    damage = liability_engine.calculate_damage_attribution(
        liability_engine.exposure_history,
        transit_delay_hours=random.randint(1, 8)  # Simulated delay
    )
    
    # Generate responsibility report
    parties = {
        'CoolTemp Logistics': 'CARRIER',
        'FreshFarm Shippers': 'SHIPPER',
        'Arctic Cool Systems': 'REFRIGERATION'
    }
    report = liability_engine.generate_responsibility_report(damage, parties)
    
    # Exposure summary
    exposure = liability_engine.get_exposure_summary()
    
    response = {
        'damage_attribution': damage,
        'responsibility_report': report,
        'exposure_summary': exposure
    }
    
    return jsonify(response)


@app.route('/api/explain', methods=['GET'])
def get_explanation():
    """
    Get comprehensive AI explanation (Layer 10)
    
    Returns full explainable AI report
    """
    telemetry = generate_telemetry()
    facilities = get_facilities()
    
    # Get all predictions
    hybrid_result = hybrid_engine.predict(
        temperature=telemetry['temperature'],
        humidity=telemetry['humidity'],
        vibration=telemetry['vibration']
    )
    days_left = hybrid_result['final_days_left']
    
    # Get route decision
    route_result = survival_optimizer.optimize(facilities, days_left)
    
    # Get profit
    profit_result = profit_optimizer.calculate_profit_saved(10000, days_left)
    
    # Get recommendations
    survival_margin = None
    if route_result.get('travel_time_hours') and isinstance(route_result.get('travel_time_hours'), (int, float)):
        survival_margin = days_left * 24 - route_result['travel_time_hours']
    recommendations = driver_recommender.generate_recommendations(telemetry, survival_margin)
    
    # Get trust score
    trust_result = trust_engine.calculate_trust_score(telemetry)
    
    # Generate full explanation
    all_data = {
        'hybrid': hybrid_result,
        'future': future_engine.predict(days_left, hybrid_result['physics_details']['decay_rate']),
        'route': route_result,
        'profit': profit_result,
        'recommendations': recommendations,
        'trust': trust_result
    }
    
    full_explanation = explainable_ai.generate_full_explanation(all_data)
    
    return jsonify(full_explanation)


@app.route('/api/chaos', methods=['POST'])
def toggle_chaos():
    """Toggle chaos mode"""
    global is_chaos_mode
    data = request.get_json()
    is_chaos_mode = data.get('enabled', not is_chaos_mode)
    
    if is_chaos_mode:
        trust_engine.add_chaos_event('Manual chaos toggle')
    
    return jsonify({'chaos_mode': is_chaos_mode})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current chaos mode status"""
    return jsonify({'chaos_mode': is_chaos_mode})


@app.route('/api/market-pivot', methods=['GET', 'POST'])
def get_market_pivot():
    """
    Get Market Pivot / Emergency Rescue Analysis
    
    Calculates if cargo needs to be pivoted to secondary markets
    based on remaining shelf life vs time to destination.
    
    GET: Uses current telemetry and default values
    POST: Uses provided values for custom calculation
    """
    
    if request.method == 'POST':
        # Use provided values
        data = request.get_json() or {}
        cargo_value = data.get('cargo_value', 700000)
        remaining_shelf_life_hrs = data.get('remaining_shelf_life_hrs', 3.0)
        original_eta_hrs = data.get('original_eta_hrs', 4.0)
        travel_times = data.get('travel_times', {})
    else:
        # Use current telemetry and defaults
        telemetry = generate_telemetry()
        
        # Get hybrid prediction for remaining shelf life
        hybrid_result = hybrid_engine.predict(
            temperature=telemetry['temperature'],
            humidity=telemetry['humidity'],
            vibration=telemetry['vibration']
        )
        days_left = hybrid_result['final_days_left']
        remaining_shelf_life_hrs = days_left * 24  # Convert days to hours
        
        # Default values
        cargo_value = 700000  # ₹7 Lakhs
        original_eta_hrs = 4.0
        travel_times = {
            'Plant_Alpha': 2.5,
            'Market_Beta': 1.5,
            'BioFuel_Gamma': 1.0,
            'Premium_Supermarket': 4.0
        }
    
    # Calculate emergency triage
    result = market_pivot_engine.calculate_emergency_triage(
        current_cargo_value=cargo_value,
        remaining_shelf_life_hrs=remaining_shelf_life_hrs,
        original_destination_eta_hrs=original_eta_hrs,
        travel_times=travel_times
    )
    
    # Get available markets
    markets = market_pivot_engine.get_market_options()
    
    return jsonify({
        'triage': result,
        'available_markets': markets,
        'input_values': {
            'cargo_value': cargo_value,
            'remaining_shelf_life_hrs': remaining_shelf_life_hrs,
            'original_eta_hrs': original_eta_hrs,
            'travel_times': travel_times
        }
    })


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Aegis Harvest - Spoilage Shield 2.0")
    print("="*60)
    print("Starting Intelligent Logistics System...")
    print(f"✓ Services Loaded: {len([hybrid_engine, future_engine, survival_optimizer, profit_optimizer, driver_recommender, countdown_timer, trust_engine, liability_engine, explainable_ai, market_pivot_engine])}")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
