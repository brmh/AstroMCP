"""Utility Endpoints"""

from fastapi import APIRouter
from api.models.request_models import GeocodeRequest, JulianDayRequest
from api.dependencies import geocode_city
from api.core.ephemeris import (
    SIGNS, SIGNS_SANSKRIT, SIGN_ELEMENTS, SIGN_MODALITIES, SIGN_RULERS,
    NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_DEITIES, NAKSHATRA_GANAS,
    HOUSE_SYSTEMS, AYANAMSA_MODES, PLANETS, get_julian_day,
)
from api.config import settings

router = APIRouter(prefix="/utilities", tags=["Utilities"])


@router.get("/health")
async def health():
    return {"status": "ok", "version": settings.API_VERSION, "ephemeris_path": settings.EPHE_PATH}


@router.get("/zodiac-signs")
async def zodiac_signs():
    return [{"index": i, "name": SIGNS[i], "sanskrit": SIGNS_SANSKRIT[i],
             "element": SIGN_ELEMENTS[i], "modality": SIGN_MODALITIES[i],
             "ruler": SIGN_RULERS[i], "natural_house": i + 1} for i in range(12)]


@router.get("/nakshatras")
async def nakshatras():
    return [{"number": i + 1, "name": NAKSHATRAS[i], "lord": NAKSHATRA_LORDS[i],
             "deity": NAKSHATRA_DEITIES[i], "gana": NAKSHATRA_GANAS[i]} for i in range(27)]


@router.get("/planets")
async def planets():
    return [{"name": k, "swe_id": v} for k, v in PLANETS.items()]


@router.get("/house-systems")
async def house_systems():
    return [{"name": k, "code": v.decode()} for k, v in HOUSE_SYSTEMS.items()]


@router.get("/ayanamsas")
async def ayanamsas():
    return [{"name": k, "swe_id": v} for k, v in AYANAMSA_MODES.items()]


@router.post("/geocode")
async def geocode(request: GeocodeRequest):
    return geocode_city(request.city, request.country)


@router.post("/julian-day")
async def julian_day(request: JulianDayRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, request.second, request.timezone)
    return {"julian_day": jd}

from api.models.request_models import PanchangRequest
from api.core.planetary_hours import get_planetary_hours

@router.post("/planetary-hours")
async def planetary_hours(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    return get_planetary_hours(jd, request.latitude, request.longitude)


from api.core.nakshatras import get_nakshatra_info

@router.get("/nakshatra/{number}")
async def nakshatra_deep_dive(number: int):
    return get_nakshatra_info(number)


@router.get("/ephemeris-range")
async def ephemeris_range():
    return {"start_year": -5400, "end_year": 5400,
            "note": "Swiss Ephemeris covers 13200 years (5400 BC to 5400 AD) with full precision."}
