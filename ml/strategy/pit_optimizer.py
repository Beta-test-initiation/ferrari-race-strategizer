"""
Ferrari F1 Pit Stop Optimizer

This module implements intelligent pit stop timing optimization using tire degradation
predictions and race position analysis. It provides strategic recommendations for
when to pit, which compounds to use, and how to respond to competitor moves.

Key Features:
- Optimal pit window calculation based on tire degradation
- Compound selection optimization
- Competitor response analysis
- Risk assessment for different strategies
- Real-time strategy updates during races

Usage:
    optimizer = PitStopOptimizer(degradation_model)
    recommendation = optimizer.optimize_pit_strategy(
        current_lap=20, position=3, gap_ahead=2.5, gap_behind=4.1
    )
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PitStopOptimizer:
    """
    Advanced pit stop timing optimizer for Ferrari F1 strategy.
    
    Uses tire degradation predictions to optimize pit stop timing, compound selection,
    and strategic responses to competitor moves.
    """
    
    def __init__(self, degradation_model, track_config=None):
        """
        Initialize the pit stop optimizer.
        
        Args:
            degradation_model: Trained TireDegradationPredictor instance
            track_config (dict): Track-specific configuration (pit loss, lap time, etc.)
        """
        self.degradation_model = degradation_model
        self.track_config = track_config or self._get_default_track_config()
        
        # Strategic constants
        self.PIT_STOP_TIME_LOSS = self.track_config.get('pit_stop_time_loss', 22.0)  # seconds
        self.SAFETY_CAR_PROBABILITY = 0.15  # 15% chance per race
        self.TIRE_WARM_UP_TIME = 2  # laps to reach optimal performance
        
    def _get_default_track_config(self):
        """
        Get default track configuration parameters.
        
        Returns:
            dict: Default track configuration
        """
        return {
            'pit_stop_time_loss': 22.0,  # Average pit stop time loss in seconds
            'lap_time_baseline': 110.0,   # Baseline lap time in seconds
            'track_length': 6.003,         # Track length in km
            'total_laps': 51,           # Typical race distance
            'drs_advantage': 0.3,       # DRS advantage in seconds
            'overtaking_difficulty': 0.4  # 0-1 scale, 1 = very difficult
        }
    
    def optimize_pit_strategy(self, current_lap: int, current_position: int,
                            current_tire_age: int, current_compound: str,
                            gaps_ahead: List[float], gaps_behind: List[float],
                            track_temp: float, track_id: int, driver: str = "HAM",
                            race_laps: int = 60) -> Dict:
        """
        Optimize pit stop strategy for current race conditions.
        
        Args:
            current_lap (int): Current race lap
            current_position (int): Current track position
            current_tire_age (int): Current tire age in laps
            current_compound (str): Current tire compound
            gaps_ahead (List[float]): Time gaps to cars ahead (seconds)
            gaps_behind (List[float]): Time gaps to cars behind (seconds)
            track_temp (float): Current track temperature
            track_id (int): Track identifier
            driver (str): Driver abbreviation
            race_laps (int): Total race laps
            
        Returns:
            Dict: Comprehensive strategy recommendation
        """
        # Calculate optimal pit windows for different strategies
        strategies = self._evaluate_strategies(
            current_lap, current_position, current_tire_age, current_compound,
            gaps_ahead, gaps_behind, track_temp, track_id, driver, race_laps
        )
        
        # Find best strategy
        best_strategy = self._select_best_strategy(strategies)
        
        # Add competitor analysis
        competitor_analysis = self._analyze_competitors(
            current_lap, current_position, gaps_ahead, gaps_behind, track_temp, track_id
        )
        
        # Generate comprehensive recommendation
        recommendation = {
            'optimal_strategy': best_strategy,
            'alternative_strategies': strategies[:3],  # Top 3 alternatives
            'competitor_analysis': competitor_analysis,
            'risk_assessment': self._assess_strategy_risk(best_strategy),
            'decision_urgency': self._calculate_decision_urgency(
                current_lap, best_strategy, gaps_ahead, gaps_behind
            )
        }
        
        return recommendation
    
    def _evaluate_strategies(self, current_lap: int, current_position: int,
                           current_tire_age: int, current_compound: str,
                           gaps_ahead: List[float], gaps_behind: List[float],
                           track_temp: float, track_id: int, driver: str,
                           race_laps: int) -> List[Dict]:
        """
        Evaluate multiple pit stop strategies and rank them.
        
        Returns:
            List[Dict]: Ranked list of strategies with expected outcomes
        """
        strategies = []
        
        # Generate strategy candidates
        pit_windows = self._generate_pit_windows(current_lap, race_laps)
        compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        for pit_lap in pit_windows:
            for new_compound in compounds:
                # Skip if same compound (unless tire age is very high)
                if new_compound == current_compound and current_tire_age < 30:
                    continue
                
                strategy = self._evaluate_single_strategy(
                    current_lap, current_position, current_tire_age, current_compound,
                    pit_lap, new_compound, gaps_ahead, gaps_behind,
                    track_temp, track_id, driver, race_laps
                )
                
                strategies.append(strategy)
        
        # Sort by expected race time
        strategies.sort(key=lambda x: x['expected_race_time'])
        
        return strategies
    
    def _evaluate_single_strategy(self, current_lap: int, current_position: int,
                                current_tire_age: int, current_compound: str,
                                pit_lap: int, new_compound: str,
                                gaps_ahead: List[float], gaps_behind: List[float],
                                track_temp: float, track_id: int, driver: str,
                                race_laps: int) -> Dict:
        """
        Evaluate a single pit stop strategy.
        
        Returns:
            Dict: Strategy evaluation with expected outcomes
        """
        # Calculate tire degradation for different phases
        
        # Phase 1: Current stint to pit lap
        stint1_length = pit_lap - current_lap
        if stint1_length > 0:
            current_degradation = self.degradation_model.predict_degradation(
                track_temp=track_temp,
                compound=current_compound,
                stint_length=current_tire_age + stint1_length,
                track_id=track_id,
                driver=driver
            )
            phase1_time_loss = current_degradation['degradation_rate'] * stint1_length
        else:
            phase1_time_loss = 0.0
        
        # Phase 2: New stint to race end
        stint2_length = race_laps - pit_lap
        new_degradation = self.degradation_model.predict_degradation(
            track_temp=track_temp,
            compound=new_compound,
            stint_length=stint2_length,
            track_id=track_id,
            driver=driver
        )
        phase2_time_loss = new_degradation['degradation_rate'] * stint2_length
        
        # Calculate total time
        total_degradation_loss = phase1_time_loss + phase2_time_loss
        pit_stop_loss = self.PIT_STOP_TIME_LOSS
        
        # Position change estimation
        position_change = self._estimate_position_change(
            current_position, gaps_ahead, gaps_behind, pit_stop_loss
        )
        
        # Calculate expected race time
        baseline_race_time = race_laps * self.track_config['lap_time_baseline']
        expected_race_time = baseline_race_time + total_degradation_loss + pit_stop_loss
        
        strategy = {
            'pit_lap': pit_lap,
            'new_compound': new_compound,
            'stint_lengths': [current_tire_age + stint1_length, stint2_length],
            'expected_race_time': expected_race_time,
            'time_loss_breakdown': {
                'phase1_degradation': phase1_time_loss,
                'phase2_degradation': phase2_time_loss,
                'pit_stop_loss': pit_stop_loss,
                'total_loss': total_degradation_loss + pit_stop_loss
            },
            'position_change': position_change,
            'expected_final_position': current_position + position_change,
            'risk_level': max(current_degradation.get('risk_level', 'LOW'),
                            new_degradation.get('risk_level', 'LOW'))
        }
        
        return strategy
    
    def _generate_pit_windows(self, current_lap: int, race_laps: int) -> List[int]:
        """
        Generate candidate pit stop laps.
        
        Returns:
            List[int]: List of potential pit stop laps
        """
        # Early pit window (laps 15-25)
        early_window = list(range(max(15, current_lap + 1), min(26, race_laps - 10)))
        
        # Mid race window (laps 25-40)
        mid_window = list(range(max(25, current_lap + 1), min(41, race_laps - 10)))
        
        # Late window (laps 40-50)
        late_window = list(range(max(40, current_lap + 1), min(51, race_laps - 5)))
        
        # Combine and remove duplicates
        all_windows = list(set(early_window + mid_window + late_window))
        all_windows.sort()
        
        return all_windows
    
    def _estimate_position_change(self, current_position: int,
                                gaps_ahead: List[float], gaps_behind: List[float],
                                pit_stop_loss: float) -> int:
        """
        Estimate position change due to pit stop.
        
        Returns:
            int: Estimated position change (positive = positions lost)
        """
        positions_lost = 0
        positions_gained = 0
        
        # Calculate positions lost to cars behind
        for gap in gaps_behind:
            if gap < pit_stop_loss:
                positions_lost += 1
        
        # Calculate positions gained from cars ahead (undercut potential)
        undercut_advantage = 2.0  # seconds advantage from fresh tires
        for gap in gaps_ahead:
            if gap < (pit_stop_loss - undercut_advantage):
                positions_gained += 1
        
        return positions_lost - positions_gained
    
    def _select_best_strategy(self, strategies: List[Dict]) -> Dict:
        """
        Select the best strategy from evaluated options.
        
        Returns:
            Dict: Best strategy with justification
        """
        if not strategies:
            return {}
        
        # Primary criterion: expected race time
        best_strategy = strategies[0]
        
        # Add strategic reasoning
        best_strategy['strategic_reasoning'] = self._generate_reasoning(best_strategy)
        
        return best_strategy
    
    def _generate_reasoning(self, strategy: Dict) -> str:
        """
        Generate human-readable reasoning for strategy choice.
        
        Returns:
            str: Strategic reasoning
        """
        pit_lap = strategy['pit_lap']
        compound = strategy['new_compound']
        time_loss = strategy['time_loss_breakdown']['total_loss']
        position_change = strategy['position_change']
        
        reasoning = f"Pit on lap {pit_lap} for {compound} compound. "
        reasoning += f"Expected total time loss: {time_loss:.1f} seconds. "
        
        if position_change <= 0:
            reasoning += f"Should maintain or gain {abs(position_change)} positions. "
        else:
            reasoning += f"May lose {position_change} positions initially. "
        
        if strategy['risk_level'] == 'LOW':
            reasoning += "Low risk strategy with high success probability."
        elif strategy['risk_level'] == 'MEDIUM':
            reasoning += "Moderate risk strategy - monitor tire performance."
        else:
            reasoning += "High risk strategy - consider alternatives."
        
        return reasoning
    
    def _analyze_competitors(self, current_lap: int, current_position: int,
                           gaps_ahead: List[float], gaps_behind: List[float],
                           track_temp: float, track_id: int) -> Dict:
        """
        Analyze competitor pit stop probabilities and optimal responses.
        
        Returns:
            Dict: Competitor analysis and response recommendations
        """
        analysis = {
            'competitor_pit_probability': self._estimate_competitor_pit_probability(
                current_lap, gaps_ahead, gaps_behind
            ),
            'optimal_response': self._calculate_optimal_response(
                current_lap, current_position, gaps_ahead, gaps_behind
            ),
            'undercut_risk': self._assess_undercut_risk(gaps_ahead, gaps_behind),
            'overcut_opportunity': self._assess_overcut_opportunity(gaps_ahead, gaps_behind)
        }
        
        return analysis
    
    def _estimate_competitor_pit_probability(self, current_lap: int,
                                           gaps_ahead: List[float],
                                           gaps_behind: List[float]) -> float:
        """
        Estimate probability of competitors pitting in next few laps.
        
        Returns:
            float: Pit probability (0-1)
        """
        # Base probability increases with lap number
        base_probability = min(0.8, current_lap / 50.0)
        
        # Increase if cars are close (DRS battles)
        close_battles = sum(1 for gap in gaps_ahead + gaps_behind if gap < 1.0)
        battle_multiplier = 1.0 + (close_battles * 0.2)
        
        # Typical pit window increases probability
        if 18 <= current_lap <= 35:
            window_multiplier = 1.5
        else:
            window_multiplier = 1.0
        
        probability = base_probability * battle_multiplier * window_multiplier
        
        return min(1.0, probability)
    
    def _calculate_optimal_response(self, current_lap: int, current_position: int,
                                  gaps_ahead: List[float], gaps_behind: List[float]) -> str:
        """
        Calculate optimal response to competitor pit stops.
        
        Returns:
            str: Response recommendation
        """
        if not gaps_ahead:
            return "Cover cars behind - pit when they pit"
        
        if not gaps_behind:
            return "Pit for undercut opportunity"
        
        # If close battle ahead
        if gaps_ahead[0] < 2.0:
            return "Pit for undercut - gain track position"
        
        # If close battle behind
        if gaps_behind[0] < 2.0:
            return "Cover defensive position - pit after opponent"
        
        return "Pit at optimal window regardless of competitors"
    
    def _assess_undercut_risk(self, gaps_ahead: List[float],
                            gaps_behind: List[float]) -> str:
        """
        Assess risk of being undercut by competitors.
        
        Returns:
            str: Risk level assessment
        """
        if not gaps_behind:
            return "LOW"
        
        closest_behind = min(gaps_behind)
        
        if closest_behind < 3.0:
            return "HIGH"
        elif closest_behind < 8.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_overcut_opportunity(self, gaps_ahead: List[float],
                                  gaps_behind: List[float]) -> str:
        """
        Assess opportunity for overcut strategy.
        
        Returns:
            str: Opportunity level
        """
        if not gaps_ahead:
            return "LOW"
        
        closest_ahead = min(gaps_ahead)
        
        if closest_ahead < 5.0:
            return "HIGH"
        elif closest_ahead < 12.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_strategy_risk(self, strategy: Dict) -> Dict:
        """
        Assess overall risk of selected strategy.
        
        Returns:
            Dict: Risk assessment breakdown
        """
        risk_factors = {
            'tire_degradation_risk': strategy.get('risk_level', 'LOW'),
            'position_loss_risk': 'HIGH' if strategy['position_change'] > 2 else 'LOW',
            'stint_length_risk': 'HIGH' if max(strategy['stint_lengths']) > 35 else 'LOW',
            'timing_risk': 'MEDIUM'  # Default timing risk
        }
        
        # Calculate overall risk
        risk_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        avg_risk_score = sum(risk_scores[risk] for risk in risk_factors.values()) / len(risk_factors)
        
        if avg_risk_score < 1.5:
            overall_risk = 'LOW'
        elif avg_risk_score < 2.5:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'HIGH'
        
        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'risk_score': avg_risk_score
        }
    
    def _calculate_decision_urgency(self, current_lap: int, strategy: Dict,
                                  gaps_ahead: List[float], gaps_behind: List[float]) -> str:
        """
        Calculate urgency of pit stop decision.
        
        Returns:
            str: Urgency level
        """
        pit_lap = strategy['pit_lap']
        laps_to_pit = pit_lap - current_lap
        
        # High urgency if pit window is soon
        if laps_to_pit <= 2:
            return "IMMEDIATE"
        elif laps_to_pit <= 5:
            return "HIGH"
        elif laps_to_pit <= 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def quick_pit_recommendation(self, current_lap: int, tire_age: int,
                               current_compound: str, track_temp: float,
                               track_id: int, driver: str = "HAM") -> Dict:
        """
        Quick pit stop recommendation for immediate decisions.
        
        Returns:
            Dict: Simplified recommendation
        """
        # Predict degradation if continuing current stint
        extended_degradation = self.degradation_model.predict_degradation(
            track_temp=track_temp,
            compound=current_compound,
            stint_length=tire_age + 10,  # 10 more laps
            track_id=track_id,
            driver=driver
        )
        
        # Should pit if degradation is high or risk is high
        should_pit = (
            extended_degradation['degradation_rate'] > 0.08 or
            extended_degradation['risk_level'] == 'HIGH' or
            tire_age > 30
        )

        
        if should_pit:
            # Recommend best compound for current conditions
            best_compound = self._recommend_compound(track_temp, current_compound)
            
            return {
                'recommendation': 'PIT_NOW',
                'recommended_compound': best_compound,
                'current_degradation': extended_degradation['degradation_rate'],
                'risk_level': extended_degradation['risk_level'],
                'reasoning': f"High degradation rate ({extended_degradation['degradation_rate']:.3f} sec/lap) detected"
            }
        else:
            return {
                'recommendation': 'CONTINUE',
                'laps_remaining': max(0, 35 - tire_age),  # Rough estimate
                'current_degradation': extended_degradation['degradation_rate'],
                'risk_level': extended_degradation['risk_level'],
                'reasoning': f"Degradation still manageable ({extended_degradation['degradation_rate']:.3f} sec/lap)"
            }
    
    def _recommend_compound(self, track_temp: float, current_compound: str) -> str:
        """
        Recommend best tire compound for current conditions.
        
        Returns:
            str: Recommended compound
        """
        # Based on temperature and Ferrari's model performance
        if track_temp > 40:
            return "HARD"
        elif track_temp > 30:
            return "MEDIUM"  # Ferrari's sweet spot
        else:
            return "SOFT"


# Example usage and testing
if __name__ == "__main__":
    print("Ferrari Pit Stop Optimizer ")
    print("=" * 50)
    
    print("To use this optimizer:")
    print("1. Load your trained TireDegradationPredictor model")
    print("2. Create PitStopOptimizer with the model")
    print("3. Call optimize_pit_strategy() with current race conditions")
    print("\nExample code:")
    print("""
    from ml.models.degradation_predictor import TireDegradationPredictor
    from ml.strategy.pit_optimizer import PitStopOptimizer
    
    # Load trained model
    predictor = TireDegradationPredictor()
    predictor.load_model("ml/saved_models/ferrari_degradation_model.pkl")
    
    # Create optimizer
    optimizer = PitStopOptimizer(predictor)
    
    # Get strategy recommendation
    recommendation = optimizer.optimize_pit_strategy(
        current_lap=22,
        current_position=3,
        current_tire_age=18,
        current_compound="MEDIUM",
        gaps_ahead=[2.1, 5.7],
        gaps_behind=[3.2, 8.9],
        track_temp=42.0,
        track_id=3,
        driver="HAM"
    )
    
    print("Optimal Strategy:")
    print(f"  Pit on lap: {recommendation['optimal_strategy']['pit_lap']}")
    print(f"  New compound: {recommendation['optimal_strategy']['new_compound']}")
    print(f"  Risk level: {recommendation['optimal_strategy']['risk_level']}")
    """) 