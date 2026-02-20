"""
Aegis Harvest - Spoilage Shield
Flask Backend API
Predictive Supply Chain Dashboard
"""

from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd
import random
import time

app = Flask(__name__, template_folder='templates')

# Global state for chaos mode
is_chaos_mode = False

# Load model and scaler
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("Model loaded successfully!")
except:
    print("Warning: Model not found. Run train_model.py first.")
    model = None
    scaler = None

# Mock data for normal and crisis scenarios
NORMAL_TELEMETRY = {
    'temperature': (2, 8),      # Ideal refrigerated range
    'humidity': (40, 60),       # Optimal humidity
    'vibration': (0.1, 0.3),   # Smooth ride
}

CRISIS_TELEMETRY = {
    'temperature': (30, 45),   # Cooling failure - extreme heat
    'humidity': (70, 95),       # High humidity
    'vibration': (0.8, 1.5),   # Bumpy road / rough handling
}

# Facility data
FACILITIES = {
    'Center_A': {'distance': 45, 'capacity': 75, 'road_condition': 'Good'},
    'Center_B': {'distance': 60, 'capacity': 85, 'road_condition': 'Good'},
    'Original': {'distance': 30, 'capacity': 60, 'road_condition': 'Good'},
}

def predict_shelf_life(temperature, humidity, vibration):
    """Predict remaining shelf life using ML model"""
    if model is None or scaler is None:
        # Fallback calculation based on biological rules
        temp_above_ideal = max(0, temperature - 4)
        temp_multiplier = 2 ** (temp_above_ideal / 10)
        vibration_multiplier = 1.5 if vibration > 0.5 else 1.0
        humidity_multiplier = 1 + (humidity - 50) / 100
        days_left = 14 / (temp_multiplier * vibration_multiplier * humidity_multiplier)
        return max(0, days_left)
    
    features = np.array([[temperature, humidity, vibration]])
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    return max(0, prediction)

def calculate_travel_time(distance, road_condition):
    """Calculate travel time based on distance and road condition"""
    if road_condition == 'Blocked':
        return float('inf')
    base_speed = 60  # km/h
    return distance / base_speed

def calculate_survival_margin(days_left, travel_time):
    """Calculate Survival Margin: SM = Days_Left - Travel_Time"""
    if travel_time == float('inf'):
        return float('-inf')
    return days_left - travel_time

def smart_reroute(days_left, facilities):
    """Smart Reroute Engine - determines best destination"""
    candidates = []
    
    for name, data in facilities.items():
        travel_time = calculate_travel_time(data['distance'], data['road_condition'])
        capacity = data['capacity']
        
        # Skip if road is blocked
        if travel_time == float('inf'):
            continue
        
        # Skip if capacity > 90% (high risk)
        if capacity > 90:
            continue
        
        sm = calculate_survival_margin(days_left, travel_time)
        candidates.append({
            'destination': name,
            'travel_time': round(travel_time, 2),
            'survival_margin': round(sm, 2),
            'capacity': capacity,
            'distance': data['distance']
        })
    
    if not candidates:
        return {'destination': 'Dump', 'reason': 'All destinations are inviable', 'candidates': []}
    
    # Select best center based on highest survival margin
    best = max(candidates, key=lambda x: x['survival_margin'])
    
    if best['survival_margin'] < 0:
        return {
            'destination': 'Dump',
            'reason': f'All survival margins are negative. Best SM: {best["survival_margin"]:.2f}',
            'candidates': candidates
        }
    
    return {
        'destination': best['destination'],
        'reason': f'Highest survival margin: {best["survival_margin"]:.2f} days',
        'travel_time': best['travel_time'],
        'distance': best['distance'],
        'capacity': best['capacity'],
        'candidates': candidates
    }

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
    
    return telemetry

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    """Get current telemetry data"""
    telemetry = generate_telemetry()
    
    # Calculate derived values
    days_left = predict_shelf_life(
        telemetry['temperature'],
        telemetry['humidity'],
        telemetry['vibration']
    )
    
    telemetry['days_left'] = round(days_left, 1)
    
    # Determine status
    if days_left < 2:
        telemetry['status'] = 'CRITICAL'
        telemetry['status_color'] = '#ff4444'
    elif days_left < 5:
        telemetry['status'] = 'WARNING'
        telemetry['status_color'] = '#ffaa00'
    else:
        telemetry['status'] = 'NORMAL'
        telemetry['status_color'] = '#00cc66'
    
    return jsonify(telemetry)

@app.route('/api/reroute', methods=['GET'])
def get_reroute():
    """Get smart reroute recommendation"""
    telemetry = generate_telemetry()
    
    days_left = predict_shelf_life(
        telemetry['temperature'],
        telemetry['humidity'],
        telemetry['vibration']
    )
    
    # Get facility data with current road conditions
    # Randomly vary road conditions for demo
    facilities = {
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
    
    recommendation = smart_reroute(days_left, facilities)
    recommendation['days_left'] = round(days_left, 1)
    recommendation['telemetry'] = telemetry
    
    return jsonify(recommendation)

@app.route('/api/chaos', methods=['POST'])
def toggle_chaos():
    """Toggle chaos mode"""
    global is_chaos_mode
    data = request.get_json()
    is_chaos_mode = data.get('enabled', not is_chaos_mode)
    return jsonify({'chaos_mode': is_chaos_mode})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current chaos mode status"""
    return jsonify({'chaos_mode': is_chaos_mode})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
