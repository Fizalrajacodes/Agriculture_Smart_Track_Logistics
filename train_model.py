"""
Aegis Harvest - Spoilage Shield
Predictive Supply Chain Dashboard
ML Model for Shelf-Life Prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

# Create sample dataset based on the problem description
def create_sample_dataset():
    """Generate a dataset following the biological and mechanical spoilage rules"""
    np.random.seed(42)
    n_samples = 2000
    
    # Generate base temperature (normal range 2-8°C, crisis 30-45°C)
    temperature = np.random.uniform(2, 45, n_samples)
    
    # Generate humidity (30-95%)
    humidity = np.random.uniform(30, 95, n_samples)
    
    # Generate vibration (0-2G)
    vibration = np.random.uniform(0, 2, n_samples)
    
    # Initial shelf life at ideal conditions (4°C, 0 vibration) = 14 days
    base_shelf_life = 14
    
    # Biological Decay Rule: For every 10°C above 4°C, decay doubles
    temp_above_ideal = np.maximum(0, temperature - 4)
    temp_multiplier = 2 ** (temp_above_ideal / 10)
    
    # Mechanical Stress Rule: Vibration > 0.5G acts as 1.5x multiplier
    vibration_multiplier = np.where(vibration > 0.5, 1.5, 1.0)
    
    # Humidity impact (high humidity accelerates spoilage)
    humidity_multiplier = 1 + (humidity - 50) / 100
    
    # Calculate days left
    days_left = base_shelf_life / (temp_multiplier * vibration_multiplier * humidity_multiplier)
    
    # Add some noise
    days_left = days_left + np.random.normal(0, 0.5, n_samples)
    days_left = np.maximum(0, days_left)  # Can't be negative
    
    # Generate facility data
    center_a_distance = np.random.uniform(20, 100, n_samples)
    center_b_distance = np.random.uniform(30, 120, n_samples)
    
    # Road conditions (0=Good, 1=Blocked)
    road_condition_a = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    road_condition_b = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    
    # Facility capacity (0-100%)
    capacity_a = np.random.uniform(30, 100, n_samples)
    capacity_b = np.random.uniform(30, 100, n_samples)
    
    # Travel time calculation
    def calc_travel_time(distance, road_blocked):
        if road_blocked == 1:
            return float('inf')
        base_speed = 60  # km/h
        return distance / base_speed
    
    travel_time_a = np.array([calc_travel_time(d, r) for d, r in zip(center_a_distance, road_condition_a)])
    travel_time_b = np.array([calc_travel_time(d, r) for d, r in zip(center_b_distance, road_condition_b)])
    travel_time_orig = np.random.uniform(2, 8, n_samples)  # Original destination
    
    # Calculate Survival Margin: SM = Days_Left - Travel_Time
    sm_a = days_left - travel_time_a
    sm_b = days_left - travel_time_b
    sm_orig = days_left - travel_time_orig
    
    # Determine best center
    best_centers = []
    for i in range(n_samples):
        candidates = []
        if not np.isinf(travel_time_orig[i]):
            candidates.append(('Original', sm_orig[i]))
        if road_condition_a[i] == 0 and capacity_a[i] < 90:
            candidates.append(('Center_A', sm_a[i]))
        if road_condition_b[i] == 0 and capacity_b[i] < 90:
            candidates.append(('Center_B', sm_b[i]))
        
        # If all SM are negative, dump
        if not candidates or all(sm < 0 for _, sm in candidates):
            best_centers.append('Dump')
        else:
            best_center = max(candidates, key=lambda x: x[1])
            best_centers.append(best_center[0])
    
    # Create DataFrame
    df = pd.DataFrame({
        'Temperature': temperature,
        'Humidity': humidity,
        'Vibration': vibration,
        'Days_Left': days_left,
        'Center_A_Distance': center_a_distance,
        'Center_B_Distance': center_b_distance,
        'Road_Condition_A': road_condition_a,
        'Road_Condition_B': road_condition_b,
        'Capacity_A': capacity_a,
        'Capacity_B': capacity_b,
        'Travel_Time_A': travel_time_a,
        'Travel_Time_B': travel_time_b,
        'Travel_Time_Orig': travel_time_orig,
        'Best_Center': best_centers
    })
    
    return df

def train_model():
    """Train the ML model for shelf-life prediction"""
    print("Creating sample dataset...")
    df = create_sample_dataset()
    
    # Features for ML model
    features = ['Temperature', 'Humidity', 'Vibration']
    X = df[features]
    y = df['Days_Left']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("Training ML model...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"Training R² Score: {train_score:.4f}")
    print(f"Test R² Score: {test_score:.4f}")
    
    # Save model and scaler
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save sample data
    df.to_csv('aegis_harvest_dataset.csv', index=False)
    print("Model and data saved successfully!")
    
    return model, scaler

if __name__ == "__main__":
    train_model()
