"""
Ferrari F1 Strategy Engine

Main strategic decision-making engine that combines tire degradation predictions,
pit stop optimization, and race simulation to provide comprehensive race strategy
recommendations for Ferrari F1 team.

Key Features:
- Real-time strategy recommendations
- Multi-scenario analysis
- Competitor response modeling
- Risk-adjusted strategy selection
- Decision urgency assessment

Usage:
    engine = StrategyEngine(degradation_model)
    recommendation = engine.get_strategy_recommendation(race_state)
"""

import pandas as pd
from typing import Dict, List, Optional
from .pit_optimizer import PitStopOptimizer
from .race_simulator import RaceSimulator, RaceConfig


class StrategyEngine:
    """
    Comprehensive F1 strategy engine for Ferrari race strategy optimization.
    
    Integrates tire degradation predictions, pit stop optimization, and race
    simulation to provide strategic recommendations.
    """
    
    def __init__(self, degradation_model, track_configs=None):
        """
        Initialize strategy engine.
        
        Args:
            degradation_model: Trained TireDegradationPredictor instance
            track_configs (dict): Track-specific configurations
        """
        self.degradation_model = degradation_model
        self.pit_optimizer = PitStopOptimizer(degradation_model)
        self.race_simulator = RaceSimulator(degradation_model)
        self.track_configs = track_configs or {}
        
    def get_strategy_recommendation(self, race_state: Dict) -> Dict:
        """
        Get comprehensive strategy recommendation for current race state.
        
        Args:
            race_state (Dict): Current race conditions and position
            
        Returns:
            Dict: Complete strategy recommendation
        """
        # Extract race state information
        current_lap = race_state['current_lap']
        position = race_state['position']
        tire_age = race_state['tire_age']
        compound = race_state['compound']
        track_temp = race_state['track_temp']
        track_id = race_state['track_id']
        driver = race_state.get('driver', 'HAM')
        gaps_ahead = race_state.get('gaps_ahead', [])
        gaps_behind = race_state.get('gaps_behind', [])
        
        # Get pit stop optimization
        pit_recommendation = self.pit_optimizer.optimize_pit_strategy(
            current_lap=current_lap,
            current_position=position,
            current_tire_age=tire_age,
            current_compound=compound,
            gaps_ahead=gaps_ahead,
            gaps_behind=gaps_behind,
            track_temp=track_temp,
            track_id=track_id,
            driver=driver
        )
        
        # Get quick recommendation for immediate decisions
        quick_rec = self.pit_optimizer.quick_pit_recommendation(
            current_lap=current_lap,
            tire_age=tire_age,
            current_compound=compound,
            track_temp=track_temp,
            track_id=track_id,
            driver=driver
        )
        
        # Combine recommendations
        comprehensive_recommendation = {
            'immediate_action': quick_rec,
            'optimal_strategy': pit_recommendation['optimal_strategy'],
            'alternative_strategies': pit_recommendation['alternative_strategies'],
            'competitor_analysis': pit_recommendation['competitor_analysis'],
            'risk_assessment': pit_recommendation['risk_assessment'],
            'decision_urgency': pit_recommendation['decision_urgency'],
            'strategic_summary': self._generate_strategic_summary(
                pit_recommendation, quick_rec, race_state
            )
        }
        
        return comprehensive_recommendation
    
    def _generate_strategic_summary(self, pit_rec: Dict, quick_rec: Dict, 
                                  race_state: Dict) -> Dict:
        """
        Generate executive summary of strategic situation.
        
        Returns:
            Dict: Strategic summary
        """
        current_lap = race_state['current_lap']
        position = race_state['position']
        
        # Key strategic insights
        insights = []
        
        # Immediate action insight
        if quick_rec['recommendation'] == 'PIT_NOW':
            insights.append(f"IMMEDIATE: Pit this lap - {quick_rec['reasoning']}")
        else:
            insights.append(f"CONTINUE: Stay out for {quick_rec.get('laps_remaining', 'unknown')} more laps")
        
        # Optimal strategy insight
        optimal = pit_rec['optimal_strategy']
        insights.append(f"OPTIMAL: Pit lap {optimal['pit_lap']} for {optimal['new_compound']} compound")
        
        # Risk insight
        risk = pit_rec['risk_assessment']['overall_risk']
        insights.append(f"RISK: {risk} risk strategy")
        
        # Competitor insight
        comp_analysis = pit_rec['competitor_analysis']
        if comp_analysis['undercut_risk'] == 'HIGH':
            insights.append("WARNING: High undercut risk from cars behind")
        
        return {
            'current_situation': f"Lap {current_lap}, P{position}",
            'key_insights': insights,
            'recommendation_confidence': self._calculate_confidence(pit_rec),
            'next_decision_point': f"Lap {optimal['pit_lap'] - 2}"
        }
    
    def _calculate_confidence(self, pit_recommendation: Dict) -> str:
        """
        Calculate confidence level in recommendation.
        
        Returns:
            str: Confidence level
        """
        risk_level = pit_recommendation['risk_assessment']['overall_risk']
        decision_urgency = pit_recommendation['decision_urgency']
        
        if risk_level == 'LOW' and decision_urgency in ['LOW', 'MEDIUM']:
            return 'HIGH'
        elif risk_level == 'MEDIUM':
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def compare_strategy_scenarios(self, base_race_state: Dict, 
                                 scenario_modifications: List[Dict]) -> Dict:
        """
        Compare strategies under different race scenarios.
        
        Args:
            base_race_state (Dict): Base race conditions
            scenario_modifications (List[Dict]): Different scenario conditions
            
        Returns:
            Dict: Scenario comparison results
        """
        scenario_results = {}
        
        for i, modification in enumerate(scenario_modifications):
            scenario_name = modification.get('name', f'Scenario_{i+1}')
            
            # Apply modifications to base state
            modified_state = base_race_state.copy()
            modified_state.update(modification.get('changes', {}))
            
            # Get recommendation for this scenario
            recommendation = self.get_strategy_recommendation(modified_state)
            
            scenario_results[scenario_name] = {
                'scenario_conditions': modification,
                'recommendation': recommendation,
                'optimal_pit_lap': recommendation['optimal_strategy']['pit_lap'],
                'risk_level': recommendation['risk_assessment']['overall_risk']
            }
        
        return {
            'scenarios': scenario_results,
            'best_scenario': self._find_best_scenario(scenario_results),
            'scenario_comparison': self._compare_scenarios(scenario_results)
        }
    
    def _find_best_scenario(self, scenarios: Dict) -> str:
        """
        Find the best performing scenario.
        
        Returns:
            str: Name of best scenario
        """
        best_scenario = None
        best_score = float('inf')
        
        for name, data in scenarios.items():
            # Simple scoring: lower pit lap = earlier strategy = potentially better
            pit_lap = data['optimal_pit_lap']
            risk_penalty = {'LOW': 0, 'MEDIUM': 5, 'HIGH': 15}
            risk_score = risk_penalty.get(data['risk_level'], 10)
            
            total_score = pit_lap + risk_score
            
            if total_score < best_score:
                best_score = total_score
                best_scenario = name
        
        return best_scenario
    
    def _compare_scenarios(self, scenarios: Dict) -> List[Dict]:
        """
        Compare scenarios and provide insights.
        
        Returns:
            List[Dict]: Scenario comparison insights
        """
        comparisons = []
        
        scenario_items = list(scenarios.items())
        for i, (name1, data1) in enumerate(scenario_items):
            for name2, data2 in scenario_items[i+1:]:
                pit_diff = data2['optimal_pit_lap'] - data1['optimal_pit_lap']
                
                comparison = {
                    'scenario_1': name1,
                    'scenario_2': name2,
                    'pit_lap_difference': pit_diff,
                    'risk_comparison': f"{data1['risk_level']} vs {data2['risk_level']}",
                    'recommendation': self._generate_scenario_comparison_text(
                        name1, name2, pit_diff, data1['risk_level'], data2['risk_level']
                    )
                }
                comparisons.append(comparison)
        
        return comparisons
    
    def _generate_scenario_comparison_text(self, name1: str, name2: str, 
                                         pit_diff: int, risk1: str, risk2: str) -> str:
        """
        Generate comparison text between scenarios.
        
        Returns:
            str: Comparison recommendation
        """
        if abs(pit_diff) <= 2:
            return f"{name1} and {name2} have similar pit timing"
        elif pit_diff > 0:
            return f"{name1} suggests {pit_diff} laps earlier pit than {name2}"
        else:
            return f"{name2} suggests {abs(pit_diff)} laps earlier pit than {name1}"


# Example usage
if __name__ == "__main__":
    print("Ferrari Strategy Engine - Example Usage")
    print("=" * 50)
    
    print("Complete strategy engine combining:")
    print("- Tire degradation predictions")
    print("- Pit stop optimization") 
    print("- Race simulation")
    print("- Scenario analysis")
    print("\nExample code:")
    print("""
    from ml.models.degradation_predictor import TireDegradationPredictor
    from ml.strategy.strategy_engine import StrategyEngine
    
    # Load model and create engine
    predictor = TireDegradationPredictor()
    predictor.load_model("ml/saved_models/ferrari_degradation_model.pkl")
    engine = StrategyEngine(predictor)
    
    # Define current race state
    race_state = {
        'current_lap': 25,
        'position': 3,
        'tire_age': 20,
        'compound': 'MEDIUM',
        'track_temp': 42.0,
        'track_id': 3,
        'driver': 'HAM',
        'gaps_ahead': [2.1, 5.7],
        'gaps_behind': [3.2, 8.9]
    }
    
    # Get comprehensive recommendation
    recommendation = engine.get_strategy_recommendation(race_state)
    
    print("Strategic Summary:")
    summary = recommendation['strategic_summary']
    print(f"  Situation: {summary['current_situation']}")
    for insight in summary['key_insights']:
        print(f"  - {insight}")
    """) 