"""Natal Chart Endpoints"""

from fastapi import APIRouter
from api.models.request_models import NatalChartRequest
from api.dependencies import birth_data_to_jd
from api.core.charts import build_natal_chart
from api.core.calculations import (
    get_all_planet_positions, get_houses, get_aspects, assign_houses_to_planets,
    get_arabic_parts, get_fixed_star_conjunctions, get_declinations,
    get_parallel_aspects, get_midpoints, get_antiscia,
)
from api.core.dignities import get_essential_dignities

router = APIRouter(prefix="/natal", tags=["Natal Chart"])


@router.post("/chart")
async def natal_chart(request: NatalChartRequest):
    """Complete natal chart with planets, houses, aspects, angles."""
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    chart = build_natal_chart(
        jd, bd.latitude, bd.longitude,
        house_system=opts.house_system.value,
        zodiac_type=opts.zodiac_type.value,
        ayanamsa=opts.ayanamsa.value,
        include_chiron=opts.include_chiron,
        include_lilith=opts.include_lilith,
        include_asteroids=opts.include_asteroids,
        orb_settings=opts.orb_settings.model_dump() if opts.orb_settings else None,
    )
    chart["name"] = bd.name
    return chart


@router.post("/planets")
async def natal_planets(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    return get_all_planet_positions(
        jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value,
        include_chiron=opts.include_chiron, include_lilith=opts.include_lilith,
        include_asteroids=opts.include_asteroids,
    )


@router.post("/houses")
async def natal_houses(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    return get_houses(jd, bd.latitude, bd.longitude, opts.house_system.value,
                      opts.zodiac_type.value, opts.ayanamsa.value)


@router.post("/aspects")
async def natal_aspects(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_aspects(positions, opts.orb_settings.model_dump() if opts.orb_settings else None)


@router.post("/arabic-parts")
async def natal_arabic_parts(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, opts.house_system.value)
    return get_arabic_parts(positions, houses["ascendant"], houses)


@router.post("/fixed-stars")
async def natal_fixed_stars(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_fixed_star_conjunctions(jd, positions)


@router.post("/dignities")
async def natal_dignities(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_essential_dignities(positions)


@router.post("/declinations")
async def natal_declinations(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    decl = get_declinations(jd)
    parallels = get_parallel_aspects(decl)
    return {"declinations": decl, "parallel_aspects": parallels}


@router.post("/midpoints")
async def natal_midpoints(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_midpoints(positions)


@router.post("/antiscia")
async def natal_antiscia(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_antiscia(positions)
