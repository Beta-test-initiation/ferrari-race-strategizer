"""Pydantic models for request/response validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums
class TireCompound(str, Enum):
    """Tire compound types."""
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class UrgencyLevel(str, Enum):
    """Urgency levels for recommendations."""
    IMMEDIATE = "IMMEDIATE"
    SOON = "SOON"
    MONITOR = "MONITOR"
    LOW = "LOW"


class RiskLevel(str, Enum):
    """Risk levels for strategies."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ThreatLevel(str, Enum):
    """Threat levels for competitors."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# Request Models

class RaceStateRequest(BaseModel):
    """Current race state information."""

    current_lap: int = Field(..., ge=1, le=100, description="Current lap number")
    position: int = Field(..., ge=1, le=20, description="Current position (1-20)")
    tire_age: int = Field(..., ge=0, le=100, description="Age of current tires in laps")
    compound: TireCompound = Field(..., description="Current tire compound")
    track_temp: float = Field(..., ge=0, le=100, description="Track temperature in Celsius")
    track_id: int = Field(..., ge=1, description="Track identifier")
    driver: str = Field(..., description="Driver name (HAM, LEC, etc)")
    gaps_ahead: List[float] = Field(default=[], description="Time gaps to cars ahead (seconds)")
    gaps_behind: List[float] = Field(default=[], description="Time gaps to cars behind (seconds)")
    total_laps: int = Field(..., ge=10, le=100, description="Total race laps")
    fuel_load: Optional[float] = Field(default=None, description="Current fuel load in kg")
    drs_available: Optional[bool] = Field(default=False, description="Is DRS available")

    class Config:
        json_schema_extra = {
            "example": {
                "current_lap": 25,
                "position": 3,
                "tire_age": 20,
                "compound": "MEDIUM",
                "track_temp": 35.0,
                "track_id": 1,
                "driver": "HAM",
                "gaps_ahead": [2.1, 5.7],
                "gaps_behind": [3.2, 8.9],
                "total_laps": 58,
            }
        }


class DegradationPredictionRequest(BaseModel):
    """Request for tire degradation prediction."""

    track_temp: float = Field(..., ge=0, le=100, description="Track temperature in Celsius")
    compound: TireCompound = Field(..., description="Tire compound")
    stint_length: int = Field(..., ge=1, le=100, description="Length of stint in laps")
    track_id: int = Field(..., ge=1, description="Track identifier")
    driver: str = Field(..., description="Driver name")
    humidity: Optional[float] = Field(default=50, ge=0, le=100, description="Humidity percentage")
    wind_speed: Optional[float] = Field(default=0, ge=0, description="Wind speed in km/h")

    class Config:
        json_schema_extra = {
            "example": {
                "track_temp": 35.0,
                "compound": "MEDIUM",
                "stint_length": 20,
                "track_id": 1,
                "driver": "HAM",
            }
        }


class RaceSimulationRequest(BaseModel):
    """Request for race simulation."""

    race_state: RaceStateRequest = Field(..., description="Current race state")
    strategy_name: str = Field(..., description="Strategy name to simulate")
    pit_lap: int = Field(..., ge=1, description="Pit stop lap")
    new_compound: TireCompound = Field(..., description="New tire compound after pit")
    num_simulations: int = Field(default=100, ge=10, le=1000, description="Number of Monte Carlo simulations")

    class Config:
        json_schema_extra = {
            "example": {
                "race_state": {
                    "current_lap": 25,
                    "position": 3,
                    "tire_age": 20,
                    "compound": "MEDIUM",
                    "track_temp": 35.0,
                    "track_id": 1,
                    "driver": "HAM",
                    "gaps_ahead": [2.1, 5.7],
                    "gaps_behind": [3.2, 8.9],
                    "total_laps": 58,
                },
                "strategy_name": "AGGRESSIVE_UNDERCUT",
                "pit_lap": 28,
                "new_compound": "HARD",
                "num_simulations": 100,
            }
        }


# Response Models

class ImmediateAction(BaseModel):
    """Immediate action recommendation."""

    recommendation: str = Field(..., description="Recommendation text")
    urgency: UrgencyLevel = Field(..., description="Urgency level")
    confidence: int = Field(..., ge=0, le=100, description="Confidence percentage")
    reason: Optional[str] = Field(default=None, description="Explanation for recommendation")


class OptimalStrategy(BaseModel):
    """Optimal strategy details."""

    pit_lap: int = Field(..., description="Recommended pit lap")
    new_compound: TireCompound = Field(..., description="Recommended tire compound")
    expected_position_gain: float = Field(..., description="Expected position change")
    expected_time_gain: float = Field(..., description="Expected time gain in seconds")
    confidence: int = Field(..., ge=0, le=100, description="Strategy confidence")
    risk_level: RiskLevel = Field(..., description="Risk assessment")
    weather_impact: Optional[str] = Field(default=None, description="Weather impact on strategy")


class ScenarioOutcome(BaseModel):
    """Outcome for a specific scenario."""

    final_position: int = Field(..., description="Predicted final position")
    final_position_distribution: Dict[str, float] = Field(..., description="Position distribution")
    probability: float = Field(..., ge=0, le=1, description="Probability of this outcome")
    race_time: Optional[str] = Field(default=None, description="Estimated race time")
    points: Optional[int] = Field(default=None, description="Expected points")


class CompetitorThreat(BaseModel):
    """Competitor threat analysis."""

    driver: str = Field(..., description="Competitor driver name")
    position: int = Field(..., description="Current position")
    gap: float = Field(..., description="Gap to us in seconds")
    current_compound: TireCompound = Field(..., description="Current tire compound")
    threat_level: ThreatLevel = Field(..., description="Threat assessment")
    critical_move: Optional[str] = Field(default=None, description="Expected critical move")


class StrategyRecommendationResponse(BaseModel):
    """Complete strategy recommendation response."""

    immediate_action: ImmediateAction = Field(..., description="Immediate action")
    optimal_strategy: OptimalStrategy = Field(..., description="Optimal pit strategy")
    scenario_analysis: Dict[str, ScenarioOutcome] = Field(..., description="Multiple scenarios analyzed")
    competitor_response: Dict[str, Any] = Field(..., description="Competitor analysis")
    timestamp: str = Field(..., description="Timestamp of recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "immediate_action": {
                    "recommendation": "MONITOR",
                    "urgency": "SOON",
                    "confidence": 78,
                    "reason": "Tire degradation is manageable for 3 more laps",
                },
                "optimal_strategy": {
                    "pit_lap": 28,
                    "new_compound": "HARD",
                    "expected_position_gain": 1.0,
                    "expected_time_gain": 2.3,
                    "confidence": 82,
                    "risk_level": "MEDIUM",
                },
                "scenario_analysis": {
                    "pit_now": {"final_position": 2, "final_position_distribution": {"1": 0.45, "2": 0.45, "3": 0.1}, "probability": 0.45},
                    "pit_in_3_laps": {"final_position": 1, "final_position_distribution": {"1": 0.62, "2": 0.30, "3": 0.08}, "probability": 0.62},
                    "continue_full_stint": {"final_position": 4, "final_position_distribution": {"3": 0.28, "4": 0.50, "5": 0.22}, "probability": 0.28},
                },
                "competitor_response": {
                    "threat_level": "MEDIUM",
                    "critical_competitors": ["Norris", "Russell"],
                },
                "timestamp": "2025-11-05T14:32:10Z",
            }
        }


class DegradationPredictionResponse(BaseModel):
    """Tire degradation prediction response."""

    degradation_rate: float = Field(..., description="Degradation rate in seconds per lap")
    confidence_interval_lower: float = Field(..., description="Lower confidence bound")
    confidence_interval_upper: float = Field(..., description="Upper confidence bound")
    risk_level: RiskLevel = Field(..., description="Risk level assessment")
    estimated_stint_duration: int = Field(..., description="Estimated stint duration in laps")
    recommendation: str = Field(..., description="Recommendation text")
    timestamp: str = Field(..., description="Timestamp of prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "degradation_rate": 0.042,
                "confidence_interval_lower": 0.038,
                "confidence_interval_upper": 0.046,
                "risk_level": "MEDIUM",
                "estimated_stint_duration": 28,
                "recommendation": "Consider pit stop around lap 28-30",
                "timestamp": "2025-11-05T14:32:10Z",
            }
        }


class RaceSimulationResponse(BaseModel):
    """Race simulation response."""

    strategy_name: str = Field(..., description="Strategy name")
    final_position_distribution: List[float] = Field(..., description="Distribution of final positions")
    win_probability: float = Field(..., ge=0, le=1, description="Probability of winning")
    podium_probability: float = Field(..., ge=0, le=1, description="Probability of podium")
    points_expected: float = Field(..., description="Expected points")
    finish_time_estimate: Optional[str] = Field(default=None, description="Estimated finish time")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in simulation")
    timestamp: str = Field(..., description="Timestamp of simulation")

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_name": "AGGRESSIVE_UNDERCUT",
                "final_position_distribution": [0.45, 0.35, 0.15, 0.05],
                "win_probability": 0.45,
                "podium_probability": 0.95,
                "points_expected": 18.5,
                "finish_time_estimate": "1:45:32.123",
                "confidence": 0.78,
                "timestamp": "2025-11-05T14:32:10Z",
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="Error timestamp")


# WebSocket Models

class LiveAlert(BaseModel):
    """Live alert for WebSocket."""

    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    driver: Optional[str] = Field(default=None, description="Affected driver")
    timestamp: str = Field(..., description="Alert timestamp")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: str = Field(..., description="Message timestamp")
