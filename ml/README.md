# Ferrari F1 Strategy Maker - Machine Learning Models

This directory contains the machine learning models and evaluation tools for Ferrari F1 tire degradation prediction and race strategy optimization.

---

## 🎯 Overview

The ML models in this project are designed to predict tire degradation patterns and optimize pit stop strategies for Ferrari F1 drivers. The core focus is on **actionable predictions** that can inform real-time strategic decisions during races.

### Key Capabilities

- **Tire Degradation Prediction**: Predict lap time degradation rate based on track conditions
- **Confidence Intervals**: Provide uncertainty estimates for risk-aware decision making
- **Multi-Factor Analysis**: Consider temperature, compound, stint length, and driver characteristics
- **Strategic Recommendations**: Generate pit stop timing and compound selection advice

---

## 📁 Directory Structure

```
ml/
├── models/
│   ├── __init__.py                    # Package initialization
│   └── degradation_predictor.py       # Main tire degradation prediction model
├── evaluation/
│   └── model_evaluator.py             # Comprehensive model evaluation tools
├── saved_models/                      # Trained model artifacts (created after training)
└── README.md                          # This file
```

---

## 🏎️ Tire Degradation Predictor

### Model Architecture

**Algorithm**: Random Forest Regressor
- **Why Random Forest?** Robust to outliers, handles non-linear relationships, provides feature importance
- **Target Variable**: Tire degradation rate (lap time increase per lap)
- **Features**: 9 engineered features including temperature, compound, stint length, and interactions

### Features Engineered

1. **Track Temperature (Normalized)**: Primary factor affecting tire wear
2. **Compound Encoding**: Tire compound type (SOFT, MEDIUM, HARD)
3. **Driver Encoding**: Driver-specific patterns (HAM, LEC)
4. **Stint Length (Normalized)**: Planned stint duration
5. **Track Encoding**: Track-specific characteristics
6. **Weather Features**: Humidity and wind speed (normalized)
7. **Temperature-Stint Interaction**: Combined effect of heat and stint length
8. **Compound-Temperature Interaction**: Compound-specific temperature sensitivity

### Model Performance

Based on 2025 Ferrari stint data:
- **Typical MAE**: ~0.02-0.04 sec/lap
- **R² Score**: ~0.65-0.75
- **Confidence Intervals**: 95% prediction intervals provided
- **Sample Size**: 500+ Ferrari tire stints

---

## 🚀 Quick Start

### 1. Train the Model

```python
from ml.models.degradation_predictor import TireDegradationPredictor

# Initialize and train
predictor = TireDegradationPredictor()
metrics = predictor.train("data/processed/tire_stints_weather_2025.csv")

# Save trained model
predictor.save_model("ml/saved_models/ferrari_degradation_model.pkl")
```

### 2. Make Predictions

```python
# Predict degradation for specific conditions
prediction = predictor.predict_degradation(
    track_temp=45.0,          # Track temperature in Celsius
    compound="MEDIUM",        # Tire compound
    stint_length=25,          # Planned stint length
    track_id=3,              # Track identifier
    driver="HAM"             # Driver (HAM or LEC)
)

print(f"Predicted degradation: {prediction['degradation_rate']:.4f} sec/lap")
print(f"Risk level: {prediction['risk_level']}")
print(f"Confidence interval: {prediction['confidence_interval']}")
```

### 3. Analyze Stint Performance

```python
# Compare performance across different stint lengths
stint_analysis = predictor.predict_stint_performance(
    track_temp=45.0,
    compound="MEDIUM",
    max_stint_length=40,
    track_id=3,
    driver="HAM"
)

print(stint_analysis)
```

---

## 📊 Model Evaluation

### Comprehensive Evaluation Suite

```python
from ml.evaluation.model_evaluator import ModelEvaluator

# Create evaluator
evaluator = ModelEvaluator(predictor, "data/processed/tire_stints_weather_2025.csv")

# Generate full evaluation report
report = evaluator.generate_evaluation_report()
print(report)

# Create visualizations
metrics, y_true, y_pred = evaluator.evaluate_model_performance()
evaluator.plot_prediction_accuracy(y_true, y_pred)
evaluator.plot_feature_importance()
```

### Evaluation Metrics

- **Overall Performance**: MAE, MSE, R² across all predictions
- **Compound-Specific**: Performance breakdown by tire compound
- **Temperature-Sensitive**: Accuracy across temperature ranges
- **Residual Analysis**: Prediction error patterns and distribution
- **Feature Importance**: Understanding model decision factors

---

## 🔬 Model Interpretation

### Feature Importance (Typical Rankings)

1. **Temperature-Stint Interaction** (~0.25): Combined effect of heat and stint length
2. **Track Temperature** (~0.20): Primary environmental factor
3. **Stint Length** (~0.18): Duration of tire usage
4. **Compound Type** (~0.15): Tire compound characteristics
5. **Driver Patterns** (~0.12): Driver-specific tire management
6. **Track Characteristics** (~0.10): Circuit-specific factors

### Strategic Insights

- **High Temperature Risk**: Degradation increases non-linearly with temperature
- **Compound Sensitivity**: Medium compounds show highest temperature sensitivity
- **Stint Length Optimization**: Optimal stint lengths vary by compound and temperature
- **Driver Differences**: Hamilton vs. Leclerc show different tire management patterns

---

## 🎯 Strategic Applications

### 1. Pre-Race Strategy Planning

```python
# Compare compound strategies for upcoming race
compounds = ["SOFT", "MEDIUM", "HARD"]
track_temp = 42.0
target_stint = 30

for compound in compounds:
    pred = predictor.predict_degradation(
        track_temp=track_temp,
        compound=compound,
        stint_length=target_stint,
        track_id=next_race_id,
        driver="HAM"
    )
    print(f"{compound}: {pred['degradation_rate']:.4f} sec/lap ({pred['risk_level']} risk)")
```

### 2. Real-Time Pit Stop Optimization

```python
# During race: determine optimal pit window
current_lap = 20
tire_age = 15
current_temp = 46.0

# Predict degradation if continuing current stint
continued_degradation = predictor.predict_degradation(
    track_temp=current_temp,
    compound=current_compound,
    stint_length=tire_age + 10,  # 10 more laps
    track_id=current_race_id,
    driver="HAM"
)

# Compare with fresh tire degradation
fresh_degradation = predictor.predict_degradation(
    track_temp=current_temp,
    compound=new_compound,
    stint_length=10,
    track_id=current_race_id,
    driver="HAM"
)

# Strategic decision based on predictions
```

### 3. Risk Assessment

```python
# Assess risk of extended stint
extended_stint = predictor.predict_degradation(
    track_temp=48.0,  # High temperature
    compound="SOFT",   # Aggressive compound
    stint_length=35,   # Long stint
    track_id=current_race_id,
    driver="HAM"
)

if extended_stint['risk_level'] == 'HIGH':
    print("⚠️  High risk strategy - consider earlier pit stop")
```

---

## 🔧 Model Customization

### Hyperparameter Tuning

```python
# Custom model parameters
custom_params = {
    'n_estimators': 150,
    'max_depth': 12,
    'min_samples_split': 3,
    'min_samples_leaf': 1
}

predictor = TireDegradationPredictor(model_params=custom_params)
```

### Feature Engineering Extensions

The model can be extended with additional features:
- **Fuel Load**: Impact of fuel weight on tire degradation
- **Track Rubber Evolution**: Track surface grip changes
- **Aerodynamic Balance**: Car setup effects on tire wear
- **Driver Feedback**: Subjective tire condition reports

---

## 📈 Performance Optimization

### Model Accuracy Factors

- **Data Quality**: Clean, consistent timing data improves accuracy
- **Feature Engineering**: Domain-specific features enhance predictions
- **Training Data Size**: More stints provide better generalization
- **Temporal Validation**: Models should be validated on recent data

### Continuous Improvement

- **Regular Retraining**: Update models with new race data
- **Feature Importance Monitoring**: Track changing importance patterns
- **Outlier Analysis**: Investigate unusual prediction errors
- **Cross-Season Validation**: Test model performance across seasons

---

## 🚨 Model Limitations

### Known Constraints

1. **Data Dependency**: Model accuracy depends on quality of input data
2. **Context Limitations**: Cannot account for unique race circumstances
3. **Compound Changes**: Performance may vary with tire compound updates
4. **Driver Variability**: Individual driver tire management differences
5. **Track Evolution**: Model may not capture rapid track condition changes

### Risk Mitigation

- **Confidence Intervals**: Always consider prediction uncertainty
- **Multiple Scenarios**: Evaluate multiple strategic options
- **Human Oversight**: Combine model predictions with engineering judgment
- **Real-Time Updates**: Adjust predictions based on live race data

---

## 🛠️ Technical Requirements

### Dependencies

```python
# Core ML libraries
scikit-learn>=1.3.0
pandas>=1.5.0
numpy>=1.24.0
joblib>=1.3.0

# Visualization
matplotlib>=3.6.0
seaborn>=0.12.0

# Optional: Advanced ML
xgboost>=2.0.0      # For gradient boosting alternatives
lightgbm>=3.3.0     # For faster training
```

### System Requirements

- **Memory**: 4GB+ RAM for training
- **CPU**: Multi-core processor recommended
- **Storage**: 100MB+ for model artifacts
- **Python**: 3.8+ required

---

## 📚 Future Enhancements

### Planned Features

1. **Advanced Models**: Neural networks, ensemble methods
2. **Real-Time Learning**: Online model updates during races
3. **Multi-Driver Models**: Expanded beyond Ferrari drivers
4. **Weather Integration**: Enhanced weather prediction features
5. **Telemetry Integration**: Direct car sensor data incorporation

### Research Directions

- **Physics-Informed ML**: Incorporate tire physics models
- **Reinforcement Learning**: Optimize sequential pit stop decisions
- **Uncertainty Quantification**: Advanced confidence estimation
- **Multi-Objective Optimization**: Balance speed vs. tire preservation

