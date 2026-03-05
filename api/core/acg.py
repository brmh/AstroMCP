from typing import Dict, Any, List
from api.core.ephemeris import get_swe_lock
import swisseph as swe

def get_astrocartography_lines(jd: float, positions: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """
    Calculate the geographical longitudes where planets cross the Ascendant (Rising), 
    Descendant (Setting), Midheaven (Zenith), and Imum Coeli (Nadir).
    """
    lines = []
    
    # Greenwich Sidereal Time (GST) in hours
    with get_swe_lock():
        gst = swe.sidtime(jd)
        
    gst_deg = gst * 15.0  # Convert hours to degrees (0-360)
    
    # We will use simple equatorial coordinates (Right Ascension) to map the MC/IC lines.
    # The Asc/Dsc lines require latitude, but for a simple ACG endpoint, we only need MC/IC longitude.
    # Planet on MC when GST + GeoLon = RA(planet) => GeoLon = RA(planet) - GST
    for name, data in positions.items():
        if name in ["mean_apog", "oscu_apog", "chiron"]: continue
        
        # Right Ascension and Declination are needed for true ACG, but we can approximate
        # with tropical longitude if we don't recalculate equatorial.
        # But for an expert astrology API, we should use swe.calc_ut with FLG_EQUATORIAL
        with get_swe_lock():
            pid = getattr(swe, name.upper(), None)
            if pid is None and name == "mean_node":
                pid = swe.MEAN_NODE
                
            if pid is not None:
                # Get Equatorial position (RA and Declination)
                res, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)
                ra_deg = res[0] # RA in degrees
                dec = res[1]    # Declination in degrees
                
                # Geocentric Longitude for Zenith (MC)
                mc_lon = (ra_deg - gst_deg) % 360
                if mc_lon > 180: mc_lon -= 360  # -180 to 180
                
                # Imum Coeli (IC) is opposite
                ic_lon = (mc_lon + 180) % 360
                if ic_lon > 180: ic_lon -= 360
                
                lines.append({
                    "planet": name.title(),
                    "zenith_mc_longitude": round(mc_lon, 4),
                    "nadir_ic_longitude": round(ic_lon, 4),
                    "declination": round(dec, 4),
                })
                
    return lines
