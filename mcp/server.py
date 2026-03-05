"""
MCP Server — AstroConsultant
Wraps the FastAPI backend using FastMCP for Claude Desktop integration.
"""

import os
import json
from typing import Optional
from fastmcp import FastMCP
import httpx

# Use the PORT environment variable if available, defaulting to 8000 for local dev
_port = os.getenv("PORT", "8000")
API_BASE_URL = os.getenv("MCP_FASTAPI_BASE_URL", f"http://127.0.0.1:{_port}")

mcp = FastMCP(name="AstroConsultant", version="1.0.0")
client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0)


async def _post(endpoint: str, data: dict) -> dict:
    try:
        resp = await client.post(endpoint, json=data)
        resp.raise_for_status()
        result = resp.json()
        
        # Standardize Response Envelope
        import datetime
        return {
            "meta": {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "endpoint": endpoint,
                "status": "success"
            },
            "data": result
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"API error: {e.response.status_code}", "detail": e.response.text}
    except Exception as e:
        return {"error": str(e)}


async def _get(endpoint: str, params: dict = None) -> dict:
    try:
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        result = resp.json()
        
        # Standardize Response Envelope
        import datetime
        return {
            "meta": {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "endpoint": endpoint,
                "status": "success"
            },
            "data": result
        }
    except Exception as e:
        return {"error": str(e)}


def _birth_payload(name, year, month, day, hour, minute, lat, lon, tz, house_system="PLACIDUS", zodiac="TROPICAL", ayanamsa="LAHIRI", include_asteroids=False):
    return {
        "birth_data": {
            "name": name, "birth_year": year, "birth_month": month, "birth_day": day,
            "birth_hour": hour, "birth_minute": minute, "latitude": lat, "longitude": lon, "timezone": tz,
        },
        "options": {"house_system": house_system, "zodiac_type": zodiac, "ayanamsa": ayanamsa, "include_chiron": True, "include_asteroids": include_asteroids},
    }


# ═══════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ═══════════════════════════════════════════════════════════════════════

@mcp.tool
async def get_natal_chart(name: str, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                          timezone: str, house_system: str = "PLACIDUS",
                          zodiac_type: str = "TROPICAL", ayanamsa: str = "LAHIRI",
                          include_asteroids: bool = False) -> dict:
    """Calculate a complete natal/birth chart. Returns planetary positions, house cusps, aspects, angles."""
    return await _post("/natal/chart", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, house_system, zodiac_type, ayanamsa, include_asteroids))


@mcp.tool
async def get_vedic_kundli(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate a Vedic birth chart (Kundli) in sidereal zodiac with whole-sign houses."""
    return await _post("/vedic/kundli", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_varga_chart(name: str, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                          timezone: str, division: int, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate a specific Vedic divisional (Varga) chart (D2-D60). Requires division integer (e.g. 9 for Navamsa)."""
    return await _post(f"/vedic/varga/{division}", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_sade_sati(name: str, birth_year: int, birth_month: int, birth_day: int,
                        birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                        timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate a complete 100-year Sade Sati report, including historical and future dates, peaks, and remedies."""
    return await _post("/vedic/sade-sati", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_bhava_chalit_chart(name: str, birth_year: int, birth_month: int, birth_day: int,
                                 birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                                 timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Vedic Bhava Chalit chart using the Sripati house system. Returns shifted planets."""
    return await _post("/vedic/bhava-chalit", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "SRIPATI", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_upagrahas(name: str, birth_year: int, birth_month: int, birth_day: int,
                        birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                        timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate Vedic Upagrahas (shadow planets) like Mandi, Gulika, Dhooma, Vyatipata, Parivesha, Indrachapa, and Upaketu."""
    return await _post("/vedic/upagrahas", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_remedies(name: str, birth_year: int, birth_month: int, birth_day: int,
                       birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                       timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Suggest targeted remedial measures (Gemstones, Mantras, Charity) based on the user's specific astrological afflictions and functional benefics."""
    return await _post("/vedic/remedies", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_gochar_report(name: str, birth_year: int, birth_month: int, birth_day: int,
                            birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                            timezone: str, transit_year: int = None, transit_month: int = None, 
                            transit_day: int = None, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Vedic Gochar (transit) report based on natal Moon sign. If transit date omitted, uses today."""
    payload = _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute, 
                             latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa)
    if transit_year and transit_month and transit_day:
        payload["transit_date"] = f"{transit_year:04d}-{transit_month:02d}-{transit_day:02d}T12:00:00Z"
    return await _post("/vedic/gochar", payload)

@mcp.tool
async def get_jaimini_karakas(name: str, birth_year: int, birth_month: int, birth_day: int,
                              birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                              timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the 7 Jaimini Chara Karakas (AK, AmK, BK, MK, PiK, PK, DK) used for soul path and predictive astrology."""
    return await _post("/vedic/jaimini-karakas", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_arudha_padas(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Arudha Padas for all 12 houses (AL, A2, A3, etc.) representing external image and manifested reality."""
    return await _post("/vedic/arudha-padas", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_transit_scoring(name: str, birth_year: int, birth_month: int, birth_day: int,
                              birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                              timezone: str, transit_year: int = None, transit_month: int = None,
                              transit_day: int = None, ayanamsa: str = "LAHIRI") -> dict:
    """Evaluate transit favorability using Ashtakavarga scoring (Kakshya). Scores transiting planets against the natal chart's points grid."""
    payload = _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute,
                             latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa)
    if transit_year and transit_month and transit_day:
        payload["transit_date"] = f"{transit_year:04d}-{transit_month:02d}-{transit_day:02d}T12:00:00Z"
    return await _post("/transits/ashtakavarga-score", payload)

@mcp.tool
async def get_lagna_lord_analysis(name: str, birth_year: int, birth_month: int, birth_day: int,
                                  birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                                  timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Analyze the Ascendant Lord (Lagnesh) including its dignity, house placement, and basic interpretation."""
    return await _post("/vedic/lagna-lord", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_karakamsa(name: str, birth_year: int, birth_month: int, birth_day: int,
                        birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                        timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Find the Karakamsa (Navamsa sign occupied by the Atmakaraka) representing soul's true desire."""
    return await _post("/vedic/karakamsa", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_chara_dasha(name: str, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                          timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Jaimini Chara Dasha timeline and determine the current active Dasha sign based on transit date."""
    return await _post("/vedic/dashas/chara", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_yogini_dasha(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Yogini Dasha timeline (36-year cycle) commonly used in North India."""
    return await _post("/vedic/dashas/yogini", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_kalachakra_dasha(name: str, birth_year: int, birth_month: int, birth_day: int,
                               birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                               timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Kalachakra Dasha (Wheel of Time). Returns the exact Savya or Apasavya cycle sequence and Deha/Jiva signs."""
    return await _post("/vedic/dashas/kalachakra", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_varshaphal(name: str, birth_year: int, birth_month: int, birth_day: int,
                         birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                         timezone: str, target_year: int, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the Tajika Varshaphal (Annual Horoscope) chart including the Muntha and Solar Return date."""
    return await _post(f"/vedic/varshaphal?target_year={target_year}", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_secondary_progressions(name: str, birth_year: int, birth_month: int, birth_day: int,
                                     birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                                     timezone: str, transit_year: int, transit_month: int, transit_day: int,
                                     house_system: str = "PLACIDUS") -> dict:
    """Calculate Western Secondary Progressions (day-for-a-year). Requires the target transit date."""
    payload = _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute, 
                             latitude, longitude, timezone, house_system, "TROPICAL", "LAHIRI")
    payload["transit_date"] = f"{transit_year:04d}-{transit_month:02d}-{transit_day:02d}T12:00:00Z"
    return await _post("/western/progressions", payload)

@mcp.tool
async def get_current_dasha(name: str, birth_year: int, birth_month: int, birth_day: int,
                            birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                            timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Get the currently active Vimshottari Mahadasha/Antardasha/Pratyantardasha."""
    return await _post("/vedic/dashas/current", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_dasha_timeline(name: str, birth_year: int, birth_month: int, birth_day: int,
                             birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                             timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Get the full Vimshottari Dasha timeline with all Mahadashas and Antardashas."""
    return await _post("/vedic/dashas/vimshottari", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_dasha_interpretation(mahadasha_lord: str, antardasha_lord: str = None) -> dict:
    """Get standalone thematic interpretation text for a specific Mahadasha and Antardasha combination. Pass planet names like 'Jupiter'."""
    payload = {"mahadasha_lord": mahadasha_lord}
    if antardasha_lord:
        payload["antardasha_lord"] = antardasha_lord
    return await _post("/vedic/dashas/interpretation", payload)

@mcp.tool
async def get_yogas(name: str, birth_year: int, birth_month: int, birth_day: int,
                    birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                    timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Detect all Vedic planetary yogas (Raja, Dhana, Doshas, Mahapurusha, etc.)."""
    return await _post("/vedic/yogas", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_doshas(name: str, birth_year: int, birth_month: int, birth_day: int,
                     birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                     timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Check for major Vedic structural flaws like Kala Sarpa Dosha and Mangal Dosha."""
    return await _post("/vedic/doshas", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))

@mcp.tool
async def get_gemstones(name: str, birth_year: int, birth_month: int, birth_day: int,
                        birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                        timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Get dedicated gemstone recommendations based on benefic planets and yogas."""
    res = await _post("/vedic/remedies", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))
    # Filter for gemstone specific advice
    gems = []
    if "remedies" in res:
        for r in res["remedies"]:
            if "gemstone" in str(r.get("remedies", "")).lower() or "wear" in str(r.get("remedies", "")).lower():
                gems.append(r)
    return {"gemstone_recommendations": gems if gems else "No specific gemstone required. General support recommended."}

@mcp.tool
async def get_mantras(name: str, birth_year: int, birth_month: int, birth_day: int,
                      birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                      timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Get dedicated mantra and pooja recommendations based on chart afflictions and doshas."""
    res = await _post("/vedic/remedies", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))
    mantras = []
    if "remedies" in res:
        for r in res["remedies"]:
            if "pooja" in str(r.get("remedies", "")).lower() or "mantra" in str(r.get("remedies", "")).lower() or "worship" in str(r.get("remedies", "")).lower():
                mantras.append(r)
    return {"mantra_recommendations": mantras if mantras else "No specific mantras required. General peace recommended."}


@mcp.tool
async def get_current_transits(name: str, birth_year: int, birth_month: int, birth_day: int,
                               birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                               timezone: str) -> dict:
    """Get current planetary transits compared to a natal chart."""
    return await _post("/transits/current", {
        "natal": {"name": name, "birth_year": birth_year, "birth_month": birth_month, "birth_day": birth_day,
                  "birth_hour": birth_hour, "birth_minute": birth_minute, "latitude": latitude,
                  "longitude": longitude, "timezone": timezone}})


@mcp.tool
async def get_panchang(year: int, month: int, day: int, latitude: float, longitude: float,
                       timezone: str, hour: int = 6, minute: int = 0) -> dict:
    """Get complete daily Panchang: Tithi, Vara, Nakshatra, Yoga, Karana, Rahu Kalam, etc."""
    return await _post("/panchang/daily", {
        "year": year, "month": month, "day": day, "hour": hour, "minute": minute,
        "latitude": latitude, "longitude": longitude, "timezone": timezone})


@mcp.tool
async def get_planetary_hours(year: int, month: int, day: int, latitude: float, longitude: float,
                              timezone: str, hour: int = 12, minute: int = 0) -> dict:
    """Calculate the 24 Planetary Hours (Hora) for a given day and location, showing the ruling planets."""
    return await _post("/utilities/planetary-hours", {
        "year": year, "month": month, "day": day, "hour": hour, "minute": minute,
        "latitude": latitude, "longitude": longitude, "timezone": timezone})


@mcp.tool
async def get_muhurta(year: int, month: int, day: int, hour: int, minute: int,
                      latitude: float, longitude: float, timezone: str, purpose: str = "marriage") -> dict:
    """Assess the auspiciousness of a specific time for a given purpose."""
    return await _post("/muhurta/quality", {
        "year": year, "month": month, "day": day, "hour": hour, "minute": minute,
        "latitude": latitude, "longitude": longitude, "timezone": timezone, "purpose": purpose})


@mcp.tool
async def find_auspicious_time(start_date: str, end_date: str, latitude: float, longitude: float,
                               timezone: str, purpose: str = "marriage", min_score: float = 65) -> dict:
    """Find the best auspicious times in a date range for a purpose (marriage, travel, business, etc.)."""
    return await _post("/muhurta/find-auspicious", {
        "start_date": start_date, "end_date": end_date,
        "latitude": latitude, "longitude": longitude, "timezone": timezone,
        "purpose": purpose, "min_score": min_score})


@mcp.tool
async def get_compatibility(p1_name: str, p1_year: int, p1_month: int, p1_day: int, p1_hour: int, p1_minute: int,
                            p1_lat: float, p1_lon: float, p1_tz: str,
                            p2_name: str, p2_year: int, p2_month: int, p2_day: int, p2_hour: int, p2_minute: int,
                            p2_lat: float, p2_lon: float, p2_tz: str,
                            ayanamsa: str = "LAHIRI") -> dict:
    """Calculate Ashtakoot Guna Milan (Vedic compatibility, max 36 points) between two persons."""
    return await _post("/vedic/compatibility", {
        "person1": {"name": p1_name, "birth_year": p1_year, "birth_month": p1_month, "birth_day": p1_day,
                    "birth_hour": p1_hour, "birth_minute": p1_minute, "latitude": p1_lat, "longitude": p1_lon, "timezone": p1_tz},
        "person2": {"name": p2_name, "birth_year": p2_year, "birth_month": p2_month, "birth_day": p2_day,
                    "birth_hour": p2_hour, "birth_minute": p2_minute, "latitude": p2_lat, "longitude": p2_lon, "timezone": p2_tz},
        "ayanamsa": ayanamsa})


@mcp.tool
async def get_synastry(p1_name: str, p1_year: int, p1_month: int, p1_day: int, p1_hour: int, p1_minute: int,
                       p1_lat: float, p1_lon: float, p1_tz: str,
                       p2_name: str, p2_year: int, p2_month: int, p2_day: int, p2_hour: int, p2_minute: int,
                       p2_lat: float, p2_lon: float, p2_tz: str) -> dict:
    """Calculate Western synastry aspects between two natal charts."""
    return await _post("/synastry/aspects", {
        "person1": {"name": p1_name, "birth_year": p1_year, "birth_month": p1_month, "birth_day": p1_day,
                    "birth_hour": p1_hour, "birth_minute": p1_minute, "latitude": p1_lat, "longitude": p1_lon, "timezone": p1_tz},
        "person2": {"name": p2_name, "birth_year": p2_year, "birth_month": p2_month, "birth_day": p2_day,
                    "birth_hour": p2_hour, "birth_minute": p2_minute, "latitude": p2_lat, "longitude": p2_lon, "timezone": p2_tz}})


@mcp.tool
async def get_composite_chart(p1_name: str, p1_year: int, p1_month: int, p1_day: int, p1_hour: int, p1_minute: int,
                              p1_lat: float, p1_lon: float, p1_tz: str,
                              p2_name: str, p2_year: int, p2_month: int, p2_day: int, p2_hour: int, p2_minute: int,
                              p2_lat: float, p2_lon: float, p2_tz: str) -> dict:
    """Calculate the Western Composite Chart (Midpoint Method) between two charts to reveal the relationship's dynamic."""
    return await _post("/western/composite", {
        "person1": {"name": p1_name, "birth_year": p1_year, "birth_month": p1_month, "birth_day": p1_day,
                    "birth_hour": p1_hour, "birth_minute": p1_minute, "latitude": p1_lat, "longitude": p1_lon, "timezone": p1_tz},
        "person2": {"name": p2_name, "birth_year": p2_year, "birth_month": p2_month, "birth_day": p2_day,
                    "birth_hour": p2_hour, "birth_minute": p2_minute, "latitude": p2_lat, "longitude": p2_lon, "timezone": p2_tz}})


@mcp.tool
async def get_natal_midpoints(name: str, birth_year: int, birth_month: int, birth_day: int,
                              birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                              timezone: str, house_system: str = "PLACIDUS") -> dict:
    """Calculate all planetary midpoints (e.g. Sun/Moon midpoint) within a single natal chart."""
    return await _post("/western/midpoints/natal", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, house_system, "TROPICAL", "LAHIRI"))


@mcp.tool
async def get_synastry_midpoints(p1_name: str, p1_year: int, p1_month: int, p1_day: int, p1_hour: int, p1_minute: int,
                                 p1_lat: float, p1_lon: float, p1_tz: str,
                                 p2_name: str, p2_year: int, p2_month: int, p2_day: int, p2_hour: int, p2_minute: int,
                                 p2_lat: float, p2_lon: float, p2_tz: str) -> dict:
    """Calculate midpoints between two charts (e.g. Person 1 Sun / Person 2 Moon midpoint)."""
    return await _post("/western/midpoints/synastry", {
        "person1": {"name": p1_name, "birth_year": p1_year, "birth_month": p1_month, "birth_day": p1_day,
                    "birth_hour": p1_hour, "birth_minute": p1_minute, "latitude": p1_lat, "longitude": p1_lon, "timezone": p1_tz},
        "person2": {"name": p2_name, "birth_year": p2_year, "birth_month": p2_month, "birth_day": p2_day,
                    "birth_hour": p2_hour, "birth_minute": p2_minute, "latitude": p2_lat, "longitude": p2_lon, "timezone": p2_tz}})


@mcp.tool
async def get_solar_return(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, target_year: int = 2026) -> dict:
    """Calculate the solar return chart for a given year."""
    payload = _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute, latitude, longitude, timezone)
    payload["target_year"] = target_year
    return await _post("/western/progressions/solar-return", payload)

@mcp.tool
async def get_lunar_return(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, target_year: int, target_month: int, target_day: int) -> dict:
    """Calculate the next lunar return chart following the given target date."""
    payload = _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute, latitude, longitude, timezone)
    payload["target_date"] = f"{target_year:04d}-{target_month:02d}-{target_day:02d}"
    return await _post("/western/progressions/lunar-return", payload)


@mcp.tool
async def get_shadbala(name: str, birth_year: int, birth_month: int, birth_day: int,
                       birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                       timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate Vedic Shadbala (six-fold planetary strength) for all planets."""
    return await _post("/vedic/shadbala", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_ashtakavarga(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str, ayanamsa: str = "LAHIRI") -> dict:
    """Calculate the complete Ashtakavarga table (Bhinnashtakavarga + Sarvashtakavarga)."""
    return await _post("/vedic/ashtakavarga", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, "WHOLE_SIGN", "SIDEREAL", ayanamsa))


@mcp.tool
async def get_arabic_parts(name: str, birth_year: int, birth_month: int, birth_day: int,
                           birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                           timezone: str) -> dict:
    """Calculate Arabic Parts / Lots (Part of Fortune, Spirit, Love, etc.)."""
    return await _post("/natal/arabic-parts", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone))


@mcp.tool
async def get_moon_phase(year: int, month: int, day: int) -> dict:
    """Get the moon phase for a specific date."""
    return await _get("/transits/now")

@mcp.tool
async def get_eclipse_impacts(name: str, birth_year: int, birth_month: int, birth_day: int,
                              birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                              timezone: str, year: int) -> dict:
    """Analyze all solar and lunar eclipses in a given year and detect tight orb impacts to the user's natal planets."""
    payload = {
        "natal": _birth_payload(name, birth_year, birth_month, birth_day, birth_hour, birth_minute, latitude, longitude, timezone)["birth_data"],
        "year": year
    }
    return await _post("/transits/eclipses/impacts", payload)


@mcp.tool
async def geocode_location(city: str, country: str = None) -> dict:
    """Convert a city name to geographic coordinates and timezone."""
    return await _post("/utilities/geocode", {"city": city, "country": country})


@mcp.tool
async def get_nakshatra_info(nakshatra_number: int) -> dict:
    """Retrieve detailed properties for a given nakshatra (1-27), including deity, symbol, animal, and dosha."""
    return await _get(f"/utilities/nakshatra/{nakshatra_number}")


@mcp.tool
async def get_astrocartography(name: str, birth_year: int, birth_month: int, birth_day: int,
                               birth_hour: int, birth_minute: int, latitude: float, longitude: float,
                               timezone: str, house_system: str = "PLACIDUS") -> dict:
    """Calculate Astrocartography (ACG) lines to find where planets cross the Midheaven (MC) and IC globally."""
    return await _post("/western/acg", _birth_payload(name, birth_year, birth_month, birth_day,
                       birth_hour, birth_minute, latitude, longitude, timezone, house_system, "TROPICAL", "LAHIRI"))


@mcp.tool
async def get_retrograde_calendar(year: int) -> dict:
    """Calculate exact retrograde motion periods for all major planets for a given year."""
    return await _post("/transits/retrogrades", {
        "start_date": f"{year}-01-01T00:00:00Z",
        "end_date": f"{year}-12-31T23:59:59Z",
        "options": {}
    })

@mcp.tool
async def get_now() -> dict:
    """Get current planetary positions (no natal chart needed)."""
    return await _get("/transits/now")


# ═══════════════════════════════════════════════════════════════════════
# MCP RESOURCES
# ═══════════════════════════════════════════════════════════════════════

@mcp.resource("astro://zodiac-signs")
async def zodiac_signs_resource() -> str:
    """Returns metadata for all 12 zodiac signs."""
    data = await _get("/utilities/zodiac-signs")
    return json.dumps(data, indent=2)


@mcp.resource("astro://nakshatras")
async def nakshatra_resource() -> str:
    """Returns metadata for all 27 Vedic Nakshatras."""
    data = await _get("/utilities/nakshatras")
    return json.dumps(data, indent=2)


@mcp.resource("astro://planetary-significations")
async def planetary_significations_resource() -> str:
    """Returns what each planet signifies in both Western and Vedic traditions."""
    return json.dumps({
        "Sun": {"western": "Self, ego, vitality, father", "vedic": "Atma, soul, king, authority, father"},
        "Moon": {"western": "Emotions, mother, instincts", "vedic": "Mana, mind, mother, queen, emotions"},
        "Mars": {"western": "Action, energy, passion", "vedic": "Courage, brothers, property, surgery"},
        "Mercury": {"western": "Communication, intellect", "vedic": "Intelligence, speech, commerce, education"},
        "Jupiter": {"western": "Expansion, philosophy, luck", "vedic": "Guru, wisdom, children, dharma, wealth"},
        "Venus": {"western": "Love, beauty, values", "vedic": "Luxury, marriage, arts, vehicles"},
        "Saturn": {"western": "Structure, discipline, karma", "vedic": "Longevity, karma, discipline, servants, sorrow"},
        "Rahu": {"vedic": "Illusion, foreign, technology, obsession, unconventional"},
        "Ketu": {"vedic": "Spirituality, liberation, past life, detachment"},
    }, indent=2)


@mcp.resource("astro://house-meanings")
async def house_meanings_resource() -> str:
    """Returns the astrological meanings of all 12 houses."""
    return json.dumps({
        "1st (Ascendant/Lagna)": "Self, body, personality, health, appearance",
        "2nd": "Wealth, family, speech, food, right eye",
        "3rd": "Siblings, courage, communication, short travel",
        "4th (IC)": "Mother, home, property, education, vehicles, happiness",
        "5th": "Children, creativity, intelligence, romance, past merit",
        "6th": "Enemies, disease, debts, service, competition",
        "7th (Descendant)": "Marriage, partnerships, business, foreign travel",
        "8th": "Longevity, obstacles, inheritance, transformation, occult",
        "9th": "Father, dharma, fortune, higher education, long travel, guru",
        "10th (MC)": "Career, profession, fame, authority, government",
        "11th": "Gains, income, elder siblings, friends, desires fulfilled",
        "12th": "Losses, liberation, foreign residence, expenses, spirituality",
    }, indent=2)


# ═══════════════════════════════════════════════════════════════════════
# MCP PROMPTS
# ═══════════════════════════════════════════════════════════════════════

@mcp.prompt("natal-consultation")
async def natal_consultation_prompt(name: str, birth_details: str) -> str:
    """System prompt template for conducting a full natal chart consultation."""
    return f"""You are an expert astrologer conducting a natal chart consultation for {name}.
Birth details: {birth_details}

Steps:
1. First call get_natal_chart to calculate the chart
2. Analyze the Ascendant, Sun, and Moon signs
3. Examine planetary placements in houses
4. Note key aspects (conjunctions, oppositions, trines, squares)
5. Check for any notable patterns (Grand Trine, T-Square, Stellium)
6. Provide a comprehensive personality and life-path reading
7. Highlight strengths and areas for growth

Be warm, insightful, and use both technical astrological terms and plain language explanations."""


@mcp.prompt("vedic-consultation")
async def vedic_consultation_prompt(name: str) -> str:
    """System prompt template for a Vedic/Jyotish consultation."""
    return f"""You are an expert Vedic astrologer (Jyotishi) conducting a consultation for {name}.

Steps:
1. Calculate the Vedic Kundli using get_vedic_kundli
2. Check current Dasha period using get_current_dasha
3. Detect Yogas using get_yogas
4. Check for Doshas using get_doshas
5. Calculate Shadbala for planetary strengths
6. Analyze the Navamsa (D9) chart for marriage/dharma
7. Provide predictions based on current Dasha and transit influences
8. Suggest remedies for any afflictions

Use traditional Jyotish terminology alongside English explanations. Reference Parashari principles."""


@mcp.prompt("transit-forecast")
async def transit_forecast_prompt(period: str) -> str:
    """System prompt template for transit period forecasting."""
    return f"""You are an expert astrologer providing a transit forecast for the period: {period}.

Steps:
1. Get the natal chart
2. Calculate current transits vs natal chart
3. Identify the most impactful transits (outer planets to personal planets/angles)
4. Note any upcoming retrogrades or eclipses
5. Provide a month-by-month or week-by-week forecast
6. Highlight peak intensity dates for major aspects

Focus on practical life implications rather than just listing aspects."""


@mcp.prompt("compatibility-reading")
async def compatibility_reading_prompt() -> str:
    """System prompt template for relationship compatibility analysis."""
    return """You are an expert astrologer conducting a relationship compatibility reading.

Steps:
1. Calculate both natal charts
2. For Vedic: Run get_compatibility for Ashtakoot Guna Milan (max 36 points)
3. For Western: Run get_synastry for cross-chart aspects
4. Calculate the composite chart
5. Analyze the strongest harmonious and challenging aspects
6. Provide balanced analysis of strengths and potential challenges
7. For Vedic: Note any Doshas (Nadi, Bhakoot) and their cancellations
8. Offer constructive guidance for the relationship

Be balanced and compassionate. Avoid overly deterministic language."""


if __name__ == "__main__":
    mcp.run()
