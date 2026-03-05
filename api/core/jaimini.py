from typing import Dict, Any, List
from api.core.ephemeris import SIGNS, SIGN_RULERS

def get_chara_karakas(positions: Dict) -> Dict[str, Any]:
    """Calculate the 7 Jaimini Chara Karakas (AK, AmK, BK, MK, PiK, PK, DK)."""
    valid_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    
    planet_degrees = []
    for name in valid_planets:
        if name in positions:
            deg = positions[name].get("degree_in_sign", 0)
            planet_degrees.append((name, deg))
            
    # Sort descending by degree
    planet_degrees.sort(key=lambda x: x[1], reverse=True)
    
    karakas = [
        "AK (Atmakaraka - Soul)", 
        "AmK (Amatyakaraka - Career)", 
        "BK (Bhratrukaraka - Siblings)",
        "MK (Matrukaraka - Mother)", 
        "PiK (Pitrukaraka - Father)", 
        "PK (Putrakaraka - Children)",
        "DK (Darakaraka - Spouse)"
    ]
               
    result = {}
    for i, (p_name, deg) in enumerate(planet_degrees):
        if i < len(karakas):
            k_name = karakas[i]
            result[k_name] = {
                "planet": p_name.title(),
                "degree": round(deg, 4),
                "sign": positions[p_name]["sign"],
                "house": positions[p_name].get("house", 0)
            }
            
    return result

def get_arudha_padas(positions: Dict, houses: Dict) -> Dict[str, int]:
    """Calculate the Arudha Padas for all 12 houses."""
    arudhas = {}
    
    def get_lord(sign_idx: int) -> str:
        # Scorpio has co-lord Ketu, Aquarius has co-lord Rahu.
        # Strict Jaimini rules use stronger lord, but standard assigns primary lords.
        ruler = SIGN_RULERS[sign_idx].lower()
        return ruler

    def get_house_of_planet(p_name: str) -> int:
        return positions.get(p_name, {}).get("house", 1)
        
    for h in range(1, 13):
        cusp_sign = houses.get("cusps", {}).get(f"house_{h}", {}).get("sign")
        if not cusp_sign:
            arudhas[f"A{h}"] = h
            continue
            
        sign_idx = SIGNS.index(cusp_sign)
        lord = get_lord(sign_idx)
        
        lord_house = get_house_of_planet(lord)
        
        # Count from house 'h' to 'lord_house' (inclusive)
        count = (lord_house - h) % 12 + 1
        
        # Arudha falls 'count' houses away from 'lord_house'
        pada_house = (lord_house + count - 1) % 12
        if pada_house == 0:
            pada_house = 12
            
        # Apply Jaimini Exceptions
        # If Pada falls in the 1st from the original house
        if pada_house == h:
            pada_house = (h + 9) % 12 + 1  # 10th from original house
        # If Pada falls in the 7th from the original house
        elif pada_house == (h + 6 - 1) % 12 + 1:
            pada_house = (h + 3) % 12 + 1  # 4th from original house
            
        pada_name = "AL" if h == 1 else ("UL" if h == 12 else f"A{h}")
        arudhas[pada_name] = pada_house

    return arudhas

def get_karakamsa(positions: Dict) -> Dict[str, Any]:
    """Find the Karakamsa (Navamsa sign occupied by the Atmakaraka)."""
    karakas = get_chara_karakas(positions)
    ak_data = karakas.get("AK (Atmakaraka - Soul)")
    
    if not ak_data:
        return {"error": "Could not determine Atmakaraka."}
        
    ak_planet = ak_data["planet"].lower()
    
    # Get Navamsa sign of AK
    navamsa_sign = positions.get(ak_planet, {}).get("navamsa_sign")
    
    return {
        "atmakaraka": ak_planet.title(),
        "rasi_sign": ak_data["sign"],
        "karakamsa_sign": navamsa_sign
    }
