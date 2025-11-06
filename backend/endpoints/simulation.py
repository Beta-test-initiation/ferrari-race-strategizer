"""Race simulation endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from backend.models import (
    RaceSimulationRequest,
    RaceSimulationResponse,
)
from backend.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["simulation"])

# Initialize service
strategy_service = StrategyService()


@router.post(
    "/race",
    response_model=RaceSimulationResponse,
    summary="Simulate race scenario",
    description="Run Monte Carlo simulation for a specific strategy",
)
async def simulate_race(request: RaceSimulationRequest):
    """
    Simulate race with given strategy using Monte Carlo methods.

    - **race_state**: Current race state
    - **strategy_name**: Strategy name to simulate
    - **pit_lap**: Lap number for pit stop
    - **new_compound**: Tire compound for next stint
    - **num_simulations**: Number of Monte Carlo simulations (10-1000)

    Returns:
    - Position distribution
    - Win probability
    - Podium probability
    - Expected points
    - Confidence level
    """
    try:
        logger.info(f"Race simulation requested: {request.strategy_name}")
        result = strategy_service.simulate_race(request)

        return RaceSimulationResponse(
            strategy_name=result["strategy_name"],
            final_position_distribution=result["final_position_distribution"],
            win_probability=result["win_probability"],
            podium_probability=result["podium_probability"],
            points_expected=result["points_expected"],
            finish_time_estimate=result.get("finish_time_estimate"),
            confidence=result["confidence"],
            timestamp=result["timestamp"],
        )
    except Exception as e:
        logger.error(f"Error simulating race: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/compare-strategies",
    summary="Compare multiple strategies",
    description="Compare outcomes of multiple strategies",
)
async def compare_strategies(requests: list[RaceSimulationRequest]):
    """
    Compare multiple race strategies.

    Returns comparison of all strategies with outcomes for each.
    """
    try:
        logger.info(f"Comparing {len(requests)} strategies")
        results = []

        for request in requests:
            result = strategy_service.simulate_race(request)
            results.append(result)

        return {
            "strategies": results,
            "best_strategy": max(results, key=lambda x: x["win_probability"]),
            "timestamp": results[0]["timestamp"] if results else None,
        }
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    description="Check if simulation service is operational",
)
async def simulation_health():
    """Check simulation service health."""
    try:
        return {
            "status": "ok",
            "service": "simulation",
            "ready": True,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Simulation service unavailable")
