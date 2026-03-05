"""
API Configuration Module
Loads settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Swiss Ephemeris
    EPHE_PATH: str = Field(default="./ephe", description="Path to Swiss Ephemeris data files")
    EPHE_MODE: str = Field(default="swiss", description="Ephemeris mode: swiss, jpl, moshier")

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = False
    API_TITLE: str = "AstroConsultant API"
    API_VERSION: str = "1.0.0"

    # Default Ayanamsa
    DEFAULT_AYANAMSA: str = "LAHIRI"

    # Default House System
    DEFAULT_HOUSE_SYSTEM: str = "PLACIDUS"

    # Caching
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_SIZE: int = 1000

    # Geocoding
    GEOCODING_TIMEOUT: int = 5

    # MCP Server
    MCP_SERVER_NAME: str = "AstroConsultant"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_FASTAPI_BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
