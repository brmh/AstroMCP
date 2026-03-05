"""
Shared FastAPI Dependencies
Common utilities used across routers.
"""

import logging
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from api.config import settings
from api.core import InvalidBirthDataError, InvalidTimezoneError, GeocodingError
from api.core.ephemeris import get_julian_day
from api.models.request_models import BirthData

logger = logging.getLogger(__name__)
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="astro_consultant", timeout=settings.GEOCODING_TIMEOUT)


def birth_data_to_jd(birth: BirthData) -> float:
    """Convert BirthData to Julian Day."""
    try:
        return get_julian_day(
            birth.birth_year, birth.birth_month, birth.birth_day,
            birth.birth_hour, birth.birth_minute, birth.birth_second,
            birth.timezone,
        )
    except Exception as e:
        raise InvalidBirthDataError(f"Invalid birth data: {e}")


def geocode_city(city: str, country: str = None) -> dict:
    """Geocode a city name to lat/lon/timezone."""
    try:
        query = f"{city}, {country}" if country else city
        location = geolocator.geocode(query)
        if not location:
            raise GeocodingError(f"Could not geocode: {query}")

        tz_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)
        return {
            "city": city,
            "latitude": round(location.latitude, 4),
            "longitude": round(location.longitude, 4),
            "timezone": tz_str or "UTC",
            "country": country,
            "display_name": location.address,
        }
    except GeocoderTimedOut:
        raise GeocodingError("Geocoding timed out")
    except Exception as e:
        raise GeocodingError(f"Geocoding error: {e}")


def get_current_jd() -> float:
    """Get the current Julian Day."""
    now = datetime.now(pytz.utc)
    return get_julian_day(now.year, now.month, now.day, now.hour, now.minute, now.second, "UTC")
