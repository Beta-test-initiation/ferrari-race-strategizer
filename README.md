# Ferrari F1 Startegizer

A **data-driven Strategy Maker** for Ferrari Formula 1 team performance optimization. This project collects, processes, and analyzes real F1 telemetry data to provide insights into tire strategy decisions.

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

### Analysis & Visualization
- **Degradation Rate Analysis**: Compound-specific tire wear patterns
- **Temperature Correlation**: Track temperature impact on tire performance
- **Track Comparison**: Performance variations across different circuits
- **Ferrari Benchmarking**: Comparison against competitor tire strategies



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
python3 scripts/get_data.py

# Step 2: Collect weather data for race locations
python3 scripts/fetch_weather.py

# Step 3: Process raw data into tire degradation metrics
python3 scripts/preprocess_stints.py

# Step 4: Merge weather data with stint analysis
python3 scripts/merge_weather_into_stints.py
```


## License

This project is for educational and analytical purposes. F1 data usage complies with FastF1 API terms of service.

