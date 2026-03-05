"""Synastry / Relationship Endpoints"""

from fastapi import APIRouter
from api.models.request_models import SynastryRequest
from api.dependencies import birth_data_to_jd
from api.core.calculations import get_all_planet_positions, get_houses, get_aspects
from api.core.compatibility import get_synastry_aspects
from api.core.charts import build_composite_chart

router = APIRouter(prefix="/synastry", tags=["Synastry"])


@router.post("/aspects")
async def synastry_aspects(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    opts = request.options
    pos1 = get_all_planet_positions(jd1, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    pos2 = get_all_planet_positions(jd2, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    return {"aspects": get_synastry_aspects(pos1, pos2)}


@router.post("/composite")
async def composite_chart(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    opts = request.options
    pos1 = get_all_planet_positions(jd1, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    pos2 = get_all_planet_positions(jd2, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    composite = build_composite_chart(pos1, pos2)
    composite_aspects = get_aspects(composite)
    return {"composite_positions": composite, "aspects": composite_aspects}


@router.post("/davison")
async def davison_chart(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    midpoint_jd = (jd1 + jd2) / 2
    mid_lat = (request.person1.latitude + request.person2.latitude) / 2
    mid_lon = (request.person1.longitude + request.person2.longitude) / 2
    opts = request.options
    pos = get_all_planet_positions(midpoint_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    houses = get_houses(midpoint_jd, mid_lat, mid_lon, opts.house_system.value)
    aspects = get_aspects(pos)
    return {"davison_jd": midpoint_jd, "positions": pos, "houses": houses, "aspects": aspects}


@router.post("/compatibility-score")
async def compatibility_score(request: SynastryRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    opts = request.options
    pos1 = get_all_planet_positions(jd1, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    pos2 = get_all_planet_positions(jd2, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    aspects = get_synastry_aspects(pos1, pos2)
    harmonious = [a for a in aspects if a["aspect_name"] in ("Trine", "Sextile", "Conjunction")]
    challenging = [a for a in aspects if a["aspect_name"] in ("Square", "Opposition")]
    score = min(100, max(0, 50 + len(harmonious) * 3 - len(challenging) * 2))
    return {
        "overall_score": score,
        "harmonious_aspects": len(harmonious),
        "challenging_aspects": len(challenging),
        "total_aspects": len(aspects),
        "top_aspects": aspects[:10],
    }
