"""
=============================================================================
LAYER 2: PHYSICS + ML HYBRID ENGINE
=============================================================================

This engine combines biological physics-based decay modeling with 
machine learning predictions for accurate shelf-life estimation.

Physics Model: Biological exponential decay based on temperature & vibration
ML Model: RandomForestRegressor trained on historical data
Hybrid: Weighted combination of both predictions

Formula:
- Physics: DecayRate = BaseRate × 2^((Temp − 4) / 10)
- If vibration > 0.5G: multiply decay rate by 1.5
- Final = 0.4 × Physics + 0.6 × ML (configurable weights)

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

import numpy as np
import pickle
import os

class HybridEngine:
    """
    Hybrid Physics + ML Engine for Shelf-Life Prediction
    
    Combines biological decay physics with ML predictions for
    more accurate shelf-life estimation.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        'physics_weight': 0.4,
        'ml_weight': 0.6,
        'base_decay_rate': 1.0,  # Base decay rate per day at 4°C
        'base_shelf_life': 14,   # Maximum shelf life in days at ideal conditions
        'vibration_threshold': 0.5,  # G threshold for damage
        'vibration_penalty': 1.5,    # Multiplier when vibration > threshold
        'temperature_reference': 4   # Reference temperature in °C
    }
    
    def __init__(self, config=None, model_path='model.pkl', scaler_path='scaler.pkl'):
        """
        Initialize Hybrid Engine with optional configuration
        
        Args:
            config: Dictionary with custom weights and parameters
            model_path: Path to trained ML model
            scaler_path: Path to feature scaler
        """
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.model = None
        self.scaler = None
        self._load_model(model_path, scaler_path)
        
    def _load_model(self, model_path, scaler_path):
        """Load trained ML model and scaler"""
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"[HybridEngine] Model loaded from {model_path}")
            else:
                print(f"[HybridEngine] Warning: Model not found at {model_path}")
                
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"[HybridEngine] Scaler loaded from {scaler_path}")
            else:
                print(f"[HybridEngine] Warning: Scaler not found at {scaler_path}")
        except Exception as e:
            print(f"[HybridEngine] Error loading model: {e}")
    
    def calculate_physics_decay(self, temperature, humidity, vibration):
        """
        Calculate physics-based decay rate and predicted days left
        
        Physics Formula:
        DecayRate = BaseRate × 2^((Temp − 4) / 10)
        
        If vibration > 0.5G: multiply decay rate by 1.5
        
        Args:
            temperature: Temperature in °C
            humidity: Humidity percentage
            vibration: Vibration in G
            
        Returns:
            Dictionary with decay_rate and days_left_physics
        """
        temp_ref = self.config['temperature_reference']
        base_rate = self.config['base_decay_rate']
        
        # Temperature effect: Q10 principle (rate doubles for every 10°C increase)
        temp_diff = temperature - temp_ref
        temp_multiplier = 2 ** (temp_diff / 10)
        
        # Vibration effect: mechanical stress increases decay
        if vibration > self.config['vibration_threshold']:
            vibration_multiplier = self.config['vibration_penalty']
        else:
            vibration_multiplier = 1.0
            
        # Humidity effect: high humidity accelerates decay
        humidity_multiplier = 1 + max(0, (humidity - 50)) / 100
        
        # Calculate total decay rate
        decay_rate = base_rate * temp_multiplier * vibration_multiplier * humidity_multiplier
        
        # Convert decay rate to days left
        base_shelf_life = self.config['base_shelf_life']
        days_left = base_shelf_life / decay_rate
        
        return {
            'decay_rate': round(decay_rate, 4),
            'days_left_physics': round(max(0, days_left), 2),
            'temp_multiplier': round(temp_multiplier, 4),
            'vibration_multiplier': round(vibration_multiplier, 2),
            'humidity_multiplier': round(humidity_multiplier, 4)
        }
    
    def predict_ml(self, temperature, humidity, vibration, road_condition=0):
        """
        Predict shelf life using ML model
        
        Args:
            temperature: Temperature in °C
            humidity: Humidity percentage
            vibration: Vibration in G
            road_condition: Encoded road condition (0=Good, 1=Moderate, 2=Poor)
            
        Returns:
            Dictionary with ML prediction
        """
        if self.model is None or self.scaler is None:
            # Fallback to physics-only if ML not available
            physics_result = self.calculate_physics_decay(temperature, humidity, vibration)
            return {
                'days_left_ml': physics_result['days_left_physics'],
                'ml_available': False
            }
        
        try:
            # Prepare features
            features = np.array([[temperature, humidity, vibration, road_condition]])
            features_scaled = self.scaler.transform(features)
            
            # Get ML prediction
            ml_prediction = self.model.predict(features_scaled)[0]
            ml_prediction = max(0, ml_prediction)
            
            return {
                'days_left_ml': round(ml_prediction, 2),
                'ml_available': True
            }
        except Exception as e:
            print(f"[HybridEngine] ML prediction error: {e}")
            # Fallback to physics
            physics_result = self.calculate_physics_decay(temperature, humidity, vibration)
            return {
                'days_left_ml': physics_result['days_left_physics'],
                'ml_available': False
            }
    
    def predict(self, temperature, humidity, vibration, road_condition=0):
        """
        Main prediction method - combines physics and ML
        
        Final_Days_Left = Physics_Weight × Physics_Prediction + 
                          ML_Weight × ML_Prediction
        
        Args:
            temperature: Temperature in °C
            humidity: Humidity percentage  
            vibration: Vibration in G
            road_condition: Encoded road condition (0=Good, 1=Moderate, 2=Poor)
            
        Returns:
            Dictionary with physics, ML, and final predictions
        """
        # Get physics prediction
        physics_result = self.calculate_physics_decay(temperature, humidity, vibration)
        physics_prediction = physics_result['days_left_physics']
        
        # Get ML prediction
        ml_result = self.predict_ml(temperature, humidity, vibration, road_condition)
        ml_prediction = ml_result['days_left_ml']
        
        # Calculate weighted final prediction
        physics_weight = self.config['physics_weight']
        ml_weight = self.config['ml_weight']
        
        final_days_left = (
            physics_weight * physics_prediction + 
            ml_weight * ml_prediction
        )
        
        return {
            'physics_prediction': round(physics_prediction, 2),
            'ml_prediction': round(ml_prediction, 2),
            'final_days_left': round(final_days_left, 2),
            'weights': {
                'physics': physics_weight,
                'ml': ml_weight
            },
            'physics_details': {
                'decay_rate': physics_result['decay_rate'],
                'temp_multiplier': physics_result['temp_multiplier'],
                'vibration_multiplier': physics_result['vibration_multiplier'],
                'humidity_multiplier': physics_result['humidity_multiplier']
            },
            'ml_available': ml_result['ml_available']
        }
    
    def update_weights(self, physics_weight, ml_weight):
        """
        Update the hybrid weights dynamically
        
        Args:
            physics_weight: Weight for physics prediction (0-1)
            ml_weight: Weight for ML prediction (0-1)
        """
        total = physics_weight + ml_weight
        if total == 0:
            raise ValueError("Weights cannot both be zero")
        
        self.config['physics_weight'] = physics_weight / total
        self.config['ml_weight'] = ml_weight / total
        
        print(f"[HybridEngine] Weights updated: Physics={self.config['physics_weight']:.2f}, ML={self.config['ml_weight']:.2f}")
    
    def get_health_status(self, days_left):
        """
        Determine health status based on days left
        
        Args:
            days_left: Remaining shelf life in days
            
        Returns:
            Status string and color
        """
        if days_left < 2:
            return {'status': 'CRITICAL', 'status_color': '#ff4444'}
        elif days_left < 5:
            return {'status': 'WARNING', 'status_color': '#ffaa00'}
        else:
            return {'status': 'NORMAL', 'status_color': '#00cc66'}


# =============================================================================
# HACKATHON DEMO FUNCTION - Quick standalone test
# =============================================================================

def demo_hybrid_engine():
    """Demo function to test the hybrid engine"""
    engine = HybridEngine()
    
    # Test case 1: Ideal conditions
    print("\n" + "="*60)
    print("TEST 1: Ideal refrigerated conditions")
    print("="*60)
    result = engine.predict(temperature=4, humidity=50, vibration=0.1)
    print(f"Temperature: 4°C, Humidity: 50%, Vibration: 0.1G")
    print(f"Physics Prediction: {result['physics_prediction']} days")
    print(f"ML Prediction: {result['ml_prediction']} days")
    print(f"FINAL (Hybrid): {result['final_days_left']} days")
    
    # Test case 2: High temperature + vibration
    print("\n" + "="*60)
    print("TEST 2: High stress conditions")
    print("="*60)
    result = engine.predict(temperature=25, humidity=80, vibration=0.8)
    print(f"Temperature: 25°C, Humidity: 80%, Vibration: 0.8G")
    print(f"Physics Prediction: {result['physics_prediction']} days")
    print(f"ML Prediction: {result['ml_prediction']} days")
    print(f"FINAL (Hybrid): {result['final_days_left']} days")
    print(f"Decay Rate: {result['physics_details']['decay_rate']}/day")
    print(f"Temp Multiplier: {result['physics_details']['temp_multiplier']}x")
    print(f"Vibration Multiplier: {result['physics_details']['vibration_multiplier']}x")
    
    # Test case 3: Custom weights
    print("\n" + "="*60)
    print("TEST 3: Custom weights (80% physics, 20% ML)")
    print("="*60)
    engine.update_weights(0.8, 0.2)
    result = engine.predict(temperature=10, humidity=60, vibration=0.3)
    print(f"Temperature: 10°C, Humidity: 60%, Vibration: 0.3G")
    print(f"Physics Prediction: {result['physics_prediction']} days")
    print(f"ML Prediction: {result['ml_prediction']} days")
    print(f"FINAL (Hybrid): {result['final_days_left']} days")


if __name__ == '__main__':
    demo_hybrid_engine()
