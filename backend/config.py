"""Configuration management for Ferrari Race Strategizer API."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# API Configuration
API_TITLE = "Ferrari Race Strategizer API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Real-time race strategy optimization API for Ferrari F1 team"

# Server Configuration
HOST = os.getenv("API_HOST", "localhost")
PORT = int(os.getenv("API_PORT", 8000))
RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = [FRONTEND_URL]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# ML Models Configuration
MODELS_DIR = Path(__file__).parent.parent / "ml" / "saved_models"
DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model paths
DEGRADATION_MODEL_PATH = MODELS_DIR / "ferrari_degradation_model.pkl"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = 5  # seconds
WS_MAX_CONNECTIONS = 100

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # 5 minutes

# Feature flags
ENABLE_MOCK_DATA = os.getenv("ENABLE_MOCK_DATA", "false").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Race simulation parameters
SIMULATION_NUM_ITERATIONS = 100
SIMULATION_TIMEOUT_SECONDS = 10

# Pit stop constants (used by backend for validation)
TYPICAL_PIT_STOP_TIME = 22  # seconds
TIRE_WARM_UP_LAPS = 2
DRS_ADVANTAGE = 0.3  # seconds
