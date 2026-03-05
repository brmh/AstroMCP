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
