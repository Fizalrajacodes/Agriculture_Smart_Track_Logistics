"""
=============================================================================
LAYER 3: FUTURE PREDICTION ENGINE
=============================================================================

This engine provides short-term shelf-life forecasting using linear
trend extrapolation based on current decay rates.

Predicts shelf life for:
- +1 hour
- +2 hours
- +4 hours

Formula:
future_value = current - (decay_rate × hours)

Also generates a complete curve array for chart plotting.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

import numpy as np
from typing import Dict, List, Tuple

class FuturePredictionEngine:
    """
    Future Prediction Engine for Short-Term Shelf-Life Forecasting
    
    Uses linear trend extrapolation based on current decay rates
    to predict shelf life at specific time intervals.
    """
    
    # future Time intervals for prediction (in hours)
    PREDICTION_INTERVALS = [1, 2, 4]
    
    def __init__(self):
        """Initialize the future prediction engine"""
        self.history = []
        self.max_history = 100  # Keep last 100 readings
        
    def calculate_decay_rate_per_hour(self, days_left, decay_rate_per_day):
        """
        Convert daily decay rate to hourly
        
        Args:
            days_left: Current days left
            decay_rate_per_day: Decay rate per day
            
        Returns:
            Hourly decay rate
        """
        if days_left <= 0:
            return 0
        # Rate at which shelf life decreases per hour
        return decay_rate_per_day / 24
    
    def predict_future(self, current_days_left, decay_rate_per_day, hours_ahead):
        """
        Predict shelf life after X hours
        
        Formula: future_value = current - (decay_rate × hours)
        
        Args:
            current_days_left: Current remaining shelf life in days
            decay_rate_per_day: Daily decay rate
            hours_ahead: Number of hours into the future
            
        Returns:
            Predicted days left after specified hours
        """
        hourly_rate = self.calculate_decay_rate_per_hour(current_days_left, decay_rate_per_day)
        future_days_left = current_days_left - (hourly_rate * hours_ahead)
        return max(0, future_days_left)
    
    def predict(self, current_days_left, decay_rate_per_day):
        """
        Generate predictions for all time intervals
        
        Args:
            current_days_left: Current remaining shelf life in days
            decay_rate_per_day: Daily decay rate
            
        Returns:
            Dictionary with predictions at each time interval
        """
        predictions = {
            'now': round(current_days_left, 2),
            'after_1h': round(self.predict_future(current_days_left, decay_rate_per_day, 1), 2),
            'after_2h': round(self.predict_future(current_days_left, decay_rate_per_day, 2), 2),
            'after_4h': round(self.predict_future(current_days_left, decay_rate_per_day, 4), 2),
            'decay_rate_per_hour': round(self.calculate_decay_rate_per_hour(current_days_left, decay_rate_per_day), 4)
        }
        
        # Add trend analysis
        predictions['trend'] = self._analyze_trend(predictions)
        
        return predictions
    
    def generate_curve(self, current_days_left, decay_rate_per_day, hours=24, points=100):
        """
        Generate future shelf-life curve for chart plotting
        
        Args:
            current_days_left: Current remaining shelf life in days
            decay_rate_per_day: Daily decay rate
            hours: Total hours to project (default 24)
            points: Number of data points for the curve
            
        Returns:
            List of (time_hours, days_left) tuples for plotting
        """
        curve = []
        hourly_rate = self.calculate_decay_rate_per_hour(current_days_left, decay_rate_per_day)
        
        for i in range(points + 1):
            t = (hours / points) * i  # Time in hours
            days_left = max(0, current_days_left - (hourly_rate * t))
            curve.append({
                'time_hours': round(t, 2),
                'days_left': round(days_left, 2)
            })
            
        return curve
    
    def _analyze_trend(self, predictions):
        """
        Analyze the trend of shelf-life decay
        
        Args:
            predictions: Dictionary with predictions at different times
            
        Returns:
            Trend analysis dictionary
        """
        decline_1h = predictions['now'] - predictions['after_1h']
        decline_2h = predictions['now'] - predictions['after_2h']
        decline_4h = predictions['now'] - predictions['after_4h']
        
        # Determine trend severity
        if decline_4h > predictions['now'] * 0.5:
            severity = 'CRITICAL'
            description = 'Rapid decay - less than 50% shelf life in 4 hours'
        elif decline_4h > predictions['now'] * 0.25:
            severity = 'WARNING'
            description = 'Moderate decay - monitor closely'
        else:
            severity = 'NORMAL'
            description = 'Stable shelf life'
            
        return {
            'severity': severity,
            'description': description,
            'decline_per_hour': round(decline_1h, 3),
            'decline_4h_percent': round((decline_4h / predictions['now']) * 100, 1) if predictions['now'] > 0 else 0
        }
    
    def add_reading(self, days_left, decay_rate):
        """
        Add a reading to history for trend analysis
        
        Args:
            days_left: Current days left
            decay_rate: Current decay rate
        """
        self.history.append({
            'days_left': days_left,
            'decay_rate': decay_rate,
        })
        
        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_historical_trend(self):
        """
        Analyze historical trend from stored readings
        
        Returns:
            Dictionary with historical trend analysis
        """
        if len(self.history) < 2:
            return {'trend': 'INSUFFICIENT_DATA'}
        
        # Calculate average decay rate
        avg_decay = sum(h['decay_rate'] for h in self.history) / len(self.history)
        
        # Calculate variance in days_left
        days_values = [h['days_left'] for h in self.history]
        variance = np.var(days_values)
        
        return {
            'avg_decay_rate': round(avg_decay, 4),
            'variance': round(variance, 4),
            'readings': len(self.history),
            'trend_direction': 'DECREASING' if days_values[-1] < days_values[0] else 'STABLE'
        }
    
    def get_warnings(self, predictions):
        """
        Generate warnings based on predictions
        
        Args:
            predictions: Dictionary with predictions
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        if predictions['after_1h'] < 2:
            warnings.append("CRITICAL: Shelf life will drop below 2 days in 1 hour!")
            
        if predictions['after_2h'] < 1:
            warnings.append("CRITICAL: Shelf life will drop below 1 day in 2 hours!")
            
        if predictions['trend']['severity'] == 'CRITICAL':
            warnings.append("RAPID DECAY: Immediate action required!")
            
        return warnings


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_future_prediction():
    """Demo function to test the future prediction engine"""
    engine = FuturePredictionEngine()
    
    # Test case 1: Normal decay
    print("\n" + "="*60)
    print("TEST 1: Normal decay scenario")
    print("="*60)
    
    current_days = 10.0
    decay_rate = 0.5  # 0.5 days decay per day
    
    predictions = engine.predict(current_days, decay_rate)
    print(f"Current Days Left: {current_days} days")
    print(f"Decay Rate: {decay_rate}/day")
    print(f"\nPredictions:")
    print(f"  Now:     {predictions['now']} days")
    print(f"  +1 hour: {predictions['after_1h']} days")
    print(f"  +2 hours: {predictions['after_2h']} days")
    print(f"  +4 hours: {predictions['after_4h']} days")
    print(f"\nTrend: {predictions['trend']['severity']} - {predictions['trend']['description']}")
    
    # Generate curve for charting
    curve = engine.generate_curve(current_days, decay_rate, hours=24, points=10)
    print(f"\nShelf-Life Curve (sample points):")
    for point in curve[::2]:  # Every other point
        print(f"  {point['time_hours']:5.1f}h: {point['days_left']:.2f} days")
    
    # Test case 2: Rapid decay (stress conditions)
    print("\n" + "="*60)
    print("TEST 2: Rapid decay scenario (high stress)")
    print("="*60)
    
    current_days = 5.0
    decay_rate = 3.0  # High decay rate
    
    predictions = engine.predict(current_days, decay_rate)
    print(f"Current Days Left: {current_days} days")
    print(f"Decay Rate: {decay_rate}/day")
    print(f"\nPredictions:")
    print(f"  Now:     {predictions['now']} days")
    print(f"  +1 hour: {predictions['after_1h']} days")
    print(f"  +2 hours: {predictions['after_2h']} days")
    print(f"  +4 hours: {predictions['after_4h']} days")
    print(f"\nTrend: {predictions['trend']['severity']} - {predictions['trend']['description']}")
    
    # Get warnings
    warnings = engine.get_warnings(predictions)
    print(f"\nWarnings:")
    for w in warnings:
        print(f"  ⚠️  {w}")
    
    # Test case 3: Historical tracking
    print("\n" + "="*60)
    print("TEST 3: Historical trend analysis")
    print("="*60)
    
    # Simulate historical readings
    for days in [12, 11.5, 11, 10.2, 9.5, 8.8]:
        engine.add_reading(days, 0.5)
    
    historical = engine.get_historical_trend()
    print(f"Average Decay Rate: {historical['avg_decay_rate']}/day")
    print(f"Variance: {historical['variance']}")
    print(f"Readings: {historical['readings']}")
    print(f"Trend Direction: {historical['trend_direction']}")


if __name__ == '__main__':
    demo_future_prediction()
