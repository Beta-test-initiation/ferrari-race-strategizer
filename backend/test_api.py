#!/usr/bin/env python3
"""Quick test to verify API structure without running full server."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing Backend API Structure...")
print("=" * 60)

# Test imports
try:
    print("\n1. Testing imports...")
    from backend.config import API_TITLE, API_VERSION
    print(f"   ✓ Config loaded: {API_TITLE} v{API_VERSION}")

    from backend.models import RaceStateRequest, StrategyRecommendationResponse
    print("   ✓ Models loaded successfully")

    from backend.dependencies import get_degradation_model
    print("   ✓ Dependencies loaded successfully")

    from backend.services.strategy_service import StrategyService
    print("   ✓ Strategy service loaded successfully")

    from backend.endpoints import strategy, prediction, simulation, race, websocket
    print("   ✓ All endpoints loaded successfully")

    from backend.main import app
    print("   ✓ FastAPI app loaded successfully")

except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test model validation
try:
    print("\n2. Testing Pydantic models...")
    race_state = RaceStateRequest(
        current_lap=25,
        position=3,
        tire_age=20,
        compound="MEDIUM",
        track_temp=35.0,
        track_id=1,
        driver="HAM",
        gaps_ahead=[2.1, 5.7],
        gaps_behind=[3.2, 8.9],
        total_laps=58,
    )
    print("   ✓ RaceStateRequest validated")

except Exception as e:
    print(f"   ✗ Validation error: {e}")
    sys.exit(1)

# Test service initialization
try:
    print("\n3. Testing service initialization...")
    service = StrategyService()
    print("   ✓ StrategyService initialized")

except Exception as e:
    print(f"   ✗ Service initialization error: {e}")
    sys.exit(1)

# Test API routes
try:
    print("\n4. Testing API routes...")
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append((route.path, getattr(route, "methods", ["N/A"])))

    strategy_routes = [r for r in routes if "/strategy" in r[0]]
    predict_routes = [r for r in routes if "/predict" in r[0]]
    simulate_routes = [r for r in routes if "/simulate" in r[0]]
    race_routes = [r for r in routes if "/race" in r[0]]
    ws_routes = [r for r in routes if "/ws" in r[0]]

    print(f"   ✓ Strategy endpoints: {len(strategy_routes)}")
    print(f"   ✓ Prediction endpoints: {len(predict_routes)}")
    print(f"   ✓ Simulation endpoints: {len(simulate_routes)}")
    print(f"   ✓ Race endpoints: {len(race_routes)}")
    print(f"   ✓ WebSocket endpoints: {len(ws_routes)}")
    print(f"   ✓ Total routes: {len(routes)}")

except Exception as e:
    print(f"   ✗ Route error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nTo start the backend server, run:")
print("  python3 -m uvicorn backend.main:app --reload --port 8000")
print("\nAPI Documentation:")
print("  Swagger UI: http://localhost:8000/docs")
print("  ReDoc: http://localhost:8000/redoc")
print("=" * 60)
