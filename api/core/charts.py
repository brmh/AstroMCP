"""
Chart Assembly Logic
Builds natal, transit, synastry, composite, and divisional charts.
Includes all Vedic Varga charts D1–D60.
"""

from typing import Dict, List, Any, Optional
from api.core.ephemeris import (
    SIGNS, longitude_to_sign, get_navamsa_sign, get_swe_lock,
    get_ayanamsa_value, set_sidereal_mode, get_house_system_flag,
)
from api.core.calculations import (
    get_all_planet_positions, get_houses, assign_houses_to_planets,
    get_aspects, get_moon_phase, check_combustion, check_planetary_war,
)
import swisseph as swe
import logging

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# NATAL CHART
# ══════════════════════════════════════════════════════════════════════════

def build_natal_chart(
    jd: float,
    latitude: float,
    longitude: float,
    house_system: str = "PLACIDUS",
    zodiac_type: str = "TROPICAL",
    ayanamsa: str = "LAHIRI",
    include_chiron: bool = True,
    include_lilith: bool = True,
    include_asteroids: bool = False,
    orb_settings: Dict = None,
) -> Dict[str, Any]:
    """Build a complete natal chart with positions, houses, aspects, etc."""

    positions = get_all_planet_positions(
        jd, zodiac_type=zodiac_type, ayanamsa=ayanamsa,
        include_chiron=include_chiron, include_lilith=include_lilith,
        include_asteroids=include_asteroids,
    )

    houses = get_houses(jd, latitude, longitude, house_system, zodiac_type, ayanamsa)
    positions = assign_houses_to_planets(positions, houses)
    aspects = get_aspects(positions, orb_settings)
    moon_phase = get_moon_phase(jd)
    combust = check_combustion(positions)
    planetary_war = check_planetary_war(positions)

    # Determine if day/night chart
    sun_lon = positions.get("sun", {}).get("longitude", 0)
    asc_lon = houses.get("ascendant", 0)
    is_day = _is_day_chart(sun_lon, houses)

    return {
        "chart_type": "natal",
        "zodiac_type": zodiac_type,
        "ayanamsa": ayanamsa if zodiac_type.upper() == "SIDEREAL" else None,
        "house_system": house_system,
        "julian_day": jd,
        "planets": positions,
        "houses": houses,
        "aspects": aspects,
        "moon_phase": moon_phase,
        "combust_planets": combust,
        "planetary_wars": planetary_war,
        "is_day_chart": is_day,
    }


def _is_day_chart(sun_longitude: float, houses: Dict) -> bool:
    """Determine if chart is a day chart (Sun above horizon)."""
    asc = houses.get("ascendant", 0)
    dsc = houses.get("descendant", 0)
    sun = sun_longitude

    # Sun is above horizon if between ASC and DSC (going through MC)
    if asc < dsc:
        return not (asc <= sun < dsc)
    else:
        return asc <= sun or sun < dsc


# ══════════════════════════════════════════════════════════════════════════
# DIVISIONAL CHARTS (Vedic Vargas D1–D60)
# ══════════════════════════════════════════════════════════════════════════

def get_divisional_chart_sign(sidereal_longitude: float, division: int) -> str:
    """
    Calculate the sign in a divisional chart for a given sidereal longitude.
    """
    lon = sidereal_longitude % 360

    if division == 1:  # D1 Rasi
        return SIGNS[int(lon / 30)]

    elif division == 2:  # D2 Hora
        deg_in_sign = lon % 30
        sign_idx = int(lon / 30)
        if deg_in_sign < 15:
            return "Leo" if sign_idx % 2 == 0 else "Cancer"  # Odd/even sign
        else:
            return "Cancer" if sign_idx % 2 == 0 else "Leo"

    elif division == 3:  # D3 Drekkana
        deg_in_sign = lon % 30
        sign_idx = int(lon / 30)
        if deg_in_sign < 10:
            return SIGNS[sign_idx]
        elif deg_in_sign < 20:
            return SIGNS[(sign_idx + 4) % 12]
        else:
            return SIGNS[(sign_idx + 8) % 12]

    elif division == 4:  # D4 Chaturthamsa
        part = int((lon % 30) / 7.5)
        sign_idx = int(lon / 30)
        return SIGNS[(sign_idx + part * 3) % 12]

    elif division == 7:  # D7 Saptamsa
        part = int((lon % 30) / (30 / 7))
        sign_idx = int(lon / 30)
        if sign_idx % 2 == 0:  # Odd sign
            return SIGNS[(sign_idx + part) % 12]
        else:
            return SIGNS[(sign_idx + 6 + part) % 12]

    elif division == 9:  # D9 Navamsa
        navamsa_index = int(lon / (360 / 108)) % 12
        return SIGNS[navamsa_index]

    elif division == 10:  # D10 Dasamsa
        part = int((lon % 30) / 3)
        sign_idx = int(lon / 30)
        if sign_idx % 2 == 0:  # Odd sign
            return SIGNS[(sign_idx + part) % 12]
        else:
            return SIGNS[(sign_idx + 9 + part) % 12]

    elif division == 12:  # D12 Dvadasamsa
        part = int((lon % 30) / 2.5)
        sign_idx = int(lon / 30)
        return SIGNS[(sign_idx + part) % 12]

    elif division == 16:  # D16 Shodasamsa
        part = int((lon % 30) / (30 / 16))
        sign_idx = int(lon / 30)
        # Starting from Aries for moveable, Leo for fixed, Sagittarius for dual
        modality = sign_idx % 3
        starts = [0, 4, 8]  # Aries, Leo, Sagittarius
        return SIGNS[(starts[modality] + part) % 12]

    elif division == 20:  # D20 Vimsamsa
        part = int((lon % 30) / 1.5)
        sign_idx = int(lon / 30)
        modality = sign_idx % 3
        starts = [0, 4, 8]
        return SIGNS[(starts[modality] + part) % 12]

    elif division == 24:  # D24 Chaturvimsamsa
        part = int((lon % 30) / 1.25)
        sign_idx = int(lon / 30)
        if sign_idx % 2 == 0:
            return SIGNS[(4 + part) % 12]  # Start from Leo
        else:
            return SIGNS[(3 + part) % 12]  # Start from Cancer

    elif division == 27:  # D27 Bhamsa/Nakshatramsa
        part = int((lon % 30) / (30 / 27))
        sign_idx = int(lon / 30)
        element = sign_idx % 4
        starts = [0, 3, 6, 9]
        return SIGNS[(starts[element] + part) % 12]

    elif division == 30:  # D30 Trimsamsa (special division)
        deg = lon % 30
        sign_idx = int(lon / 30)
        if sign_idx % 2 == 0:  # Odd signs
            if deg < 5:
                return SIGNS[0]   # Aries (Mars)
            elif deg < 10:
                return SIGNS[10]  # Aquarius (Saturn)
            elif deg < 18:
                return SIGNS[5]   # Sagittarius (Jupiter)
            elif deg < 25:
                return SIGNS[2]   # Gemini (Mercury)
            else:
                return SIGNS[7]   # Libra (Venus)
        else:  # Even signs (reverse)
            if deg < 5:
                return SIGNS[1]   # Taurus (Venus)
            elif deg < 12:
                return SIGNS[5]   # Virgo (Mercury)
            elif deg < 20:
                return SIGNS[11]  # Pisces (Jupiter)
            elif deg < 25:
                return SIGNS[3]   # Capricorn (Saturn)
            else:
                return SIGNS[8]   # Scorpio (Mars)

    elif division == 40:  # D40 Khavedamsa
        part = int((lon % 30) / 0.75)
        sign_idx = int(lon / 30)
        if sign_idx % 2 == 0:
            return SIGNS[(0 + part) % 12]
        else:
            return SIGNS[(6 + part) % 12]

    elif division == 45:  # D45 Akshavedamsa
        part = int((lon % 30) / (30 / 45))
        sign_idx = int(lon / 30)
        modality = sign_idx % 3
        starts = [0, 4, 8]
        return SIGNS[(starts[modality] + part) % 12]

    elif division == 60:  # D60 Shashtiamsa
        part = int((lon % 30) / 0.5)
        sign_idx = int(lon / 30)
        return SIGNS[(sign_idx + part) % 12]

    else:
        # Generic division
        span = 30.0 / division
        part = int((lon % 30) / span)
        sign_idx = int(lon / 30)
        return SIGNS[(sign_idx + part) % 12]


def build_divisional_chart(
    positions: Dict[str, Dict],
    division: int,
    ayanamsa: str = "LAHIRI",
    jd: float = None,
) -> Dict[str, Any]:
    """
    Build a divisional chart for all planets.
    Positions should already be in sidereal longitude if using Vedic.
    """
    chart = {}
    for name, pos in positions.items():
        sid_lon = pos.get("longitude", 0)
        div_sign = get_divisional_chart_sign(sid_lon, division)
        sign_idx = SIGNS.index(div_sign)
        chart[name] = {
            "sign": div_sign,
            "sign_index": sign_idx,
            "original_longitude": pos.get("longitude"),
        }
    return {
        "division": f"D{division}",
        "planets": chart,
    }


VARGA_DIVISIONS = {
    "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5, "D6": 6,
    "D7": 7, "D8": 8, "D9": 9, "D10": 10, "D12": 12,
    "D16": 16, "D20": 20, "D24": 24, "D27": 27, "D30": 30,
    "D40": 40, "D45": 45, "D60": 60,
}


def build_all_divisional_charts(
    positions: Dict[str, Dict],
    jd: float = None,
    ayanamsa: str = "LAHIRI",
) -> Dict[str, Any]:
    """Build all standard Vedic divisional charts (D1-D60)."""
    charts = {}
    for name, div in VARGA_DIVISIONS.items():
        charts[name] = build_divisional_chart(positions, div, ayanamsa, jd)
    return charts


# ══════════════════════════════════════════════════════════════════════════
# COMPOSITE CHART (Midpoint Method)
# ══════════════════════════════════════════════════════════════════════════

def build_composite_chart(
    positions1: Dict[str, Dict],
    positions2: Dict[str, Dict],
) -> Dict[str, Dict]:
    """Build a composite chart using the midpoint method."""
    composite = {}
    common_planets = set(positions1.keys()) & set(positions2.keys())

    for name in common_planets:
        lon1 = positions1[name]["longitude"]
        lon2 = positions2[name]["longitude"]
        diff = (lon2 - lon1) % 360
        if diff > 180:
            mp = (lon1 + diff / 2 + 180) % 360
        else:
            mp = (lon1 + diff / 2) % 360

        sign, idx, deg = longitude_to_sign(mp)
        composite[name] = {
            "longitude": round(mp, 4),
            "sign": sign,
            "sign_index": idx,
            "degree_in_sign": round(deg, 4),
        }

    return composite
