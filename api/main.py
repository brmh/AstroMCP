"""
AstroConsultant API — FastAPI Entrypoint
Professional astrology API powered by Swiss Ephemeris.
"""

import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import swisseph as swe

from api.config import settings
from api.core import (
    AstrologyCalculationError, InvalidBirthDataError,
    EphemerisFileNotFoundError, UnsupportedHouseSystemError,
    InvalidTimezoneError, GeocodingError,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and close Swiss Ephemeris."""
    swe.set_ephe_path(settings.EPHE_PATH)
    logger.info(f"Swiss Ephemeris initialized. Path: {settings.EPHE_PATH}")
    logger.info(f"API Version: {settings.API_VERSION}")
    yield
    swe.close()
    logger.info("Swiss Ephemeris closed.")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Professional astrology API powered by Swiss Ephemeris. "
                "Supports Western (Tropical) and Vedic (Sidereal) traditions.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ───────────────────────────────────────────────────
def _error_response(error_type: str, message: str, status: int, detail: str = None):
    return JSONResponse(
        status_code=status,
        content={
            "error": error_type,
            "message": message,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

@app.exception_handler(InvalidBirthDataError)
async def invalid_birth_data_handler(request: Request, exc: InvalidBirthDataError):
    return _error_response("InvalidBirthDataError", str(exc), 400)

@app.exception_handler(AstrologyCalculationError)
async def calculation_error_handler(request: Request, exc: AstrologyCalculationError):
    return _error_response("AstrologyCalculationError", str(exc), 500)

@app.exception_handler(EphemerisFileNotFoundError)
async def ephemeris_not_found_handler(request: Request, exc: EphemerisFileNotFoundError):
    return _error_response("EphemerisFileNotFoundError", str(exc), 500,
                          "Run 'python scripts/download_ephemeris.py' to download ephemeris files.")

@app.exception_handler(UnsupportedHouseSystemError)
async def house_system_handler(request: Request, exc: UnsupportedHouseSystemError):
    return _error_response("UnsupportedHouseSystemError", str(exc), 400)

@app.exception_handler(InvalidTimezoneError)
async def timezone_handler(request: Request, exc: InvalidTimezoneError):
    return _error_response("InvalidTimezoneError", str(exc), 400)

@app.exception_handler(GeocodingError)
async def geocoding_handler(request: Request, exc: GeocodingError):
    return _error_response("GeocodingError", str(exc), 400)

@app.exception_handler(Exception)
async def general_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return _error_response("InternalError", "An unexpected error occurred.", 500, str(exc))


# ── Include Routers ──────────────────────────────────────────────────────
from api.routers import natal, vedic, transits, synastry, panchang as panchang_router
from api.routers import muhurta as muhurta_router, timing, western, fixed_stars, utilities

app.include_router(natal.router)
app.include_router(vedic.router)
app.include_router(transits.router)
app.include_router(synastry.router)
app.include_router(panchang_router.router)
app.include_router(muhurta_router.router)
app.include_router(timing.router)
app.include_router(western.router)
app.include_router(fixed_stars.router)
app.include_router(utilities.router)


# ── Root Endpoint ────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "Professional Astrology API powered by Swiss Ephemeris",
        "documentation": "/docs",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "endpoints": {
            "natal": "/natal/chart",
            "vedic": "/vedic/kundli",
            "transits": "/transits/current",
            "synastry": "/synastry/aspects",
            "panchang": "/panchang/daily",
            "muhurta": "/muhurta/quality",
            "progressions": "/progressions/secondary",
            "western": "/western/chart",
            "fixed_stars": "/fixed-stars/list",
            "utilities": "/utilities/health",
        },
        "supported_traditions": ["Western (Tropical)", "Vedic/Jyotish (Sidereal)"],
    }
