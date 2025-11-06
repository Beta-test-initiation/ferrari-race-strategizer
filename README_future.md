# Ferrari F1 Tire Strategy Analysis

A **data-driven tire degradation analysis system** for Ferrari Formula 1 team performance optimization. This project collects, processes, and analyzes real F1 telemetry data to provide insights into tire strategy decisions.

---

## Overview

This system analyzes Ferrari's tire performance using real race data from the 2025 F1 season, focusing on:

- **Tire degradation patterns** across different compounds
- **Optimal stint lengths** for each tire compound
- **Track temperature impact** on tire performance
- **Ferrari performance benchmarking** against competitors
- **Track-specific strategy insights**

---

## Current Capabilities

### Data Collection
- **F1 Telemetry Data**: Lap times, pit stops, and stint information via FastF1 API
- **Weather Data**: Historical track conditions via Visual Crossing API
- **2025 Season Focus**: Analysis of Hamilton (HAM) and Leclerc (LEC) performance

### Data Processing
- **Stint-level Analysis**: Tire degradation rate calculation using linear regression
- **Weather Integration**: Temperature correlation with tire wear patterns
- **Feature Engineering**: Performance metrics for strategic decision making

### Machine Learning Models
- **Tire Degradation Predictor**: Random Forest model for predicting tire wear rates
- **Performance Evaluation**: Comprehensive model testing with 0.06 sec/lap average error
- **Risk Assessment**: Confidence intervals and uncertainty quantification
- **Strategic Insights**: Ferrari's optimal performance at 30-33°C with medium compounds

### Strategy Optimization
- **Pit Stop Optimization**: Intelligent pit window calculation and timing recommendations
- **Competitor Analysis**: Undercut/overcut risk assessment and strategic responses
- **Race Simulation**: Monte Carlo analysis for strategy validation
- **Real-time Decision Support**: Immediate "PIT NOW" vs "CONTINUE" recommendations
- **Scenario Analysis**: What-if analysis for different race conditions

### Interactive Dashboard
- **Professional Web Interface**: Ferrari-branded dashboard with real-time data visualization
- **Live Strategy Monitoring**: Real-time alerts, pit recommendations, and race status
- **Advanced Data Visualization**: Interactive charts for tire degradation and performance analysis
- **Multi-Component Dashboard**: Strategy overview, pit optimizer, race simulation, and weather impact
- **Responsive Design**: Optimized for desktop and mobile race operations

### Analysis & Visualization
- **Degradation Rate Analysis**: Compound-specific tire wear patterns
- **Temperature Correlation**: Track temperature impact on tire performance
- **Track Comparison**: Performance variations across different circuits
- **Ferrari Benchmarking**: Comparison against competitor tire strategies

---

## Project Structure

```
ferrari-strategy-maker/
├── scripts/                    # Data collection and processing pipeline
│   ├── get_data.py            # Collect F1 telemetry data (FastF1 API)
│   ├── fetch_weather.py       # Collect weather data (Visual Crossing API)
│   ├── preprocess_stints.py   # Process raw data into tire degradation metrics
│   └── merge_weather_into_stints.py  # Integrate weather data with stint analysis
├── notebooks/                 # Analysis and visualization scripts
│   ├── ferrari_tire_analysis.py      # Main Ferrari tire performance analysis
│   ├── degradation_vs_temp.py        # Temperature correlation analysis
│   ├── degradation_barplot.py        # Track comparison visualizations
│   └── README.md                      # Analysis documentation
├── ml/                        # Machine learning and strategy optimization
│   ├── models/                # Machine learning models
│   │   ├── __init__.py
│   │   └── degradation_predictor.py  # Tire degradation prediction model
│   ├── evaluation/            # Model evaluation and validation
│   │   └── model_evaluator.py        # Comprehensive model evaluation tools
│   ├── strategy/              # Strategy optimization engine
│   │   ├── __init__.py
│   │   ├── pit_optimizer.py          # Pit stop timing optimization
│   │   ├── race_simulator.py         # Monte Carlo race simulation
│   │   ├── strategy_engine.py        # Main strategy decision engine
│   │   ├── strategy_demo.py          # Complete system demonstration
│   │   └── README.md                 # Strategy system documentation
│   ├── saved_models/          # Trained ML models
│   ├── train_and_evaluate.py # Model training and evaluation pipeline
│   └── README.md              # ML system documentation
├── frontend/                  # Interactive web dashboard
│   ├── src/                   # React application source
│   │   ├── components/        # Dashboard components
│   │   │   ├── Header.tsx            # Ferrari-branded header
│   │   │   ├── LiveAlerts.tsx        # Real-time race alerts
│   │   │   ├── StrategyOverview.tsx  # Race status overview
│   │   │   ├── TireDegradationChart.tsx  # Tire performance visualization
│   │   │   ├── PitStopOptimizer.tsx  # Pit strategy recommendations
│   │   │   ├── RaceSimulation.tsx    # What-if scenario analysis
│   │   │   └── WeatherImpact.tsx     # Weather conditions and impact
│   │   ├── App.tsx            # Main application component
│   │   ├── main.tsx           # React entry point
│   │   └── index.css          # Global styles with Ferrari theme
│   ├── public/                # Static assets
│   ├── package.json           # Frontend dependencies
│   ├── tailwind.config.js     # Ferrari-themed styling configuration
│   ├── vite.config.ts         # Build configuration
│   └── README.md              # Frontend documentation
├── data/
│   ├── raw/                   # Raw F1 telemetry and weather data
│   │   ├── laps_2025.csv     # Lap-by-lap data
│   │   ├── stints_2025.csv   # Stint information
│   │   └── weather_2025.csv  # Weather conditions
│   └── processed/             # Processed analytical datasets
│       ├── tire_stints_2025.csv           # Tire degradation metrics
│       └── tire_stints_weather_2025.csv   # Combined stint + weather data
├── cache/                     # FastF1 API cache
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Setup & Installation

### 1. Clone and Setup Environment

```bash
git clone https://github.com/your-username/ferrari-strategy-maker.git
cd ferrari-strategy-maker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Access

Create a `.env` file in the project root:

```bash
# Required for weather data collection
VISUAL_CROSSING_API_KEY=your_visual_crossing_api_key_here
```

**Get your API key**: [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)

### 3. Run the Complete Analysis Pipeline

```bash
# Step 1: Collect F1 telemetry data
python scripts/get_data.py

# Step 2: Collect weather data for race locations
python scripts/fetch_weather.py

# Step 3: Process raw data into tire degradation metrics
python scripts/preprocess_stints.py

# Step 4: Merge weather data with stint analysis
python scripts/merge_weather_into_stints.py

# Step 5: Train machine learning models
python ml/train_and_evaluate.py

# Step 6: Run Ferrari tire analysis
python notebooks/ferrari_tire_analysis.py

# Step 7: Analyze temperature impact on tire degradation
python notebooks/degradation_vs_temp.py

# Step 8: Generate track comparison visualizations
python notebooks/degradation_barplot.py

# Step 9: Demo complete strategy optimization system
python ml/strategy/strategy_demo.py

# Step 10: Launch the interactive dashboard
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3000`

---

## Key Insights Generated

The analysis produces several strategic insights:

### 1. **Tire Degradation Rates**
- Compound-specific degradation patterns for Ferrari
- Comparison with competitor performance
- Optimal stint length recommendations

### 2. **Temperature Impact Analysis**
- Track temperature correlation with tire wear
- Compound performance variation across weather conditions
- Heat-sensitive strategy adjustments

### 3. **Track-Specific Performance**
- Circuit-by-circuit tire performance analysis
- Identification of Ferrari's strongest/weakest tracks
- Strategic recommendations for specific venues

### 4. **Competitive Benchmarking**
- Ferrari vs. competitor tire degradation rates
- Performance gaps identification
- Strategic advantage/disadvantage areas

### 5. **Machine Learning Predictions**
- Tire degradation rate predictions with 0.06 sec/lap average error
- Ferrari's optimal performance window: 30-33°C with medium compounds
- Risk assessment for different strategic scenarios
- Confidence intervals for prediction reliability

### 6. **Strategic Recommendations**
- Real-time pit stop timing optimization
- Competitor response analysis (undercut/overcut strategies)
- Race scenario simulation with Monte Carlo analysis
- Immediate decision support for race engineers

---

## Quick Start - Strategy Optimization

For immediate strategic recommendations, use the strategy optimization system:

```python
from ml.models.degradation_predictor import TireDegradationPredictor
from ml.strategy.strategy_engine import StrategyEngine

# Load trained model
predictor = TireDegradationPredictor()
predictor.load_model("ml/saved_models/ferrari_degradation_model.pkl")

# Create strategy engine
engine = StrategyEngine(predictor)

# Define current race situation
race_state = {
    'current_lap': 25,
    'position': 3,
    'tire_age': 20,
    'compound': 'MEDIUM',
    'track_temp': 35.0,
    'track_id': 1,
    'driver': 'HAM',
    'gaps_ahead': [2.1, 5.7],
    'gaps_behind': [3.2, 8.9]
}

# Get strategic recommendation
recommendation = engine.get_strategy_recommendation(race_state)

print(f"Immediate Action: {recommendation['immediate_action']['recommendation']}")
print(f"Optimal Pit Lap: {recommendation['optimal_strategy']['pit_lap']}")
print(f"Recommended Compound: {recommendation['optimal_strategy']['new_compound']}")
```

**Expected Output:**
```
Immediate Action: CONTINUE
Optimal Pit Lap: 28
Recommended Compound: MEDIUM
```

---

## Data Sources

- **F1 Telemetry**: [FastF1 API](https://github.com/theOehrly/FastF1) - Official F1 timing data
- **Weather Data**: [Visual Crossing API](https://www.visualcrossing.com/) - Historical weather conditions
- **Season Coverage**: 2025 F1 season races (updated as races occur)

---

## Technical Details

### Dependencies
- **FastF1**: F1 telemetry data collection
- **Pandas**: Data manipulation and analysis
- **Matplotlib/Seaborn**: Data visualization
- **Scikit-learn**: Linear regression for degradation modeling
- **Requests**: API communication

### Data Processing Pipeline
1. **Raw Data Collection**: FastF1 API provides lap times, pit stops, and stint data
2. **Degradation Calculation**: Linear regression on lap times vs. lap number per stint
3. **Weather Integration**: Historical weather data mapped to race locations
4. **Feature Engineering**: Performance metrics calculated for strategic analysis

---

## Future Enhancements

**Completed Features:**
- ✅ **Machine Learning Models**: Predictive tire degradation modeling
- ✅ **Strategy Optimization**: Pit stop timing and compound selection
- ✅ **Strategy Simulation**: What-if scenario modeling
- ✅ **Interactive Web Dashboard**: Ferrari-branded real-time dashboard with professional race interface

**Planned Features:**
- **Live Data Integration**: Real-time telemetry processing
- **Multi-team Analysis**: Extended analysis beyond Ferrari
- **Advanced Competitor Modeling**: Team-specific behavior prediction
- **Weather Radar Integration**: Dynamic condition updates

---

## Contributing

This project focuses on Ferrari F1 tire strategy analysis. Contributions welcome for:
- Additional data sources integration
- Advanced degradation modeling techniques
- Enhanced visualization capabilities
- Real-time data processing improvements

---

## License

This project is for educational and analytical purposes. F1 data usage complies with FastF1 API terms of service.
