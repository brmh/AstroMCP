"""
Astrological Calculations Module
All planetary, house, aspect, fixed star, moon phase, eclipse, retrograde,
ingress, sunrise/sunset, and related calculations using Swiss Ephemeris.
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import swisseph as swe
import pytz

from api.core.ephemeris import (
    PLANETS, STANDARD_PLANETS, VEDIC_PLANETS, SIGNS, NAKSHATRAS,
    NAKSHATRA_LORDS, NAKSHATRA_DEITIES,
    EXALTATION, DEBILITATION, COMBUSTION_DEGREES, PLANETARY_FRIENDSHIP,
    longitude_to_sign, longitude_to_nakshatra, get_navamsa_sign,
    angular_difference, get_swe_lock,
    get_julian_day, get_ayanamsa_value, set_sidereal_mode,
    get_house_system_flag,
)
from api.core import AstrologyCalculationError

logger = logging.getLogger(__name__)

# ── Fixed Stars List ──────────────────────────────────────────────────────
MAJOR_FIXED_STARS = [
    "Algol", "Alcyone", "Aldebaran", "Rigel", "Capella", "Sirius",
    "Procyon", "Regulus", "Spica", "Arcturus", "Antares", "Vega",
    "Altair", "Fomalhaut", "Achernar", "Deneb", "Betelgeuse", "Pollux",
    "Castor", "Alphecca", "Agena", "Canopus", "Wega", "Scheat",
    "Markab", "Denebola", "Vindemiatrix", "Zuben Elgenubi",
    "Zuben Eschamali", "Unukalhai", "Ras Alhague",
]

# ── Aspect Definitions ───────────────────────────────────────────────────
ASPECT_DEFINITIONS = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
    "Trine": {"angle": 120, "orb": 8},
    "Square": {"angle": 90, "orb": 7},
    "Sextile": {"angle": 60, "orb": 6},
    "Semi-sextile": {"angle": 30, "orb": 2},
    "Quincunx": {"angle": 150, "orb": 3},
    "Semi-square": {"angle": 45, "orb": 2},
    "Sesquiquadrate": {"angle": 135, "orb": 2},
    "Quintile": {"angle": 72, "orb": 2},
    "Biquintile": {"angle": 144, "orb": 2},
}

# ── Arabic Parts Formulas ─────────────────────────────────────────────────
# Format: (name, day_formula, night_formula_or_None)
# Formula: (sign, A, B) meaning result = A + B - sign  OR  result = sign + A - B
ARABIC_PARTS_FORMULAS = {
    "Part of Fortune": {"day": "ASC+MOON-SUN", "night": "ASC+SUN-MOON"},
    "Part of Spirit": {"day": "ASC+SUN-MOON", "night": "ASC+MOON-SUN"},
    "Part of Love": {"day": "ASC+VENUS-SUN", "night": "ASC+SUN-VENUS"},
    "Part of Marriage": {"day": "ASC+DSC-VENUS", "night": None},
    "Part of Illness": {"day": "ASC+MARS-SATURN", "night": None},
    "Part of Death": {"day": "ASC+8CUSP-MOON", "night": None},
    "Part of Career": {"day": "ASC+MC-SUN", "night": None},
    "Part of Children": {"day": "ASC+JUPITER-SATURN", "night": None},
    "Part of Travel": {"day": "ASC+9CUSP-RULER9", "night": None},
    "Part of Inheritance": {"day": "ASC+MOON-SATURN", "night": None},
    "Part of Faith": {"day": "ASC+MERCURY-MOON", "night": None},
}


# ══════════════════════════════════════════════════════════════════════════
# 1. PLANETARY POSITIONS
# ══════════════════════════════════════════════════════════════════════════

def get_planet_position(
    jd: float,
    planet_id: int,
    flags: int = swe.FLG_SWIEPH | swe.FLG_SPEED,
    zodiac_type: str = "TROPICAL",
    ayanamsa: str = None
) -> Dict[str, Any]:
    """
    Calculate planetary position for a given Julian Day.
    Returns longitude, latitude, distance, speed, sign, nakshatra, etc.
    """
    try:
        with get_swe_lock():
            if zodiac_type.upper() == "SIDEREAL" and ayanamsa:
                set_sidereal_mode(ayanamsa)
                flags |= swe.FLG_SIDEREAL

            result, ret_flags = swe.calc_ut(jd, planet_id, flags)
    except Exception as e:
        raise AstrologyCalculationError(f"Failed to calculate planet {planet_id}: {e}")

    longitude = result[0]
    latitude = result[1]
    distance = result[2]
    speed_longitude = result[3]
    speed_latitude = result[4]
    speed_distance = result[5]

    is_retrograde = speed_longitude < 0
    sign_name, sign_index, degree_in_sign = longitude_to_sign(longitude)

    # For nakshatra, use sidereal longitude
    if zodiac_type.upper() == "SIDEREAL":
        sid_lon = longitude
    else:
        ayanamsa_val = get_ayanamsa_value(jd, ayanamsa)
        sid_lon = (longitude - ayanamsa_val) % 360

    nak_name, nak_num, nak_pada, nak_lord, nak_deity = longitude_to_nakshatra(sid_lon)
    navamsa = get_navamsa_sign(sid_lon)

    return {
        "longitude": round(longitude, 6),
        "latitude": round(latitude, 6),
        "distance": round(distance, 6),
        "speed_longitude": round(speed_longitude, 6),
        "speed_latitude": round(speed_latitude, 6),
        "speed_distance": round(speed_distance, 6),
        "is_retrograde": is_retrograde,
        "sign": sign_name,
        "sign_index": sign_index,
        "degree_in_sign": round(degree_in_sign, 4),
        "nakshatra": nak_name,
        "nakshatra_number": nak_num,
        "nakshatra_pada": nak_pada,
        "nakshatra_lord": nak_lord,
        "nakshatra_deity": nak_deity,
        "navamsa_sign": navamsa,
    }


def get_all_planet_positions(
    jd: float,
    planet_list: Dict[str, int] = None,
    zodiac_type: str = "TROPICAL",
    ayanamsa: str = None,
    include_chiron: bool = True,
    include_lilith: bool = True,
    include_asteroids: bool = False,
) -> Dict[str, Dict]:
    """Get positions for all requested planets."""
    planets = dict(planet_list or STANDARD_PLANETS)

    if include_chiron:
        planets["chiron"] = swe.CHIRON
    if include_lilith:
        planets["mean_apog"] = swe.MEAN_APOG
    if include_asteroids:
        for name in ["ceres", "pallas", "juno", "vesta"]:
            planets[name] = PLANETS[name]

    positions = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    for name, pid in planets.items():
        try:
            positions[name] = get_planet_position(jd, pid, flags, zodiac_type, ayanamsa)
            positions[name]["planet_name"] = name
        except AstrologyCalculationError:
            logger.warning(f"Could not calculate position for {name}")
            continue

    # Calculate Ketu (always opposite Rahu) for Vedic charts
    if "mean_node" in positions:
        rahu_lon = positions["mean_node"]["longitude"]
        ketu_lon = (rahu_lon + 180) % 360
        ketu_sign, ketu_idx, ketu_deg = longitude_to_sign(ketu_lon)
        if zodiac_type.upper() == "SIDEREAL":
            ketu_sid = ketu_lon
        else:
            ayanamsa_val = get_ayanamsa_value(jd, ayanamsa)
            ketu_sid = (ketu_lon - ayanamsa_val) % 360
        nak_name, nak_num, nak_pada, nak_lord, nak_deity = longitude_to_nakshatra(ketu_sid)
        positions["ketu"] = {
            "longitude": round(ketu_lon, 6),
            "latitude": 0.0,
            "distance": positions["mean_node"].get("distance", 0),
            "speed_longitude": positions["mean_node"].get("speed_longitude", 0),
            "speed_latitude": 0.0,
            "speed_distance": 0.0,
            "is_retrograde": True,
            "sign": ketu_sign,
            "sign_index": ketu_idx,
            "degree_in_sign": round(ketu_deg, 4),
            "nakshatra": nak_name,
            "nakshatra_number": nak_num,
            "nakshatra_pada": nak_pada,
            "nakshatra_lord": nak_lord,
            "nakshatra_deity": nak_deity,
            "navamsa_sign": get_navamsa_sign(ketu_sid),
            "planet_name": "ketu",
        }

    return positions


# ══════════════════════════════════════════════════════════════════════════
# 2. HOUSE CUSPS & ANGLES
# ══════════════════════════════════════════════════════════════════════════

def get_houses(
    jd: float,
    latitude: float,
    longitude: float,
    house_system: str = "PLACIDUS",
    zodiac_type: str = "TROPICAL",
    ayanamsa: str = None,
) -> Dict[str, Any]:
    """
    Calculate house cusps and angles.
    Returns all 12 house cusps plus ASC, MC, DC, IC, and other special points.
    """
    hsys = get_house_system_flag(house_system)

    try:
        with get_swe_lock():
            if zodiac_type.upper() == "SIDEREAL" and ayanamsa:
                set_sidereal_mode(ayanamsa)
                flags = swe.FLG_SIDEREAL
            else:
                flags = 0
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, hsys, flags)
    except Exception as e:
        raise AstrologyCalculationError(f"Failed to calculate houses: {e}")

    house_cusps = {}
    for i in range(12):
        sign_name, sign_idx, deg = longitude_to_sign(cusps[i])
        house_cusps[f"house_{i+1}"] = {
            "cusp_longitude": round(cusps[i], 4),
            "sign": sign_name,
            "degree_in_sign": round(deg, 4),
        }

    return {
        "cusps": house_cusps,
        "ascendant": round(ascmc[0], 4),
        "midheaven": round(ascmc[1], 4),
        "armc": round(ascmc[2], 4),
        "vertex": round(ascmc[3], 4),
        "equatorial_ascendant": round(ascmc[4], 4),
        "co_ascendant_w": round(ascmc[5], 4),
        "co_ascendant_f": round(ascmc[6], 4),
        "polar_ascendant": round(ascmc[7], 4),
        "descendant": round((ascmc[0] + 180) % 360, 4),
        "imum_coeli": round((ascmc[1] + 180) % 360, 4),
        "house_system": house_system,
    }


# ══════════════════════════════════════════════════════════════════════════
# 3. PLANET IN HOUSE
# ══════════════════════════════════════════════════════════════════════════

def get_planet_house(planet_longitude: float, house_cusps_list: List[float]) -> int:
    """Determine which house (1-12) a planet occupies based on house cusps."""
    planet_longitude = planet_longitude % 360
    for i in range(12):
        cusp_start = house_cusps_list[i] % 360
        cusp_end = house_cusps_list[(i + 1) % 12] % 360

        if cusp_start < cusp_end:
            if cusp_start <= planet_longitude < cusp_end:
                return i + 1
        else:  # Wraps around 0°
            if planet_longitude >= cusp_start or planet_longitude < cusp_end:
                return i + 1
    return 1  # Fallback


def assign_houses_to_planets(
    positions: Dict[str, Dict],
    houses: Dict[str, Any]
) -> Dict[str, Dict]:
    """Add house number to each planet's position data."""
    cusp_list = [houses["cusps"][f"house_{i+1}"]["cusp_longitude"] for i in range(12)]
    for name, pos in positions.items():
        pos["house"] = get_planet_house(pos["longitude"], cusp_list)
    return positions


# ══════════════════════════════════════════════════════════════════════════
# 4. ASPECTS
# ══════════════════════════════════════════════════════════════════════════

def get_aspects(
    positions: Dict[str, Dict],
    orb_settings: Dict[str, float] = None,
    aspect_definitions: Dict = None,
) -> List[Dict[str, Any]]:
    """
    Calculate all aspects between planets.
    Returns a list of aspect dicts with planet pair, aspect type, orb, etc.
    """
    defs = aspect_definitions or ASPECT_DEFINITIONS
    if orb_settings:
        for asp_name, asp_data in defs.items():
            key = asp_name.lower().replace("-", "_").replace(" ", "_")
            if key in orb_settings:
                asp_data["orb"] = orb_settings[key]

    planet_names = list(positions.keys())
    aspects = []

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1_name = planet_names[i]
            p2_name = planet_names[j]
            p1_lon = positions[p1_name]["longitude"]
            p2_lon = positions[p2_name]["longitude"]
            diff = angular_difference(p1_lon, p2_lon)

            for asp_name, asp_data in defs.items():
                target_angle = asp_data["angle"]
                max_orb = asp_data["orb"]
                orb = abs(diff - target_angle)

                if orb <= max_orb:
                    strength = round((1 - orb / max_orb) * 100, 1)

                    # Determine applying/separating
                    p1_speed = positions[p1_name].get("speed_longitude", 0)
                    p2_speed = positions[p2_name].get("speed_longitude", 0)
                    relative_speed = p1_speed - p2_speed

                    raw_diff = (p2_lon - p1_lon) % 360
                    if raw_diff > 180:
                        raw_diff -= 360

                    if abs(target_angle) < 0.01:
                        applying = (raw_diff > 0 and relative_speed > 0) or (raw_diff < 0 and relative_speed < 0)
                    else:
                        current_sep = abs(raw_diff)
                        applying = (relative_speed > 0 and current_sep > target_angle) or \
                                   (relative_speed < 0 and current_sep < target_angle)

                    aspects.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "aspect_name": asp_name,
                        "aspect_angle": target_angle,
                        "actual_angle": round(diff, 4),
                        "orb": round(orb, 4),
                        "strength": strength,
                        "applying_or_separating": "Applying" if applying else "Separating",
                    })

    aspects.sort(key=lambda x: x["orb"])
    return aspects


def get_transit_aspects(
    natal_positions: Dict[str, Dict],
    transit_positions: Dict[str, Dict],
    orb_settings: Dict[str, float] = None,
) -> List[Dict[str, Any]]:
    """Calculate aspects between transit planets and natal planets."""
    defs = dict(ASPECT_DEFINITIONS)
    if orb_settings:
        for asp_name, asp_data in defs.items():
            key = asp_name.lower().replace("-", "_").replace(" ", "_")
            if key in orb_settings:
                asp_data["orb"] = orb_settings[key]

    aspects = []
    for t_name, t_pos in transit_positions.items():
        for n_name, n_pos in natal_positions.items():
            diff = angular_difference(t_pos["longitude"], n_pos["longitude"])
            for asp_name, asp_data in defs.items():
                orb = abs(diff - asp_data["angle"])
                if orb <= asp_data["orb"]:
                    strength = round((1 - orb / asp_data["orb"]) * 100, 1)
                    aspects.append({
                        "transit_planet": t_name,
                        "natal_planet": n_name,
                        "aspect_name": asp_name,
                        "aspect_angle": asp_data["angle"],
                        "actual_angle": round(diff, 4),
                        "orb": round(orb, 4),
                        "strength": strength,
                    })

    aspects.sort(key=lambda x: x["orb"])
    return aspects


# ══════════════════════════════════════════════════════════════════════════
# 5. DECLINATIONS
# ══════════════════════════════════════════════════════════════════════════

def get_declinations(jd: float, planet_ids: Dict[str, int] = None) -> Dict[str, Dict]:
    """Calculate declinations for all planets. Uses equatorial coordinates."""
    pids = planet_ids or STANDARD_PLANETS
    result = {}

    for name, pid in pids.items():
        try:
            with get_swe_lock():
                pos, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)
            result[name] = {
                "right_ascension": round(pos[0], 6),
                "declination": round(pos[1], 6),
                "distance": round(pos[2], 6),
            }
        except Exception:
            logger.warning(f"Could not calculate declination for {name}")
    return result


def get_parallel_aspects(declinations: Dict[str, Dict], orb: float = 1.0) -> List[Dict]:
    """Find parallel and contra-parallel aspects between planets."""
    names = list(declinations.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d1 = declinations[names[i]]["declination"]
            d2 = declinations[names[j]]["declination"]
            diff_same = abs(d1 - d2)
            diff_opp = abs(d1 + d2)

            if diff_same <= orb:
                aspects.append({
                    "planet1": names[i], "planet2": names[j],
                    "aspect_name": "Parallel",
                    "orb": round(diff_same, 4),
                    "declination1": d1, "declination2": d2,
                })
            if diff_opp <= orb:
                aspects.append({
                    "planet1": names[i], "planet2": names[j],
                    "aspect_name": "Contra-parallel",
                    "orb": round(diff_opp, 4),
                    "declination1": d1, "declination2": d2,
                })
    return aspects


# ══════════════════════════════════════════════════════════════════════════
# 6. MIDPOINTS
# ══════════════════════════════════════════════════════════════════════════

def get_midpoints(positions: Dict[str, Dict]) -> Dict[str, Dict]:
    """Calculate all planet-pair midpoints."""
    names = list(positions.keys())
    midpoints = {}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lon1 = positions[names[i]]["longitude"]
            lon2 = positions[names[j]]["longitude"]

            diff = (lon2 - lon1) % 360
            if diff > 180:
                mp = (lon1 + diff / 2 + 180) % 360
            else:
                mp = (lon1 + diff / 2) % 360

            sign, idx, deg = longitude_to_sign(mp)
            key = f"{names[i]}/{names[j]}"
            midpoints[key] = {
                "longitude": round(mp, 4),
                "sign": sign,
                "degree_in_sign": round(deg, 4),
            }

    return midpoints


# ══════════════════════════════════════════════════════════════════════════
# 7. ARABIC PARTS / LOTS
# ══════════════════════════════════════════════════════════════════════════

def get_arabic_parts(
    positions: Dict[str, Dict],
    ascendant: float,
    houses: Dict[str, Any],
    is_day_chart: bool = True,
) -> Dict[str, Dict]:
    """Calculate Arabic Parts / Lots."""
    sun_lon = positions.get("sun", {}).get("longitude", 0)
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    venus_lon = positions.get("venus", {}).get("longitude", 0)
    mars_lon = positions.get("mars", {}).get("longitude", 0)
    jupiter_lon = positions.get("jupiter", {}).get("longitude", 0)
    saturn_lon = positions.get("saturn", {}).get("longitude", 0)
    mercury_lon = positions.get("mercury", {}).get("longitude", 0)
    mc = houses.get("midheaven", 0)
    dsc = houses.get("descendant", 0)

    cusp_8 = houses.get("cusps", {}).get("house_8", {}).get("cusp_longitude", 0)
    cusp_9 = houses.get("cusps", {}).get("house_9", {}).get("cusp_longitude", 0)

    parts = {}

    def calc_part(a, b, c):
        return (a + b - c) % 360

    # Part of Fortune
    if is_day_chart:
        pof = calc_part(ascendant, moon_lon, sun_lon)
    else:
        pof = calc_part(ascendant, sun_lon, moon_lon)
    sign, idx, deg = longitude_to_sign(pof)
    parts["Part of Fortune"] = {"longitude": round(pof, 4), "sign": sign, "degree_in_sign": round(deg, 4)}

    # Part of Spirit
    if is_day_chart:
        pos_val = calc_part(ascendant, sun_lon, moon_lon)
    else:
        pos_val = calc_part(ascendant, moon_lon, sun_lon)
    sign, idx, deg = longitude_to_sign(pos_val)
    parts["Part of Spirit"] = {"longitude": round(pos_val, 4), "sign": sign, "degree_in_sign": round(deg, 4)}

    # Other parts
    simple_parts = {
        "Part of Love": calc_part(ascendant, venus_lon, sun_lon),
        "Part of Marriage": calc_part(ascendant, dsc, venus_lon),
        "Part of Illness": calc_part(ascendant, mars_lon, saturn_lon),
        "Part of Death": calc_part(ascendant, cusp_8, moon_lon),
        "Part of Career": calc_part(ascendant, mc, sun_lon),
        "Part of Children": calc_part(ascendant, jupiter_lon, saturn_lon),
        "Part of Travel": calc_part(ascendant, cusp_9, sun_lon),
        "Part of Inheritance": calc_part(ascendant, moon_lon, saturn_lon),
        "Part of Faith": calc_part(ascendant, mercury_lon, moon_lon),
    }

    for name, lon in simple_parts.items():
        sign, idx, deg = longitude_to_sign(lon)
        parts[name] = {"longitude": round(lon, 4), "sign": sign, "degree_in_sign": round(deg, 4)}

    return parts


# ══════════════════════════════════════════════════════════════════════════
# 8. FIXED STARS
# ══════════════════════════════════════════════════════════════════════════

def get_fixed_star_positions(jd: float, stars: List[str] = None) -> List[Dict]:
    """Calculate positions for major fixed stars using swe.fixstar2_ut()."""
    star_list = stars or MAJOR_FIXED_STARS
    results = []

    for star_name in star_list:
        try:
            with get_swe_lock():
                result, star_info = swe.fixstar2_ut(star_name, jd, swe.FLG_SWIEPH)
            sign, idx, deg = longitude_to_sign(result[0])
            results.append({
                "name": star_name,
                "longitude": round(result[0], 4),
                "latitude": round(result[1], 4),
                "distance": round(result[2], 4) if len(result) > 2 else None,
                "sign": sign,
                "degree_in_sign": round(deg, 4),
                "speed_longitude": round(result[3], 6) if len(result) > 3 else 0,
            })
        except Exception as e:
            logger.warning(f"Could not calculate fixed star {star_name}: {e}")
            continue

    return results


def get_fixed_star_conjunctions(
    jd: float,
    positions: Dict[str, Dict],
    orb: float = 1.0,
    stars: List[str] = None,
) -> List[Dict]:
    """Find fixed stars conjunct natal planets within the given orb."""
    star_positions = get_fixed_star_positions(jd, stars)
    conjunctions = []

    for star in star_positions:
        for planet_name, planet_pos in positions.items():
            diff = angular_difference(star["longitude"], planet_pos["longitude"])
            if diff <= orb:
                conjunctions.append({
                    "star": star["name"],
                    "star_longitude": star["longitude"],
                    "planet": planet_name,
                    "planet_longitude": planet_pos["longitude"],
                    "orb": round(diff, 4),
                })

    conjunctions.sort(key=lambda x: x["orb"])
    return conjunctions


# ══════════════════════════════════════════════════════════════════════════
# 9. LUNAR PHASES & MOON DATA
# ══════════════════════════════════════════════════════════════════════════

def get_moon_phase(jd: float) -> Dict[str, Any]:
    """Calculate the current moon phase for the given Julian Day."""
    with get_swe_lock():
        sun_pos, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
        moon_pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)

    sun_lon = sun_pos[0]
    moon_lon = moon_pos[0]
    elongation = (moon_lon - sun_lon) % 360

    # Phase name
    if elongation < 22.5:
        phase_name = "New Moon"
    elif elongation < 67.5:
        phase_name = "Waxing Crescent"
    elif elongation < 112.5:
        phase_name = "First Quarter"
    elif elongation < 157.5:
        phase_name = "Waxing Gibbous"
    elif elongation < 202.5:
        phase_name = "Full Moon"
    elif elongation < 247.5:
        phase_name = "Waning Gibbous"
    elif elongation < 292.5:
        phase_name = "Last Quarter"
    elif elongation < 337.5:
        phase_name = "Waning Crescent"
    else:
        phase_name = "New Moon"

    # Illumination percentage (approximation)
    illumination = round((1 - math.cos(math.radians(elongation))) / 2 * 100, 1)

    # Approximate age in days (synodic month ≈ 29.53 days)
    age = round(elongation / 360 * 29.53, 1)

    return {
        "phase_name": phase_name,
        "elongation": round(elongation, 4),
        "illumination_percent": illumination,
        "age_days": age,
        "sun_longitude": round(sun_lon, 4),
        "moon_longitude": round(moon_lon, 4),
    }


def get_lunar_eclipses(jd_start: float, jd_end: float) -> List[Dict]:
    """Find lunar eclipses in the given Julian Day range."""
    eclipses = []
    jd = jd_start
    try:
        while jd < jd_end:
            with get_swe_lock():
                ret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0)
            if ret[0] == 0 or ret[1][0] >= jd_end:
                break
            eclipse_jd = ret[1][0]
            if eclipse_jd >= jd_start:
                # Determine type
                ecl_type = ret[0]
                type_name = "Partial"
                if ecl_type & swe.ECL_TOTAL:
                    type_name = "Total"
                elif ecl_type & swe.ECL_PENUMBRAL:
                    type_name = "Penumbral"

                eclipses.append({
                    "type": type_name,
                    "julian_day": eclipse_jd,
                    "maximum_jd": ret[1][0],
                })
            jd = eclipse_jd + 20  # Jump ahead
    except Exception as e:
        logger.warning(f"Eclipse calculation error: {e}")
    return eclipses


def get_solar_eclipses(jd_start: float, jd_end: float) -> List[Dict]:
    """Find solar eclipses in the given Julian Day range."""
    eclipses = []
    jd = jd_start
    try:
        while jd < jd_end:
            with get_swe_lock():
                ret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0)
            if ret[0] == 0 or ret[1][0] >= jd_end:
                break
            eclipse_jd = ret[1][0]
            if eclipse_jd >= jd_start:
                ecl_type = ret[0]
                type_name = "Partial"
                if ecl_type & swe.ECL_TOTAL:
                    type_name = "Total"
                elif ecl_type & swe.ECL_ANNULAR:
                    type_name = "Annular"
                elif ecl_type & swe.ECL_ANNULAR_TOTAL:
                    type_name = "Hybrid"

                eclipses.append({
                    "type": type_name,
                    "julian_day": eclipse_jd,
                })
            jd = eclipse_jd + 20
    except Exception as e:
        logger.warning(f"Solar eclipse calculation error: {e}")
    return eclipses


# ══════════════════════════════════════════════════════════════════════════
# 10. RETROGRADE PERIODS
# ══════════════════════════════════════════════════════════════════════════

def get_retrograde_periods(
    planet_id: int,
    jd_start: float,
    jd_end: float,
    step: float = 1.0,
) -> List[Dict]:
    """Find retrograde periods for a planet in the given date range."""
    periods = []
    jd = jd_start
    was_retrograde = False
    retro_start = None

    while jd <= jd_end:
        with get_swe_lock():
            pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
        is_retro = pos[3] < 0

        if is_retro and not was_retrograde:
            retro_start = jd
        elif not is_retro and was_retrograde and retro_start:
            sign_start, _, _ = longitude_to_sign(pos[0])
            periods.append({
                "retrograde_start_jd": retro_start,
                "retrograde_end_jd": jd,
                "sign_at_station": sign_start,
                "degree_at_station": round(pos[0] % 30, 4),
            })
            retro_start = None

        was_retrograde = is_retro
        jd += step

    return periods


# ══════════════════════════════════════════════════════════════════════════
# 11. PLANETARY INGRESSES
# ══════════════════════════════════════════════════════════════════════════

def get_planetary_ingresses(
    planet_id: int,
    jd_start: float,
    jd_end: float,
    step: float = 1.0,
) -> List[Dict]:
    """Find dates when a planet changes zodiac signs."""
    ingresses = []
    jd = jd_start
    prev_sign = None

    while jd <= jd_end:
        with get_swe_lock():
            pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
        current_sign = int(pos[0] / 30)

        if prev_sign is not None and current_sign != prev_sign:
            new_sign = SIGNS[current_sign]
            ingresses.append({
                "julian_day": jd,
                "new_sign": new_sign,
                "sign_index": current_sign,
                "longitude": round(pos[0], 4),
            })

        prev_sign = current_sign
        jd += step

    return ingresses


# ══════════════════════════════════════════════════════════════════════════
# 12. SUNRISE / SUNSET / TWILIGHT
# ══════════════════════════════════════════════════════════════════════════

def get_solar_events(
    jd: float,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> Dict[str, Any]:
    """
    Calculate sunrise, sunset, and twilight times using swe.rise_trans().
    """
    geopos = (longitude, latitude, altitude)
    events = {}

    event_types = {
        "sunrise": swe.CALC_RISE | swe.BIT_DISC_CENTER,
        "sunset": swe.CALC_SET | swe.BIT_DISC_CENTER,
        "transit": swe.CALC_MTRANSIT,
    }

    for name, flag in event_types.items():
        try:
            with get_swe_lock():
                ret = swe.rise_trans(jd, swe.SUN, "", 0, flag, geopos, 0, 0)
                if ret[0] >= 0:
                    events[name] = ret[1][0]
        except Exception:
            events[name] = None

    # Day length
    if events.get("sunrise") and events.get("sunset"):
        day_length_hours = (events["sunset"] - events["sunrise"]) * 24
        events["day_length_hours"] = round(day_length_hours, 2)
    else:
        events["day_length_hours"] = None

    return events


# ══════════════════════════════════════════════════════════════════════════
# 13. LUNAR RISE / SET
# ══════════════════════════════════════════════════════════════════════════

def get_lunar_events(
    jd: float,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> Dict[str, Any]:
    """Calculate moonrise and moonset times."""
    geopos = (longitude, latitude, altitude)
    events = {}

    for name, flag in [("moonrise", swe.CALC_RISE), ("moonset", swe.CALC_SET)]:
        try:
            with get_swe_lock():
                ret = swe.rise_trans(jd, swe.MOON, "", 0, flag, geopos, 0, 0)
                if ret[0] >= 0:
                    events[name] = ret[1][0]
        except Exception:
            events[name] = None

    return events


# ══════════════════════════════════════════════════════════════════════════
# 14. HELIACAL RISE/SET
# ══════════════════════════════════════════════════════════════════════════

def get_heliacal_phenomena(
    jd: float,
    planet_or_star: str,
    latitude: float,
    longitude: float,
    altitude: float = 0,
) -> Dict[str, Any]:
    """Calculate heliacal rise/set for a planet or star."""
    geopos = (longitude, latitude, altitude)
    atmo = (1013.25, 15, 50, 0.25)  # pressure, temp, humidity, extinction coeff
    observer = (25, 1, 1)  # age, Snellen ratio, telescope

    result = {}
    try:
        if planet_or_star.lower() in PLANETS:
            obj_name = ""
            planet_id = PLANETS[planet_or_star.lower()]
            with get_swe_lock():
                ret = swe.heliacal_ut(jd, geopos, atmo, observer, planet_or_star, swe.HELIACAL_RISING, 0)
            result["heliacal_rising_jd"] = ret[0] if ret else None
        else:
            result["note"] = "Heliacal calculation attempted"
    except Exception as e:
        result["error"] = str(e)

    return result


# ══════════════════════════════════════════════════════════════════════════
# 15. SIDEREAL TIME
# ══════════════════════════════════════════════════════════════════════════

def get_sidereal_time(jd: float, longitude: float = 0) -> float:
    """Calculate local sidereal time in degrees."""
    with get_swe_lock():
        lst = swe.sidtime(jd) * 15  # Convert hours to degrees
    lst = (lst + longitude) % 360
    return round(lst, 6)


# ══════════════════════════════════════════════════════════════════════════
# ANTISCIA
# ══════════════════════════════════════════════════════════════════════════

def get_antiscia(positions: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Calculate antiscia (mirror point across Cancer-Capricorn axis)
    and contra-antiscia (mirror across Aries-Libra axis).
    """
    result = {}
    for name, pos in positions.items():
        lon = pos["longitude"]
        antiscion = (360 - lon + 180) % 360  # Mirror across 0° Cancer
        contra = (180 - lon) % 360  # Mirror across 0° Aries

        a_sign, _, a_deg = longitude_to_sign(antiscion)
        c_sign, _, c_deg = longitude_to_sign(contra)

        result[name] = {
            "antiscion_longitude": round(antiscion, 4),
            "antiscion_sign": a_sign,
            "antiscion_degree": round(a_deg, 4),
            "contra_antiscion_longitude": round(contra, 4),
            "contra_antiscion_sign": c_sign,
            "contra_antiscion_degree": round(c_deg, 4),
        }
    return result


# ══════════════════════════════════════════════════════════════════════════
# COMBUSTION CHECK
# ══════════════════════════════════════════════════════════════════════════

def check_combustion(positions: Dict[str, Dict]) -> List[Dict]:
    """Check which planets are combust (too close to the Sun)."""
    sun_lon = positions.get("sun", {}).get("longitude")
    if sun_lon is None:
        return []

    combust = []
    for name, pos in positions.items():
        if name in ("sun", "mean_node", "true_node", "ketu", "rahu"):
            continue

        distance_from_sun = angular_difference(pos["longitude"], sun_lon)
        is_retro = pos.get("is_retrograde", False)

        # Get combustion threshold
        if name == "mercury":
            threshold = COMBUSTION_DEGREES["mercury_retrograde"] if is_retro else COMBUSTION_DEGREES["mercury_direct"]
        elif name == "venus":
            threshold = COMBUSTION_DEGREES["venus_retrograde"] if is_retro else COMBUSTION_DEGREES["venus_direct"]
        elif name in COMBUSTION_DEGREES:
            threshold = COMBUSTION_DEGREES[name]
        else:
            continue

        if distance_from_sun <= threshold:
            combust.append({
                "planet": name,
                "distance_from_sun": round(distance_from_sun, 4),
                "threshold": threshold,
                "is_combust": True,
            })

    return combust


# ══════════════════════════════════════════════════════════════════════════
# PLANETARY WAR (Graha Yuddha)
# ══════════════════════════════════════════════════════════════════════════

def check_planetary_war(positions: Dict[str, Dict]) -> List[Dict]:
    """
    Detect Graha Yuddha (planetary war).
    Two planets (excluding Sun/Moon/Rahu/Ketu) within 1° of each other.
    The planet with lower latitude wins.
    """
    excluded = {"sun", "moon", "mean_node", "true_node", "ketu", "rahu"}
    planet_names = [n for n in positions if n not in excluded]
    wars = []

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]
            diff = angular_difference(positions[p1]["longitude"], positions[p2]["longitude"])

            if diff <= 1.0:
                lat1 = abs(positions[p1].get("latitude", 0))
                lat2 = abs(positions[p2].get("latitude", 0))
                winner = p1 if lat1 < lat2 else p2
                loser = p2 if winner == p1 else p1

                wars.append({
                    "planet1": p1,
                    "planet2": p2,
                    "separation": round(diff, 4),
                    "winner": winner,
                    "loser": loser,
                })

    return wars
