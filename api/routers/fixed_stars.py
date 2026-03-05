"""Fixed Stars Endpoints"""

from fastapi import APIRouter
from api.models.request_models import NatalChartRequest
from api.dependencies import birth_data_to_jd, get_current_jd
from api.core.calculations import get_fixed_star_positions, get_fixed_star_conjunctions, get_all_planet_positions

router = APIRouter(prefix="/fixed-stars", tags=["Fixed Stars"])


@router.get("/list")
async def fixed_star_list():
    jd = get_current_jd()
    return get_fixed_star_positions(jd)


@router.post("/conjunctions")
async def fixed_star_conjunctions(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    opts = request.options
    positions = get_all_planet_positions(jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return get_fixed_star_conjunctions(jd, positions)


@router.post("/heliacal")
async def heliacal_events(request: NatalChartRequest):
    from api.core.calculations import get_heliacal_phenomena
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    return get_heliacal_phenomena(jd, "sirius", bd.latitude, bd.longitude)
