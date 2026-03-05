"""
Pydantic Response Models
Standardized output models for API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[str] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    version: str
    ephemeris_path: str
    uptime_seconds: Optional[float] = None


class NatalChartResponse(BaseModel):
    chart_type: str
    zodiac_type: str
    ayanamsa: Optional[str] = None
    house_system: str
    julian_day: float
    planets: Dict[str, Any]
    houses: Dict[str, Any]
    aspects: List[Dict[str, Any]]
    moon_phase: Dict[str, Any]
    combust_planets: List[Dict[str, Any]]
    planetary_wars: List[Dict[str, Any]]
    is_day_chart: bool


class PanchangResponse(BaseModel):
    tithi: Dict[str, Any]
    vara: Dict[str, Any]
    nakshatra: Dict[str, Any]
    yoga: Dict[str, Any]
    karana: Dict[str, Any]
    paksha: str
    masa: str
    ritu: str
    ayana: str
    sunrise_jd: Optional[float] = None
    sunset_jd: Optional[float] = None
    moonrise_jd: Optional[float] = None
    moonset_jd: Optional[float] = None
    brahma_muhurta: Optional[Dict[str, Any]] = None
    abhijit_muhurta: Optional[Dict[str, Any]] = None
    rahu_kalam: Optional[Dict[str, Any]] = None
    yamaganda: Optional[Dict[str, Any]] = None
    gulika_kalam: Optional[Dict[str, Any]] = None
    choghadiya_day: List[Dict[str, Any]] = []
    choghadiya_night: List[Dict[str, Any]] = []
    ayanamsa_degrees: Optional[float] = None


class MuhurtaResponse(BaseModel):
    purpose: str
    overall_score: float
    assessment: str
    breakdown: Dict[str, Any]
    recommendations: List[str]
    panchang_summary: Dict[str, Any]


class CompatibilityResponse(BaseModel):
    total_points: int
    max_points: int
    assessment: str
    kutas: Dict[str, Any]
    doshas: List[Dict[str, Any]]
    person1_nakshatra: str
    person2_nakshatra: str
    person1_moon_sign: str
    person2_moon_sign: str


class YogaResponse(BaseModel):
    yoga_name: str
    category: str
    is_present: bool
    strength: str
    participating_planets: List[str]
    houses_involved: List[int]
    description: str
    effects: str
    remedies: Optional[str] = None


class DashaResponse(BaseModel):
    mahadasha: Dict[str, Any]
    antardasha: Optional[Dict[str, Any]] = None
    pratyantardasha: Optional[Dict[str, Any]] = None


class GeocodeResponse(BaseModel):
    city: str
    latitude: float
    longitude: float
    timezone: str
    country: Optional[str] = None
    state: Optional[str] = None
