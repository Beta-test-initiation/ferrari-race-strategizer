"""Live race data service using FastF1."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Cache for live data
_live_data_cache = {
    "race_data": None,
    "last_update": None,
    "cache_duration": 5,  # seconds
}


def get_live_race_data() -> Optional[Dict[str, Any]]:
    """
    Fetch live race data from FastF1 API.

    Returns the current session data or None if unavailable.
    Uses caching to avoid excessive API calls.
    """
    try:
        import fastf1
        import pandas as pd
        from datetime import datetime, timedelta

        # Check cache first
        if _live_data_cache["race_data"] is not None:
            if _live_data_cache["last_update"] is not None:
                elapsed = (datetime.now() - _live_data_cache["last_update"]).total_seconds()
                if elapsed < _live_data_cache["cache_duration"]:
                    logger.debug("Returning cached live data")
                    return _live_data_cache["race_data"]

        logger.info("Fetching live race data from FastF1...")

        # Get latest race session
        # This automatically detects current/latest race
        try:
            session = fastf1.get_session(2025, 'latest', 'R')  # 2025 season, latest race
            session.load()

            logger.info(f"Loaded session: {session.name} - {session.date}")

            # Parse driver data
            drivers = []
            if hasattr(session, 'results'):
                for idx, driver in session.results.iterrows():
                    driver_data = {
                        "name": driver.get('Abbreviation', 'UNK'),
                        "number": int(driver.get('DriverNumber', 0)),
                        "position": int(driver.get('Position', 99)),
                        "lap": int(driver.get('Laps', 0)),
                        "lap_time": str(driver.get('Time', 'N/A')),
                        "tire_compound": str(driver.get('Compound', 'UNKNOWN')).upper(),
                        "tire_age": int(driver.get('TireLife', 0)),
                        "pit_stops": int(driver.get('PitStops', 0)),
                        "gap": float(driver.get('Points', 0)),
                        "gap_to_leader": 0.0,
                    }
                    drivers.append(driver_data)

            # Calculate gaps to leader
            if drivers and len(drivers) > 0:
                for i, driver in enumerate(drivers):
                    if i > 0:
                        # Approximate gap in seconds (simplified)
                        driver["gap_to_leader"] = i * 0.5  # placeholder

            # Get track temp if available
            track_temp = 35.0
            if hasattr(session, 'weather_data'):
                track_temp = session.weather_data.get('TrackTemp', 35.0)

            race_data = {
                "race_name": session.name if hasattr(session, 'name') else "Current Race",
                "season": 2025,
                "current_lap": int(drivers[0].get('lap', 0)) if drivers else 0,
                "total_laps": 58,  # Default, should get from session
                "race_time": datetime.now().isoformat(),
                "track_temp": track_temp,
                "air_temp": 28.2,
                "weather": "CLEAR",
                "safety_car_active": False,
                "safety_car_laps": 0,
                "status": "RUNNING",
                "drivers": drivers,
            }

            # Cache the data
            _live_data_cache["race_data"] = race_data
            _live_data_cache["last_update"] = datetime.now()

            logger.info(f"Successfully fetched live data for {len(drivers)} drivers")
            return race_data

        except Exception as fastf1_error:
            logger.warning(f"FastF1 fetch failed: {fastf1_error}")
            logger.info("Falling back to mock data")
            return None

    except ImportError:
        logger.warning("FastF1 not installed. Install with: pip install fastf1")
        return None
    except Exception as e:
        logger.error(f"Error fetching live race data: {e}")
        return None


def get_live_telemetry(driver_number: int) -> Optional[Dict[str, Any]]:
    """
    Get live telemetry for a specific driver.

    Args:
        driver_number: F1 driver number (e.g., 44 for Hamilton)

    Returns:
        Telemetry data or None if unavailable
    """
    try:
        import fastf1

        session = fastf1.get_session(2025, 'latest', 'R')
        session.load()

        # Get driver telemetry
        if hasattr(session, 'telemetry'):
            driver_telem = session.telemetry[session.telemetry['DriverNumber'] == driver_number]

            if not driver_telem.empty:
                return {
                    "driver_number": driver_number,
                    "telemetry_points": len(driver_telem),
                    "max_speed": float(driver_telem['Speed'].max()),
                    "avg_speed": float(driver_telem['Speed'].mean()),
                    "last_update": datetime.now().isoformat(),
                }

        return None

    except Exception as e:
        logger.error(f"Error fetching driver telemetry: {e}")
        return None


def is_live_data_available() -> bool:
    """Check if live data can be fetched."""
    try:
        import fastf1
        return True
    except ImportError:
        return False


def get_data_source_info() -> Dict[str, Any]:
    """Get information about the data source being used."""
    live_available = is_live_data_available()

    return {
        "live_data_available": live_available,
        "using_fastf1": live_available,
        "data_source": "FastF1 (live)" if live_available else "Mock data",
        "note": "Install FastF1 with: pip install fastf1" if not live_available else None,
    }
