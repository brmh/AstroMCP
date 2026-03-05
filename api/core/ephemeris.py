"""
Swiss Ephemeris Wrapper & Initialization
Centralizes all ephemeris access, Julian Day conversion, ayanamsa handling,
house system mapping, and thread-safe sidereal mode switching.
"""

import threading
import logging
from datetime import datetime
from typing import Optional, Tuple

import swisseph as swe
import pytz

from api.config import settings

logger = logging.getLogger(__name__)

# ── Thread lock for Swiss Ephemeris global state ──────────────────────────
_swe_lock = threading.Lock()

# ── Planet ID Mappings ────────────────────────────────────────────────────
PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
    "mean_node": swe.MEAN_NODE,
    "true_node": swe.TRUE_NODE,
    "mean_apog": swe.MEAN_APOG,
    "oscu_apog": swe.OSCU_APOG,
    "earth": swe.EARTH,
    "chiron": swe.CHIRON,
    "pholus": swe.PHOLUS,
    "ceres": swe.CERES,
    "pallas": swe.PALLAS,
    "juno": swe.JUNO,
    "vesta": swe.VESTA,
}

# Asteroids via AST_OFFSET (only if the user has asteroid ephemeris files)
ASTEROID_PLANETS = {
    "eris": swe.AST_OFFSET + 136199,
    "sedna": swe.AST_OFFSET + 90377,
}

# Vedic planets (Navagrahas)
VEDIC_PLANETS = {
    "surya": swe.SUN,
    "chandra": swe.MOON,
    "mangala": swe.MARS,
    "budha": swe.MERCURY,
    "guru": swe.JUPITER,
    "shukra": swe.VENUS,
    "shani": swe.SATURN,
    "rahu": swe.MEAN_NODE,
    # Ketu = Rahu + 180° (always opposite)
}

# Standard planets used for natal charts
STANDARD_PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
    "mean_node": swe.MEAN_NODE,
    "true_node": swe.TRUE_NODE,
}

# ── Zodiac Signs ──────────────────────────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGNS_SANSKRIT = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

# ── Nakshatras (27 Vedic Lunar Mansions) ──────────────────────────────────
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
    "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
    "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury"
]

NAKSHATRA_DEITIES = [
    "Ashwini Kumaras", "Yama", "Agni", "Brahma", "Soma",
    "Rudra", "Aditi", "Brihaspati", "Sarpa", "Pitris",
    "Bhaga", "Aryaman", "Savitar", "Tvashtar", "Vayu",
    "Indragni", "Mitra", "Indra", "Nirrti", "Apas",
    "Vishvadevas", "Vishnu", "Vasus", "Varuna", "Aja Ekapada",
    "Ahir Budhnya", "Pushan"
]

NAKSHATRA_GANAS = [
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva",
    "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva", "Rakshasa", "Deva",
    "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya",
    "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya",
    "Manushya", "Deva"
]

# ── Ayanamsa Mapping ─────────────────────────────────────────────────────
AYANAMSA_MODES = {
    "LAHIRI": swe.SIDM_LAHIRI,
    "RAMAN": swe.SIDM_RAMAN,
    "KRISHNAMURTI": swe.SIDM_KRISHNAMURTI,
    "FAGAN_BRADLEY": swe.SIDM_FAGAN_BRADLEY,
    "TRUE_CHITRAPAKSHA": swe.SIDM_TRUE_CITRA,
    "YUKTESHWAR": swe.SIDM_YUKTESHWAR,
    "JN_BHASIN": swe.SIDM_JN_BHASIN,
    "SASSANIAN": swe.SIDM_SASSANIAN,
}

# ── House System Mapping ─────────────────────────────────────────────────
HOUSE_SYSTEMS = {
    "PLACIDUS": b'P',
    "KOCH": b'K',
    "WHOLE_SIGN": b'W',
    "EQUAL": b'E',
    "CAMPANUS": b'C',
    "REGIOMONTANUS": b'R',
    "PORPHYRY": b'O',
    "SRIPATI": b'O',
    "ALCABITIUS": b'B',
    "MORINUS": b'M',
    "MERIDIAN": b'X',
    "AZIMUTHAL": b'H',
    "POLICH_PAGE": b'T',
}

# ── Element / Modality / Ruler Data ───────────────────────────────────────
SIGN_ELEMENTS = [
    "Fire", "Earth", "Air", "Water", "Fire", "Earth",
    "Air", "Water", "Fire", "Earth", "Air", "Water"
]

SIGN_MODALITIES = [
    "Cardinal", "Fixed", "Mutable", "Cardinal", "Fixed", "Mutable",
    "Cardinal", "Fixed", "Mutable", "Cardinal", "Fixed", "Mutable"
]

SIGN_RULERS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

# ── Exaltation / Debilitation ─────────────────────────────────────────────
EXALTATION = {
    "sun": ("Aries", 10.0),
    "moon": ("Taurus", 3.0),
    "mercury": ("Virgo", 15.0),
    "venus": ("Pisces", 27.0),
    "mars": ("Capricorn", 28.0),
    "jupiter": ("Cancer", 5.0),
    "saturn": ("Libra", 20.0),
    "rahu": ("Taurus", None),
    "ketu": ("Scorpio", None),
}

DEBILITATION = {
    "sun": ("Libra", 10.0),
    "moon": ("Scorpio", 3.0),
    "mercury": ("Pisces", 15.0),
    "venus": ("Virgo", 27.0),
    "mars": ("Cancer", 28.0),
    "jupiter": ("Capricorn", 5.0),
    "saturn": ("Aries", 20.0),
    "rahu": ("Scorpio", None),
    "ketu": ("Taurus", None),
}

# Moolatrikona signs and degree ranges
MOOLATRIKONA = {
    "sun": ("Leo", 0, 20),
    "moon": ("Taurus", 4, 20),
    "mars": ("Aries", 0, 12),
    "mercury": ("Virgo", 16, 20),
    "jupiter": ("Sagittarius", 0, 10),
    "venus": ("Libra", 0, 15),
    "saturn": ("Aquarius", 0, 20),
}

# ── Planetary Friendship (Naisargika Maitri) ─────────────────────────────
PLANETARY_FRIENDSHIP = {
    "sun": {"friends": ["moon", "mars", "jupiter"], "enemies": ["venus", "saturn"], "neutral": ["mercury"]},
    "moon": {"friends": ["sun", "mercury"], "enemies": [], "neutral": ["mars", "jupiter", "venus", "saturn"]},
    "mars": {"friends": ["sun", "moon", "jupiter"], "enemies": ["mercury"], "neutral": ["venus", "saturn"]},
    "mercury": {"friends": ["sun", "venus"], "enemies": ["moon"], "neutral": ["mars", "jupiter", "saturn"]},
    "jupiter": {"friends": ["sun", "moon", "mars"], "enemies": ["mercury", "venus"], "neutral": ["saturn"]},
    "venus": {"friends": ["mercury", "saturn"], "enemies": ["sun", "moon"], "neutral": ["mars", "jupiter"]},
    "saturn": {"friends": ["mercury", "venus"], "enemies": ["sun", "moon", "mars"], "neutral": ["jupiter"]},
}

# ── Combustion Degrees ────────────────────────────────────────────────────
COMBUSTION_DEGREES = {
    "moon": 12.0,
    "mars": 17.0,
    "mercury_direct": 14.0,
    "mercury_retrograde": 12.0,
    "jupiter": 11.0,
    "venus_direct": 10.0,
    "venus_retrograde": 8.0,
    "saturn": 15.0,
}

# ── Vimshottari Dasha Order & Periods ────────────────────────────────────
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Total = 120 years

# Nakshatra-to-Dasha-Lord mapping (each lord rules 3 nakshatras)
NAKSHATRA_DASHA_LORD = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]


# ══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

def init_ephemeris():
    """Initialize the Swiss Ephemeris with the configured path."""
    ephe_path = settings.EPHE_PATH
    swe.set_ephe_path(ephe_path)
    logger.info(f"Swiss Ephemeris initialized. Path: {ephe_path}, Mode: {settings.EPHE_MODE}")


def close_ephemeris():
    """Close the Swiss Ephemeris and release resources."""
    swe.close()
    logger.info("Swiss Ephemeris closed.")


def get_julian_day(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    timezone_str: str = "UTC"
) -> float:
    """
    Convert a date/time to Julian Day Number (UT).
    Handles timezone conversion to UTC first.
    """
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        from api.core import InvalidTimezoneError
        raise InvalidTimezoneError(f"Unknown timezone: {timezone_str}")

    local_dt = datetime(year, month, day, hour, minute, second)
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)

    decimal_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)
    return jd


def get_ayanamsa_value(julian_day: float, ayanamsa_mode: str = None) -> float:
    """
    Get the Ayanamsa offset in degrees for the given Julian Day.
    Thread-safe.
    """
    mode = ayanamsa_mode or settings.DEFAULT_AYANAMSA
    sid_mode = AYANAMSA_MODES.get(mode.upper(), swe.SIDM_LAHIRI)
    with _swe_lock:
        swe.set_sid_mode(sid_mode)
        ayanamsa = swe.get_ayanamsa_ut(julian_day)
    return ayanamsa


def set_sidereal_mode(ayanamsa_mode: str = None):
    """Set the sidereal mode for Vedic calculations. Must be called within _swe_lock."""
    mode = ayanamsa_mode or settings.DEFAULT_AYANAMSA
    sid_mode = AYANAMSA_MODES.get(mode.upper(), swe.SIDM_LAHIRI)
    swe.set_sid_mode(sid_mode)


def get_house_system_flag(system_name: str = None) -> bytes:
    """Convert a house system name to the single-character flag used by swe.houses()."""
    name = (system_name or settings.DEFAULT_HOUSE_SYSTEM).upper()
    flag = HOUSE_SYSTEMS.get(name)
    if flag is None:
        from api.core import UnsupportedHouseSystemError
        raise UnsupportedHouseSystemError(f"Unsupported house system: {name}")
    return flag


def get_swe_flags(zodiac_type: str = "TROPICAL", ayanamsa: str = None) -> int:
    """Get Swiss Ephemeris calculation flags based on zodiac type."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if zodiac_type.upper() == "SIDEREAL":
        flags |= swe.FLG_SIDEREAL
    return flags


def longitude_to_sign(longitude: float) -> Tuple[str, int, float]:
    """Convert ecliptic longitude (0-360) to sign name, index (0-11), and degree in sign."""
    longitude = longitude % 360
    sign_index = int(longitude / 30)
    degree_in_sign = longitude % 30
    sign_name = SIGNS[sign_index]
    return sign_name, sign_index, degree_in_sign


def longitude_to_nakshatra(sidereal_longitude: float) -> Tuple[str, int, int, str, str]:
    """
    Convert sidereal longitude to nakshatra info.
    Returns: (name, number 1-27, pada 1-4, lord, deity)
    """
    sidereal_longitude = sidereal_longitude % 360
    nak_span = 360.0 / 27.0  # 13.333...
    nak_index = int(sidereal_longitude / nak_span)
    if nak_index >= 27:
        nak_index = 26
    pada = int((sidereal_longitude % nak_span) / (nak_span / 4.0)) + 1
    if pada > 4:
        pada = 4
    return (
        NAKSHATRAS[nak_index],
        nak_index + 1,
        pada,
        NAKSHATRA_LORDS[nak_index],
        NAKSHATRA_DEITIES[nak_index]
    )


def get_navamsa_sign(longitude: float) -> str:
    """Calculate the Navamsa (D9) sign for a given sidereal longitude."""
    longitude = longitude % 360
    navamsa_index = int((longitude % 360) / (360 / 108)) % 12
    return SIGNS[navamsa_index]


def angular_difference(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular distance between two longitudes."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def get_swe_lock():
    """Return the threading lock for external callers that need thread-safe swe access."""
    return _swe_lock
