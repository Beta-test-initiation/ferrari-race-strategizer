"""Race data endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.models import TireCompound
from backend.services.live_data_service import get_live_race_data, get_data_source_info

logger = logging.getLogger(__name__)
router = APIRouter(tags=["race"])


# Mock race data - fallback when live data unavailable
CURRENT_RACE_STATE = {
    "race_name": "Abu Dhabi Grand Prix",
    "season": 2025,
    "current_lap": 25,
    "total_laps": 58,
    "race_time": "1:05:32.123",
    "track_temp": 35.5,
    "air_temp": 28.2,
    "weather": "CLEAR",
    "safety_car_active": False,
    "safety_car_laps": 0,
    "status": "RUNNING",
    "drivers": [
        {
            "name": "Hamilton",
            "number": 44,
            "position": 1,
            "lap": 25,
            "lap_time": "1:42.345",
            "tire_compound": "MEDIUM",
            "tire_age": 12,
            "pit_stops": 0,
            "gap": 0.0,
            "gap_to_leader": 0.0,
        },
        {
            "name": "Leclerc",
            "number": 16,
            "position": 2,
            "lap": 25,
            "lap_time": "1:42.912",
            "tire_compound": "MEDIUM",
            "tire_age": 12,
            "pit_stops": 0,
            "gap": 1.234,
            "gap_to_leader": 1.234,
        },
        {
            "name": "Norris",
            "number": 4,
            "position": 3,
            "lap": 25,
            "lap_time": "1:43.102",
            "tire_compound": "SOFT",
            "tire_age": 8,
            "pit_stops": 1,
            "gap": 3.456,
            "gap_to_leader": 3.456,
        },
    ],
}

WEATHER_FORECAST = {
    "current": {
        "temp": 28.2,
        "humidity": 45,
        "wind_speed": 12.5,
        "conditions": "CLEAR",
        "precipitation": 0,
        "pressure": 1013.25,
    },
    "forecast": [
        {
            "time": "14:35",
            "temp": 28.5,
            "conditions": "CLEAR",
            "rain_probability": 5,
            "impact_level": "NONE",
        },
        {
            "time": "14:45",
            "temp": 28.3,
            "conditions": "CLEAR",
            "rain_probability": 5,
            "impact_level": "NONE",
        },
        {
            "time": "14:55",
            "temp": 28.0,
            "conditions": "PARTLY_CLOUDY",
            "rain_probability": 10,
            "impact_level": "LOW",
        },
        {
            "time": "15:05",
            "temp": 27.8,
            "conditions": "PARTLY_CLOUDY",
            "rain_probability": 15,
            "impact_level": "LOW",
        },
        {
            "time": "15:15",
            "temp": 27.5,
            "conditions": "CLOUDY",
            "rain_probability": 25,
            "impact_level": "MEDIUM",
        },
    ],
    "track_impact": {
        "grip_level": "HIGH",
        "tire_wear_factor": 1.0,
        "degradation_rate_change": 0,
        "recommended_tire": "MEDIUM",
        "strategy_impact": "Normal race pace expected",
    },
}


@router.get(
    "/current",
    summary="Get current race state",
    description="Get current race state including driver positions and telemetry",
)
async def get_current_race_state():
    """
    Get current race state.

    Returns:
    - Race information (name, lap progress, etc)
    - Driver positions and telemetry
    - Track conditions
    - Safety car status
    """
    try:
        logger.info("Current race state requested")

        # Try to fetch live data from FastF1
        live_data = get_live_race_data()

        if live_data:
            logger.info("Using live race data from FastF1")
            return {
                **live_data,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data_source": "live",
            }
        else:
            logger.info("Live data unavailable, using mock race data")
            return {
                **CURRENT_RACE_STATE,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data_source": "mock",
            }
    except Exception as e:
        logger.error(f"Error fetching race state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/telemetry",
    summary="Get driver telemetry",
    description="Get detailed telemetry for all drivers",
)
async def get_telemetry():
    """
    Get detailed driver telemetry.

    Returns telemetry for all drivers including:
    - Position and lap progress
    - Tire information
    - Pit stop history
    - Time gaps
    """
    try:
        logger.info("Telemetry requested")
        return {
            "drivers": CURRENT_RACE_STATE["drivers"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/weather",
    summary="Get weather data",
    description="Get current weather and forecast",
)
async def get_weather():
    """
    Get weather information.

    Returns:
    - Current conditions
    - 5-hour forecast
    - Track impact assessment
    - Strategy recommendations
    """
    try:
        logger.info("Weather data requested")
        return {
            **WEATHER_FORECAST,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status",
    summary="Get race status",
    description="Get high-level race status",
)
async def get_race_status():
    """
    Get race status.

    Returns:
    - Current status (RUNNING, PAUSED, FINISHED, etc)
    - Current lap / total laps
    - Race elapsed time
    - Leader information
    """
    try:
        logger.info("Race status requested")
        leader = CURRENT_RACE_STATE["drivers"][0]

        return {
            "status": CURRENT_RACE_STATE["status"],
            "current_lap": CURRENT_RACE_STATE["current_lap"],
            "total_laps": CURRENT_RACE_STATE["total_laps"],
            "race_time": CURRENT_RACE_STATE["race_time"],
            "leader": leader["name"],
            "leader_gap": 0.0,
            "safety_car_active": CURRENT_RACE_STATE["safety_car_active"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Error fetching race status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    description="Check if race data service is operational",
)
async def race_health():
    """Check race data service health."""
    try:
        return {
            "status": "ok",
            "service": "race",
            "data_available": True,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Race service unavailable")


@router.get(
    "/data-source",
    summary="Get data source info",
    description="Check which data source is being used (live FastF1 or mock)",
)
async def get_data_source():
    """Get information about the current data source."""
    try:
        logger.info("Data source info requested")
        return {
            **get_data_source_info(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Error fetching data source info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
