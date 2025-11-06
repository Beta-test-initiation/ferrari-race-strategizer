"""Strategy service - interfaces with Python ML modules."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

from backend.models import (
    RaceStateRequest,
    DegradationPredictionRequest,
    RaceSimulationRequest,
    StrategyRecommendationResponse,
    ImmediateAction,
    OptimalStrategy,
    ScenarioOutcome,
    UrgencyLevel,
    RiskLevel,
)
from backend.dependencies import get_degradation_model

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class StrategyService:
    """Service layer for strategy operations."""

    def __init__(self):
        """Initialize strategy service."""
        self.degradation_model = get_degradation_model()
        self._initialize_ml_modules()

    def _initialize_ml_modules(self):
        """Initialize ML modules."""
        try:
            from ml.strategy.strategy_engine import StrategyEngine
            from ml.models.degradation_predictor import TireDegradationPredictor

            self.StrategyEngine = StrategyEngine
            self.TireDegradationPredictor = TireDegradationPredictor
            logger.info("ML modules initialized successfully")
        except Exception as e:
            logger.warning(f"Could not import ML modules: {e}")
            self.StrategyEngine = None
            self.TireDegradationPredictor = None

    def predict_degradation(
        self, request: DegradationPredictionRequest
    ) -> Dict[str, Any]:
        """Predict tire degradation for given conditions."""
        logger.info(
            f"Predicting degradation for {request.compound} at {request.track_temp}°C"
        )

        try:
            if self.degradation_model is None:
                logger.warning("Degradation model not loaded - using fallback")
                return self._fallback_degradation_prediction(request)

            # Use the loaded model for prediction
            degradation_rate = self.degradation_model.predict_degradation(
                track_temp=request.track_temp,
                compound=request.compound.value,
                stint_length=request.stint_length,
                track_id=request.track_id,
                driver=request.driver,
            )

            # Estimate stint duration based on degradation
            estimated_stint = max(
                15, int(80 / (degradation_rate + 0.01)) if degradation_rate > 0 else 30
            )

            return {
                "degradation_rate": float(degradation_rate),
                "confidence_interval_lower": float(degradation_rate * 0.9),
                "confidence_interval_upper": float(degradation_rate * 1.1),
                "risk_level": self._assess_risk_level(degradation_rate),
                "estimated_stint_duration": estimated_stint,
                "recommendation": self._get_degradation_recommendation(degradation_rate),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        except Exception as e:
            logger.error(f"Error predicting degradation: {e}")
            raise

    def get_strategy_recommendation(
        self, race_state: RaceStateRequest
    ) -> StrategyRecommendationResponse:
        """Get comprehensive strategy recommendation."""
        logger.info(f"Getting strategy recommendation for {race_state.driver} at lap {race_state.current_lap}")

        try:
            # Predict current tire degradation
            degradation_pred = self.predict_degradation(
                DegradationPredictionRequest(
                    track_temp=race_state.track_temp,
                    compound=race_state.compound,
                    stint_length=race_state.tire_age,
                    track_id=race_state.track_id,
                    driver=race_state.driver,
                )
            )

            # Determine immediate action
            immediate_action = self._determine_immediate_action(
                race_state, degradation_pred
            )

            # Calculate optimal pit strategy
            optimal_strategy = self._calculate_optimal_strategy(
                race_state, degradation_pred
            )

            # Analyze multiple scenarios
            scenario_analysis = self._analyze_scenarios(race_state, optimal_strategy)

            # Analyze competitor threats
            competitor_response = self._analyze_competitors(race_state)

            return StrategyRecommendationResponse(
                immediate_action=immediate_action,
                optimal_strategy=optimal_strategy,
                scenario_analysis=scenario_analysis,
                competitor_response=competitor_response,
                timestamp=datetime.utcnow().isoformat() + "Z",
            )

        except Exception as e:
            logger.error(f"Error getting strategy recommendation: {e}")
            raise

    def simulate_race(self, request: RaceSimulationRequest) -> Dict[str, Any]:
        """Simulate race with given strategy."""
        logger.info(
            f"Simulating race strategy: {request.strategy_name} with pit at lap {request.pit_lap}"
        )

        try:
            # Basic race simulation logic
            # In production, would call actual RaceSimulator from ML pipeline
            race_state = request.race_state

            # Simple probability calculation based on pit timing
            current_gap_to_leader = sum(race_state.gaps_ahead) if race_state.gaps_ahead else 5.0
            pit_timing_quality = self._assess_pit_timing(
                race_state.current_lap,
                request.pit_lap,
                race_state.total_laps,
            )

            # Simulate outcomes
            win_prob = max(0.05, 0.7 * pit_timing_quality)
            podium_prob = max(0.3, 0.9 * pit_timing_quality)

            # Position distribution (simplified)
            position_distribution = [
                win_prob,
                podium_prob - win_prob,
                0.3 - (podium_prob - win_prob),
                0.2,
            ]

            return {
                "strategy_name": request.strategy_name,
                "final_position_distribution": position_distribution[:4],
                "win_probability": win_prob,
                "podium_probability": podium_prob,
                "points_expected": self._calculate_expected_points(position_distribution),
                "finish_time_estimate": self._estimate_finish_time(
                    race_state.total_laps, race_state.current_lap
                ),
                "confidence": pit_timing_quality,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        except Exception as e:
            logger.error(f"Error simulating race: {e}")
            raise

    def _determine_immediate_action(
        self, race_state: RaceStateRequest, degradation_pred: Dict[str, Any]
    ) -> ImmediateAction:
        """Determine immediate action based on tire state."""
        degradation_rate = degradation_pred["degradation_rate"]
        tire_age = race_state.tire_age

        # Simple heuristic: pit if tires are old and degrading fast
        laps_to_critical = max(2, int(15 / (degradation_rate + 0.01)))

        if tire_age >= laps_to_critical - 2:
            return ImmediateAction(
                recommendation="PIT SOON",
                urgency=UrgencyLevel.SOON,
                confidence=80,
                reason=f"Tire degradation accelerating after {tire_age} laps",
            )
        elif tire_age >= laps_to_critical:
            return ImmediateAction(
                recommendation="PIT NOW",
                urgency=UrgencyLevel.IMMEDIATE,
                confidence=85,
                reason="Critical tire wear detected",
            )
        else:
            return ImmediateAction(
                recommendation="MONITOR",
                urgency=UrgencyLevel.MONITOR,
                confidence=75,
                reason="Tires performing within expected parameters",
            )

    def _calculate_optimal_strategy(
        self, race_state: RaceStateRequest, degradation_pred: Dict[str, Any]
    ) -> OptimalStrategy:
        """Calculate optimal pit strategy."""
        estimated_stint = degradation_pred["estimated_stint_duration"]
        optimal_pit_lap = race_state.current_lap + max(2, int(estimated_stint * 0.6))

        # Determine best compound for next stint
        next_compound = "HARD" if race_state.current_lap > race_state.total_laps * 0.7 else "SOFT"

        # Simple position gain estimation
        pit_loss = 22  # seconds pit stop time
        drs_advantage = 0.3  # seconds per lap
        laps_gained_back = max(1, int(pit_loss / drs_advantage))
        position_gain = min(2, int(len(race_state.gaps_behind) / 3))

        return OptimalStrategy(
            pit_lap=optimal_pit_lap,
            new_compound=next_compound,
            expected_position_gain=position_gain,
            expected_time_gain=2.3,
            confidence=78,
            risk_level=RiskLevel.MEDIUM,
            weather_impact="No significant weather impact expected",
        )

    def _analyze_scenarios(
        self, race_state: RaceStateRequest, optimal_strategy: OptimalStrategy
    ) -> Dict[str, ScenarioOutcome]:
        """Analyze different race scenarios."""
        scenarios = {}

        # Scenario 1: Pit now
        scenarios["pit_now"] = ScenarioOutcome(
            final_position=2,
            final_position_distribution={"1": 0.45, "2": 0.45, "3": 0.1},
            probability=0.45,
            points=18,
        )

        # Scenario 2: Pit at optimal time
        scenarios["pit_optimal"] = ScenarioOutcome(
            final_position=1,
            final_position_distribution={"1": 0.62, "2": 0.30, "3": 0.08},
            probability=0.62,
            points=25,
        )

        # Scenario 3: Continue full stint
        scenarios["continue_full_stint"] = ScenarioOutcome(
            final_position=4,
            final_position_distribution={"3": 0.28, "4": 0.50, "5": 0.22},
            probability=0.28,
            points=8,
        )

        return scenarios

    def _analyze_competitors(self, race_state: RaceStateRequest) -> Dict[str, Any]:
        """Analyze competitor threats."""
        competitors = [
            {"name": "Norris", "gap": 2.1, "threat": "HIGH"},
            {"name": "Russell", "gap": 5.7, "threat": "MEDIUM"},
            {"name": "Piastri", "gap": 8.9, "threat": "MEDIUM"},
            {"name": "Sainz", "gap": 12.3, "threat": "LOW"},
        ]

        return {
            "threat_level": "MEDIUM",
            "critical_competitors": ["Norris", "Russell"],
            "competitors": competitors,
        }

    def _assess_risk_level(self, degradation_rate: float) -> str:
        """Assess risk level based on degradation rate."""
        if degradation_rate < 0.02:
            return RiskLevel.LOW
        elif degradation_rate < 0.05:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _get_degradation_recommendation(self, degradation_rate: float) -> str:
        """Get recommendation text based on degradation rate."""
        if degradation_rate < 0.02:
            return "Tires are performing well - consider extending this stint"
        elif degradation_rate < 0.05:
            return "Normal degradation - consider pit stop around optimal window"
        else:
            return "High degradation - pit stop recommended soon"

    def _assess_pit_timing(
        self, current_lap: int, pit_lap: int, total_laps: int
    ) -> float:
        """Assess quality of pit timing."""
        laps_remaining_after_pit = total_laps - pit_lap
        optimal_remaining = total_laps * 0.4

        if laps_remaining_after_pit < 5:
            return 0.5  # Too late to pit
        elif abs(laps_remaining_after_pit - optimal_remaining) < 5:
            return 0.9  # Good timing
        else:
            return 0.7  # Acceptable

    def _calculate_expected_points(self, position_distribution: list) -> float:
        """Calculate expected points from position distribution."""
        points_table = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        expected = 0.0

        for i, prob in enumerate(position_distribution):
            if i < len(points_table):
                expected += prob * points_table[i]

        return expected

    def _estimate_finish_time(self, total_laps: int, current_lap: int) -> str:
        """Estimate race finish time."""
        avg_lap_time = 105  # seconds
        laps_remaining = total_laps - current_lap
        seconds_remaining = laps_remaining * avg_lap_time

        hours = int(seconds_remaining // 3600)
        minutes = int((seconds_remaining % 3600) // 60)
        seconds = int(seconds_remaining % 60)

        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _fallback_degradation_prediction(
        self, request: DegradationPredictionRequest
    ) -> Dict[str, Any]:
        """Fallback prediction when model is not available."""
        logger.info("Using fallback degradation prediction")

        # Simple heuristic based on compound and temperature
        base_degradation = {
            "SOFT": 0.08,
            "MEDIUM": 0.05,
            "HARD": 0.03,
        }

        compound_degradation = base_degradation.get(request.compound.value, 0.05)
        temp_factor = 1.0 + (request.track_temp - 30) * 0.01
        degradation_rate = compound_degradation * temp_factor

        return {
            "degradation_rate": float(degradation_rate),
            "confidence_interval_lower": float(degradation_rate * 0.8),
            "confidence_interval_upper": float(degradation_rate * 1.2),
            "risk_level": self._assess_risk_level(degradation_rate),
            "estimated_stint_duration": max(15, int(80 / (degradation_rate + 0.01))),
            "recommendation": self._get_degradation_recommendation(degradation_rate),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
