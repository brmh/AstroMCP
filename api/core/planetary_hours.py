from typing import Dict, Any, List
from datetime import datetime
import swisseph as swe
from api.core.ephemeris import get_swe_lock
from api.core.calculations import get_solar_events

CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

WEEKDAY_RULERS = {
    6: "Sun",      # Sunday
    0: "Moon",     # Monday
    1: "Mars",     # Tuesday
    2: "Mercury",  # Wednesday
    3: "Jupiter",  # Thursday
    4: "Venus",    # Friday
    5: "Saturn",   # Saturday
}

def get_planetary_hours(jd: float, latitude: float, longitude: float, altitude: float = 0) -> List[Dict[str, Any]]:
    """
    Calculate the 24 planetary hours (12 day, 12 night) starting from the previous sunrise.
    Uses the get_solar_events helper for cross-version compatibility.
    """
    # Get sunrise/sunset for today's JD
    events_today = get_solar_events(jd, latitude, longitude, altitude)
    sunrise1 = events_today.get("sunrise")
    sunset = events_today.get("sunset")
    
    # If sunrise hasn't happened yet (or wasn't found), try the previous day
    if not sunrise1 or sunrise1 > jd:
        events_prev = get_solar_events(jd - 1.0, latitude, longitude, altitude)
        sunrise1 = events_prev.get("sunrise")
        sunset = events_prev.get("sunset")
        
    if not sunrise1 or not sunset:
        return [{"error": "Could not calculate sunrise/sunset for this location and date."}]
        
    # Next day's sunrise
    events_next = get_solar_events(jd + 1.0, latitude, longitude, altitude)
    sunrise2 = events_next.get("sunrise") or (sunrise1 + 1.0)
    
    # Get weekday of the first sunrise to determine the first planetary ruler
    year, month, day, _ = swe.revjul(sunrise1)
    dt = datetime(year, month, day)
    weekday = dt.weekday()  # Monday=0, Sunday=6
    current_ruler_idx = CHALDEAN_ORDER.index(WEEKDAY_RULERS[weekday])
    
    day_hour_length = (sunset - sunrise1) / 12.0
    night_hour_length = (sunrise2 - sunset) / 12.0
    
    hours = []
    
    # Daytime hours
    for i in range(12):
        start = sunrise1 + (i * day_hour_length)
        end = sunrise1 + ((i + 1) * day_hour_length)
        ruler = CHALDEAN_ORDER[current_ruler_idx]
        
        is_current = start <= jd < end
        
        hours.append({
            "hour_number": i + 1,
            "period": "Day",
            "ruler": ruler,
            "start_jd": round(start, 6),
            "end_jd": round(end, 6),
            "is_current": is_current
        })
        current_ruler_idx = (current_ruler_idx + 1) % 7
        
    # Nighttime hours
    for i in range(12):
        start = sunset + (i * night_hour_length)
        end = sunset + ((i + 1) * night_hour_length)
        ruler = CHALDEAN_ORDER[current_ruler_idx]
        
        is_current = start <= jd < end
        
        hours.append({
            "hour_number": i + 13,
            "period": "Night",
            "ruler": ruler,
            "start_jd": round(start, 6),
            "end_jd": round(end, 6),
            "is_current": is_current
        })
        current_ruler_idx = (current_ruler_idx + 1) % 7
        
    return hours


