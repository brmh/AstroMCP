"""
Core module — custom exceptions and shared utilities.
"""


class AstrologyCalculationError(Exception):
    """Raised when an astrological calculation fails."""
    pass


class InvalidBirthDataError(ValueError):
    """Raised when birth data is invalid (e.g., impossible date)."""
    pass


class EphemerisFileNotFoundError(FileNotFoundError):
    """Raised when Swiss Ephemeris data files are missing."""
    pass


class UnsupportedHouseSystemError(ValueError):
    """Raised when an unsupported house system is requested."""
    pass


class InvalidTimezoneError(ValueError):
    """Raised when an invalid timezone string is provided."""
    pass


class GeocodingError(Exception):
    """Raised when geocoding a location fails."""
    pass
