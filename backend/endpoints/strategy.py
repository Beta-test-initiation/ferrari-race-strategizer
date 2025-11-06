"""Strategy recommendation endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from backend.models import (
    RaceStateRequest,
    StrategyRecommendationResponse,
)
from backend.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["strategy"])

# Initialize service
strategy_service = StrategyService()


@router.post(
    "/recommendation",
    response_model=StrategyRecommendationResponse,
    summary="Get strategy recommendation",
    description="Get comprehensive pit stop and strategy recommendation based on current race state",
)
async def get_strategy_recommendation(race_state: RaceStateRequest):
    """
    Get strategy recommendation for current race state.

    - **current_lap**: Current lap number
    - **position**: Current grid position (1-20)
    - **tire_age**: Age of current tires in laps
    - **compound**: Current tire compound (SOFT, MEDIUM, HARD)
    - **track_temp**: Track temperature in Celsius
    - **track_id**: Track identifier
    - **driver**: Driver identifier (HAM, LEC, etc)
    - **gaps_ahead**: List of time gaps to cars ahead
    - **gaps_behind**: List of time gaps to cars behind
    - **total_laps**: Total race laps

    Returns comprehensive strategy recommendation including:
    - Immediate action (pit now/soon/monitor)
    - Optimal pit strategy
    - Scenario analysis
    - Competitor threat assessment
    """
    try:
        logger.info(f"Strategy recommendation requested for {race_state.driver}")
        recommendation = strategy_service.get_strategy_recommendation(race_state)
        return recommendation
    except Exception as e:
        logger.error(f"Error generating strategy recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    description="Check if strategy service is operational",
)
async def strategy_health():
    """Check strategy service health."""
    try:
        return {
            "status": "ok",
            "service": "strategy",
            "models_available": strategy_service.degradation_model is not None,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Strategy service unavailable")
