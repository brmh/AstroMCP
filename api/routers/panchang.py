"""Panchang Endpoints"""

from fastapi import APIRouter
from api.models.request_models import PanchangRequest, MonthlyPanchangRequest
from api.core.panchang import get_panchang
from api.core.ephemeris import get_julian_day, NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_DEITIES, NAKSHATRA_GANAS

router = APIRouter(prefix="/panchang", tags=["Panchang"])


@router.post("/daily")
async def daily_panchang(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    return get_panchang(jd, request.latitude, request.longitude, request.timezone)


@router.post("/monthly")
async def monthly_panchang(request: MonthlyPanchangRequest):
    import calendar
    days_in_month = calendar.monthrange(request.year, request.month)[1]
    result = []
    for day in range(1, days_in_month + 1):
        jd = get_julian_day(request.year, request.month, day, 6, 0, 0, request.timezone)
        panchang = get_panchang(jd, request.latitude, request.longitude, request.timezone)
        panchang["date"] = f"{request.year}-{request.month:02d}-{day:02d}"
        result.append(panchang)
    return result


@router.post("/nakshatra")
async def current_nakshatra(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    panchang = get_panchang(jd, request.latitude, request.longitude, request.timezone)
    return panchang["nakshatra"]


@router.post("/tithi")
async def current_tithi(request: PanchangRequest):
    jd = get_julian_day(request.year, request.month, request.day, request.hour, request.minute, 0, request.timezone)
    panchang = get_panchang(jd, request.latitude, request.longitude, request.timezone)
    return panchang["tithi"]


@router.get("/festivals")
async def festivals(year: int = 2026):
    """Returns major Hindu festivals (simplified list)."""
    return [
        {"name": "Makar Sankranti", "month": 1, "approximate_day": 14},
        {"name": "Maha Shivaratri", "month": 2, "approximate_day": 26},
        {"name": "Holi", "month": 3, "approximate_day": 14},
        {"name": "Ram Navami", "month": 4, "approximate_day": 6},
        {"name": "Akshaya Tritiya", "month": 5, "approximate_day": 2},
        {"name": "Guru Purnima", "month": 7, "approximate_day": 13},
        {"name": "Raksha Bandhan", "month": 8, "approximate_day": 9},
        {"name": "Krishna Janmashtami", "month": 8, "approximate_day": 16},
        {"name": "Ganesh Chaturthi", "month": 9, "approximate_day": 7},
        {"name": "Navratri", "month": 10, "approximate_day": 2},
        {"name": "Dussehra", "month": 10, "approximate_day": 12},
        {"name": "Diwali", "month": 10, "approximate_day": 31},
        {"name": "Kartik Purnima", "month": 11, "approximate_day": 15},
    ]
