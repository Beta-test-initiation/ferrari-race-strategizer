# Ferrari Race Strategizer - Backend API

Professional FastAPI backend for Ferrari F1 race strategy optimization. Serves machine learning models through REST endpoints and WebSocket connections.

## Overview

The backend provides:
- ✅ **Strategy Recommendations** - Optimal pit stop timing and tire compound selection
- ✅ **Tire Degradation Predictions** - ML-powered lap-by-lap performance forecasting
- ✅ **Race Simulations** - Monte Carlo scenario analysis with probability distributions
- ✅ **Real-time Updates** - WebSocket for live race state and alert streaming
- ✅ **Type Safety** - Pydantic models for all requests and responses
- ✅ **CORS Support** - Ready for frontend integration
- ✅ **Auto Documentation** - Swagger UI and ReDoc at /docs and /redoc

## Quick Start

### 1. Install Dependencies

```bash
# Install backend-specific requirements
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp backend/.env.example .env

# Edit .env with your settings (optional - defaults work for local dev)
```

### 3. Start the Server

```bash
# Development mode (with auto-reload)
python3 -m uvicorn backend.main:app --reload --port 8000

# Production mode
python3 -m uvicorn backend.main:app --port 8000 --workers 4
```

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Directory Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration management
├── models.py                  # Pydantic request/response models
├── dependencies.py            # Dependency injection & model loading
├── services/
│   ├── __init__.py
│   └── strategy_service.py   # Business logic for strategy operations
├── endpoints/
│   ├── __init__.py
│   ├── strategy.py           # Strategy recommendation endpoints
│   ├── prediction.py         # Tire degradation prediction endpoints
│   ├── simulation.py         # Race simulation endpoints
│   ├── race.py               # Race data endpoints
│   └── websocket.py          # WebSocket endpoints
├── test_api.py               # Quick API structure test
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Endpoints

### Health & Info

- `GET /` - API root information
- `GET /health` - Comprehensive health check
- `GET /version` - Version information

### Strategy Endpoints (`/api/strategy`)

**POST** `/api/strategy/recommendation`
- Get comprehensive pit stop and strategy recommendation
- Request: Current race state (lap, position, tires, etc)
- Response: Immediate action, optimal strategy, scenario analysis, competitor threats

**GET** `/api/strategy/health`
- Check strategy service health

**Example Request:**
```json
{
  "current_lap": 25,
  "position": 3,
  "tire_age": 20,
  "compound": "MEDIUM",
  "track_temp": 35.0,
  "track_id": 1,
  "driver": "HAM",
  "gaps_ahead": [2.1, 5.7],
  "gaps_behind": [3.2, 8.9],
  "total_laps": 58
}
```

### Prediction Endpoints (`/api/predict`)

**POST** `/api/predict/degradation`
- Predict tire degradation rate for given conditions
- Request: Track conditions, tire compound, driver, etc
- Response: Degradation rate, confidence intervals, risk level, recommendations

**GET** `/api/predict/health`
- Check prediction service health

**Example Request:**
```json
{
  "track_temp": 35.0,
  "compound": "MEDIUM",
  "stint_length": 20,
  "track_id": 1,
  "driver": "HAM"
}
```

### Simulation Endpoints (`/api/simulate`)

**POST** `/api/simulate/race`
- Run Monte Carlo simulation for a specific strategy
- Request: Race state, strategy details, number of simulations
- Response: Position distribution, win probability, expected points

**POST** `/api/simulate/compare-strategies`
- Compare multiple strategies simultaneously
- Request: List of RaceSimulationRequest objects
- Response: Results for each strategy, best strategy identified

**GET** `/api/simulate/health`
- Check simulation service health

### Race Data Endpoints (`/api/race`)

**GET** `/api/race/current`
- Get current race state
- Response: Race info, driver positions, telemetry, track conditions

**GET** `/api/race/telemetry`
- Get detailed driver telemetry
- Response: Driver positions, tire info, pit history, gaps

**GET** `/api/race/weather`
- Get weather information
- Response: Current conditions, 5-hour forecast, track impact

**GET** `/api/race/status`
- Get high-level race status
- Response: Status, lap progress, leader, safety car info

**GET** `/api/race/health`
- Check race data service health

### WebSocket Endpoints

**WS** `/ws/live-updates`
- Real-time race state updates
- Connects to: Race state, lap timings, tire info
- Messages every 5-10 seconds
- Supports heartbeat pings

**WS** `/ws/alerts`
- Real-time alert streaming
- Sends: Pit alerts, tire warnings, strategy updates
- Connects for live race event notifications

## Models & Types

### Enums

```python
# Tire Compounds
TireCompound: SOFT | MEDIUM | HARD

# Urgency Levels
UrgencyLevel: IMMEDIATE | SOON | MONITOR | LOW

# Risk Levels
RiskLevel: LOW | MEDIUM | HIGH

# Threat Levels
ThreatLevel: LOW | MEDIUM | HIGH

# Alert Severity
AlertSeverity: INFO | WARNING | CRITICAL
```

### Key Request/Response Models

See [models.py](models.py) for complete type definitions. Key models include:

- `RaceStateRequest` - Current race conditions
- `DegradationPredictionRequest` - Tire degradation parameters
- `RaceSimulationRequest` - Simulation configuration
- `StrategyRecommendationResponse` - Complete strategy output
- `DegradationPredictionResponse` - Prediction output
- `RaceSimulationResponse` - Simulation results

## Configuration

### Environment Variables

Create `.env` file (or use defaults):

```bash
# Server
API_HOST=localhost
API_PORT=8000
API_RELOAD=true

# CORS
FRONTEND_URL=http://localhost:3000

# Models
ENABLE_MOCK_DATA=false
DEBUG_MODE=false

# Logging
LOG_LEVEL=INFO

# Cache
CACHE_ENABLED=true
CACHE_TTL=300

# WebSocket
WS_HEARTBEAT_INTERVAL=5
WS_MAX_CONNECTIONS=100
```

## Features

### Type Safety
- All requests validated with Pydantic
- Type hints throughout
- Automatic request/response validation

### Error Handling
- Proper HTTP status codes (400, 403, 404, 500, etc)
- Detailed error messages
- Exception logging

### CORS Support
- Configured for frontend on http://localhost:3000
- Adjustable via `FRONTEND_URL` environment variable

### Model Loading
- Automatic model loading on startup
- Fallback predictions if models unavailable
- Graceful degradation

### Logging
- Structured logging with timestamps
- Request/response logging
- Error tracking

### WebSocket Support
- Two separate WebSocket connections
- Heartbeat mechanism for keeping connection alive
- Client connection management

## Running Tests

### Structure Test
```bash
python3 backend/test_api.py
```

This verifies:
- All imports work
- Pydantic models validate correctly
- Services initialize properly
- All API routes are registered

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Get current race state
curl http://localhost:8000/api/race/current

# Get strategy recommendation
curl -X POST http://localhost:8000/api/strategy/recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "current_lap": 25,
    "position": 3,
    "tire_age": 20,
    "compound": "MEDIUM",
    "track_temp": 35.0,
    "track_id": 1,
    "driver": "HAM",
    "gaps_ahead": [2.1, 5.7],
    "gaps_behind": [3.2, 8.9],
    "total_laps": 58
  }'

# Predict tire degradation
curl -X POST http://localhost:8000/api/predict/degradation \
  -H "Content-Type: application/json" \
  -d '{
    "track_temp": 35.0,
    "compound": "MEDIUM",
    "stint_length": 20,
    "track_id": 1,
    "driver": "HAM"
  }'
```

## Development Notes

### Adding New Endpoints

1. Create endpoint function in `endpoints/*.py`
2. Define Pydantic models in `models.py`
3. Implement logic in `services/*.py`
4. Include router in `main.py`
5. Document in `endpoints` docstrings

### Model Training

To train the tire degradation predictor:

```bash
# From project root
python3 ml/train_and_evaluate.py
```

This creates the model file at: `ml/saved_models/tire_degradation_predictor.pkl`

The backend will automatically load it on startup.

### Debugging

Enable debug mode in `.env`:
```
DEBUG_MODE=true
```

View logs with:
```bash
# Watch logs while server runs
tail -f logs/api.log  # if implemented
```

## Performance Considerations

- **Response Time**: Most endpoints should respond in < 500ms
- **Concurrency**: WebSocket supports 100+ concurrent connections
- **Memory**: Model loaded once, shared across requests
- **Caching**: Optional caching layer (5 minute TTL default)

## Security

- CORS properly configured
- Input validation with Pydantic
- Type hints for type safety
- Error handling prevents information leaks

## Production Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ferrari-api .
docker run -p 8000:8000 ferrari-api
```

### Scaling

- Use multiple workers: `--workers 4`
- Put behind Nginx for load balancing
- Use Redis for distributed caching
- Monitor with Prometheus/Grafana

## Troubleshooting

### Model Not Loading

If you see warnings about missing models:

```bash
# Train models first
python3 ml/train_and_evaluate.py

# Check model file exists
ls -la ml/saved_models/
```

### CORS Issues

If frontend can't reach backend:

1. Check `FRONTEND_URL` in `.env` matches frontend URL
2. Verify backend is running on correct port
3. Check browser console for CORS error details

### WebSocket Connection Issues

1. Ensure WebSocket is not blocked by firewall
2. Check browser DevTools Network tab
3. Verify endpoint URL (ws:// not http://)

## API Documentation

Full interactive documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Related

- Frontend: `frontend/README.md`
- ML Pipeline: `ml/README.md`
- Configuration: `docs/sketchpad.md`

## Support

For issues or questions, check:
1. Endpoint docstrings in code
2. API documentation at /docs
3. Test output from `backend/test_api.py`
4. Application logs with `LOG_LEVEL=DEBUG`
