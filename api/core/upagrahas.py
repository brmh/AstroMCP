from typing import Dict, Any
from api.core.ephemeris import get_julian_day, longitude_to_sign
from api.core.calculations import get_solar_events, get_planet_position
import swisseph as swe
from datetime import datetime, timedelta

def _calc_ascendant_for_time(jd: float, lat: float, lon: float, ayanamsa: str) -> float:
    from api.core.calculations import get_houses
    houses = get_houses(jd, lat, lon, "WHOLE_SIGN", "SIDEREAL", ayanamsa)
    return houses.get("ascendant", 0)

def get_upagrahas(jd_birth: float, lat: float, lon: float, sun_sidereal: float, ayanamsa: str) -> Dict[str, Any]:
    """Calculate the 7 non-luminous planets (Upagrahas and Aprakash Grahas)."""
    
    # 1. Mathematical derivations from Sun
    dhooma = (sun_sidereal + 133.333333) % 360
    vyatipata = (360 - dhooma) % 360
    parivesha = (vyatipata + 180) % 360
    indrachapa = (360 - parivesha) % 360
    upaketu = (indrachapa + 16.666666) % 360
    
    def format_planet(name, pos):
        sign, idx, deg = longitude_to_sign(pos)
        return {
            "longitude": round(pos, 4),
            "sign": sign,
            "sign_index": idx,
            "degree_in_sign": round(deg, 4)
        }
        
    results = {
        "dhooma": format_planet("Dhooma", dhooma),
        "vyatipata": format_planet("Vyatipata", vyatipata),
        "parivesha": format_planet("Parivesha", parivesha),
        "indrachapa": format_planet("Indrachapa", indrachapa),
        "upaketu": format_planet("Upaketu", upaketu),
    }

    # 2. Gulika and Mandi based on daytime/nighttime divisions
    events = get_solar_events(jd_birth, lat, lon)
    sunrise = events.get("sunrise")
    sunset = events.get("sunset")
    
    if not sunrise or not sunset:
        # Fallback if polar regions
        return results

    # Get Swiss Ephemeris day of week (0=Mon, 1=Tue... 6=Sun)
    # Swe uses Monday as 0 in revjul, but let's just get python datetime
    y, m, d, h = swe.revjul(jd_birth)
    h_int = int(h)
    min_int = int((h - h_int) * 60)
    sec_int = int((((h - h_int) * 60) - min_int) * 60)
    dt = datetime(y, m, d, h_int, min_int, sec_int)
    # 0=Mon, 6=Sun
    weekday = dt.weekday()
    
    # Map to Sunday=1, Monday=2, ... Saturday=7
    vedic_weekday = (weekday + 1) % 7 + 1
    if vedic_weekday == 8: vedic_weekday = 1

    is_day = sunrise <= jd_birth <= sunset
    
    # Gulika day parts (1-based index) for Sunday to Saturday
    gulika_day_parts = {1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1}
    gulika_night_parts = {1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5, 7: 4}
    
    # Mandi day parts (1-based index)
    mandi_day_parts = {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 7}
    mandi_night_parts = {1: 2, 2: 1, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3}
    
    if is_day:
        part_len = (sunset - sunrise) / 8.0
        g_part = gulika_day_parts[vedic_weekday]
        m_part = mandi_day_parts[vedic_weekday]
        
        g_time = sunrise + (g_part - 1) * part_len
        m_time = sunrise + (m_part - 1) * part_len
    else:
        # Need next sunrise if after sunset
        if jd_birth > sunset:
            next_events = get_solar_events(jd_birth + 1.0, lat, lon)
            next_sunrise = next_events.get("sunrise", jd_birth + 0.5)
            part_len = (next_sunrise - sunset) / 8.0
            g_part = gulika_night_parts[vedic_weekday]
            m_part = mandi_night_parts[vedic_weekday]
            
            g_time = sunset + (g_part - 1) * part_len
            m_time = sunset + (m_part - 1) * part_len
        else:
            # Before sunrise, so use previous sunset
            prev_events = get_solar_events(jd_birth - 1.0, lat, lon)
            prev_sunset = prev_events.get("sunset", jd_birth - 0.5)
            part_len = (sunrise - prev_sunset) / 8.0
            # Weekday is the previous day's weekday technically!
            prev_weekday = vedic_weekday - 1 if vedic_weekday > 1 else 7
            g_part = gulika_night_parts[prev_weekday]
            m_part = mandi_night_parts[prev_weekday]
            
            g_time = prev_sunset + (g_part - 1) * part_len
            m_time = prev_sunset + (m_part - 1) * part_len

    # Ascendant at g_time and m_time is the longitude of Gulika and Mandi
    gulika_lon = _calc_ascendant_for_time(g_time, lat, lon, ayanamsa)
    mandi_lon = _calc_ascendant_for_time(m_time, lat, lon, ayanamsa)
    
    results["gulika"] = format_planet("Gulika", gulika_lon)
    results["mandi"] = format_planet("Mandi", mandi_lon)
    
    return results
