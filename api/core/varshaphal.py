from typing import Dict, Any
import swisseph as swe
from api.core.ephemeris import SIGNS, get_swe_lock
from api.core.calculations import get_all_planet_positions, get_houses

def get_solar_return_jd(natal_sun_sidereal: float, target_year: int, ayanamsa: str) -> float:
    """
    Find the exact Julian Date when the transiting Sun returns to its natal pos.
    This works for sidereal longitude (meaning we must check when transiting
    sidereal Sun equals natal sidereal Sun).
    To simplify: transiting tropical Sun returns to (natal sid. Sun + transiting ayanamsa).
    """
    import math
    
    # Rough JD of Jan 1st of the target year
    jd_iter = swe.julday(target_year, 1, 1, 0.0)
    
    from api.core.ephemeris import set_sidereal_mode, get_ayanamsa_value
    
    # A year is 365.25 days. The sun moves approx 1 degree/day.
    # We will do a binary search style or fine-step search.
    
    # First, scan the year by days to get within 1 day bounds
    closest_jd = jd_iter
    min_diff = 360.0
    
    with get_swe_lock():
        for i in range(366):
            check_jd = jd_iter + i
            # Get sidereal sun position at this JD
            if ayanamsa:
                set_sidereal_mode(ayanamsa)
            flag = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
            result, _ = swe.calc_ut(check_jd, swe.SUN, flag)
            lon = result[0]
            
            diff = min(abs(lon - natal_sun_sidereal), 360 - abs(lon - natal_sun_sidereal))
            if diff < min_diff:
                min_diff = diff
                closest_jd = check_jd
                
    # Now refine for exact hour/minute
    refine_jd = closest_jd - 1.0
    min_diff = 360.0
    exact_jd = closest_jd
    
    with get_swe_lock():
        # Step every 10 minutes (approx 0.007 days)
        step = 10 / (24 * 60)
        while refine_jd <= closest_jd + 1.0:
            if ayanamsa:
                set_sidereal_mode(ayanamsa)
            result, _ = swe.calc_ut(refine_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL)
            lon = result[0]
            diff = min(abs(lon - natal_sun_sidereal), 360 - abs(lon - natal_sun_sidereal))
            if diff < min_diff:
                min_diff = diff
                exact_jd = refine_jd
            refine_jd += step
            
    return exact_jd

def get_varshaphal_chart(natal_jd: float, natal_sun_sidereal: float, 
                         natal_ascendant_sign: str, target_year: int, 
                         lat: float, lon: float, ayanamsa: str = "LAHIRI") -> Dict[str, Any]:
    """Calculate the Tajika Varshaphal (Annual) chart."""
    
    try:
        y, m, d, h = swe.revjul(natal_jd)
        birth_year = y
    except:
        birth_year = target_year - 30 # fallback if jd invalid
        
    year_of_life = target_year - birth_year
    
    # Find exact solar return
    return_jd = get_solar_return_jd(natal_sun_sidereal, target_year, ayanamsa)
    
    year, month, day, _ = swe.revjul(return_jd)
    return_date_str = f"{year:04d}-{month:02d}-{day:02d}"
    
    # Build chart for the return JD
    positions = get_all_planet_positions(return_jd, zodiac_type="SIDEREAL", ayanamsa=ayanamsa)
    houses = get_houses(return_jd, lat, lon, "WHOLE_SIGN", "SIDEREAL", ayanamsa)
    
    from api.core.calculations import assign_houses_to_planets
    positions = assign_houses_to_planets(positions, houses)
    
    # Calculate Muntha
    try:
        asc_idx = SIGNS.index(natal_ascendant_sign)
        muntha_idx = (asc_idx + year_of_life) % 12
        muntha_sign = SIGNS[muntha_idx]
    except:
        muntha_sign = "Unknown"
        
    # Find Muntha in Varshaphal houses
    muntha_house = 1
    varsha_asc_sign = houses.get("cusps", {}).get("house_1", {}).get("sign")
    if varsha_asc_sign in SIGNS and muntha_sign in SIGNS:
        v_asc_idx = SIGNS.index(varsha_asc_sign)
        m_idx = SIGNS.index(muntha_sign)
        muntha_house = (m_idx - v_asc_idx) % 12 + 1
        
    return {
        "chart_type": "varshaphal",
        "target_year": target_year,
        "year_of_life": year_of_life + 1,
        "solar_return_jd": return_jd,
        "solar_return_date": return_date_str,
        "muntha": {
            "sign": muntha_sign,
            "house": muntha_house
        },
        "houses": houses,
        "planets": positions
    }
