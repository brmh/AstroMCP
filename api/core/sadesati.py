import swisseph as swe
from typing import Dict, List, Any
from api.core.ephemeris import SIGNS, get_julian_day, longitude_to_sign
from api.core.calculations import get_planetary_ingresses, get_planet_position
from datetime import timedelta

def _jd_to_date_str(jd: float) -> str:
    # Approximate Gregorian date for output
    try:
        y, m, d, hut = swe.revjul(jd)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except:
        return str(round(jd, 2))

def get_sade_sati_report(jd_birth: float, natal_moon_sidereal: float, current_jd: float, ayanamsa: str) -> Dict[str, Any]:
    """Calculate the full Sade Sati timeline and current status."""
    natal_moon_sign, moon_idx, _ = longitude_to_sign(natal_moon_sidereal)
    
    # Sade Sati signs: 12th, 1st, 2nd from moon
    ss_signs_idx = [(moon_idx - 1) % 12, moon_idx, (moon_idx + 1) % 12]
    
    # 4th (Dhaiya/Small Panoti), 8th (Ashtama Shani)
    dhaiya_idx = (moon_idx + 3) % 12 # 4th from moon
    ashtama_idx = (moon_idx + 7) % 12 # 8th from moon
    
    # Get Saturn's ingresses for a 100 year span from birth
    jd_end = jd_birth + 36525 # roughly 100 years
    ingresses = get_planetary_ingresses(swe.SATURN, jd_birth, jd_end, step=5.0)
    
    # Current Saturn state
    current_saturn = get_planet_position(current_jd, swe.SATURN, zodiac_type="SIDEREAL", ayanamsa=ayanamsa)
    curr_sat_idx = current_saturn["sign_index"]
    
    diff = (curr_sat_idx - moon_idx) % 12
    
    is_sade_sati = False
    current_phase = None
    if diff == 11:
        is_sade_sati = True
        current_phase = "Rising (1st phase)"
    elif diff == 0:
        is_sade_sati = True
        current_phase = "Peak (2nd phase)"
    elif diff == 1:
        is_sade_sati = True
        current_phase = "Setting (3rd phase)"
        
    is_dhaiya = diff == 3
    is_ashtama = diff == 7
    
    # Build periods
    all_periods = []
    phases = []
    current_sade_sati_cycle = []
    
    # Naive grouping of ingresses
    for i in range(len(ingresses) - 1):
        ing = ingresses[i]
        next_ing = ingresses[i+1]
        s_idx = ing["sign_index"]
        
        if s_idx in ss_signs_idx:
            phase_name = "Rising" if s_idx == ss_signs_idx[0] else ("Peak" if s_idx == ss_signs_idx[1] else "Setting")
            intensity = "Moderate" if phase_name != "Peak" else "High"
            period = {
                "phase": phase_name,
                "saturn_sign": ing["new_sign"],
                "start": _jd_to_date_str(ing["julian_day"]),
                "end": _jd_to_date_str(next_ing["julian_day"]),
                "intensity": intensity
            }
            all_periods.append(period)
            
            # If this period covers the current date
            if ing["julian_day"] <= current_jd <= next_ing["julian_day"]:
                # To build the 'phases' list for the CURRENT active Sade Sati block
                # We do a basic window search 2 items back and forward
                start_i = max(0, i - 2)
                end_i = min(len(ingresses) - 1, i + 3)
                for j in range(start_i, end_i):
                    j_idx = ingresses[j]["sign_index"]
                    if j_idx in ss_signs_idx and j < len(ingresses) - 1:
                        j_phase = "Rising" if j_idx == ss_signs_idx[0] else ("Peak" if j_idx == ss_signs_idx[1] else "Setting")
                        phases.append({
                            "phase": j_phase,
                            "saturn_sign": ingresses[j]["new_sign"],
                            "start": _jd_to_date_str(ingresses[j]["julian_day"]),
                            "end": _jd_to_date_str(ingresses[j+1]["julian_day"]),
                            "intensity": "High" if j_phase == "Peak" else "Moderate"
                        })
                
    # Remove duplicates in phases (caused by retrogrades sometimes)
    unique_phases = []
    seen = set()
    for p in phases:
        sig = f"{p['phase']}_{p['saturn_sign']}_{p['start']}"
        if sig not in seen:
            seen.add(sig)
            unique_phases.append(p)

    return {
        "natal_moon_sign": natal_moon_sign,
        "is_currently_in_sade_sati": is_sade_sati,
        "current_phase": current_phase,
        "current_saturn_sign": current_saturn["sign"],
        "phases": unique_phases,
        "all_periods": all_periods,
        "small_panoti": {
            "active": is_dhaiya,
            "details": f"Saturn is in {current_saturn['sign']}, the 4th from natal Moon." if is_dhaiya else "Not active"
        },
        "ashtama_shani": {
            "active": is_ashtama,
            "details": f"Saturn is in {current_saturn['sign']}, the 8th from natal Moon." if is_ashtama else "Not active"
        },
        "remedies": [
            "Worship Shani Dev every Saturday",
            "Chant Shani mantra: Om Sham Shanicharaya Namah",
            "Donate sesame seeds, black cloth, or iron on Saturdays",
            "Recite Hanuman Chalisa daily"
        ]
    }
