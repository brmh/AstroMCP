"""
Progressions — Secondary, Solar Arc, Solar/Lunar Return, Profections, Firdaria.
"""

from typing import Dict, List, Any
import swisseph as swe
from api.core.ephemeris import (
    SIGNS, longitude_to_sign, get_swe_lock,
)
from api.core.calculations import get_all_planet_positions, get_houses

JD_PER_YEAR = 365.25


def get_secondary_progressions(
    birth_jd: float, target_jd: float,
    latitude: float, longitude: float,
    zodiac_type: str = "TROPICAL", ayanamsa: str = None,
    house_system: str = "PLACIDUS",
) -> Dict[str, Any]:
    """
    Calculate secondary progressions (day-for-a-year method).
    Each day after birth = one year of life.
    """
    years_elapsed = (target_jd - birth_jd) / JD_PER_YEAR
    progressed_jd = birth_jd + years_elapsed  # 1 day per year

    positions = get_all_planet_positions(progressed_jd, zodiac_type=zodiac_type, ayanamsa=ayanamsa)
    houses = get_houses(progressed_jd, latitude, longitude, house_system, zodiac_type, ayanamsa)

    return {
        "type": "secondary_progressions",
        "progressed_jd": progressed_jd,
        "years_elapsed": round(years_elapsed, 2),
        "planets": positions,
        "houses": houses,
    }


def get_solar_arc_directions(
    birth_jd: float, target_jd: float, birth_positions: Dict[str, Dict],
    zodiac_type: str = "TROPICAL", ayanamsa: str = None,
) -> Dict[str, Any]:
    """
    Calculate solar arc directions.
    All planets advance by the same arc as the progressed Sun's movement.
    """
    years_elapsed = (target_jd - birth_jd) / JD_PER_YEAR
    progressed_jd = birth_jd + years_elapsed

    with get_swe_lock():
        natal_sun, _ = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)
        prog_sun, _ = swe.calc_ut(progressed_jd, swe.SUN, swe.FLG_SWIEPH)

    solar_arc = (prog_sun[0] - natal_sun[0]) % 360

    directed = {}
    for name, pos in birth_positions.items():
        dir_lon = (pos["longitude"] + solar_arc) % 360
        sign, idx, deg = longitude_to_sign(dir_lon)
        directed[name] = {
            "directed_longitude": round(dir_lon, 4),
            "sign": sign, "degree_in_sign": round(deg, 4),
            "natal_longitude": pos["longitude"],
        }

    return {
        "type": "solar_arc", "solar_arc_degrees": round(solar_arc, 4),
        "years_elapsed": round(years_elapsed, 2), "directed_planets": directed,
    }


def get_solar_return(
    birth_jd: float, target_year: int,
    latitude: float, longitude: float,
    house_system: str = "PLACIDUS",
) -> Dict[str, Any]:
    """Calculate the solar return chart for a given year."""
    with get_swe_lock():
        natal_sun, _ = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)
    natal_sun_lon = natal_sun[0]

    # Search for when transiting Sun returns to natal Sun longitude
    search_jd = swe.julday(target_year, 1, 1, 0)
    step = 1.0
    for _ in range(400):
        with get_swe_lock():
            current_sun, _ = swe.calc_ut(search_jd, swe.SUN, swe.FLG_SWIEPH)
        diff = (current_sun[0] - natal_sun_lon) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < 0.001:
            break
        search_jd += diff / (360 / JD_PER_YEAR)

    sr_jd = search_jd
    positions = get_all_planet_positions(sr_jd)
    houses = get_houses(sr_jd, latitude, longitude, house_system)

    return {
        "type": "solar_return", "year": target_year,
        "solar_return_jd": sr_jd, "planets": positions, "houses": houses,
    }


def get_lunar_return(
    birth_jd: float, target_jd: float,
    latitude: float, longitude: float,
    house_system: str = "PLACIDUS",
) -> Dict[str, Any]:
    """Calculate the next lunar return chart from target_jd."""
    with get_swe_lock():
        natal_moon, _ = swe.calc_ut(birth_jd, swe.MOON, swe.FLG_SWIEPH)
    natal_moon_lon = natal_moon[0]

    search_jd = target_jd
    for _ in range(60):
        with get_swe_lock():
            current_moon, _ = swe.calc_ut(search_jd, swe.MOON, swe.FLG_SWIEPH)
        diff = (current_moon[0] - natal_moon_lon) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < 0.01:
            break
        search_jd += diff / (360 / 27.3)

    lr_jd = search_jd
    positions = get_all_planet_positions(lr_jd)
    houses = get_houses(lr_jd, latitude, longitude, house_system)

    return {
        "type": "lunar_return", "lunar_return_jd": lr_jd,
        "planets": positions, "houses": houses,
    }


def get_annual_profections(birth_jd: float, target_jd: float) -> Dict[str, Any]:
    """Calculate annual profections (traditional time-lord technique)."""
    years = int((target_jd - birth_jd) / JD_PER_YEAR)
    profected_house = (years % 12) + 1
    profected_sign_idx = (years % 12)
    profected_sign = SIGNS[profected_sign_idx]
    from api.core.ephemeris import SIGN_RULERS
    time_lord = SIGN_RULERS[profected_sign_idx]

    return {
        "type": "annual_profections", "age": years,
        "profected_house": profected_house, "profected_sign": profected_sign,
        "time_lord": time_lord,
    }


def get_firdaria(birth_jd: float, is_day_birth: bool = True) -> List[Dict]:
    """Calculate Firdaria (Persian time lords). 75-year cycle."""
    if is_day_birth:
        order = [("Sun", 10), ("Venus", 8), ("Mercury", 13), ("Moon", 9),
                 ("Saturn", 11), ("Jupiter", 12), ("Mars", 7), ("North Node", 3), ("South Node", 2)]
    else:
        order = [("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
                 ("Sun", 10), ("Venus", 8), ("Mercury", 13), ("North Node", 3), ("South Node", 2)]

    periods = []
    cur = birth_jd
    for lord, years in order:
        end = cur + years * JD_PER_YEAR
        periods.append({"lord": lord, "start_jd": cur, "end_jd": end, "duration_years": years})
        cur = end

    return periods
