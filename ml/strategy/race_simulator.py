"""
Ferrari F1 Race Simulator

This module simulates complete race scenarios to evaluate different strategic options.
It models lap-by-lap progression, tire degradation, and competitor interactions
to provide comprehensive strategy analysis.

Key Features:
- Full race simulation with multiple pit stop strategies
- Competitor behavior modeling
- Safety car and weather change simulation
- Monte Carlo analysis for uncertainty quantification
- What-if scenario analysis

Usage:
    simulator = RaceSimulator(degradation_model)
    results = simulator.simulate_race_strategies(
        race_config, driver_states, strategy_options
    )
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import random
from dataclasses import dataclass


@dataclass
class DriverState:
    """Represents current state of a driver during race simulation."""
    position: int
    lap_time: float
    tire_age: int
    compound: str
    fuel_load: float
    gap_to_leader: float


@dataclass
class RaceConfig:
    """Configuration for race simulation."""
    track_id: int
    total_laps: int
    track_temp: float
    lap_length: float
    pit_stop_time: float
    safety_car_probability: float
    weather_change_probability: float


class RaceSimulator:
    """
    Advanced race simulation engine for strategy optimization.
    
    Simulates complete races with tire degradation, pit stops, and competitor
    interactions to evaluate strategic options.
    """
    
    def __init__(self, degradation_model):
        """
        Initialize race simulator.
        
        Args:
            degradation_model: Trained TireDegradationPredictor instance
        """
        self.degradation_model = degradation_model
        
        # Simulation parameters
        self.BASE_LAP_TIME = 104.0  # Base lap time in seconds
        self.FUEL_EFFECT = 0.03    # Seconds per kg of fuel
        self.DIRTY_AIR_EFFECT = 0.5  # Seconds lost in dirty air
        self.DRS_ADVANTAGE = 0.3   # DRS advantage in seconds
        self.OVERTAKING_PROBABILITY = 0.15  # Base overtaking probability
        
    def simulate_strategy(self, race_config: RaceConfig, 
                         ferrari_strategy: Dict, competitor_strategies: List[Dict],
                         driver: str = "HAM", num_simulations: int = 100) -> Dict:
        """
        Simulate a specific strategy across multiple race scenarios.
        
        Args:
            race_config (RaceConfig): Race configuration
            ferrari_strategy (Dict): Ferrari pit stop strategy
            competitor_strategies (List[Dict]): Competitor strategies
            driver (str): Ferrari driver
            num_simulations (int): Number of Monte Carlo simulations
            
        Returns:
            Dict: Simulation results with statistics
        """
        results = []
        
        for sim in range(num_simulations):
            # Run single race simulation
            race_result = self._simulate_single_race(
                race_config, ferrari_strategy, competitor_strategies, driver, sim
            )
            results.append(race_result)
        
        # Aggregate results
        return self._aggregate_simulation_results(results, ferrari_strategy)
    
    def _simulate_single_race(self, race_config: RaceConfig, 
                            ferrari_strategy: Dict, competitor_strategies: List[Dict],
                            driver: str, simulation_seed: int) -> Dict:
        """
        Simulate a single race with given strategies.
        
        Returns:
            Dict: Single race simulation result
        """
        # Set random seed for reproducible results
        random.seed(simulation_seed)
        np.random.seed(simulation_seed)
        
        # Initialize race state
        race_state = self._initialize_race_state(race_config, ferrari_strategy, competitor_strategies)
        
        # Initialize Ferrari driver state
        ferrari_state = DriverState(
            position=ferrari_strategy.get('starting_position', 3),
            lap_time=self.BASE_LAP_TIME,
            tire_age=0,
            compound=ferrari_strategy.get('starting_compound', 'MEDIUM'),
            fuel_load=100.0,
            gap_to_leader=0.0
        )
        
        # Track race events
        race_events = []
        lap_times = []
        positions = []
        
        # Simulate lap by lap
        for lap in range(1, race_config.total_laps + 1):
            # Check for race events (safety car, weather)
            events = self._check_race_events(lap, race_config, simulation_seed)
            race_events.extend(events)
            
            # Check for pit stops
            if self._should_pit_this_lap(lap, ferrari_strategy, ferrari_state):
                ferrari_state = self._execute_pit_stop(
                    ferrari_state, ferrari_strategy, race_config, lap
                )
                race_events.append({
                    'lap': lap,
                    'event': 'pit_stop',
                    'compound': ferrari_state.compound
                })
            
            # Calculate lap time with current tire degradation
            lap_time = self._calculate_lap_time(
                ferrari_state, race_config, lap, driver
            )
            
            # Update driver state
            ferrari_state.tire_age += 1
            ferrari_state.fuel_load -= 1.5  # Fuel consumption per lap
            ferrari_state.lap_time = lap_time
            
            # Track progression
            lap_times.append(lap_time)
            positions.append(ferrari_state.position)
            
            # Update position based on performance vs competitors
            ferrari_state.position = self._update_position(
                ferrari_state, lap, competitor_strategies, race_events
            )
        
        return {
            'final_position': ferrari_state.position,
            'total_race_time': sum(lap_times),
            'race_events': race_events,
            'lap_times': lap_times,
            'position_progression': positions,
            'strategy_executed': ferrari_strategy
        }
    
    def _initialize_race_state(self, race_config: RaceConfig, 
                             ferrari_strategy: Dict, competitor_strategies: List[Dict]) -> Dict:
        """
        Initialize race state for simulation.
        
        Returns:
            Dict: Initial race state
        """
        return {
            'safety_car_laps': [],
            'weather_changes': [],
            'competitor_pit_stops': {},
            'current_lap': 0
        }
    
    def _should_pit_this_lap(self, lap: int, strategy: Dict, driver_state: DriverState) -> bool:
        """
        Determine if Ferrari should pit on this lap.
        
        Returns:
            bool: True if should pit this lap
        """
        pit_laps = strategy.get('pit_laps', [])
        return lap in pit_laps
    
    def _execute_pit_stop(self, driver_state: DriverState, strategy: Dict, 
                         race_config: RaceConfig, lap: int) -> DriverState:
        """
        Execute pit stop and update driver state.
        
        Returns:
            DriverState: Updated driver state after pit stop
        """
        # Get new compound from strategy
        pit_laps = strategy.get('pit_laps', [])
        compounds = strategy.get('compounds', ['MEDIUM'])
        
        if lap in pit_laps:
            pit_index = pit_laps.index(lap)
            new_compound = compounds[min(pit_index + 1, len(compounds) - 1)]
        else:
            new_compound = driver_state.compound
        
        # Update state
        driver_state.compound = new_compound
        driver_state.tire_age = 0
        driver_state.lap_time += race_config.pit_stop_time
        
        # Position loss due to pit stop
        positions_lost = self._calculate_pit_stop_position_loss(
            driver_state, race_config.pit_stop_time
        )
        driver_state.position += positions_lost
        
        return driver_state
    
    def _calculate_lap_time(self, driver_state: DriverState, race_config: RaceConfig,
                          lap: int, driver: str) -> float:
        """
        Calculate lap time based on current conditions.
        
        Returns:
            float: Predicted lap time in seconds
        """
        # Get tire degradation prediction
        degradation_prediction = self.degradation_model.predict_degradation(
            track_temp=race_config.track_temp,
            compound=driver_state.compound,
            stint_length=driver_state.tire_age,
            track_id=race_config.track_id,
            driver=driver
        )
        
        # Base lap time
        base_time = self.BASE_LAP_TIME
        
        # Add tire degradation
        tire_degradation = degradation_prediction['degradation_rate'] * driver_state.tire_age
        
        # Add fuel effect
        fuel_effect = driver_state.fuel_load * self.FUEL_EFFECT
        
        # Add track position effects (dirty air, etc.)
        position_effect = self._calculate_position_effect(driver_state.position)
        
        # Add random variation
        random_variation = np.random.normal(0, 0.2)  # ±0.2 second variation
        
        total_lap_time = base_time + tire_degradation + fuel_effect + position_effect + random_variation
        
        return max(total_lap_time, base_time * 0.95)  # Minimum lap time constraint
    
    def _calculate_position_effect(self, position: int) -> float:
        """
        Calculate lap time effect based on track position.
        
        Returns:
            float: Time effect in seconds
        """
        if position == 1:
            return 0.0  # Clear air
        elif position <= 3:
            return 0.1  # Minimal dirty air
        elif position <= 6:
            return 0.3  # Moderate dirty air
        else:
            return 0.5  # Heavy traffic
    
    def _calculate_pit_stop_position_loss(self, driver_state: DriverState, 
                                        pit_stop_time: float) -> int:
        """
        Calculate positions lost due to pit stop.
        
        Returns:
            int: Number of positions lost
        """
        # Simplified position loss calculation
        # Based on pit stop time and gaps to other cars
        base_loss = int(pit_stop_time / 25.0)  # Rough estimate
        
        # Add randomness for other cars' strategies
        additional_loss = random.randint(0, 2)
        
        return min(base_loss + additional_loss, 5)  # Max 5 positions lost
    
    def _update_position(self, driver_state: DriverState, lap: int,
                        competitor_strategies: List[Dict], race_events: List[Dict]) -> int:
        """
        Update driver position based on relative performance.
        
        Returns:
            int: Updated position
        """
        # Simplified position update based on lap time performance
        current_position = driver_state.position
        
        # Check for overtaking opportunities
        if driver_state.lap_time < self.BASE_LAP_TIME + 0.2:  # Fast lap
            if random.random() < self.OVERTAKING_PROBABILITY and current_position > 1:
                current_position -= 1  # Gain position
        
        # Check for being overtaken
        elif driver_state.lap_time > self.BASE_LAP_TIME + 0.5:  # Slow lap
            if random.random() < self.OVERTAKING_PROBABILITY and current_position < 20:
                current_position += 1  # Lose position
        
        return max(1, min(current_position, 20))  # Keep in valid range
    
    def _check_race_events(self, lap: int, race_config: RaceConfig, 
                          simulation_seed: int) -> List[Dict]:
        """
        Check for random race events (safety car, weather changes).
        
        Returns:
            List[Dict]: List of race events this lap
        """
        events = []
        
        # Safety car probability
        if random.random() < race_config.safety_car_probability / race_config.total_laps:
            events.append({
                'lap': lap,
                'event': 'safety_car',
                'duration': random.randint(3, 8)
            })
        
        # Weather change probability
        if random.random() < race_config.weather_change_probability / race_config.total_laps:
            temp_change = random.uniform(-5, 5)
            events.append({
                'lap': lap,
                'event': 'weather_change',
                'temperature_change': temp_change
            })
        
        return events
    
    def _aggregate_simulation_results(self, results: List[Dict], 
                                    strategy: Dict) -> Dict:
        """
        Aggregate results from multiple simulations.
        
        Returns:
            Dict: Aggregated statistics
        """
        final_positions = [r['final_position'] for r in results]
        race_times = [r['total_race_time'] for r in results]
        
        # Calculate statistics
        stats = {
            'strategy': strategy,
            'simulations_run': len(results),
            'average_finish_position': np.mean(final_positions),
            'median_finish_position': np.median(final_positions),
            'position_std': np.std(final_positions),
            'best_finish': min(final_positions),
            'worst_finish': max(final_positions),
            'podium_probability': sum(1 for p in final_positions if p <= 3) / len(results),
            'points_probability': sum(1 for p in final_positions if p <= 10) / len(results),
            'average_race_time': np.mean(race_times),
            'race_time_std': np.std(race_times),
            'position_distribution': self._calculate_position_distribution(final_positions),
            'success_rate': sum(1 for p in final_positions if p <= strategy.get('target_position', 5)) / len(results)
        }
        
        return stats
    
    def _calculate_position_distribution(self, positions: List[int]) -> Dict:
        """
        Calculate distribution of finishing positions.
        
        Returns:
            Dict: Position distribution
        """
        distribution = {}
        for pos in range(1, 21):  # Positions 1-20
            count = sum(1 for p in positions if p == pos)
            distribution[pos] = count / len(positions)
        
        return distribution
    
    def compare_strategies(self, race_config: RaceConfig, 
                         strategies: List[Dict], driver: str = "HAM",
                         num_simulations: int = 100) -> Dict:
        """
        Compare multiple strategies using race simulation.
        
        Args:
            race_config (RaceConfig): Race configuration
            strategies (List[Dict]): List of strategies to compare
            driver (str): Ferrari driver
            num_simulations (int): Simulations per strategy
            
        Returns:
            Dict: Strategy comparison results
        """
        comparison_results = {}
        
        for i, strategy in enumerate(strategies):
            strategy_name = f"Strategy_{i+1}"
            
            # Simulate this strategy
            results = self.simulate_strategy(
                race_config, strategy, [], driver, num_simulations
            )
            
            comparison_results[strategy_name] = results
        
        # Find best strategy
        best_strategy = min(
            comparison_results.items(),
            key=lambda x: x[1]['average_finish_position']
        )
        
        return {
            'strategy_results': comparison_results,
            'best_strategy': best_strategy[0],
            'best_strategy_results': best_strategy[1],
            'ranking': self._rank_strategies(comparison_results)
        }
    
    def _rank_strategies(self, results: Dict) -> List[Tuple[str, float]]:
        """
        Rank strategies by expected performance.
        
        Returns:
            List[Tuple[str, float]]: Ranked strategies with scores
        """
        rankings = []
        
        for strategy_name, stats in results.items():
            # Calculate composite score
            position_score = stats['average_finish_position']
            podium_bonus = stats['podium_probability'] * 2
            consistency_bonus = 1.0 / (stats['position_std'] + 0.1)
            
            composite_score = position_score - podium_bonus - consistency_bonus
            rankings.append((strategy_name, composite_score))
        
        # Sort by score (lower is better)
        rankings.sort(key=lambda x: x[1])
        
        return rankings


# Example usage and testing
if __name__ == "__main__":
    print("Ferrari Race Simulator - Example Usage")
    print("=" * 50)
    
    print("To use this simulator:")
    print("1. Create RaceConfig with track parameters")
    print("2. Define Ferrari and competitor strategies")
    print("3. Run simulations to compare strategies")
    print("\nExample code:")
    print("""
    from ml.models.degradation_predictor import TireDegradationPredictor
    from ml.strategy.race_simulator import RaceSimulator, RaceConfig
    
    # Load model and create simulator
    predictor = TireDegradationPredictor()
    predictor.load_model("ml/saved_models/ferrari_degradation_model.pkl")
    simulator = RaceSimulator(predictor)
    
    # Configure race
    race_config = RaceConfig(
        track_id=3,
        total_laps=60,
        track_temp=35.0,
        lap_length=5.0,
        pit_stop_time=22.0,
        safety_car_probability=0.15,
        weather_change_probability=0.1
    )
    
    # Define strategies
    strategies = [
        {
            'name': '1-stop',
            'pit_laps': [30],
            'compounds': ['MEDIUM', 'HARD'],
            'starting_position': 3
        },
        {
            'name': '2-stop',
            'pit_laps': [20, 40],
            'compounds': ['MEDIUM', 'MEDIUM', 'SOFT'],
            'starting_position': 3
        }
    ]
    
    # Compare strategies
    comparison = simulator.compare_strategies(race_config, strategies)
    print(f"Best strategy: {comparison['best_strategy']}")
    """) 