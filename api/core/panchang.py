"""
Panchang (Hindu Calendar) Calculations
Tithi, Vara, Nakshatra, Yoga, Karana, Rahu Kalam, Choghadiya, etc.
"""

from typing import Dict, Any
from api.core.ephemeris import (
    SIGNS, NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_DEITIES, NAKSHATRA_GANAS,
    longitude_to_nakshatra, longitude_to_sign, get_swe_lock,
)
from api.core.calculations import get_solar_events, get_lunar_events
import swisseph as swe
import math
import logging

logger = logging.getLogger(__name__)

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

TITHI_DEITIES = [
    "Agni", "Brahma", "Gauri", "Ganesha", "Sarpa", "Kartikeya", "Surya",
    "Shiva", "Durga", "Yama", "Vishvadeva", "Vishnu", "Kamadeva", "Shiva", "Chandra",
    "Agni", "Brahma", "Gauri", "Ganesha", "Sarpa", "Kartikeya", "Surya",
    "Shiva", "Durga", "Yama", "Vishvadeva", "Vishnu", "Kamadeva", "Shiva", "Pitris",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_RULERS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Rahu Kalam: which 1/8th segment of day (0-based) — Mon=1, Tue=6, etc.
RAHU_KALAM_SEGMENTS = {0: 7, 1: 1, 2: 6, 3: 4, 4: 5, 5: 3, 6: 2}  # Sun=0..Sat=6

# Yamaganda segments
YAMAGANDA_SEGMENTS = {0: 4, 1: 3, 2: 5, 3: 1, 4: 2, 5: 0, 6: 6}

# Gulika segments
GULIKA_SEGMENTS = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}

CHOGHADIYA_NAMES = ["Udveg", "Chal", "Labh", "Amrit", "Kal", "Shubh", "Rog"]
CHOGHADIYA_DAY_START = {0: 0, 1: 3, 2: 6, 3: 2, 4: 5, 5: 1, 6: 4}  # Sun..Sat

RITU_NAMES = ["Vasanta", "Grishma", "Varsha", "Sharada", "Hemanta", "Shishira"]
MASA_NAMES = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
]


def get_panchang(jd: float, latitude: float, longitude: float, timezone_str: str = "UTC") -> Dict[str, Any]:
    """Calculate complete Panchang for the given Julian Day and location."""

    # Get Sun and Moon positions
    with get_swe_lock():
        sun_pos, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        moon_pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)

    sun_lon = sun_pos[0]
    moon_lon = moon_pos[0]

    # Get sidereal positions for nakshatra
    ayanamsa = swe.get_ayanamsa_ut(jd)
    sun_sid = (sun_lon - ayanamsa) % 360
    moon_sid = (moon_lon - ayanamsa) % 360

    # ── Tithi ─────────────────────────────────────────────────────────────
    tithi_angle = (moon_lon - sun_lon) % 360
    tithi_index = int(tithi_angle / 12)
    tithi_completion = ((tithi_angle % 12) / 12) * 100
    paksha = "Shukla" if tithi_index < 15 else "Krishna"

    # ── Nakshatra ─────────────────────────────────────────────────────────
    nak_name, nak_num, nak_pada, nak_lord, nak_deity = longitude_to_nakshatra(moon_sid)
    nak_span = 360.0 / 27.0
    nak_completion = ((moon_sid % nak_span) / nak_span) * 100

    # ── Yoga (Sun + Moon sidereal longitude) ──────────────────────────────
    yoga_angle = (sun_sid + moon_sid) % 360
    yoga_index = int(yoga_angle / (360 / 27))
    if yoga_index >= 27:
        yoga_index = 26
    yoga_completion = ((yoga_angle % (360 / 27)) / (360 / 27)) * 100

    # ── Karana (half-tithi) ───────────────────────────────────────────────
    karana_angle = tithi_angle
    karana_index_raw = int(karana_angle / 6)
    if karana_index_raw < 1:
        karana_name = KARANA_NAMES[10]  # Kimstughna
    elif karana_index_raw >= 57:
        fixed_karanas = [KARANA_NAMES[7], KARANA_NAMES[8], KARANA_NAMES[9], KARANA_NAMES[10]]
        karana_name = fixed_karanas[min(karana_index_raw - 57, 3)]
    else:
        karana_name = KARANA_NAMES[(karana_index_raw - 1) % 7]

    # ── Vara (weekday) ────────────────────────────────────────────────────
    day_of_week = int((jd + 1.5) % 7)
    vara = VARA_NAMES[day_of_week]
    vara_ruler = VARA_RULERS[day_of_week]

    # ── Solar events ──────────────────────────────────────────────────────
    solar = get_solar_events(jd, latitude, longitude)
    sunrise_jd = solar.get("sunrise")
    sunset_jd = solar.get("sunset")
    lunar = get_lunar_events(jd, latitude, longitude)

    # ── Rahu Kalam, Yamaganda, Gulika ─────────────────────────────────────
    rahu_kalam = None
    yamaganda = None
    gulika = None
    if sunrise_jd and sunset_jd:
        day_dur = sunset_jd - sunrise_jd
        seg = day_dur / 8

        rk_seg = RAHU_KALAM_SEGMENTS.get(day_of_week, 7)
        rahu_kalam = {"start_jd": sunrise_jd + rk_seg * seg, "end_jd": sunrise_jd + (rk_seg + 1) * seg}

        yg_seg = YAMAGANDA_SEGMENTS.get(day_of_week, 4)
        yamaganda = {"start_jd": sunrise_jd + yg_seg * seg, "end_jd": sunrise_jd + (yg_seg + 1) * seg}

        gk_seg = GULIKA_SEGMENTS.get(day_of_week, 6)
        gulika = {"start_jd": sunrise_jd + gk_seg * seg, "end_jd": sunrise_jd + (gk_seg + 1) * seg}

    # ── Brahma Muhurta ────────────────────────────────────────────────────
    brahma_muhurta = None
    if sunrise_jd:
        bm_start = sunrise_jd - (96.0 / 60 / 24)  # 1h 36m before sunrise
        bm_end = bm_start + (48.0 / 60 / 24)       # 48 minutes duration
        brahma_muhurta = {"start_jd": bm_start, "end_jd": bm_end}

    # ── Abhijit Muhurta ───────────────────────────────────────────────────
    abhijit = None
    if sunrise_jd and sunset_jd:
        midday = (sunrise_jd + sunset_jd) / 2
        half_muhurta = (sunset_jd - sunrise_jd) / 30  # 1 muhurta = day/15
        abhijit = {"start_jd": midday - half_muhurta / 2, "end_jd": midday + half_muhurta / 2}

    # ── Choghadiya ────────────────────────────────────────────────────────
    choghadiya_day = []
    choghadiya_night = []
    if sunrise_jd and sunset_jd:
        day_seg = (sunset_jd - sunrise_jd) / 8
        night_seg = (1 - (sunset_jd - sunrise_jd)) / 8  # Approximate
        start_idx = CHOGHADIYA_DAY_START.get(day_of_week, 0)
        for i in range(8):
            idx = (start_idx + i) % 7
            choghadiya_day.append({
                "name": CHOGHADIYA_NAMES[idx],
                "start_jd": sunrise_jd + i * day_seg,
                "end_jd": sunrise_jd + (i + 1) * day_seg,
            })
        for i in range(8):
            idx = (start_idx + 4 + i) % 7
            choghadiya_night.append({
                "name": CHOGHADIYA_NAMES[idx],
                "start_jd": sunset_jd + i * night_seg,
                "end_jd": sunset_jd + (i + 1) * night_seg,
            })

    # ── Masa and Ritu ─────────────────────────────────────────────────────
    sun_sign_idx = int(sun_sid / 30)
    masa = MASA_NAMES[sun_sign_idx % 12]
    ritu = RITU_NAMES[(sun_sign_idx // 2) % 6]
    ayana = "Uttarayana" if 9 <= sun_sign_idx <= 2 or sun_sign_idx >= 9 else "Dakshinayana"

    return {
        "tithi": {
            "number": tithi_index + 1, "name": TITHI_NAMES[tithi_index],
            "deity": TITHI_DEITIES[tithi_index], "paksha": paksha,
            "completion_percent": round(tithi_completion, 2),
        },
        "vara": {"name": vara, "ruler": vara_ruler},
        "nakshatra": {
            "number": nak_num, "name": nak_name, "pada": nak_pada,
            "lord": nak_lord, "deity": nak_deity,
            "gana": NAKSHATRA_GANAS[nak_num - 1] if nak_num <= 27 else "Unknown",
            "completion_percent": round(nak_completion, 2),
        },
        "yoga": {
            "number": yoga_index + 1, "name": YOGA_NAMES[yoga_index],
            "completion_percent": round(yoga_completion, 2),
        },
        "karana": {"name": karana_name},
        "paksha": paksha,
        "masa": masa,
        "ritu": ritu,
        "ayana": ayana,
        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
        "moonrise_jd": lunar.get("moonrise"),
        "moonset_jd": lunar.get("moonset"),
        "brahma_muhurta": brahma_muhurta,
        "abhijit_muhurta": abhijit,
        "rahu_kalam": rahu_kalam,
        "yamaganda": yamaganda,
        "gulika_kalam": gulika,
        "choghadiya_day": choghadiya_day,
        "choghadiya_night": choghadiya_night,
        "ayanamsa_degrees": round(ayanamsa, 4),
    }
