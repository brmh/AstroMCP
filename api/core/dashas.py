"""
Vimshottari Dasha Engine + Yogini, Ashtottari, Char Dasha Systems.
"""

import math
from typing import Dict, List, Any, Optional
from api.core.ephemeris import (
    DASHA_LORDS, DASHA_YEARS, SIGNS, longitude_to_nakshatra,
)

TOTAL_DASHA_YEARS = 120
JD_PER_YEAR = 365.25

YOGINI_LORDS = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
YOGINI_PLANETS = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"]

ASHTOTTARI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus"]
ASHTOTTARI_YEARS = [6, 15, 8, 17, 10, 19, 12, 21]


def get_vimshottari_dasha_start(moon_longitude: float, birth_jd: float) -> Dict:
    nak_name, nak_num, nak_pada, nak_lord, _ = longitude_to_nakshatra(moon_longitude)
    lord_index = DASHA_LORDS.index(nak_lord)
    dasha_period_years = DASHA_YEARS[lord_index]
    nak_span = 360.0 / 27.0
    fraction_elapsed = (moon_longitude % nak_span) / nak_span
    elapsed_years = fraction_elapsed * dasha_period_years
    remaining_years = dasha_period_years - elapsed_years
    return {
        "birth_nakshatra": nak_name, "birth_nakshatra_number": nak_num,
        "birth_nakshatra_pada": nak_pada, "birth_dasha_lord": nak_lord,
        "dasha_period_years": dasha_period_years,
        "fraction_elapsed_at_birth": round(fraction_elapsed, 6),
        "elapsed_years": round(elapsed_years, 4),
        "remaining_years": round(remaining_years, 4),
        "dasha_cycle_start_jd": birth_jd - (elapsed_years * JD_PER_YEAR),
    }


def get_mahadashas(birth_jd: float, moon_longitude: float) -> List[Dict]:
    info = get_vimshottari_dasha_start(moon_longitude, birth_jd)
    lord_index = DASHA_LORDS.index(info["birth_dasha_lord"])
    remaining = info["remaining_years"]
    mahadashas = []
    cur = birth_jd
    end = cur + remaining * JD_PER_YEAR
    mahadashas.append({"lord": info["birth_dasha_lord"], "start_jd": cur, "end_jd": end,
                        "duration_years": round(remaining, 4), "is_birth_dasha": True})
    cur = end
    for i in range(1, 9):
        idx = (lord_index + i) % 9
        years = DASHA_YEARS[idx]
        end = cur + years * JD_PER_YEAR
        mahadashas.append({"lord": DASHA_LORDS[idx], "start_jd": cur, "end_jd": end,
                            "duration_years": years, "is_birth_dasha": False})
        cur = end
    return mahadashas


def get_antardashas(mahadasha: Dict) -> List[Dict]:
    lord = mahadasha["lord"]
    lord_index = DASHA_LORDS.index(lord)
    maha_years = mahadasha["duration_years"]
    antardashas = []
    cur = mahadasha["start_jd"]
    for i in range(9):
        idx = (lord_index + i) % 9
        frac = (maha_years * DASHA_YEARS[idx]) / TOTAL_DASHA_YEARS
        end = cur + frac * JD_PER_YEAR
        antardashas.append({"mahadasha_lord": lord, "antardasha_lord": DASHA_LORDS[idx],
                             "start_jd": cur, "end_jd": end, "duration_years": round(frac, 4)})
        cur = end
    return antardashas


def get_pratyantardashas(antardasha: Dict) -> List[Dict]:
    lord = antardasha["antardasha_lord"]
    lord_index = DASHA_LORDS.index(lord)
    antar_years = antardasha["duration_years"]
    pratyantars = []
    cur = antardasha["start_jd"]
    for i in range(9):
        idx = (lord_index + i) % 9
        frac = (antar_years * DASHA_YEARS[idx]) / TOTAL_DASHA_YEARS
        end = cur + frac * JD_PER_YEAR
        pratyantars.append({
            "mahadasha_lord": antardasha["mahadasha_lord"],
            "antardasha_lord": lord,
            "pratyantardasha_lord": DASHA_LORDS[idx],
            "start_jd": cur, "end_jd": end, "duration_years": round(frac, 6)
        })
        cur = end
    return pratyantars


def get_current_dasha(birth_jd: float, moon_longitude: float, query_jd: float = None) -> Dict:
    if query_jd is None:
        import swisseph as swe
        query_jd = swe.julday(2026, 3, 6, 0)
    mahadashas = get_mahadashas(birth_jd, moon_longitude)
    current_maha = next((m for m in mahadashas if m["start_jd"] <= query_jd < m["end_jd"]), None)
    if not current_maha:
        return {"error": "Query date outside dasha range"}
    antardashas = get_antardashas(current_maha)
    current_antar = next((a for a in antardashas if a["start_jd"] <= query_jd < a["end_jd"]), None)
    result = {"mahadasha": {"lord": current_maha["lord"], "start_jd": current_maha["start_jd"],
              "end_jd": current_maha["end_jd"],
              "remaining_years": round((current_maha["end_jd"] - query_jd) / JD_PER_YEAR, 4)}}
    if current_antar:
        result["antardasha"] = {"lord": current_antar["antardasha_lord"],
            "start_jd": current_antar["start_jd"], "end_jd": current_antar["end_jd"],
            "remaining_years": round((current_antar["end_jd"] - query_jd) / JD_PER_YEAR, 4)}
        pratyantars = get_pratyantardashas(current_antar)
        cp = next((p for p in pratyantars if p["start_jd"] <= query_jd < p["end_jd"]), None)
        if cp:
            result["pratyantardasha"] = {"lord": cp["pratyantardasha_lord"],
                "start_jd": cp["start_jd"], "end_jd": cp["end_jd"],
                "remaining_years": round((cp["end_jd"] - query_jd) / JD_PER_YEAR, 4)}
    return result


def get_yogini_dashas(birth_jd: float, moon_longitude: float) -> List[Dict]:
    _, nak_num, _, _, _ = longitude_to_nakshatra(moon_longitude)
    yi = (nak_num - 1) % 8
    frac = (moon_longitude % (360.0 / 27.0)) / (360.0 / 27.0)
    dashas, cur = [], birth_jd
    rem = YOGINI_YEARS[yi] * (1 - frac)
    end = cur + rem * JD_PER_YEAR
    dashas.append({"yogini": YOGINI_LORDS[yi], "planet": YOGINI_PLANETS[yi],
                   "start_jd": cur, "end_jd": end, "duration_years": round(rem, 4)})
    cur = end
    for c in range(3):
        for i in range(1, 9):
            idx = (yi + i) % 8
            end = cur + YOGINI_YEARS[idx] * JD_PER_YEAR
            dashas.append({"yogini": YOGINI_LORDS[idx], "planet": YOGINI_PLANETS[idx],
                           "start_jd": cur, "end_jd": end, "duration_years": YOGINI_YEARS[idx]})
            cur = end
    return dashas


def get_ashtottari_dashas(birth_jd: float, moon_longitude: float) -> List[Dict]:
    _, nak_num, _, _, _ = longitude_to_nakshatra(moon_longitude)
    li = (nak_num - 1) % 8
    frac = (moon_longitude % (360.0 / 27.0)) / (360.0 / 27.0)
    dashas, cur = [], birth_jd
    rem = ASHTOTTARI_YEARS[li] * (1 - frac)
    end = cur + rem * JD_PER_YEAR
    dashas.append({"lord": ASHTOTTARI_LORDS[li], "start_jd": cur, "end_jd": end,
                   "duration_years": round(rem, 4)})
    cur = end
    for i in range(1, 8):
        idx = (li + i) % 8
        end = cur + ASHTOTTARI_YEARS[idx] * JD_PER_YEAR
        dashas.append({"lord": ASHTOTTARI_LORDS[idx], "start_jd": cur, "end_jd": end,
                       "duration_years": ASHTOTTARI_YEARS[idx]})
        cur = end
    return dashas


def get_char_dashas(houses: Dict, zodiac_type: str = "SIDEREAL") -> List[Dict]:
    asc_idx = int(houses.get("ascendant", 0) / 30)
    dashas = []
    for i in range(12):
        idx = (asc_idx + i) % 12
        duration = ((idx - asc_idx) % 12) + 1
        if duration > 12:
            duration = 12
        dashas.append({"sign": SIGNS[idx], "sign_index": idx, "duration_years": duration})
    return dashas
