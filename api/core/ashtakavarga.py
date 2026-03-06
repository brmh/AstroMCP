"""
Ashtakavarga System
Calculates Bhinnashtakavarga and Sarvashtakavarga grids.
"""

from typing import Dict, List, Any

# Benefic point contribution tables for each planet
# Each row = contributing planet, each column = house from that planet
# 1 = benefic point, 0 = no point
# Standard Ashtakavarga tables from classical texts

AV_SUN = {
    "sun": [1,1,0,0,0,1,0,0,0,0,1,1],
    "moon": [0,0,1,0,0,1,0,0,0,1,1,0],
    "mars": [1,1,0,0,0,1,0,0,0,1,1,0],
    "mercury": [0,0,1,0,1,1,0,0,1,1,1,0],
    "jupiter": [0,0,0,0,1,1,0,0,1,0,1,0],
    "venus": [0,0,0,0,0,1,0,0,0,0,1,1],
    "saturn": [1,1,0,0,0,1,0,0,0,0,1,1],
    "ascendant": [0,0,1,0,0,1,0,0,1,1,1,0],
}

AV_MOON = {
    "sun": [0,0,1,0,0,1,1,1,0,1,1,0],
    "moon": [1,0,1,0,0,1,1,0,0,1,1,0],
    "mars": [0,1,0,1,0,1,0,1,0,1,1,0],
    "mercury": [1,0,1,0,0,1,0,0,0,0,1,0],
    "jupiter": [1,1,0,1,0,0,1,0,0,1,1,0],
    "venus": [0,0,1,0,0,0,1,0,0,1,1,0],
    "saturn": [0,0,1,0,0,1,0,0,0,0,1,0],
    "ascendant": [0,0,1,0,0,1,0,0,0,1,1,0],
}

AV_MARS = {
    "sun": [0,0,1,0,1,1,0,0,0,1,1,0],
    "moon": [0,0,1,0,0,1,0,0,0,0,1,0],
    "mars": [1,1,0,0,0,1,0,0,0,1,1,0],
    "mercury": [0,0,1,0,1,1,0,0,0,0,1,0],
    "jupiter": [0,0,0,0,0,1,0,0,0,1,1,0],
    "venus": [0,0,0,0,0,1,0,1,0,0,1,1],
    "saturn": [1,0,0,1,0,1,0,0,0,1,1,0],
    "ascendant": [1,0,1,0,0,1,0,0,0,1,1,0],
}

AV_MERCURY = {
    "sun": [0,0,0,0,1,1,0,0,0,0,1,1],
    "moon": [0,1,0,1,0,1,0,0,0,0,1,0],
    "mars": [1,1,0,0,0,1,0,0,0,0,1,1],
    "mercury": [1,1,0,0,1,1,0,0,0,0,1,1],
    "jupiter": [0,0,0,0,0,1,0,0,1,0,1,1],
    "venus": [1,1,0,0,1,1,0,0,1,0,1,0],
    "saturn": [1,1,0,0,0,1,0,0,0,0,1,1],
    "ascendant": [1,1,0,0,1,1,0,0,0,0,1,0],
}

AV_JUPITER = {
    "sun": [1,1,0,0,0,0,1,0,0,1,1,0],
    "moon": [0,1,0,0,1,0,1,0,0,0,1,0],
    "mars": [1,1,0,0,0,0,1,0,0,0,1,0],
    "mercury": [1,1,0,0,1,0,1,0,0,0,1,0],
    "jupiter": [1,1,1,0,0,0,1,0,0,1,1,0],
    "venus": [0,1,0,0,0,0,0,0,1,0,1,0],
    "saturn": [0,0,1,0,0,1,0,0,0,0,1,1],
    "ascendant": [1,1,0,0,0,0,1,0,0,0,1,0],
}

AV_VENUS = {
    "sun": [0,0,0,0,0,0,0,1,0,0,1,1],
    "moon": [1,1,0,0,0,0,0,0,0,0,1,1],
    "mars": [0,0,1,0,0,1,0,0,0,0,1,1],
    "mercury": [0,0,1,0,1,0,0,0,1,0,1,0],
    "jupiter": [0,0,0,0,1,0,0,1,0,0,1,0],
    "venus": [1,1,0,0,0,0,0,0,0,0,1,1],
    "saturn": [0,0,1,0,1,0,0,0,1,0,1,0],
    "ascendant": [1,1,0,0,0,0,0,0,0,0,1,1],
}

AV_SATURN = {
    "sun": [1,1,0,0,0,1,0,0,0,0,1,1],
    "moon": [0,0,1,0,0,1,0,0,0,0,1,0],
    "mars": [0,0,1,0,0,1,0,0,0,0,1,1],
    "mercury": [0,0,0,0,0,1,0,1,0,1,1,1],
    "jupiter": [0,0,0,0,1,1,0,0,0,0,1,1],
    "venus": [0,0,0,0,0,1,0,0,0,0,1,1],
    "saturn": [0,0,1,0,0,1,0,0,0,0,1,0],
    "ascendant": [1,0,1,0,0,1,0,0,0,0,1,0],
}

AV_TABLES = {
    "sun": AV_SUN, "moon": AV_MOON, "mars": AV_MARS,
    "mercury": AV_MERCURY, "jupiter": AV_JUPITER,
    "venus": AV_VENUS, "saturn": AV_SATURN,
}


def get_bhinnashtakavarga(positions: Dict, houses: Dict) -> Dict[str, List[int]]:
    """
    Calculate Bhinnashtakavarga (individual AV) for each of 7 planets.
    Returns a dict mapping planet name to a list of 12 values (benefic points per house).
    """
    asc_sign_idx = int(houses.get("ascendant", 0) / 30)
    results = {}

    for planet_name, table in AV_TABLES.items():
        house_points = [0] * 12

        for contributor, bits in table.items():
            if contributor == "ascendant":
                contrib_sign_idx = asc_sign_idx
            else:
                p_data = positions.get(contributor, {})
                # FIX Bug 4: fall back to computing sign_index from longitude
                # if assign_houses_to_planets was not called
                if "sign_index" in p_data:
                    contrib_sign_idx = p_data["sign_index"]
                else:
                    lon = p_data.get("longitude", 0)
                    contrib_sign_idx = int(lon / 30) % 12

            for offset, has_point in enumerate(bits):
                if has_point:
                    house_idx = (contrib_sign_idx + offset) % 12
                    house_points[house_idx] += 1

        results[planet_name] = house_points

    return results


def get_sarvashtakavarga(positions: Dict, houses: Dict) -> Dict[str, Any]:
    """
    Calculate Sarvashtakavarga (combined AV).
    Total benefic points in each house (should sum to 337).
    """
    bhinna = get_bhinnashtakavarga(positions, houses)
    sarva = [0] * 12

    for planet_name, points in bhinna.items():
        for i in range(12):
            sarva[i] += points[i]

    house_analysis = []
    for i in range(12):
        strength = "Strong" if sarva[i] >= 28 else ("Weak" if sarva[i] < 25 else "Average")
        house_analysis.append({
            "house": i + 1,
            "total_points": sarva[i],
            "strength": strength,
        })

    return {
        "bhinnashtakavarga": bhinna,
        "sarvashtakavarga": sarva,
        "total_points": sum(sarva),
        "house_analysis": house_analysis,
    }

def get_transit_scoring(natal_positions: Dict[str, Any], natal_houses: Dict[str, Any], transit_positions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates how favorable current transits are based on the natal Ashtakavarga scores.
    A transit planet passing through a house with >= 28 Sarvashtakavarga points is highly favorable.
    Additionally, checks the specific Bhinnashtakavarga score (>= 4 is good, <= 3 is tough).
    """
    sav_data = get_sarvashtakavarga(natal_positions, natal_houses)
    bhinna = sav_data["bhinnashtakavarga"]
    sarva = sav_data["sarvashtakavarga"]
    
    asc_sign_idx = int(natal_houses.get("ascendant", 0) / 30)
    
    results = {}
    total_transit_score = 0
    
    # We only score the 7 classic planets for Ashtakavarga
    classic_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    
    for planet in classic_planets:
        t_pos = transit_positions.get(planet)
        if not t_pos:
            continue
            
        t_sign_idx = t_pos.get("sign_index", 0)
        
        # Determine the house the transit planet is in relative to the natal Ascendant
        # Using simple whole-sign transit house logic
        house_idx = (t_sign_idx - asc_sign_idx) % 12
        actual_house = house_idx + 1
        
        # Get AV scores for that house
        planet_bav_score = bhinna.get(planet, [0]*12)[house_idx]
        total_sav_score = sarva[house_idx]
        
        # Scoring logic
        # BAV: < 4 is unfavorable, 4 is neutral, > 4 is highly favorable
        if planet_bav_score >= 5:
            bav_interp = "Highly Favorable"
            total_transit_score += 2
        elif planet_bav_score == 4:
            bav_interp = "Neutral / Mixed"
            total_transit_score += 1
        else:
            bav_interp = "Challenging / Obstacles"
            total_transit_score -= 1
            
        # SAV: < 25 weak, 25-28 avg, > 28 strong
        if total_sav_score >= 28:
            sav_interp = "Supported by environment"
            total_transit_score += 2
        elif total_sav_score >= 25:
            sav_interp = "Average environmental support"
            total_transit_score += 1
        else:
            sav_interp = "Lacking environmental support"
            total_transit_score -= 1
            
        results[planet] = {
            "transit_sign": t_pos.get("sign"),
            "transit_house": actual_house,
            "bhinnashtakavarga_score": planet_bav_score,
            "bav_interpretation": bav_interp,
            "sarvashtakavarga_score": total_sav_score,
            "sav_interpretation": sav_interp
        }
    
    overall_interp = "Positive Phase" if total_transit_score > 5 else ("Mixed/Average Phase" if total_transit_score >= 0 else "Challenging Phase")
    
    return {
        "transit_scores": results,
        "overall_score": total_transit_score,
        "overall_interpretation": overall_interp
    }
