#!/usr/bin/env python3
"""
Ferrari F1 Strategy Optimizer - Complete Demo

This script demonstrates the complete strategy optimization system:
1. Load trained tire degradation model
2. Set up race scenario
3. Get strategic recommendations
4. Analyze different scenarios
5. Provide actionable insights

Usage:
    python ml/strategy/strategy_demo.py
"""

import os
import sys
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.models.degradation_predictor import TireDegradationPredictor
from ml.strategy.pit_optimizer import PitStopOptimizer
from ml.strategy.strategy_engine import StrategyEngine


def main():
    """
    Demonstrate complete Ferrari strategy optimization workflow.
    """
    print("Ferrari F1 Strategy Optimizer - Complete Demo")
    print("=" * 60)
    
    # Step 1: Load trained model
    print("\nStep 1: Loading Trained Model")
    print("-" * 30)
    
    model_path = "ml/saved_models/ferrari_degradation_model.pkl"
    
    predictor = TireDegradationPredictor()
    
    try:
        # Try to load existing model
        if os.path.exists(model_path):
            predictor.load_model(model_path)
            print(f"Loaded existing model from {model_path}")
        else:
            # Train new model if not exists
            print("No saved model found. Training new model...")
            predictor.train("data/processed/tire_stints_weather_2025.csv")
            predictor.save_model(model_path)
            print(f"Trained and saved new model to {model_path}")
    
    except Exception as e:
        print(f"Error with model: {e}")
        print("Please ensure data files exist and model is trained")
        return
    
    # Step 2: Initialize Strategy System
    print("\nStep 2: Initializing Strategy System")
    print("-" * 30)
    
    optimizer = PitStopOptimizer(predictor)
    engine = StrategyEngine(predictor)
    
    print("Strategy optimization system ready")
    
    # Step 3: Demo Race Scenario
    print("\nStep 3: Analyzing Current Race Situation")
    print("-" * 30)
    
    # Example race state (Italian GP scenario)
    race_state = {
        'current_lap': 0,
        'position': 4,
        'tire_age': 1,
        'compound': 'MEDIUM',
        'track_temp': 40.0,  
        'track_id': 16,       # Monza
        'driver': 'LEC',
        'gaps_ahead': [1.1, 1.7, 1.9],    # Gaps to P3, P2 and P1
        'gaps_behind': [1.2, 1.9]    # Gaps from P5 and P6
    }
    
    print("Current Race Situation:")
    print(f"  Lap: {race_state['current_lap']}")
    print(f"  Position: P{race_state['position']}")
    print(f"  Tire: {race_state['compound']} compound, {race_state['tire_age']} laps old")
    print(f"  Track Temperature: {race_state['track_temp']}°C")
    print(f"  Gap to P3: +{race_state['gaps_ahead'][0]:.1f}s")
    print(f"  Gap to P5: -{race_state['gaps_behind'][0]:.1f}s")
    
    # Step 4: Get Strategy Recommendation
    print("\nStep 4: Strategic Recommendation")
    print("-" * 30)
    
    recommendation = engine.get_strategy_recommendation(race_state)
    
    # Display immediate action
    immediate = recommendation['immediate_action']
    print(f"IMMEDIATE ACTION: {immediate['recommendation']}")
    print(f"  Reasoning: {immediate['reasoning']}")
    
    if immediate['recommendation'] == 'PIT_NOW':
        print(f"  Recommended compound: {immediate['recommended_compound']}")
    else:
        print(f"  Laps remaining: {immediate.get('laps_remaining', 'TBD')}")
    
    # Display optimal strategy
    optimal = recommendation['optimal_strategy']
    print(f"\nOPTIMAL STRATEGY:")
    print(f"  Pit on lap: {optimal['pit_lap']}")
    print(f"  New compound: {optimal['new_compound']}")
    print(f"  Expected position: P{optimal['expected_final_position']}")
    print(f"  Risk level: {optimal['risk_level']}")
    print(f"  Reasoning: {optimal['strategic_reasoning']}")
    
    # Display risk assessment
    risk = recommendation['risk_assessment']
    print(f"\nRISK ASSESSMENT:")
    print(f"  Overall risk: {risk['overall_risk']}")
    print(f"  Decision urgency: {recommendation['decision_urgency']}")
    
    # Display competitor analysis
    competitor = recommendation['competitor_analysis']
    print(f"\nCOMPETITOR ANALYSIS:")
    print(f"  Undercut risk: {competitor['undercut_risk']}")
    print(f"  Overcut opportunity: {competitor['overcut_opportunity']}")
    print(f"  Optimal response: {competitor['optimal_response']}")
    
    # Step 5: Alternative Scenarios
    print("\nStep 5: Alternative Scenario Analysis")
    print("-" * 30)
    
    scenarios = [
        {
            'name': 'Hot_Weather',
            'changes': {'track_temp': 45.0},
            'description': 'If track temperature rises to 45°C'
        },
        {
            'name': 'Safety_Car',
            'changes': {'current_lap': 25, 'gaps_ahead': [0.5, 1.2]},
            'description': 'If safety car bunches up the field'
        },
        {
            'name': 'Competitor_Pits',
            'changes': {'position': 3, 'gaps_behind': [1.0, 3.5]},
            'description': 'If car ahead pits and we inherit P3'
        }
    ]
    
    scenario_comparison = engine.compare_strategy_scenarios(race_state, scenarios)
    
    print("Scenario Analysis:")
    for scenario_name, data in scenario_comparison['scenarios'].items():
        scenario_info = next(s for s in scenarios if s['name'] == scenario_name)
        print(f"\n  {scenario_name}: {scenario_info['description']}")
        print(f"    Optimal pit lap: {data['optimal_pit_lap']}")
        print(f"    Risk level: {data['risk_level']}")
    
    best_scenario = scenario_comparison['best_scenario']
    print(f"\n  Best scenario strategy: {best_scenario}")
    
    # Step 6: Quick Decision Support
    print("\nStep 6: Quick Decision Support Tool")
    print("-" * 30)
    
    print("Testing quick recommendations for different conditions:")
    

    #note these only make sense for during the race not beginning
    # test_conditions = [
    #     {'tire_age': 25, 'compound': 'MEDIUM', 'description': 'Current medium tires'},
    #     {'tire_age': 15, 'compound': 'SOFT', 'description': 'Fresh soft tires'},
    #     {'tire_age': 30, 'compound': 'HARD', 'description': 'Old hard tires'}
    # ]

    # team strategy variants
    # test_conditions = [
    #     {'tire_age': 0, 'compound': 'SOFT', 'driver': 'HAM', 'description': 'Driver 1 on softs for split strategy'},
    #     {'tire_age': 0, 'compound': 'MEDIUM', 'driver': 'LEC', 'description': 'Driver 2 on mediums for offset strategy'}
    # ]

    # Early race events
    # test_conditions = [
    #     {'current_lap': 3, 'compound': 'SOFT', 'tire_age': 3, 'description': 'Early safety car on softs – pit window opens early'},
    #     {'current_lap': 5, 'compound': 'MEDIUM', 'tire_age': 5, 'gaps_ahead': [0.3], 'description': 'Tight DRS train – undercut possible'}
    # ]

    # Starting grid position
    # test_conditions = [
    #     {'position': 1, 'compound': 'SOFT', 'description': 'Pole position, defend with aggressive tire'},
    #     {'position': 10, 'compound': 'MEDIUM', 'description': 'Midfield start, flexible strategy'},
    #     {'position': 18, 'compound': 'HARD', 'description': 'Backmarker one-stop gamble'}
    # ]


    # Starting compound variants
    test_conditions = [
        {'tire_age': 0, 'compound': 'SOFT', 'description': 'Start on softs for max launch potential'},
        {'tire_age': 0, 'compound': 'MEDIUM', 'description': 'Balanced start on mediums'},
        {'tire_age': 0, 'compound': 'HARD', 'description': 'One-stop strategy attempt starting on hards'}
    ]




    # again this is probably best for mid race scenarios
    for condition in test_conditions:
        quick_rec = optimizer.quick_pit_recommendation(
            current_lap=race_state['current_lap'],
            tire_age=condition['tire_age'],
            current_compound=condition['compound'],
            track_temp=race_state['track_temp'],
            track_id=race_state['track_id'],
            driver=race_state['driver']
        )
        
        print(f"\n  {condition['description']}:")
        print(f"    Recommendation: {quick_rec['recommendation']}")
        print(f"    Degradation rate: {quick_rec['current_degradation']:.4f} sec/lap")
        print(f"    Risk level: {quick_rec['risk_level']}")
    
    # Step 7: Strategic Summary
    print("\nStep 7: Executive Summary")
    print("-" * 30)
    
    summary = recommendation['strategic_summary']
    print(f"STRATEGIC SITUATION: {summary['current_situation']}")
    print(f"CONFIDENCE: {summary['recommendation_confidence']}")
    print(f"NEXT DECISION: {summary['next_decision_point']}")
    
    print("\nKEY INSIGHTS:")
    for insight in summary['key_insights']:
        print(f"  - {insight}")
    
    print("\nRECOMMENDATIONS:")
    print("  1. Monitor tire degradation closely")
    print("  2. Be ready to respond to competitor moves") 
    print("  3. Consider track temperature changes")
    print("  4. Maintain radio communication for real-time updates")
    
    print("\n" + "=" * 60)
    print("Strategy optimization complete!")
    print("Use these insights to make informed pit stop decisions.")


if __name__ == "__main__":
    main() 