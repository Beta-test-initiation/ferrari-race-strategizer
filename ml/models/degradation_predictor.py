"""
Ferrari F1 Tire Degradation Predictor

This module implements a machine learning model to predict tire degradation rates
based on track conditions, tire compounds, and stint characteristics.

Key Features:
- Predicts tire degradation rate (LapTimeSlope) for given conditions
- Provides confidence intervals for risk assessment
- Trained on Ferrari's historical stint data from 2025 season
- Incorporates weather conditions and track characteristics

Model Architecture:
- Random Forest Regressor for robust non-linear predictions
- Feature engineering for track temperature, compound encoding, and stint metrics
- Cross-validation for model reliability assessment

Usage:
    predictor = TireDegradationPredictor()
    predictor.train("data/processed/tire_stints_weather_2025.csv")
    degradation_rate = predictor.predict_degradation(
        track_temp=45.0, 
        compound="MEDIUM", 
        stint_length=25, 
        track_id=1
    )
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class TireDegradationPredictor:
    """
    Machine Learning model for predicting tire degradation rates in F1 racing.
    
    This model predicts the tire degradation rate (measured as lap time increase
    per lap) based on track conditions, tire compound, and stint characteristics.
    """
    
    def __init__(self, model_params=None):
        """
        Initialize the tire degradation predictor.
        
        Args:
            model_params (dict): Parameters for RandomForest model
        """
        # Default model parameters optimized for F1 tire degradation
        default_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
        
        if model_params:
            default_params.update(model_params)
            
        self.model = RandomForestRegressor(**default_params)
        self.compound_encoder = LabelEncoder()
        self.driver_encoder = LabelEncoder()
        self.is_trained = False
        self.feature_names = []
        self.model_metrics = {}
        
    def prepare_features(self, df):
        """
        Engineer features for tire degradation prediction.
        
        Features created:
        - Track temperature (normalized)
        - Compound type (encoded)
        - Stint length
        - Track characteristics (Round number as proxy)
        - Driver-specific factors
        - Weather conditions (humidity, wind)
        
        Args:
            df (DataFrame): Raw stint data with weather information
            
        Returns:
            DataFrame: Engineered features ready for ML model
        """
        # Create a copy to avoid modifying original data
        features_df = df.copy()
        
        # Remove extreme outliers in degradation rate
        # (These are often due to data quality issues or unusual circumstances)
        features_df = features_df[
            features_df['LapTimeSlope'].between(-0.3, 0.3)
        ].copy()
        
        # Feature 1: Normalized track temperature
        features_df['TrackTemp_norm'] = (
            features_df['TrackTemp'] - features_df['TrackTemp'].mean()
        ) / features_df['TrackTemp'].std()
        
        # Feature 2: Compound encoding
        features_df['Compound_encoded'] = self.compound_encoder.fit_transform(
            features_df['Compound']
        )
        
        # Feature 3: Driver encoding (Ferrari-specific patterns)
        features_df['Driver_encoded'] = self.driver_encoder.fit_transform(
            features_df['Driver']
        )
        
        # Feature 4: Stint length (key factor for degradation)
        features_df['StintLength_norm'] = (
            features_df['StintLength'] - features_df['StintLength'].mean()
        ) / features_df['StintLength'].std()
        
        # Feature 5: Track characteristics (using Round as proxy)
        features_df['Track_encoded'] = features_df['Round']
        
        # Feature 6: Weather features (if available)
        if 'Humidity' in features_df.columns:
            features_df['Humidity_norm'] = (
                features_df['Humidity'] - features_df['Humidity'].mean()
            ) / features_df['Humidity'].std()
        else:
            features_df['Humidity_norm'] = 0
            
        if 'WindSpeed' in features_df.columns:
            features_df['WindSpeed_norm'] = (
                features_df['WindSpeed'] - features_df['WindSpeed'].mean()
            ) / features_df['WindSpeed'].std()
        else:
            features_df['WindSpeed_norm'] = 0
        
        # Feature 7: Interaction features (domain knowledge)
        # High temperature + long stint = more degradation
        features_df['TempStint_interaction'] = (
            features_df['TrackTemp_norm'] * features_df['StintLength_norm']
        )
        
        # Feature 8: Compound-specific temperature sensitivity
        features_df['CompoundTemp_interaction'] = (
            features_df['Compound_encoded'] * features_df['TrackTemp_norm']
        )
        
        # Define final feature columns
        feature_columns = [
            'TrackTemp_norm', 'Compound_encoded', 'Driver_encoded',
            'StintLength_norm', 'Track_encoded', 'Humidity_norm', 
            'WindSpeed_norm', 'TempStint_interaction', 'CompoundTemp_interaction'
        ]
        
        self.feature_names = feature_columns
        
        return features_df[feature_columns + ['LapTimeSlope']].dropna()
    
    def train(self, data_path, test_size=0.2, validation_splits=5):
        """
        Train the tire degradation prediction model.
        
        Args:
            data_path (str): Path to processed stint data CSV
            test_size (float): Proportion of data for testing
            validation_splits (int): Number of CV folds for validation
            
        Returns:
            dict: Training metrics and model performance
        """
        print("Loading Ferrari tire degradation data...")
        
        # Load and prepare data
        df = pd.read_csv(data_path)
        
        # Filter for Ferrari drivers only
        ferrari_drivers = ['HAM', 'LEC']
        df = df[df['Driver'].isin(ferrari_drivers)].copy()
        
        print(f"Data loaded: {len(df)} Ferrari tire stints")
        print(f"Tracks covered: {df['Round'].nunique()}")
        print(f"Compounds analyzed: {df['Compound'].unique()}")
        
        # Prepare features
        prepared_df = self.prepare_features(df)
        
        print(f"Features engineered: {len(self.feature_names)} features")
        print(f"Training samples: {len(prepared_df)}")
        
        # Split features and target
        X = prepared_df[self.feature_names]
        y = prepared_df['LapTimeSlope']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=None
        )
        
        print(f"Training model on {len(X_train)} samples...")
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Calculate metrics
        train_metrics = {
            'mae': mean_absolute_error(y_train, y_pred_train),
            'mse': mean_squared_error(y_train, y_pred_train),
            'r2': r2_score(y_train, y_pred_train)
        }
        
        test_metrics = {
            'mae': mean_absolute_error(y_test, y_pred_test),
            'mse': mean_squared_error(y_test, y_pred_test),
            'r2': r2_score(y_test, y_pred_test)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train, y_train, 
            cv=validation_splits, scoring='neg_mean_absolute_error'
        )
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_names, 
            self.model.feature_importances_
        ))
        
        # Store metrics
        self.model_metrics = {
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'cv_mae_mean': -cv_scores.mean(),
            'cv_mae_std': cv_scores.std(),
            'feature_importance': feature_importance
        }
        
        self.is_trained = True
        
        # Print results
        print("\nModel Training Results:")
        print(f"   Test MAE: {test_metrics['mae']:.4f} sec/lap")
        print(f"   Test R²:  {test_metrics['r2']:.4f}")
        print(f"   CV MAE:   {self.model_metrics['cv_mae_mean']:.4f} ± {self.model_metrics['cv_mae_std']:.4f}")
        
        print("\nTop Feature Importance:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:5]:
            print(f"   {feature}: {importance:.4f}")
        
        return self.model_metrics
    
    def predict_degradation(self, track_temp, compound, stint_length, 
                          track_id, driver='LEC', humidity=50, wind_speed=5):
        """
        Predict tire degradation rate for given conditions.
        
        Args:
            track_temp (float): Track temperature in Celsius
            compound (str): Tire compound ('SOFT', 'MEDIUM', 'HARD')
            stint_length (int): Planned stint length in laps
            track_id (int): Track identifier (Round number)
            driver (str): Driver abbreviation ('HAM', 'LEC')
            humidity (float): Humidity percentage (default: 50)
            wind_speed (float): Wind speed in km/h (default: 5)
            
        Returns:
            dict: Prediction results with confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create prediction input
        prediction_data = {
            'TrackTemp': track_temp,
            'Compound': compound,
            'Driver': driver,
            'StintLength': stint_length,
            'Round': track_id,
            'Humidity': humidity,
            'WindSpeed': wind_speed
        }
        
        # Convert to DataFrame for processing
        pred_df = pd.DataFrame([prediction_data])
        
        # Apply same feature engineering (without target)
        # Normalize using training data statistics
        pred_df['TrackTemp_norm'] = (track_temp - 35.0) / 10.0  # Approximate normalization
        pred_df['Compound_encoded'] = self.compound_encoder.transform([compound])[0]
        pred_df['Driver_encoded'] = self.driver_encoder.transform([driver])[0]
        pred_df['StintLength_norm'] = (stint_length - 20.0) / 10.0  # Approximate normalization
        pred_df['Track_encoded'] = track_id
        pred_df['Humidity_norm'] = (humidity - 50.0) / 20.0
        pred_df['WindSpeed_norm'] = (wind_speed - 5.0) / 5.0
        pred_df['TempStint_interaction'] = pred_df['TrackTemp_norm'] * pred_df['StintLength_norm']
        pred_df['CompoundTemp_interaction'] = pred_df['Compound_encoded'] * pred_df['TrackTemp_norm']
        
        # Make prediction
        X_pred = pred_df[self.feature_names]
        degradation_rate = self.model.predict(X_pred)[0]
        
        # Calculate confidence interval using individual tree predictions
        tree_predictions = [tree.predict(X_pred)[0] for tree in self.model.estimators_]
        prediction_std = np.std(tree_predictions)
        
        # 95% confidence interval
        confidence_interval = {
            'lower': degradation_rate - 1.96 * prediction_std,
            'upper': degradation_rate + 1.96 * prediction_std
        }
        
        return {
            'degradation_rate': degradation_rate,
            'confidence_interval': confidence_interval,
            'prediction_std': prediction_std,
            'risk_level': self._assess_risk_level(degradation_rate, prediction_std)
        }
    
    def _assess_risk_level(self, degradation_rate, std):
        """
        Assess the risk level of the predicted degradation rate.
        
        Args:
            degradation_rate (float): Predicted degradation rate
            std (float): Prediction standard deviation
            
        Returns:
            str: Risk level ('LOW', 'MEDIUM', 'HIGH')
        """

        # Risk assessment based on degradation rate and uncertainty
        if abs(degradation_rate) > 0.1 or std > 0.08:
            return 'HIGH'
        elif abs(degradation_rate) > 0.05 or std > 0.05:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save_model(self, filepath):
        """
        Save the trained model to disk.
        
        Args:
            filepath (str): Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model and encoders
        model_data = {
            'model': self.model,
            'compound_encoder': self.compound_encoder,
            'driver_encoder': self.driver_encoder,
            'feature_names': self.feature_names,
            'model_metrics': self.model_metrics,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a trained model from disk.
        
        Args:
            filepath (str): Path to load the model from
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.compound_encoder = model_data['compound_encoder']
        self.driver_encoder = model_data['driver_encoder']
        self.feature_names = model_data['feature_names']
        self.model_metrics = model_data['model_metrics']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
    
    def get_feature_importance(self):
        """
        Get feature importance for model interpretation.
        
        Returns:
            dict: Feature importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")
        
        return self.model_metrics['feature_importance']
    
    def predict_stint_performance(self, track_temp, compound, max_stint_length, 
                                 track_id, driver='HAM'):
        """
        Predict tire performance across different stint lengths.
        
        Args:
            track_temp (float): Track temperature
            compound (str): Tire compound
            max_stint_length (int): Maximum stint length to analyze
            track_id (int): Track identifier
            driver (str): Driver abbreviation
            
        Returns:
            DataFrame: Stint length vs predicted degradation
        """
        results = []
        
        for stint_length in range(5, max_stint_length + 1, 5):
            prediction = self.predict_degradation(
                track_temp=track_temp,
                compound=compound,
                stint_length=stint_length,
                track_id=track_id,
                driver=driver
            )
            
            results.append({
                'stint_length': stint_length,
                'degradation_rate': prediction['degradation_rate'],
                'total_time_loss': prediction['degradation_rate'] * stint_length,
                'risk_level': prediction['risk_level']
            })
        
        return pd.DataFrame(results)


# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the tire degradation predictor
    print("Ferrari Tire Degradation Predictor - Example Usage")
    print("=" * 60)
    
    # Initialize predictor
    predictor = TireDegradationPredictor()
    
    # Train the model (make sure data file exists)
    try:
        metrics = predictor.train("../data/processed/tire_stints_weather_2025.csv")
        
        # Make a prediction
        prediction = predictor.predict_degradation(
            track_temp=27.0,
            compound="MEDIUM",
            stint_length=25,
            track_id=3,  # Example track
            driver="LEC"
        )
        
        print(f"\nPrediction Example:")
        print(f"   Conditions: 45°C, Medium tires, 25-lap stint")
        print(f"   Predicted degradation: {prediction['degradation_rate']:.4f} sec/lap")
        print(f"   Risk level: {prediction['risk_level']}")
        
        # Analyze stint performance
        stint_analysis = predictor.predict_stint_performance(
            track_temp=45.0,
            compound="MEDIUM",
            max_stint_length=40,
            track_id=3,
            driver="LEC"
        )
        
        print(f"\nStint Length Analysis:")
        print(stint_analysis.head())
        
    except FileNotFoundError:
        print("Data file not found. Please run data collection scripts first.")
    except Exception as e:
        print(f"Error: {e}") 