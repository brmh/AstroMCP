"""Muhurta Endpoints"""

from fastapi import APIRouter
from api.models.request_models import MuhurtaRequest, MuhurtaSearchRequest, PanchangRequest
from api.core.muhurta import get_muhurta_quality, find_auspicious_times
from api.core.panchang import get_panchang
from api.core.ephemeris import get_julian_day

router = APIRouter(prefix="/muhurta", tags=["Muhurta"])


@router.post("/quality")
async def muhurta_quality(request: MuhurtaRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    return get_muhurta_quality(jd, request.latitude, request.longitude, request.purpose, request.timezone)


@router.post("/find-auspicious")
async def find_auspicious(request: MuhurtaSearchRequest):
    start_jd = get_julian_day(request.start_date.year, request.start_date.month, request.start_date.day, timezone_str=request.timezone)
    end_jd = get_julian_day(request.end_date.year, request.end_date.month, request.end_date.day, timezone_str=request.timezone)
    return {"auspicious_times": find_auspicious_times(start_jd, end_jd, request.latitude, request.longitude, request.purpose, request.timezone, request.min_score)}


@router.post("/hora")
async def planetary_hora(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    panchang = get_panchang(jd, request.latitude, request.longitude, request.timezone)
    sunrise_jd = panchang.get("sunrise_jd")
    sunset_jd = panchang.get("sunset_jd")
    if not sunrise_jd or not sunset_jd:
        return {"error": "Could not calculate sunrise/sunset"}
    day_dur = (sunset_jd - sunrise_jd) / 12
    night_dur = (1 - (sunset_jd - sunrise_jd)) / 12
    hora_order = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    day_of_week = int((jd + 1.5) % 7)
    start_idx = day_of_week
    horas = []
    for i in range(12):
        idx = (start_idx + i) % 7
        horas.append({"hora_lord": hora_order[idx], "start_jd": sunrise_jd + i * day_dur,
                       "end_jd": sunrise_jd + (i + 1) * day_dur, "is_day": True})
    for i in range(12):
        idx = (start_idx + 12 + i) % 7
        horas.append({"hora_lord": hora_order[idx], "start_jd": sunset_jd + i * night_dur,
                       "end_jd": sunset_jd + (i + 1) * night_dur, "is_day": False})
    return {"horas": horas}


@router.post("/choghadiya")
async def choghadiya(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    panchang = get_panchang(jd, request.latitude, request.longitude, request.timezone)
    return {"day": panchang.get("choghadiya_day", []), "night": panchang.get("choghadiya_night", [])}
