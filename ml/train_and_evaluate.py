#!/usr/bin/env python3
"""
Ferrari F1 Strategy Maker - Model Training and Evaluation Script

This script demonstrates the complete ML workflow:
1. Train the tire degradation prediction model
2. Make strategic predictions
3. Evaluate model performance
4. Generate comprehensive reports

Usage:
    python ml/train_and_evaluate.py
"""

import os
import sys
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.models.degradation_predictor import TireDegradationPredictor
from ml.evaluation.model_evaluator import ModelEvaluator


def main():
    """
    Main workflow for training and evaluating the Ferrari tire degradation model.
    """
    print("Ferrari F1 Strategy Maker - ML Model Training & Evaluation")
    print("=" * 70)
    
    # Configuration
    DATA_PATH = "data/processed/tire_stints_weather_2025.csv"
    MODEL_SAVE_PATH = "ml/saved_models/ferrari_degradation_model.pkl"
    EVALUATION_REPORT_PATH = "ml/evaluation/model_evaluation_report.txt"
    
    # Create directories if they don't exist
    os.makedirs("ml/saved_models", exist_ok=True)
    os.makedirs("ml/evaluation", exist_ok=True)
    
    # Check if data file exists
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found: {DATA_PATH}")
        print("Please run the data collection pipeline first:")
        print("1. python scripts/get_data.py")
        print("2. python scripts/fetch_weather.py")
        print("3. python scripts/preprocess_stints.py")
        print("4. python scripts/merge_weather_into_stints.py")
        return
    
    # Step 1: Train the Model
    print("\nStep 1: Training Tire Degradation Prediction Model")
    print("-" * 50)
    
    predictor = TireDegradationPredictor()
    
    try:
        # Train the model
        training_metrics = predictor.train(DATA_PATH)
        
        # Save the trained model
        predictor.save_model(MODEL_SAVE_PATH)
        
        print(f"Model training completed successfully!")
        print(f"Model saved to: {MODEL_SAVE_PATH}")
        
    except Exception as e:
        print(f"Model training failed: {e}")
        return
    
    # Step 2: Make Strategic Predictions
    print("\nStep 2: Strategic Prediction Examples")
    print("-" * 50)
    
    # Example 1: Compare tire compounds for a hot race
    print("\nExample 1: Compound Comparison for Italy")
    print("   Conditions: 44°C track temperature, 32-lap stint")
    
    compounds = ["SOFT", "MEDIUM", "HARD"]
    monaco_track_id = 16  # Monaco is typically round 6
    
    for compound in compounds:
        prediction = predictor.predict_degradation(
            track_temp=44.0,
            compound=compound,
            stint_length=25,
            track_id=monaco_track_id,
            driver="LEC"
        )
        
        print(f"   {compound:6s}: {prediction['degradation_rate']:.4f} sec/lap "
              f"({prediction['risk_level']} risk)")
    
    # Example 2: Optimal stint length analysis
    print("\nExample 2: Optimal Stint Length Analysis")
    print(" Conditions: Medium tires, 40°C track temperature")
    
    stint_analysis = predictor.predict_stint_performance(
        track_temp=40.0,
        compound="MEDIUM",
        max_stint_length=40,
        track_id=16,
        driver="LEC"
    )
    
    # Find optimal stint length (minimize total time loss)
    optimal_stint = stint_analysis.loc[stint_analysis['total_time_loss'].idxmin()]
    print(f"   Optimal stint length: {optimal_stint['stint_length']} laps")
    print(f"   Expected degradation: {optimal_stint['degradation_rate']:.4f} sec/lap")
    print(f"   Total time loss: {optimal_stint['total_time_loss']:.2f} seconds")
    
    # Example 3: Risk assessment for aggressive strategy
    print("\nExample 3: Risk Assessment - Aggressive Strategy")
    print("   Conditions: Soft tires, 48°C track temperature, 35-lap stint")
    
    risky_prediction = predictor.predict_degradation(
        track_temp=48.0,
        compound="SOFT",
        stint_length=35,
        track_id=4,  # Example: Bahrain (hot race)
        driver="LEC"
    )
    
    print(f"   Predicted degradation: {risky_prediction['degradation_rate']:.4f} sec/lap")
    print(f"   Risk level: {risky_prediction['risk_level']}")
    print(f"   Confidence interval: {risky_prediction['confidence_interval']['lower']:.4f} - "
          f"{risky_prediction['confidence_interval']['upper']:.4f} sec/lap")
    
    if risky_prediction['risk_level'] == 'HIGH':
        print("   WARNING: High-risk strategy detected!")
        print("   Recommendation: Consider shorter stint or harder compound")
    
    # Step 3: Comprehensive Model Evaluation
    print("\nStep 3: Model Performance Evaluation")
    print("-" * 50)
    
    try:
        # Create model evaluator
        evaluator = ModelEvaluator(predictor, DATA_PATH)
        
        # Generate comprehensive evaluation report
        print("Generating comprehensive evaluation report...")
        evaluation_report = evaluator.generate_evaluation_report(EVALUATION_REPORT_PATH)
        
        # Print key metrics
        metrics, y_true, y_pred = evaluator.evaluate_model_performance()
        
        print(f"\nKey Performance Metrics:")
        print(f"   • Mean Absolute Error: {metrics['mae']:.4f} sec/lap")
        print(f"   • R² Score: {metrics['r2']:.4f}")
        print(f"   • Test Samples: {metrics['n_samples']}")
        print(f"   • 90th Percentile Error: {metrics['prediction_accuracy_90']:.4f} sec/lap")
        
        # Evaluate performance by compound
        print("\nPerformance by Tire Compound:")
        compound_results = evaluator.evaluate_by_compound()
        if not compound_results.empty:
            for _, row in compound_results.iterrows():
                print(f"   • {row['Compound']:6s}: MAE = {row['MAE']:.4f} sec/lap, "
                      f"R² = {row['R2']:.3f} (n={row['Sample_Size']})")
        
        # Evaluate performance by temperature
        print("\nPerformance by Temperature Range:")
        temp_results = evaluator.evaluate_by_temperature()
        if not temp_results.empty:
            for _, row in temp_results.iterrows():
                print(f"   • {row['Min_Temp']:.1f}-{row['Max_Temp']:.1f}°C: "
                      f"MAE = {row['MAE']:.4f} sec/lap, R² = {row['R2']:.3f}")
        
        # Feature importance
        print("\nTop 5 Most Important Features:")
        feature_importance = predictor.get_feature_importance()
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        for i, (feature, importance) in enumerate(sorted_features[:5]):
            print(f"   {i+1}. {feature}: {importance:.4f}")
        
        print(f"\nEvaluation complete! Full report saved to: {EVALUATION_REPORT_PATH}")
        
        # Create visualizations
        print("\nGenerating performance visualizations...")
        evaluator.plot_prediction_accuracy(y_true, y_pred, 
                                         save_path="ml/evaluation/prediction_accuracy.png")
        evaluator.plot_feature_importance(save_path="ml/evaluation/feature_importance.png")
        
        print("Visualizations saved to ml/evaluation/")
        
    except Exception as e:
        print(f"Model evaluation failed: {e}")
        return
    
    # Step 4: Strategic Recommendations
    print("\nStep 4: Strategic Recommendations")
    print("-" * 50)
    
    print("\nKey Strategic Insights:")
    
    # Analyze model performance to provide strategic guidance
    if metrics['mae'] < 0.03:
        print("   Model shows excellent predictive accuracy")
        print("   Recommendation: Use for real-time strategy decisions")
    elif metrics['mae'] < 0.05:
        print("   Model shows good predictive accuracy")
        print("   Recommendation: Use as strategic guidance with caution")
    else:
        print("   Model needs improvement")
        print("   Recommendation: Collect more data and retrain")
    
    # Temperature sensitivity analysis
    if not temp_results.empty:
        high_temp_performance = temp_results[temp_results['Max_Temp'] > 45]
        if not high_temp_performance.empty:
            avg_high_temp_error = high_temp_performance['MAE'].mean()
            print(f"\nHigh Temperature Performance:")
            print(f"   • Average error in hot conditions: {avg_high_temp_error:.4f} sec/lap")
            if avg_high_temp_error > metrics['mae'] * 1.5:
                print("   Model less accurate in hot conditions")
                print("   Recommendation: Extra caution for hot races")
    
    # Compound-specific insights
    if not compound_results.empty:
        best_compound = compound_results.loc[compound_results['R2'].idxmax()]
        print(f"\nCompound Analysis:")
        print(f"   • Best predicted compound: {best_compound['Compound']}")
        print(f"   • R² score: {best_compound['R2']:.3f}")
        
        worst_compound = compound_results.loc[compound_results['R2'].idxmin()]
        if worst_compound['R2'] < 0.5:
            print(f"   Limited accuracy for {worst_compound['Compound']} compound")
            print(f"   Recommendation: Gather more data for this compound")
    
    print("\nModel Training and Evaluation Complete!")
    print("=" * 70)
    print("Next steps:")
    print("1. Review the evaluation report and visualizations")
    print("2. Use the trained model for strategic analysis")
    print("3. Integrate predictions into race strategy workflow")
    print("4. Continuously retrain with new race data")


if __name__ == "__main__":
    main() 