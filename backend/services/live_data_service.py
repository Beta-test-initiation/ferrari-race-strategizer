"""Live race data service using FastF1 and livetiming."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import subprocess
import json

logger = logging.getLogger(__name__)

# Cache for live data
_live_data_cache = {
    "race_data": None,
    "last_update": None,
    "cache_duration": 5,  # seconds
    "livetiming_process": None,  # Store recording process
    "livetiming_file": None,  # Store recording file path
}


def get_live_race_data(race_round: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch live race data from FastF1 API.

    Args:
        race_round: Specific race round to load (1-24). If None, uses FASTF1_RACE env var or finds latest.

    Returns the current session data or None if unavailable.
    Uses caching to avoid excessive API calls.

    Environment Variables:
        FASTF1_RACE: Race round number to load (1-24)
        USE_MOCK_VEGAS: Set to "true" to force Vegas mock data
    """
    try:
        import fastf1
        import pandas as pd
        from datetime import datetime, timedelta

        # Check if user wants to force mock Vegas data
        if os.getenv('USE_MOCK_VEGAS', '').lower() == 'true':
            logger.info("USE_MOCK_VEGAS enabled - returning None to use mock data")
            return None

        # Priority 0: Try to read live timing data (if Vegas race is happening)
        live_timing_file = os.getenv('FASTF1_LIVETIMING_FILE', '/tmp/vegas_live_22.jsonl')
        live_timing_data = read_live_timing_data(live_timing_file)
        if live_timing_data:
            logger.info("✓ Using live timing data from FastF1 livetiming module")
            # Cache it
            _live_data_cache["race_data"] = live_timing_data
            _live_data_cache["last_update"] = datetime.now()
            return live_timing_data

        # Check cache first
        if _live_data_cache["race_data"] is not None:
            if _live_data_cache["last_update"] is not None:
                elapsed = (datetime.now() - _live_data_cache["last_update"]).total_seconds()
                if elapsed < _live_data_cache["cache_duration"]:
                    logger.debug("Returning cached live data")
                    return _live_data_cache["race_data"]

        logger.info("Fetching live race data from FastF1...")

        # Determine which race to load
        session = None

        # Priority 1: Explicit race_round parameter
        if race_round is not None:
            logger.info(f"Loading specified race round: {race_round}")
            try:
                session = fastf1.get_session(2025, race_round, 'R')
                session.load(telemetry=False)
            except Exception as e:
                logger.warning(f"Failed to load race {race_round}: {e}")
                session = None

        # Priority 2: Environment variable FASTF1_RACE
        if session is None:
            env_race = os.getenv('FASTF1_RACE')
            if env_race:
                try:
                    race_num = int(env_race)
                    logger.info(f"Loading race from FASTF1_RACE env var: {race_num}")
                    session = fastf1.get_session(2025, race_num, 'R')
                    session.load(telemetry=False)
                except (ValueError, Exception) as e:
                    logger.warning(f"Invalid FASTF1_RACE value or failed to load: {e}")
                    session = None

        # Priority 3: Find most recent race with data
        if session is None:
            logger.info("Searching for most recent race with available data...")
            try:
                for round_num in range(24, 0, -1):
                    try:
                        candidate = fastf1.get_session(2025, round_num, 'R')
                        candidate.load(telemetry=False)  # Skip telemetry for speed
                        if hasattr(candidate, 'results') and not candidate.results.empty:
                            session = candidate
                            logger.info(f"Found race with data: Round {round_num} - {session.name}")
                            break
                    except Exception as e:
                        logger.debug(f"Round {round_num} check failed: {type(e).__name__}")
                        continue
            except Exception as e:
                logger.warning(f"Error searching for races: {e}")

        # Priority 4: Fall back to 'latest'
        if session is None:
            logger.info("No recent race found, using 'latest'")
            session = fastf1.get_session(2025, 'latest', 'R')
            session.load(telemetry=False)

        logger.info(f"Loaded session: {session.name} - {session.date}")

        # Parse driver data
        drivers = []
        if hasattr(session, 'results'):
            for idx, driver in session.results.iterrows():
                # Get current tire compound from latest lap data
                driver_abbr = driver.get('Abbreviation', 'UNK')
                tire_compound = 'UNKNOWN'
                tire_age = 0

                if hasattr(session, 'laps') and not session.laps.empty:
                    driver_laps = session.laps[session.laps['Driver'] == driver_abbr]
                    if not driver_laps.empty:
                        # Get the last lap data (current/latest)
                        latest_lap = driver_laps.iloc[-1]
                        tire_compound = str(latest_lap.get('Compound', 'UNKNOWN')).upper()
                        # Calculate tire age (laps on current compound)
                        if tire_compound != 'UNKNOWN':
                            compound_laps = driver_laps[driver_laps['Compound'] == tire_compound]
                            tire_age = len(compound_laps)

                driver_data = {
                    "name": driver_abbr,
                    "number": int(driver.get('DriverNumber', 0)),
                    "position": int(driver.get('Position', 99)),
                    "lap": int(driver.get('Laps', 0)),
                    "lap_time": str(driver.get('Time', 'N/A')),
                    "tire_compound": tire_compound,
                    "tire_age": tire_age,
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
            temp_data = session.weather_data.get('TrackTemp', 35.0)
            # Handle Pandas Series - convert to float (get latest value)
            if hasattr(temp_data, 'iloc'):  # Pandas Series
                track_temp = float(temp_data.iloc[-1]) if len(temp_data) > 0 else 35.0
            else:
                track_temp = float(temp_data)

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

    except ImportError:
        logger.warning("FastF1 not installed. Install with: pip install fastf1")
        return None
    except Exception as e:
        logger.error(f"Error fetching live race data: {e}")
        return None


def start_live_timing_recording(year: int = 2025, round_num: int = 23) -> bool:
    """
    Start recording live F1 timing data using FastF1's livetiming module.

    This runs in the background and saves live timing messages to a file.
    Only works during active F1 race sessions.

    Args:
        year: Season year (default 2025)
        round_num: Race round number (default 23 for Vegas)

    Returns:
        True if recording started successfully, False otherwise
    """
    try:
        # Check if already recording
        if _live_data_cache["livetiming_process"] is not None:
            logger.info("Live timing already recording")
            return True

        # Create output file for live timing data
        output_file = f"/tmp/fastf1_livetiming_{year}_r{round_num}.jsonl"
        _live_data_cache["livetiming_file"] = output_file

        logger.info(f"Starting live timing recording to {output_file}...")

        # Start FastF1 livetiming recording in background
        # python -m fastf1.livetiming save <output_file>
        process = subprocess.Popen(
            ["python", "-m", "fastf1.livetiming", "save", output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        _live_data_cache["livetiming_process"] = process
        logger.info(f"✓ Live timing recording started (PID: {process.pid})")

        return True

    except Exception as e:
        logger.error(f"Failed to start live timing recording: {e}")
        return False


def read_live_timing_data(file_path: str = "/tmp/vegas_live_22.jsonl") -> Optional[Dict[str, Any]]:
    """
    Read and parse live timing data from recording file.

    Args:
        file_path: Path to the live timing recording file

    Returns:
        Formatted race state dictionary or None
    """
    try:
        from fastf1.livetiming.data import LiveTimingData
        import json as json_module

        # Driver number to abbreviation mapping for 2025 F1 season
        # Correct mapping: 4=NOR, 16=LEC, 44=HAM, 63=RUS, etc.
        DRIVER_ABBR_MAP = {
            1: 'VER', 2: 'SAR', 4: 'NOR', 14: 'ALO', 16: 'LEC', 18: 'STR',
            19: 'PIA', 20: 'MAG', 22: 'TSU', 24: 'ZHO', 27: 'HUL', 30: 'BOR',
            31: 'BOT', 44: 'HAM', 55: 'SAI', 63: 'RUS', 81: 'PIA'
        }

        # Check if file exists and has content
        if not os.path.exists(file_path):
            logger.debug(f"Live timing file not found: {file_path}")
            return None

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.debug("Live timing file is empty (recording in progress)")
            return None

        logger.info(f"Loading live timing data from {file_path} ({file_size} bytes)")

        # Load the recorded live timing data
        livetiming_data = LiveTimingData(file_path)

        # Parse the timing data into our standard format
        drivers = []

        # Extract driver information from livetiming data
        try:
            current_lap = 0

            # Get current lap count
            if livetiming_data.has("LapCount"):
                lap_count = livetiming_data.get("LapCount")
                if lap_count and len(lap_count) > 0:
                    timestamp, lap_data = lap_count[-1]
                    current_lap = lap_data.get('CurrentLap', 0)
                    logger.info(f"Current lap from live timing: {current_lap}")

            # Extract driver data from TimingAppData (has position, compound, laps)
            drivers_dict = {}

            if livetiming_data.has("TimingAppData"):
                timing_app = livetiming_data.get("TimingAppData")
                if timing_app:
                    # Scan all entries to build complete driver picture
                    for entry in timing_app[-100:]:  # Check last 100 updates for comprehensive data
                        try:
                            timestamp, data = entry
                            if 'Lines' in data:
                                for driver_num_str, driver_info in data['Lines'].items():
                                    try:
                                        driver_num = int(driver_num_str)
                                    except:
                                        continue

                                    if driver_num not in drivers_dict:
                                        drivers_dict[driver_num] = {
                                            'number': driver_num,
                                            'position': None,
                                            'compound': 'UNKNOWN',
                                            'laps_on_compound': 0,
                                            'last_lap_time': '',
                                            'current_lap_num': current_lap,
                                            'pit_stops': 0,
                                        }

                                    # Extract position (Line field)
                                    if isinstance(driver_info, dict):
                                        if 'Line' in driver_info:
                                            drivers_dict[driver_num]['position'] = driver_info['Line']

                                        # Extract stint info
                                        if 'Stints' in driver_info:
                                            stints = driver_info['Stints']
                                            for stint_num_str, stint_data in stints.items():
                                                if isinstance(stint_data, dict):
                                                    if 'Compound' in stint_data:
                                                        drivers_dict[driver_num]['compound'] = stint_data['Compound']
                                                    if 'TotalLaps' in stint_data:
                                                        drivers_dict[driver_num]['laps_on_compound'] = stint_data['TotalLaps']
                                                    if 'LapNumber' in stint_data:
                                                        drivers_dict[driver_num]['current_lap_num'] = stint_data['LapNumber']
                                                    if 'LapTime' in stint_data:
                                                        drivers_dict[driver_num]['last_lap_time'] = stint_data['LapTime']
                        except Exception as e:
                            logger.debug(f"Error processing timing app entry: {e}")
                            continue

            logger.info(f"Found {len(drivers_dict)} drivers from TimingAppData")

            # Convert drivers_dict to list and sort by position
            drivers_list = list(drivers_dict.values())
            drivers_list.sort(key=lambda x: x.get('position') or 999)

            # Build drivers array with proper data
            for i, driver_data in enumerate(drivers_list, 1):
                driver_abbr = DRIVER_ABBR_MAP.get(driver_data['number'], f"#{driver_data['number']}")
                # Default to HARD if compound is unknown (safer assumption)
                compound = driver_data['compound']
                if compound == 'UNKNOWN' or compound not in ('SOFT', 'MEDIUM', 'HARD'):
                    compound = 'HARD'

                drivers.append({
                    "name": driver_abbr,
                    "number": driver_data['number'],
                    "position": driver_data['position'] or i,
                    "lap": driver_data['current_lap_num'],
                    "lap_time": driver_data['last_lap_time'],
                    "tire_compound": compound,
                    "tire_age": driver_data['laps_on_compound'],
                    "pit_stops": driver_data['pit_stops'],
                    "gap": 0.0,
                    "gap_to_leader": 0.0,
                })

            # If we couldn't extract drivers, return None to fall back to FastF1 session data
            if not drivers:
                logger.warning("Could not extract drivers from live timing")
                return None

            race_data = {
                "race_name": "Las Vegas Grand Prix (LIVE)",
                "season": 2025,
                "current_lap": current_lap,
                "total_laps": 51,
                "race_time": datetime.now().isoformat(),
                "track_temp": 30.0,
                "air_temp": 22.0,
                "weather": "CLEAR",
                "safety_car_active": False,
                "safety_car_laps": 0,
                "status": "RUNNING",
                "drivers": drivers,
                "is_live_timing": True,
            }

            logger.info(f"✓ Successfully loaded live timing data with {len(drivers)} drivers at lap {current_lap}")
            return race_data

        except Exception as e:
            logger.warning(f"Error parsing live timing data: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    except ImportError:
        logger.warning("LiveTimingData not available - FastF1 live timing support required")
        return None
    except Exception as e:
        logger.debug(f"Error reading live timing data: {e}")
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
