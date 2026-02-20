# 🛡️ Aegis Harvest - Spoilage Shield

## Predictive Supply Chain Dashboard

### Mission
In the global food supply chain, over 30% of produce is lost before it reaches the consumer due to improper storage and transit delays. **Spoilage Shield** is an intelligent logistics application that uses Mild ML to monitor food quality in real-time and take automated actions to prevent waste.

---

## 🎯 Core Features

### 1. Command Center Dashboard
Real-time telemetry monitoring:
- 🌡️ **Temperature** - Monitor refrigerated conditions
- 💧 **Humidity** - Track moisture levels
- 📳 **Vibration** - Measure physical stress on cargo
- 📍 **Distance** - Current distance to destination

### 2. Predictive Shelf-Life (ML Model)
Machine learning regression model that predicts **Days_Left** (Remaining Shelf Life) based on:
- Temperature readings
- Humidity levels
- Vibration data

The model follows biological spoilage rules:
- **Biological Decay Rule**: For every 10°C increase above 4°C, decay rate doubles
- **Mechanical Stress Rule**: Vibration above 0.5G acts as 1.5x multiplier on decay rate

### 3. Smart Reroute Engine
Automated decision-making system that:
- Calculates **Survival Margin (SM)** = Days_Left - Travel_Time
- Evaluates multiple destination options
- Considers road conditions (blocked roads = infinite travel time)
- Factors in facility capacity (centers >90% capacity are high-risk)
- Dumps cargo if all survival margins are negative

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Train the ML model:**
```bash
python train_model.py
```

3. **Run the application:**
```bash
python app.py
```

4. **Open browser:**
Navigate to `http://localhost:5000`

---

## 🎮 How to Demo

### Normal Mode (Default)
- The dashboard shows green status
- Temperature stays in safe range (2-8°C)
- High predicted shelf-life (10-14 days)
- Continues to original destination

### Chaos Mode (Click the Button!)
1. Click the **"🔴 CHAOS MODE"** button
2. Temperature spikes to danger zone (30-45°C)
3. Vibration increases (bumpy road)
4. Watch the AI react:
   - Shelf-life drops dramatically
   - Dashboard turns red (CRITICAL)
   - Smart Reroute Engine activates
   - Recommends best center for emergency offloading

### Manual Control (Slider)
- Use the temperature slider to simulate gradual warming
- Watch shelf-life countdown in real-time
- See the AI make decisions as conditions change

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/telemetry` | GET | Get current sensor data |
| `/api/reroute` | GET | Get reroute recommendation |
| `/api/chaos` | POST | Toggle chaos mode |
| `/api/status` | GET | Get current chaos status |

---

## 🧠 Smart Reroute Logic

```
SM = Days_Left - Travel_Time

Decision Rules:
1. If road is Blocked → Skip destination
2. If Capacity > 90% → Skip destination (high risk)
3. If all SM < 0 → Dump cargo (unsalvageable)
4. Otherwise → Select destination with highest SM
```

---

## 📁 Project Structure

```
Agriculture/
├── app.py                  # Flask backend & frontend
├── train_model.py         # ML model training script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── safe_trip.json        # Normal scenario data
├── crisis_trip.json      # Crisis scenario data
├── model.pkl             # Trained ML model (generated)
├── scaler.pkl            # Feature scaler (generated)
└── aegis_harvest_dataset.csv  # Training data (generated)
```

---

## 🔬 Biological & Mechanical Rules

### Biological Decay Rule
```
For every 10°C above ideal (4°C), decay rate doubles:
Temp_Multiplier = 2^((Temperature - 4) / 10)
```

### Mechanical Stress Rule
```
If Vibration > 0.5G, apply 1.5x multiplier:
Vibration_Multiplier = 1.5 (if > 0.5G) else 1.0
```

### Final Calculation
```
Days_Left = Base_Shelf_Life / (Temp_Multiplier × Vibration_Multiplier × Humidity_Multiplier)
```

---

## 🏆 Key Capabilities

- ✅ Real-time ML predictions
- ✅ Automated emergency rerouting
- ✅ Visual dashboard with status indicators
- ✅ Chaos button for emergency simulation
- ✅ Manual temperature control slider
- ✅ Survival margin calculations
- ✅ Multi-destination optimization

---

**Built with ❤️ for Agri-Tech & Smart Logistics**
