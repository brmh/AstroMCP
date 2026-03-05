"""Transit Endpoints"""

from fastapi import APIRouter
from datetime import datetime
import pytz
from api.models.request_models import NatalChartRequest, TransitRequest, DateRangeRequest, PlanetTransitRequest
from api.dependencies import birth_data_to_jd, get_current_jd
from api.core.calculations import (
    get_all_planet_positions, get_houses, get_transit_aspects,
    get_retrograde_periods, get_planetary_ingresses,
    get_solar_eclipses, get_lunar_eclipses, assign_houses_to_planets,
)
from api.core.ephemeris import STANDARD_PLANETS, PLANETS, get_julian_day

router = APIRouter(prefix="/transits", tags=["Transits"])


@router.post("/current")
async def current_transits(request: TransitRequest):
    natal_jd = birth_data_to_jd(request.natal)
    transit_jd = get_current_jd()
    if request.transit_date:
        td = request.transit_date
        transit_jd = get_julian_day(td.year, td.month, td.day, td.hour, td.minute, td.second, "UTC")
    opts = request.options
    natal_pos = get_all_planet_positions(natal_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    transit_pos = get_all_planet_positions(transit_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return {"natal_positions": natal_pos, "transit_positions": transit_pos,
            "transit_jd": transit_jd}


@router.post("/aspects")
async def transit_aspects(request: TransitRequest):
    natal_jd = birth_data_to_jd(request.natal)
    transit_jd = get_current_jd()
    if request.transit_date:
        td = request.transit_date
        transit_jd = get_julian_day(td.year, td.month, td.day, td.hour, td.minute, td.second, "UTC")
    opts = request.options
    natal_pos = get_all_planet_positions(natal_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    transit_pos = get_all_planet_positions(transit_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_transit_aspects(natal_pos, transit_pos)


@router.post("/date-range")
async def transit_date_range(request: DateRangeRequest):
    natal_jd = birth_data_to_jd(request.natal)
    opts = request.options
    natal_pos = get_all_planet_positions(natal_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str="UTC")
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str="UTC")
    results = []
    jd = start_jd
    while jd <= end_jd:
        transit_pos = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
        aspects = get_transit_aspects(natal_pos, transit_pos)
        if aspects:
            results.append({"jd": jd, "aspects": aspects[:10]})
        jd += 1
    return results


@router.post("/planet")
async def transit_planet(request: PlanetTransitRequest):
    planet_name = request.planet.lower()
    planet_id = PLANETS.get(planet_name) or STANDARD_PLANETS.get(planet_name)
    if planet_id is None:
        return {"error": f"Unknown planet: {request.planet}"}
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str="UTC")
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str="UTC")
    ingresses = get_planetary_ingresses(planet_id, start_jd, end_jd)
    retrogrades = get_retrograde_periods(planet_id, start_jd, end_jd)
    return {"planet": planet_name, "ingresses": ingresses, "retrogrades": retrogrades}


@router.post("/retrogrades")
async def transit_retrogrades(request: DateRangeRequest):
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str="UTC")
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str="UTC")
    import swisseph as swe
    retro_planets = {"mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS,
                     "jupiter": swe.JUPITER, "saturn": swe.SATURN}
    result = {}
    for name, pid in retro_planets.items():
        result[name] = get_retrograde_periods(pid, start_jd, end_jd)
    return result


@router.post("/ingresses")
async def transit_ingresses(request: DateRangeRequest):
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str="UTC")
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str="UTC")
    import swisseph as swe
    result = {}
    for name, pid in STANDARD_PLANETS.items():
        result[name] = get_planetary_ingresses(pid, start_jd, end_jd)
    return result


@router.post("/eclipses")
async def transit_eclipses(request: DateRangeRequest):
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str="UTC")
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str="UTC")
    return {"solar": get_solar_eclipses(start_jd, end_jd), "lunar": get_lunar_eclipses(start_jd, end_jd)}


@router.get("/now")
async def current_positions():
    jd = get_current_jd()
    positions = get_all_planet_positions(jd)
    from api.core.calculations import get_moon_phase
    return {"julian_day": jd, "positions": positions, "moon_phase": get_moon_phase(jd)}


@router.post("/outer-planets")
async def outer_planet_transits(request: TransitRequest):
    natal_jd = birth_data_to_jd(request.natal)
    transit_jd = get_current_jd()
    opts = request.options
    natal_pos = get_all_planet_positions(natal_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    transit_pos = get_all_planet_positions(transit_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    outer = {k: v for k, v in transit_pos.items() if k in ("jupiter", "saturn", "mean_node", "ketu")}
    aspects = get_transit_aspects(natal_pos, outer)
    return {"outer_planet_transits": outer, "aspects_to_natal": aspects}
