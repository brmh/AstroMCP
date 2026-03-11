"""Western-specific Endpoints"""

from fastapi import APIRouter
from api.models.request_models import NatalChartRequest
from api.dependencies import birth_data_to_jd
from api.core.calculations import get_all_planet_positions, get_houses, get_aspects, assign_houses_to_planets
from api.core.dignities import get_essential_dignities, check_mutual_reception

router = APIRouter(prefix="/western", tags=["Western Astrology"])


@router.post("/dignities")
async def western_dignities(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type="TROPICAL")
    return get_essential_dignities(positions)


@router.post("/receptions")
async def mutual_receptions(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="TROPICAL")
    return check_mutual_reception(positions)


@router.post("/chart")
async def western_chart(request: NatalChartRequest):
    from api.core.charts import build_natal_chart
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    chart = build_natal_chart(jd, bd.latitude, bd.longitude,
                              house_system=opts.house_system.value, zodiac_type="TROPICAL")
    chart["dignities"] = get_essential_dignities(chart["planets"])
    chart["mutual_receptions"] = check_mutual_reception(chart["planets"])
    chart["name"] = bd.name
    return chart


from api.models.request_models import TransitRequest, SynastryRequest
from api.dependencies import get_current_jd
from api.core.ephemeris import get_julian_day
from api.core.progressions import get_secondary_progressions
from api.core.charts import build_composite_chart

@router.post("/progressions")
async def western_secondary_progressions(request: TransitRequest):
    transit_jd = get_current_jd()
    if request.transit_date:
        td = request.transit_date
        transit_jd = get_julian_day(td.year, td.month, td.day, td.hour, td.minute, td.second, "UTC")
        
    opts = request.options
    
    if isinstance(request.natal, dict) and "julian_day" in request.natal and "birth_data" in request.natal:
        natal_jd = request.natal["julian_day"]
        bd = request.natal["birth_data"]
        lat = bd["latitude"]
        lon = bd["longitude"]
    else:
        # Fallback to birth data
        natal_bd = request.natal if isinstance(request.natal, BirthData) else BirthData(**request.natal)
        natal_jd = birth_data_to_jd(natal_bd)
        lat = natal_bd.latitude
        lon = natal_bd.longitude
        
    return get_secondary_progressions(
        natal_jd, transit_jd, lat, lon,
        zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value,
        house_system=opts.house_system.value
    )

from api.models.request_models import ProgressionRequest
from api.core.progressions import get_solar_return, get_lunar_return

@router.post("/progressions/solar-return")
async def western_solar_return(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    target = request.target_year or datetime.utcnow().year
    return get_solar_return(jd, target, bd.latitude, bd.longitude, house_system=opts.house_system.value)

@router.post("/progressions/lunar-return")
async def western_lunar_return(request: ProgressionRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    opts = request.options
    if request.target_date:
        td = request.target_date
        target_jd = get_julian_day(td.year, td.month, td.day, 12, 0, 0, "UTC")
    else:
        target_jd = get_current_jd()
        
    return get_lunar_return(jd, target_jd, bd.latitude, bd.longitude, house_system=opts.house_system.value)

@router.post("/composite")
async def western_composite(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    opts = request.options
    
    pos1 = get_all_planet_positions(jd1, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    pos2 = get_all_planet_positions(jd2, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    
    chart = build_composite_chart(pos1, pos2)
    aspects = get_aspects(chart, chart, opts.orb_settings.dict())
    
    return {
        "person1_name": request.person1.name,
        "person2_name": request.person2.name,
        "composite_planets": chart,
        "composite_aspects": aspects
    }

from api.core.midpoints import get_midpoints

@router.post("/midpoints/natal")
async def western_natal_midpoints(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_midpoints(positions)

@router.post("/midpoints/synastry")
async def western_synastry_midpoints(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    opts = request.options
    pos2 = get_all_planet_positions(jd2, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_midpoints(pos1, pos2)

from api.core.acg import get_astrocartography_lines

@router.post("/acg")
async def western_astrocartography(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_astrocartography_lines(jd, positions)
