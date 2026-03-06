"""
Shadbala (Six-fold Planetary Strength) Calculations.
"""

from typing import Dict, List, Any
from api.core.ephemeris import (
    SIGNS, EXALTATION, DEBILITATION, MOOLATRIKONA, PLANETARY_FRIENDSHIP,
    SIGN_RULERS, longitude_to_sign
)
import math

# Naisargika Bala (Natural strength) — fixed values in Shashtiamsas
NAISARGIKA_BALA = {
    "sun": 60.0, "moon": 51.43, "venus": 42.86, "jupiter": 34.29,
    "mercury": 25.71, "mars": 17.14, "saturn": 8.57,
}

# Dig Bala direction strengths
DIG_BALA_STRONG_HOUSE = {
    "jupiter": 1, "mercury": 1,
    "moon": 4, "venus": 4,
    "saturn": 7,
    "sun": 10, "mars": 10,
}

# Minimum required Shadbala (in Rupas)
MIN_SHADBALA = {
    "sun": 6.5, "moon": 6.0, "mars": 5.0, "mercury": 7.0,
    "jupiter": 6.5, "venus": 5.5, "saturn": 5.0,
}


def calculate_uchcha_bala(planet: str, longitude: float) -> float:
    """Exaltation strength (0-60 Shashtiamsas). Max at exact exaltation, 0 at debilitation."""
    if planet not in EXALTATION:
        return 30.0
    exalt_sign, exalt_deg = EXALTATION[planet]
    exalt_idx = SIGNS.index(exalt_sign)
    exalt_lon = exalt_idx * 30 + (exalt_deg or 15)
    diff = abs(longitude - exalt_lon) % 360
    if diff > 180:
        diff = 360 - diff
    return round((180 - diff) / 3, 2)  # Max 60 at exact exaltation


def calculate_dignity_bala(planet: str, longitude: float) -> float:
    """
    FIX: Saptavargaja Bala (dignity strength in Rasi).
    Own sign: 45, Moolatrikona: 45, Friendly: 30, Neutral: 15, Enemy: 7.5, Debilitation: 0.
    Added to Sthana Bala for more accurate total.
    """
    if planet not in SIGN_RULERS:
        return 15.0
    sign_name, sign_idx, _ = longitude_to_sign(longitude)
    own_ruler = SIGN_RULERS[sign_idx].lower()

    # Check moolatrikona
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        deg_in_sign = longitude % 30
        if sign_name == mt_sign and mt_start <= deg_in_sign <= mt_end:
            return 45.0

    # Check own sign
    if own_ruler == planet:
        return 45.0

    # Check friendship
    friendship = PLANETARY_FRIENDSHIP.get(planet, {})
    if own_ruler in friendship.get("friends", []):
        return 30.0
    elif own_ruler in friendship.get("enemies", []):
        # Check debilitation
        if planet in DEBILITATION and DEBILITATION[planet][0] == sign_name:
            return 0.0
        return 7.5
    else:
        return 15.0  # neutral


def calculate_dig_bala(planet: str, house: int) -> float:
    """Directional strength (0-60 Shashtiamsas)."""
    if planet not in DIG_BALA_STRONG_HOUSE:
        return 30.0
    strong = DIG_BALA_STRONG_HOUSE[planet]
    diff = abs(house - strong) % 12
    if diff > 6:
        diff = 12 - diff
    return round((6 - diff) * 10, 2)  # Max 60 at strongest direction


def calculate_kala_bala(planet: str, jd: float, is_day: bool) -> float:
    """
    Temporal strength — simplified version.
    Day planets (Sun, Jupiter, Venus) stronger during day.
    Night planets (Moon, Mars, Saturn) stronger at night.
    """
    day_planets = ["sun", "jupiter", "venus"]
    night_planets = ["moon", "mars", "saturn"]
    if planet in day_planets:
        return 45.0 if is_day else 15.0
    elif planet in night_planets:
        return 15.0 if is_day else 45.0
    return 30.0  # Mercury is neutral


def calculate_chesta_bala(planet: str, speed: float) -> float:
    """Motional strength based on planetary speed. Retrograde planets get some strength."""
    if planet in ("sun", "moon"):
        return 30.0  # Sun/Moon don't have chesta bala in the traditional sense
    if speed < 0:
        return 45.0  # Retrograde gets higher chesta bala
    elif speed > 1:
        return 15.0  # Fast moving — lower
    return 30.0


def calculate_naisargika_bala(planet: str) -> float:
    """Natural strength — fixed values."""
    return NAISARGIKA_BALA.get(planet, 30.0)


def calculate_drik_bala(planet: str, aspects_received: List[Dict]) -> float:
    """Aspectual strength based on benefic/malefic aspects received."""
    benefics = {"jupiter", "venus", "mercury", "moon"}
    malefics = {"saturn", "mars", "sun", "rahu", "ketu"}
    score = 0
    for asp in aspects_received:
        other = asp.get("planet1") if asp.get("planet2") == planet else asp.get("planet2")
        if other in benefics:
            score += 10
        elif other in malefics:
            score -= 5
    return max(0, min(60, 30 + score))


def calculate_shadbala(
    positions: Dict, houses: Dict, aspects: List[Dict],
    jd: float = 0, is_day: bool = None,
) -> Dict[str, Dict]:
    """
    Calculate complete Shadbala for all planets.
    Returns strengths in Shashtiamsas and Rupas (1 Rupa = 60 Shashtiamsas).
    """
    # FIX Bug 5: Derive is_day from the actual Sun house if not provided
    if is_day is None:
        asc_lon = houses.get("ascendant", 0)
        sun_lon = positions.get("sun", {}).get("longitude", 0)
        # Sun in houses 7-12 (above horizon in whole-sign reckoning) = daytime
        sun_house_offset = int(((sun_lon - asc_lon) % 360) / 30)
        is_day = sun_house_offset >= 6  # offsets 6-11 = houses 7-12

    results = {}
    shadbala_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]

    for planet in shadbala_planets:
        if planet not in positions:
            continue
        pos = positions[planet]
        lon = pos.get("longitude", 0)
        house = pos.get("house", 1)
        speed = pos.get("speed_longitude", 0)

        planet_aspects = [a for a in aspects if a.get("planet1") == planet or a.get("planet2") == planet]

        # FIX Bug 6: Sthana Bala = Uchcha Bala + Dignity Bala (combined)
        uchcha = calculate_uchcha_bala(planet, lon)
        dignity = calculate_dignity_bala(planet, lon)
        sthana = round((uchcha + dignity) / 2, 2)  # average to keep in 0-60 range

        dig = calculate_dig_bala(planet, house)
        kala = calculate_kala_bala(planet, jd, is_day)
        chesta = calculate_chesta_bala(planet, speed)
        naisargika = calculate_naisargika_bala(planet)
        drik = calculate_drik_bala(planet, planet_aspects)

        total_shashtiamsas = sthana + dig + kala + chesta + naisargika + drik
        total_rupas = round(total_shashtiamsas / 60, 2)
        min_required = MIN_SHADBALA.get(planet, 5.0)

        results[planet] = {
            "uchcha_bala": uchcha,
            "dignity_bala": dignity,
            "sthana_bala": sthana, "dig_bala": dig, "kala_bala": kala,
            "chesta_bala": chesta, "naisargika_bala": naisargika, "drik_bala": drik,
            "total_shashtiamsas": round(total_shashtiamsas, 2),
            "total_rupas": total_rupas,
            "minimum_required_rupas": min_required,
            "is_strong": total_rupas >= min_required,
            "birth_is_daytime": is_day,
        }

    return results
