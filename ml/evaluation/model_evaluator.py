"""
Model Evaluation Utilities for Ferrari F1 Strategy Maker

This module provides comprehensive evaluation tools for the tire degradation
prediction model, including performance metrics, visualization, and validation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    """
    Comprehensive evaluation suite for tire degradation prediction models.
    
    Provides detailed performance analysis, visualization, and validation
    metrics to assess model quality and reliability.
    """
    
    def __init__(self, model, test_data_path):
        """
        Initialize model evaluator.
        
        Args:
            model: Trained TireDegradationPredictor instance
            test_data_path (str): Path to test data CSV
        """
        self.model = model
        self.test_data = pd.read_csv(test_data_path)
        self.ferrari_drivers = ['HAM', 'LEC']
        
    def evaluate_model_performance(self):
        """
        Evaluate overall model performance on test data.
        
        Returns:
            dict: Comprehensive performance metrics
        """
        # Filter for Ferrari drivers
        ferrari_data = self.test_data[
            self.test_data['Driver'].isin(self.ferrari_drivers)
        ].copy()
        
        # Prepare features using model's method
        processed_data = self.model.prepare_features(ferrari_data)
        
        if processed_data.empty:
            raise ValueError("No valid test data available")
        
        X_test = processed_data[self.model.feature_names]
        y_true = processed_data['LapTimeSlope']
        
        # Make predictions
        y_pred = self.model.model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred),
            'n_samples': len(y_true)
        }
        
        # Additional metrics
        residuals = y_true - y_pred
        metrics.update({
            'residual_mean': np.mean(residuals),
            'residual_std': np.std(residuals),
            'median_absolute_error': np.median(np.abs(residuals)),
            'prediction_accuracy_90': np.percentile(np.abs(residuals), 90)
        })
        
        return metrics, y_true, y_pred
    
    def plot_prediction_accuracy(self, y_true, y_pred, save_path=None):
        """
        Create comprehensive prediction accuracy visualizations.
        
        Args:
            y_true (array): True degradation rates
            y_pred (array): Predicted degradation rates
            save_path (str): Optional path to save plots
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Predicted vs Actual
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6, color='red')
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'k--', lw=2)
        axes[0, 0].set_xlabel('Actual Degradation Rate (sec/lap)')
        axes[0, 0].set_ylabel('Predicted Degradation Rate (sec/lap)')
        axes[0, 0].set_title('Ferrari Tire Degradation: Predicted vs Actual')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add R² to plot
        r2 = r2_score(y_true, y_pred)
        axes[0, 0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[0, 0].transAxes,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Plot 2: Residuals
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6, color='blue')
        axes[0, 1].axhline(y=0, color='k', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Degradation Rate (sec/lap)')
        axes[0, 1].set_ylabel('Residuals (sec/lap)')
        axes[0, 1].set_title('Residual Plot')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Residual Distribution
        axes[1, 0].hist(residuals, bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].set_xlabel('Residuals (sec/lap)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residual Distribution')
        axes[1, 0].axvline(x=0, color='red', linestyle='--')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Error by Prediction Value
        abs_errors = np.abs(residuals)
        axes[1, 1].scatter(y_pred, abs_errors, alpha=0.6, color='purple')
        axes[1, 1].set_xlabel('Predicted Degradation Rate (sec/lap)')
        axes[1, 1].set_ylabel('Absolute Error (sec/lap)')
        axes[1, 1].set_title('Absolute Error vs Prediction')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def evaluate_by_compound(self):
        """
        Evaluate model performance by tire compound.
        
        Returns:
            DataFrame: Performance metrics by compound
        """
        ferrari_data = self.test_data[
            self.test_data['Driver'].isin(self.ferrari_drivers)
        ].copy()
        
        results = []
        
        for compound in ferrari_data['Compound'].unique():
            compound_data = ferrari_data[ferrari_data['Compound'] == compound]
            
            if len(compound_data) < 5:  # Skip if insufficient data
                continue
                
            # Generate predictions for this compound
            predictions = []
            actuals = []
            
            for _, row in compound_data.iterrows():
                try:
                    pred = self.model.predict_degradation(
                        track_temp=row.get('TrackTemp', 35.0),
                        compound=compound,
                        stint_length=row['StintLength'],
                        track_id=row['Round'],
                        driver=row['Driver']
                    )
                    predictions.append(pred['degradation_rate'])
                    actuals.append(row['LapTimeSlope'])
                except:
                    continue
            
            if len(predictions) > 0:
                mae = mean_absolute_error(actuals, predictions)
                r2 = r2_score(actuals, predictions)
                
                results.append({
                    'Compound': compound,
                    'Sample_Size': len(predictions),
                    'MAE': mae,
                    'R2': r2,
                    'Avg_Actual': np.mean(actuals),
                    'Avg_Predicted': np.mean(predictions)
                })
        
        return pd.DataFrame(results)
    
    def evaluate_by_temperature(self, temp_bins=5):
        """
        Evaluate model performance across temperature ranges.
        
        Args:
            temp_bins (int): Number of temperature bins to create
            
        Returns:
            DataFrame: Performance metrics by temperature range
        """
        ferrari_data = self.test_data[
            self.test_data['Driver'].isin(self.ferrari_drivers)
        ].copy()
        
        # Create temperature bins
        ferrari_data['Temp_Bin'] = pd.cut(
            ferrari_data['TrackTemp'], 
            bins=temp_bins, 
            labels=[f'Bin_{i+1}' for i in range(temp_bins)]
        )
        
        results = []
        
        for temp_bin in ferrari_data['Temp_Bin'].unique():
            if pd.isna(temp_bin):
                continue
                
            bin_data = ferrari_data[ferrari_data['Temp_Bin'] == temp_bin]
            
            if len(bin_data) < 5:
                continue
            
            # Generate predictions for this temperature range
            predictions = []
            actuals = []
            
            for _, row in bin_data.iterrows():
                try:
                    pred = self.model.predict_degradation(
                        track_temp=row['TrackTemp'],
                        compound=row['Compound'],
                        stint_length=row['StintLength'],
                        track_id=row['Round'],
                        driver=row['Driver']
                    )
                    predictions.append(pred['degradation_rate'])
                    actuals.append(row['LapTimeSlope'])
                except:
                    continue
            
            if len(predictions) > 0:
                mae = mean_absolute_error(actuals, predictions)
                r2 = r2_score(actuals, predictions)
                
                results.append({
                    'Temperature_Range': temp_bin,
                    'Min_Temp': bin_data['TrackTemp'].min(),
                    'Max_Temp': bin_data['TrackTemp'].max(),
                    'Sample_Size': len(predictions),
                    'MAE': mae,
                    'R2': r2,
                    'Avg_Actual': np.mean(actuals),
                    'Avg_Predicted': np.mean(predictions)
                })
        
        return pd.DataFrame(results)
    
    def plot_feature_importance(self, save_path=None):
        """
        Visualize feature importance from the trained model.
        
        Args:
            save_path (str): Optional path to save the plot
        """
        if not self.model.is_trained:
            raise ValueError("Model must be trained to plot feature importance")
        
        feature_importance = self.model.get_feature_importance()
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        features, importance = zip(*sorted_features)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        bars = plt.barh(range(len(features)), importance, color='darkred', alpha=0.7)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title('Ferrari Tire Degradation Model - Feature Importance')
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, (feature, imp) in enumerate(sorted_features):
            plt.text(imp + 0.005, i, f'{imp:.3f}', va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_evaluation_report(self, save_path=None):
        """
        Generate a comprehensive evaluation report.
        
        Args:
            save_path (str): Optional path to save the report
            
        Returns:
            str: Formatted evaluation report
        """
        # Overall performance
        metrics, y_true, y_pred = self.evaluate_model_performance()
        
        # Performance by compound
        compound_results = self.evaluate_by_compound()
        
        # Performance by temperature
        temp_results = self.evaluate_by_temperature()
        
        # Generate report
        report = f"""
FERRARI TIRE DEGRADATION MODEL - EVALUATION REPORT
{'='*65}

OVERALL PERFORMANCE METRICS
   • Mean Absolute Error:     {metrics['mae']:.4f} sec/lap
   • Root Mean Square Error:  {metrics['rmse']:.4f} sec/lap
   • R² Score:               {metrics['r2']:.4f}
   • Test Samples:           {metrics['n_samples']}
   • Median Absolute Error:  {metrics['median_absolute_error']:.4f} sec/lap

PREDICTION ACCURACY
   • 90th Percentile Error:  {metrics['prediction_accuracy_90']:.4f} sec/lap
   • Residual Mean:          {metrics['residual_mean']:.4f} sec/lap
   • Residual Std:           {metrics['residual_std']:.4f} sec/lap

PERFORMANCE BY COMPOUND
"""
        
        if not compound_results.empty:
            for _, row in compound_results.iterrows():
                report += f"   • {row['Compound']:6s}: MAE = {row['MAE']:.4f}, R² = {row['R2']:.3f} (n={row['Sample_Size']})\n"
        
        report += f"""
PERFORMANCE BY TEMPERATURE
"""
        
        if not temp_results.empty:
            for _, row in temp_results.iterrows():
                report += f"   • {row['Min_Temp']:.1f}-{row['Max_Temp']:.1f}°C: MAE = {row['MAE']:.4f}, R² = {row['R2']:.3f} (n={row['Sample_Size']})\n"
        
        report += f"""
MODEL INTERPRETATION
   Top 3 Most Important Features:
"""
        
        feature_importance = self.model.get_feature_importance()
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        for i, (feature, importance) in enumerate(sorted_features[:3]):
            report += f"   {i+1}. {feature}: {importance:.4f}\n"
        
        report += f"""
STRATEGIC INSIGHTS
   • Model shows {'good' if metrics['r2'] > 0.6 else 'moderate'} predictive performance (R² = {metrics['r2']:.3f})
   • Average prediction error: {metrics['mae']:.4f} sec/lap
   • Model reliability: {'High' if metrics['prediction_accuracy_90'] < 0.1 else 'Moderate'}
   
RECOMMENDATIONS
   • Use model for strategic guidance with {metrics['mae']:.4f} sec/lap uncertainty
   • Consider additional data for compounds with fewer samples
   • Monitor temperature-dependent performance variations
   
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
        
        return report


# Example usage
if __name__ == "__main__":
    print("Ferrari Model Evaluator - Example Usage")
    print("=" * 50)
    
    # Note: This requires trained model and test data
    print("To use this evaluator:")
    print("1. Train your TireDegradationPredictor model")
    print("2. Create evaluator with test data")
    print("3. Run comprehensive evaluation")
    print("\nExample code:")
    print("""
    from ml.models.degradation_predictor import TireDegradationPredictor
    from ml.evaluation.model_evaluator import ModelEvaluator
    
    # Load trained model
    predictor = TireDegradationPredictor()
    predictor.train("data/processed/tire_stints_weather_2025.csv")
    
    # Create evaluator
    evaluator = ModelEvaluator(predictor, "data/processed/tire_stints_weather_2025.csv")
    
    # Generate comprehensive evaluation
    report = evaluator.generate_evaluation_report()
    print(report)
    
    # Create visualizations
    metrics, y_true, y_pred = evaluator.evaluate_model_performance()
    evaluator.plot_prediction_accuracy(y_true, y_pred)
    evaluator.plot_feature_importance()
    """) 