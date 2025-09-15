# Ferrari F1 Strategy Optimization System

This package provides comprehensive race strategy optimization for Ferrari F1 team, combining machine learning predictions with strategic decision-making algorithms.

---

## Overview

The strategy optimization system transforms tire degradation predictions into actionable pit stop recommendations, considering track position, competitor moves, and race conditions.

### Key Components

1. **PitStopOptimizer** - Optimal pit window calculation
2. **RaceSimulator** - Monte Carlo race scenario simulation  
3. **StrategyEngine** - Comprehensive strategic decision support

---

## Quick Start

### Basic Usage

```python
from ml.models.degradation_predictor import TireDegradationPredictor
from ml.strategy.strategy_engine import StrategyEngine

# Load trained model
predictor = TireDegradationPredictor()
predictor.load_model("ml/saved_models/ferrari_degradation_model.pkl")

# Create strategy engine
engine = StrategyEngine(predictor)

# Define current race state
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

print(f"Optimal pit lap: {recommendation['optimal_strategy']['pit_lap']}")
print(f"Recommended compound: {recommendation['optimal_strategy']['new_compound']}")
```

### Run Complete Demo

```bash
python ml/strategy/strategy_demo.py
```

---

## Strategic Capabilities

### 1. Pit Stop Optimization

**What it does:**
- Calculates optimal pit stop timing
- Recommends tire compound selection
- Evaluates position change impact
- Assesses risk levels

**Key outputs:**
- Optimal pit lap
- Expected final position
- Time loss breakdown
- Risk assessment

### 2. Competitor Analysis

**What it analyzes:**
- Undercut risk from cars behind
- Overcut opportunity vs cars ahead
- Optimal response to competitor moves
- Pit stop probability estimation

**Strategic insights:**
- When to cover defensive position
- When to attack with undercut
- How to respond to competitor strategies

### 3. Real-time Decision Support

**Immediate recommendations:**
- "PIT NOW" vs "CONTINUE" decisions
- Remaining stint length estimates
- Current degradation rate monitoring
- Risk level assessment

### 4. Scenario Analysis

**What-if scenarios:**
- Track temperature changes
- Safety car situations
- Competitor pit stops
- Weather condition changes

---

## Strategic Framework

### Decision Hierarchy

1. **Immediate Action** (Current lap decisions)
   - Emergency pit stops
   - Tire failure responses
   - Safety car reactions

2. **Optimal Strategy** (Medium-term planning)
   - Planned pit windows
   - Compound sequences
   - Position optimization

3. **Alternative Strategies** (Contingency planning)
   - Multiple strategic options
   - Risk/reward analysis
   - Flexibility assessment

### Risk Assessment

**Risk Factors:**
- Tire degradation predictability
- Position loss potential
- Stint length extremes
- Timing uncertainties

**Risk Levels:**
- **LOW**: High confidence, proven strategy
- **MEDIUM**: Moderate uncertainty, monitor closely
- **HIGH**: Significant risk, consider alternatives

---

## Real-World Application

### Pre-Race Strategy

```python
# Analyze different strategic options before race
strategies = [
    {'pit_laps': [25], 'compounds': ['MEDIUM', 'HARD']},      # 1-stop
    {'pit_laps': [18, 38], 'compounds': ['MEDIUM', 'MEDIUM', 'SOFT']},  # 2-stop
]

for strategy in strategies:
    # Evaluate each strategy option
    evaluation = optimizer.evaluate_single_strategy(...)
    print(f"Strategy: {strategy}")
    print(f"Expected race time: {evaluation['expected_race_time']}")
```

### During Race Decisions

```python
# Real-time strategy updates during race
current_state = get_current_race_state()  # From telemetry
recommendation = engine.get_strategy_recommendation(current_state)

if recommendation['decision_urgency'] == 'IMMEDIATE':
    action = recommendation['immediate_action']
    send_to_pit_wall(action['recommendation'])
```

### Post-Race Analysis

```python
# Analyze strategy effectiveness after race
actual_strategy = get_executed_strategy()
alternative_strategies = get_alternative_options()

# Compare what was done vs optimal strategy
comparison = simulator.compare_strategies(
    race_config, [actual_strategy] + alternative_strategies
)
```

---

## Strategic Insights from Ferrari's Model

Based on the tire degradation model evaluation:

### Optimal Conditions for Ferrari
- **Temperature Range**: 30-33°C (lowest prediction error)
- **Best Compound**: Medium tires
- **Optimal Tracks**: Bahrain, Spain, Hungary, Miami

### Strategic Advantages
1. **Predictable degradation** in warm conditions
2. **Medium compound mastery** 
3. **Temperature-stint optimization**
4. **Consistent performance** in 30-33°C range

### Risk Areas
1. **Cold conditions** (15-19°C) - high uncertainty
2. **Soft compound performance** - limited data
3. **Temperature extremes** - reduced model accuracy

---

## Integration with Race Operations

### Pit Wall Communication

```python
# Generate concise pit wall messages
def generate_pit_wall_message(recommendation):
    optimal = recommendation['optimal_strategy']
    return f"HAM: Pit lap {optimal['pit_lap']} for {optimal['new_compound']}. Risk: {optimal['risk_level']}"
```

### Driver Feedback Integration

```python
# Incorporate driver tire condition feedback
def update_strategy_with_feedback(current_strategy, driver_feedback):
    if driver_feedback['tire_condition'] == 'POOR':
        # Adjust pit timing earlier
        current_strategy['pit_lap'] = max(current_lap + 2, current_strategy['pit_lap'] - 3)
    return current_strategy
```

### Telemetry Integration

```python
# Real-time telemetry updates
def process_telemetry_update(telemetry_data):
    updated_state = {
        'current_lap': telemetry_data['lap'],
        'tire_age': telemetry_data['stint_length'],
        'track_temp': telemetry_data['track_temperature'],
        'position': telemetry_data['position'],
        'gaps': telemetry_data['time_gaps']
    }
    return engine.get_strategy_recommendation(updated_state)
```

---

## Performance Optimization

### Strategy Evaluation Speed

- **Quick recommendations**: <1 second
- **Full optimization**: 2-5 seconds  
- **Scenario analysis**: 10-30 seconds
- **Monte Carlo simulation**: 1-5 minutes

### Accuracy Metrics

Based on Ferrari 2025 data:
- **Prediction accuracy**: 0.06 sec/lap average error
- **Optimal temperature**: 30-33°C (0.23 sec/lap error)
- **Model confidence**: R² = 0.58 overall

---

## Advanced Features

### Monte Carlo Simulation

```python
# Probabilistic strategy analysis
simulation_results = simulator.simulate_strategy(
    race_config=race_config,
    ferrari_strategy=strategy,
    competitor_strategies=competitors,
    num_simulations=1000
)

print(f"Podium probability: {simulation_results['podium_probability']:.1%}")
print(f"Average finish: P{simulation_results['average_finish_position']:.1f}")
```

### Multi-Scenario Optimization

```python
# Optimize across multiple race scenarios
scenarios = [
    {'name': 'Normal', 'safety_car_prob': 0.15},
    {'name': 'Chaotic', 'safety_car_prob': 0.40},
    {'name': 'Hot', 'track_temp': 45.0}
]

best_strategy = find_robust_strategy(scenarios)
```

---

## Future Enhancements

### Planned Features
1. **Live data integration** - Real-time telemetry processing
2. **Machine learning updates** - Online model improvement
3. **Advanced competitor modeling** - Team-specific behavior prediction
4. **Weather radar integration** - Dynamic condition updates

### Research Areas
1. **Deep reinforcement learning** for strategic sequences
2. **Multi-objective optimization** balancing position vs points
3. **Uncertainty quantification** for decision confidence
4. **Driver-specific modeling** for personalized strategies

---

## Troubleshooting

### Common Issues

**Model not found:**
```bash
# Train new model
python ml/train_and_evaluate.py
```

**Import errors:**
```python
# Ensure project root in Python path
import sys
sys.path.append('/path/to/ferrari-strategy-maker')
```

**Data not available:**
```bash
# Run data collection pipeline
python scripts/get_data.py
python scripts/fetch_weather.py
python scripts/preprocess_stints.py
python scripts/merge_weather_into_stints.py
```

### Performance Issues

- **Slow predictions**: Check model size and feature complexity
- **Memory usage**: Reduce Monte Carlo simulation count
- **Accuracy concerns**: Retrain with more recent data

---

## Example Outputs

### Strategic Recommendation Output

```
IMMEDIATE ACTION: CONTINUE
  Reasoning: Degradation still manageable (0.0234 sec/lap)
  Laps remaining: 12

OPTIMAL STRATEGY:
  Pit on lap: 28
  New compound: MEDIUM
  Expected position: P3
  Risk level: LOW
  Reasoning: Pit on lap 28 for MEDIUM compound. Expected total time loss: 24.3 seconds. Should maintain or gain 0 positions. Low risk strategy with high success probability.

RISK ASSESSMENT:
  Overall risk: LOW
  Decision urgency: MEDIUM

COMPETITOR ANALYSIS:
  Undercut risk: MEDIUM
  Overcut opportunity: LOW
  Optimal response: Pit at optimal window regardless of competitors
```

