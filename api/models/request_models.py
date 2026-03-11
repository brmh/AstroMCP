"""
Pydantic Request Models
Input models for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Union
from enum import Enum
from datetime import date, datetime


class HouseSystemEnum(str, Enum):
    PLACIDUS = "PLACIDUS"
    KOCH = "KOCH"
    WHOLE_SIGN = "WHOLE_SIGN"
    EQUAL = "EQUAL"
    CAMPANUS = "CAMPANUS"
    REGIOMONTANUS = "REGIOMONTANUS"
    PORPHYRY = "PORPHYRY"
    ALCABITIUS = "ALCABITIUS"
    MORINUS = "MORINUS"
    MERIDIAN = "MERIDIAN"
    AZIMUTHAL = "AZIMUTHAL"
    POLICH_PAGE = "POLICH_PAGE"


class ZodiacTypeEnum(str, Enum):
    TROPICAL = "TROPICAL"
    SIDEREAL = "SIDEREAL"


class AyanamsaEnum(str, Enum):
    LAHIRI = "LAHIRI"
    RAMAN = "RAMAN"
    KRISHNAMURTI = "KRISHNAMURTI"
    FAGAN_BRADLEY = "FAGAN_BRADLEY"
    TRUE_CHITRAPAKSHA = "TRUE_CHITRAPAKSHA"
    YUKTESHWAR = "YUKTESHWAR"
    JN_BHASIN = "JN_BHASIN"
    SASSANIAN = "SASSANIAN"


class OrbSettings(BaseModel):
    conjunction: float = 8.0
    opposition: float = 8.0
    trine: float = 8.0
    square: float = 7.0
    sextile: float = 6.0
    semi_sextile: float = 2.0
    quincunx: float = 3.0
    semi_square: float = 2.0
    sesquiquadrate: float = 2.0
    quintile: float = 2.0
    biquintile: float = 2.0


class BirthData(BaseModel):
    name: str = "Unknown"
    birth_year: int = Field(..., ge=-5400, le=5400)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(12, ge=0, le=23)
    birth_minute: int = Field(0, ge=0, le=59)
    birth_second: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "UTC"
    altitude: float = 0.0


class ChartOptions(BaseModel):
    house_system: HouseSystemEnum = HouseSystemEnum.PLACIDUS
    zodiac_type: ZodiacTypeEnum = ZodiacTypeEnum.TROPICAL
    ayanamsa: AyanamsaEnum = AyanamsaEnum.LAHIRI
    include_chiron: bool = True
    include_lilith: bool = True
    include_asteroids: bool = False
    include_fixed_stars: bool = False
    orb_settings: OrbSettings = OrbSettings()


class NatalChartRequest(BaseModel):
    birth_data: BirthData
    options: ChartOptions = ChartOptions()


class TransitRequest(BaseModel):
    natal: Union[BirthData, Dict]
    transit_date: Optional[datetime] = None
    transit_latitude: Optional[float] = None
    transit_longitude: Optional[float] = None
    options: ChartOptions = ChartOptions()


class DateRangeRequest(BaseModel):
    natal: BirthData
    start_date: date
    end_date: date
    options: ChartOptions = ChartOptions()


class SynastryRequest(BaseModel):
    person1: BirthData
    person2: BirthData
    options: ChartOptions = ChartOptions()


class PanchangRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 6
    minute: int = 0
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "UTC"
    ayanamsa: AyanamsaEnum = AyanamsaEnum.LAHIRI


class MuhurtaRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "UTC"
    purpose: str = "marriage"


class MuhurtaSearchRequest(BaseModel):
    start_date: date
    end_date: date
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "UTC"
    purpose: str = "marriage"
    min_score: float = 65


class CompatibilityRequest(BaseModel):
    person1: BirthData
    person2: BirthData
    ayanamsa: AyanamsaEnum = AyanamsaEnum.LAHIRI


class GeocodeRequest(BaseModel):
    city: str
    country: Optional[str] = None


class JulianDayRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    timezone: str = "UTC"


class PlanetTransitRequest(BaseModel):
    natal: BirthData
    planet: str
    start_date: date
    end_date: date
    options: ChartOptions = ChartOptions()


class ProgressionRequest(BaseModel):
    birth_data: BirthData
    target_year: Optional[int] = None
    target_date: Optional[date] = None
    options: ChartOptions = ChartOptions()


class MonthlyPanchangRequest(BaseModel):
    year: int
    month: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "UTC"
    ayanamsa: AyanamsaEnum = AyanamsaEnum.LAHIRI
