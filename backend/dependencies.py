"""Dependency injection and shared services."""

import logging
from typing import Optional
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# Global cache for loaded models
_models_cache = {
    "degradation_predictor": None,
    "is_loaded": False,
}


def load_degradation_model():
    """Load tire degradation predictor model."""
    from backend.config import DEGRADATION_MODEL_PATH, ENABLE_MOCK_DATA

    if _models_cache["is_loaded"]:
        logger.info("Models already loaded in cache")
        return _models_cache["degradation_predictor"]

    if ENABLE_MOCK_DATA:
        logger.info("Mock data mode enabled - skipping model loading")
        return None

    if not DEGRADATION_MODEL_PATH.exists():
        logger.warning(
            f"Degradation model not found at {DEGRADATION_MODEL_PATH}. "
            "You may need to run: python ml/train_and_evaluate.py"
        )
        return None

    try:
        import joblib

        logger.info(f"Loading degradation model from {DEGRADATION_MODEL_PATH}")
        model = joblib.load(DEGRADATION_MODEL_PATH)
        _models_cache["degradation_predictor"] = model
        _models_cache["is_loaded"] = True
        logger.info("Degradation model loaded successfully")
        return model

    except Exception as e:
        logger.error(f"Failed to load degradation model: {e}")
        return None


def get_degradation_model():
    """Get degradation model from cache or load it."""
    if _models_cache["degradation_predictor"] is None and not _models_cache["is_loaded"]:
        load_degradation_model()
    return _models_cache["degradation_predictor"]


def load_strategy_engine():
    """Load or initialize strategy engine."""
    from backend.config import PROCESSED_DATA_DIR

    try:
        # Import strategy modules
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from ml.strategy.strategy_engine import StrategyEngine

        # Initialize strategy engine
        degradation_model = get_degradation_model()
        if degradation_model is None:
            logger.warning("Degradation model not available - strategy engine may have limited functionality")

        logger.info("Strategy engine initialized")
        return StrategyEngine()

    except Exception as e:
        logger.error(f"Failed to initialize strategy engine: {e}")
        return None


def get_models_status() -> dict:
    """Get status of all loaded models."""
    return {
        "degradation_predictor": _models_cache["degradation_predictor"] is not None,
        "is_loaded": _models_cache["is_loaded"],
    }
