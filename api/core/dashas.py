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

DASHA_INTERPRETATIONS = {
    "Sun": "A period of self-realization, career advancement, and seeking authority. Can bring issues with ego or father figures.",
    "Moon": "A time of emotional focus, changes in mindset, and maternal themes. Emotional fluctuations and travel are common.",
    "Mars": "High energy, ambition, and drive. Can bring conflict, property dealings, or sudden events requiring courage.",
    "Rahu": "Intense material desires, foreign connections, and sudden changes. A period of illusion but also immense worldly ambition.",
    "Jupiter": "Expansion, learning, spiritual growth, and financial gains. Often brings blessings, children, or higher wisdom.",
    "Saturn": "Discipline, hard work, delays, and structural growth. A karmic period demanding patience, service, and responsibility.",
    "Mercury": "Focus on communication, intellect, business, and skill development. Favorable for education, networking, and writing.",
    "Ketu": "Spiritual introspection, detachment from material goals, and sudden endings. A highly mystical or restrictive period.",
    "Venus": "Emphasis on relationships, luxury, arts, and comforts. A period of romance, vehicle purchases, and material enjoyment."
}

def get_vimshottari_dasha_start(moon_longitude: float, birth_jd: float) -> Dict:
    nak_name, nak_num, nak_pada, nak_lord, _ = longitude_to_nakshatra(moon_longitude)
    lord_index = DASHA_LORDS.index(nak_lord)
    dasha_period_years = DASHA_YEARS[lord_index]
    nak_span = 360.0 / 27.0
    # FIX: compute position within the specific nakshatra (not modulo entire zodiac)
    nak_index = int(moon_longitude / nak_span)
    pos_within_nak = moon_longitude - (nak_index * nak_span)
    fraction_elapsed = pos_within_nak / nak_span
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
    # FIX: generate 3 full 120-year cycles (27 iterations) for complete lifetime coverage
    for i in range(1, 27):
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

def get_sookshmadashas(pratyantardasha: Dict) -> List[Dict]:
    lord = pratyantardasha["pratyantardasha_lord"]
    lord_index = DASHA_LORDS.index(lord)
    pratyantar_years = pratyantardasha["duration_years"]
    sookshmas = []
    cur = pratyantardasha["start_jd"]
    for i in range(9):
        idx = (lord_index + i) % 9
        frac = (pratyantar_years * DASHA_YEARS[idx]) / TOTAL_DASHA_YEARS
        end = cur + frac * JD_PER_YEAR
        sookshmas.append({
            "mahadasha_lord": pratyantardasha["mahadasha_lord"],
            "antardasha_lord": pratyantardasha["antardasha_lord"],
            "pratyantardasha_lord": lord,
            "sookshmadasha_lord": DASHA_LORDS[idx],
            "start_jd": cur, "end_jd": end, "duration_years": round(frac, 8)
        })
        cur = end
    return sookshmas


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
                
            sookshmas = get_sookshmadashas(cp)
            cs = next((s for s in sookshmas if s["start_jd"] <= query_jd < s["end_jd"]), None)
            if cs:
                result["sookshmadasha"] = {"lord": cs["sookshmadasha_lord"],
                    "start_jd": cs["start_jd"], "end_jd": cs["end_jd"],
                    "remaining_years": round((cs["end_jd"] - query_jd) / JD_PER_YEAR, 6)}
                
    # Add interpretations
    maha_lord = result["mahadasha"]["lord"]
    result["interpretation"] = {
        "mahadasha_theme": DASHA_INTERPRETATIONS.get(maha_lord, "")
    }
    
    if current_antar:
        antar_lord = result["antardasha"]["lord"]
        result["interpretation"]["antardasha_theme"] = DASHA_INTERPRETATIONS.get(antar_lord, "")
        result["interpretation"]["synthesis"] = f"During this phase, the overarching theme of {maha_lord} ({DASHA_INTERPRETATIONS.get(maha_lord, '').lower().split('.')[0]}) is colored by the sub-influence of {antar_lord} ({DASHA_INTERPRETATIONS.get(antar_lord, '').lower().split('.')[0]})."
        
    return result

def get_dasha_interpretation(maha_lord: str, antar_lord: str = None) -> Dict[str, str]:
    """
    Returns standalone interpretation texts based on planet combinations.
    """
    maha = maha_lord.capitalize()
    maha_theme = DASHA_INTERPRETATIONS.get(maha, "Unknown or invalid planet.")
    
    result = {"mahadasha_lord": maha, "mahadasha_theme": maha_theme}
    
    if antar_lord:
        antar = antar_lord.capitalize()
        antar_theme = DASHA_INTERPRETATIONS.get(antar, "Unknown or invalid planet.")
        
        # Determine synthesis
        if maha == antar:
            synthesis = f"The energy of {maha} is intensely concentrated. " + maha_theme.split(".")[0] + " is the absolute primary focus."
        else:
            synthesis = f"During this phase, the overarching theme of {maha} ({maha_theme.lower().split('.')[0]}) is heavily colored by the sub-influence of {antar} ({antar_theme.lower().split('.')[0]})."
            
        result.update({
            "antardasha_lord": antar,
            "antardasha_theme": antar_theme,
            "synthesis": synthesis
        })
        
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


def get_char_dashas(birth_jd: float, houses: Dict, positions: Dict) -> List[Dict]:
    """Calculate the Jaimini Chara Dasha timeline."""
    asc_deg = houses.get("ascendant", 0)
    import math
    asc_idx = int(asc_deg / 30)
    
    # Direct signs: Ar, Ta, Ge, Li, Sc, Sg -> indices 0, 1, 2, 6, 7, 8
    direct_signs = {0, 1, 2, 6, 7, 8}
    
    sequence_is_direct = asc_idx in direct_signs
    
    from api.core.ephemeris import SIGN_RULERS
    
    dashas = []
    current_jd = birth_jd
    
    for i in range(12):
        # Determine the current dasha sign
        if sequence_is_direct:
            sign_idx = (asc_idx + i) % 12
        else:
            sign_idx = (asc_idx - i) % 12
            
        sign_name = SIGNS[sign_idx]
        lord = SIGN_RULERS[sign_idx].lower()
        
        lord_pos = positions.get(lord)
        if lord_pos:
            lord_sign = lord_pos.get("sign")
            lord_idx = SIGNS.index(lord_sign)
        else:
            lord_idx = sign_idx # fallback
            
        # Duration calculation
        # If Dasha Sign is Direct, count forward to Lord
        # If Dasha Sign is Indirect, count backward to Lord
        # Wait, the rule for counting duration uses the direction of the DASHA SIGN, not the Lagna.
        dasha_sign_is_direct = sign_idx in direct_signs
        
        if lord_idx == sign_idx: # Lord in own sign
            duration = 12
        else:
            if dasha_sign_is_direct:
                count = (lord_idx - sign_idx) % 12 + 1
            else:
                count = (sign_idx - lord_idx) % 12 + 1
            duration = count - 1
            
        end_jd = current_jd + (duration * JD_PER_YEAR)
        
        dashas.append({
            "sign": sign_name,
            "lord": lord.title(),
            "duration_years": duration,
            "start_jd": current_jd,
            "end_jd": end_jd
        })
        
        current_jd = end_jd
        
    return dashas

def get_current_chara_dasha(dashas: List[Dict], query_jd: float) -> Dict:
    current = next((d for d in dashas if d["start_jd"] <= query_jd < d["end_jd"]), None)
    if not current:
        return {"error": "Query date outside of calculated Chara Dasha lifecycle (1st cycle)."}
    return {
        "current_dasha": current,
        "remaining_years": round((current["end_jd"] - query_jd) / JD_PER_YEAR, 4)
    }

# Kalachakra Dasha - simplified Savya (direct) and Apasavya (indirect) groups based on Moon Nakshatra Pada
KALACHAKRA_YEARS = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 21,
    "Leo": 5, "Virgo": 9, "Libra": 16, "Scorpio": 7,
    "Sagittarius": 10, "Capricorn": 4, "Aquarius": 4, "Pisces": 10
}

def get_kalachakra_dasha(birth_jd: float, moon_longitude: float) -> Dict[str, Any]:
    """
    Calculates Kalachakra Dasha (Wheel of Time).
    Determines Savya or Apasavya cycle based on Moon's Nakshatra, and standard sequence.
    """
    nak_name, nak_num, nak_pada, _, _ = longitude_to_nakshatra(moon_longitude)
    
    # 27 Nakshatras divided into two groups: 
    # Savya (Direct): Ashwini, Bharani, Krittika, etc. (odd triplets)
    # Apasavya (Indirect): Rohini, Mrigashira, Ardra, etc. (even triplets)
    group_idx = int((nak_num - 1) / 3)
    is_savya = (group_idx % 2 == 0)
    
    cycle = "Savya (Direct)" if is_savya else "Apasavya (Inverse)"
    
    # Simplified Dasha sequence sequence
    if is_savya:
        sequence = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        deha, jiva = "Aries", "Sagittarius" # Simplified proxy for Deha/Jiva
    else:
        sequence = ["Scorpio", "Libra", "Virgo", "Cancer", "Leo", "Gemini", "Taurus", "Aries", "Pisces", "Aquarius", "Capricorn", "Sagittarius"]
        deha, jiva = "Scorpio", "Pisces"
        
    dashas = []
    current_jd = birth_jd
    
    # We begin roughly at a specific sign based on pada, but for exactness in this simplified version, we'll start at the beginning of the sequence.
    start_idx = (nak_pada - 1) % len(sequence)
    
    for i in range(len(sequence)):
        idx = (start_idx + i) % len(sequence)
        sign = sequence[idx]
        duration = KALACHAKRA_YEARS[sign]
        end_jd = current_jd + (duration * JD_PER_YEAR)
        
        dashas.append({
            "dasha_sign": sign,
            "duration_years": duration,
            "start_jd": current_jd,
            "end_jd": end_jd
        })
        current_jd = end_jd
        
    return {
        "cycle_type": cycle,
        "deha_sign": deha,
        "jiva_sign": jiva,
        "timeline": dashas
    }
