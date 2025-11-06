"""Main FastAPI application for Ferrari Race Strategizer API."""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS,
    LOG_LEVEL,
    LOG_FORMAT,
)
from backend.dependencies import load_degradation_model, get_models_status
from backend.endpoints import strategy, prediction, simulation, race, websocket

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Ferrari Race Strategizer API v{API_VERSION} Starting")
    logger.info("=" * 60)

    try:
        logger.info("Loading ML models...")
        model = load_degradation_model()
        if model:
            logger.info("✓ Degradation model loaded successfully")
        else:
            logger.warning(
                "⚠ Degradation model not loaded - API will use fallback predictions"
            )
    except Exception as e:
        logger.error(f"✗ Error loading models: {e}")

    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info("API Ready!")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("Ferrari Race Strategizer API Shutting Down")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.debug(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e),
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )


# Include routers
app.include_router(strategy.router, prefix="/api/strategy")
app.include_router(prediction.router, prefix="/api/predict")
app.include_router(simulation.router, prefix="/api/simulate")
app.include_router(race.router, prefix="/api/race")
app.include_router(websocket.router)


# Root endpoints
@app.get(
    "/",
    summary="API Root",
    description="Ferrari Race Strategizer API",
)
async def root():
    """API root endpoint."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check API and service health",
)
async def health():
    """Comprehensive health check."""
    models_status = get_models_status()

    return {
        "status": "healthy" if models_status["is_loaded"] else "degraded",
        "api": {
            "version": API_VERSION,
            "name": API_TITLE,
        },
        "models": {
            "degradation_predictor": models_status["degradation_predictor"],
            "is_loaded": models_status["is_loaded"],
        },
        "services": {
            "strategy": "operational",
            "prediction": "operational",
            "simulation": "operational",
            "race": "operational",
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get(
    "/version",
    summary="API Version",
    description="Get API version information",
)
async def version():
    """Get version information."""
    return {
        "version": API_VERSION,
        "title": API_TITLE,
        "description": API_DESCRIPTION,
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
