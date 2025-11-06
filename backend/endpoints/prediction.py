"""Tire degradation prediction endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from backend.models import (
    DegradationPredictionRequest,
    DegradationPredictionResponse,
)
from backend.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["prediction"])

# Initialize service
strategy_service = StrategyService()


@router.post(
    "/degradation",
    response_model=DegradationPredictionResponse,
    summary="Predict tire degradation",
    description="Predict tire degradation rate for given track and tire conditions",
)
async def predict_degradation(request: DegradationPredictionRequest):
    """
    Predict tire degradation for given conditions.

    - **track_temp**: Track temperature in Celsius
    - **compound**: Tire compound (SOFT, MEDIUM, HARD)
    - **stint_length**: Length of stint in laps
    - **track_id**: Track identifier
    - **driver**: Driver identifier

    Returns:
    - Degradation rate (seconds per lap)
    - Confidence intervals
    - Risk assessment
    - Estimated stint duration
    - Pit stop recommendation
    """
    try:
        logger.info(f"Degradation prediction requested for {request.compound} compound")
        result = strategy_service.predict_degradation(request)

        return DegradationPredictionResponse(
            degradation_rate=result["degradation_rate"],
            confidence_interval_lower=result["confidence_interval_lower"],
            confidence_interval_upper=result["confidence_interval_upper"],
            risk_level=result["risk_level"],
            estimated_stint_duration=result["estimated_stint_duration"],
            recommendation=result["recommendation"],
            timestamp=result["timestamp"],
        )
    except Exception as e:
        logger.error(f"Error predicting degradation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    description="Check if prediction service is operational",
)
async def prediction_health():
    """Check prediction service health."""
    try:
        return {
            "status": "ok",
            "service": "prediction",
            "models_available": strategy_service.degradation_model is not None,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Prediction service unavailable")
