from typing import Dict, Any, List
from api.core.ephemeris import longitude_to_sign
from api.core.calculations import angular_difference

def get_midpoints(positions1: Dict[str, Dict], positions2: Dict[str, Dict] = None) -> List[Dict[str, Any]]:
    """
    Calculate midpoints.
    If positions2 is None, calculates natal midpoints (all pairs in positions1).
    If positions2 is provided, calculates synastry midpoints (planet from pos1 to planet from pos2).
    """
    midpoints = []
    
    # If Synastry midpoints (pos1 vs pos2)
    if positions2:
        for p1_name, p1_data in positions1.items():
            if p1_name in ["mean_apog", "oscu_apog", "chiron"]: continue
            for p2_name, p2_data in positions2.items():
                if p2_name in ["mean_apog", "oscu_apog", "chiron"]: continue
                
                lon1 = p1_data["longitude"]
                lon2 = p2_data["longitude"]
                
                diff = (lon2 - lon1) % 360
                if diff > 180:
                    mp = (lon1 + diff / 2 + 180) % 360
                else:
                    mp = (lon1 + diff / 2) % 360
                    
                sign, idx, deg = longitude_to_sign(mp)
                midpoints.append({
                    "points": f"{p1_name.title()}/{p2_name.title()} (Synastry)",
                    "longitude": round(mp, 4),
                    "sign": sign,
                    "degree_in_sign": round(deg, 4)
                })
    else:
        # Natal Midpoints (combinatorics within one chart)
        planets = [k for k in positions1.keys() if k not in ["mean_apog", "oscu_apog", "chiron"]]
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1_name = planets[i]
                p2_name = planets[j]
                
                lon1 = positions1[p1_name]["longitude"]
                lon2 = positions1[p2_name]["longitude"]
                
                diff = (lon2 - lon1) % 360
                if diff > 180:
                    mp = (lon1 + diff / 2 + 180) % 360
                else:
                    mp = (lon1 + diff / 2) % 360
                    
                sign, idx, deg = longitude_to_sign(mp)
                midpoints.append({
                    "points": f"{p1_name.title()}/{p2_name.title()}",
                    "longitude": round(mp, 4),
                    "sign": sign,
                    "degree_in_sign": round(deg, 4)
                })
                
    return midpoints
