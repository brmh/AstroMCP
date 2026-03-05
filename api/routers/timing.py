"""Timing / Progressions Endpoints"""

from fastapi import APIRouter
from api.models.request_models import NatalChartRequest, ProgressionRequest
from api.dependencies import birth_data_to_jd, get_current_jd
from api.core.progressions import (
    get_secondary_progressions, get_solar_arc_directions,
    get_solar_return, get_lunar_return,
    get_annual_profections, get_firdaria,
)
from api.core.calculations import get_all_planet_positions

router = APIRouter(prefix="/progressions", tags=["Progressions & Timing"])


@router.post("/secondary")
async def secondary_progressions(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    target_jd = get_current_jd()
    if request.target_date:
        from api.core.ephemeris import get_julian_day
        target_jd = get_julian_day(request.target_date.year, request.target_date.month, request.target_date.day, timezone_str="UTC")
    bd = request.birth_data
    opts = request.options
    return get_secondary_progressions(jd, target_jd, bd.latitude, bd.longitude,
                                      opts.zodiac_type.value, opts.ayanamsa.value, opts.house_system.value)


@router.post("/solar-arc")
async def solar_arc(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    target_jd = get_current_jd()
    if request.target_date:
        from api.core.ephemeris import get_julian_day
        target_jd = get_julian_day(request.target_date.year, request.target_date.month, request.target_date.day, timezone_str="UTC")
    positions = get_all_planet_positions(jd, zodiac_type=request.options.zodiac_type.value, ayanamsa=request.options.ayanamsa.value)
    return get_solar_arc_directions(jd, target_jd, positions)


@router.post("/solar-return")
async def solar_return(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    year = request.target_year or 2026
    bd = request.birth_data
    return get_solar_return(jd, year, bd.latitude, bd.longitude, request.options.house_system.value)


@router.post("/lunar-return")
async def lunar_return(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    target_jd = get_current_jd()
    bd = request.birth_data
    return get_lunar_return(jd, target_jd, bd.latitude, bd.longitude, request.options.house_system.value)


@router.post("/profections")
async def profections(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    target_jd = get_current_jd()
    return get_annual_profections(jd, target_jd)


@router.post("/firdaria")
async def firdaria(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    return get_firdaria(jd)
