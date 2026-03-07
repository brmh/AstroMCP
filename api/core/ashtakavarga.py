"""
Ashtakavarga System
Calculates Bhinnashtakavarga and Sarvashtakavarga grids according to classical Vedic astrology.
"""

from typing import Dict, List, Any

# Benefic houses (counted from each planet) where bindus (points) are given
# Based on classical Parashara Ashtakavarga system
PLANET_BENEFIC_HOUSES = {
    "sun": [1, 2, 4, 7, 8, 9, 10, 11],      # Sun gives bindus to these houses
    "moon": [1, 3, 6, 7, 8, 10, 11],         # Moon gives bindus to these houses  
    "mars": [1, 3, 6, 10, 11],               # Mars gives bindus to these houses
    "mercury": [1, 3, 5, 6, 7, 9, 10, 11],  # Mercury gives bindus to these houses
    "jupiter": [1, 2, 3, 4, 7, 8, 10, 11],  # Jupiter gives bindus to these houses
    "venus": [1, 2, 3, 4, 5, 8, 9, 11],     # Venus gives bindus to these houses
    "saturn": [1, 3, 6, 11],                 # Saturn gives bindus to these houses
    "ascendant": [1, 2, 3, 4, 7, 8, 10, 11]  # Lagna gives bindus to these houses
}

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def get_planet_sign_index(positions: Dict, planet: str) -> int:
    """Get the sign index (0-11) where a planet is located."""
    planet_data = positions.get(planet, {})
    if "sign_index" in planet_data:
        return planet_data["sign_index"]
    else:
        # Fallback: calculate from longitude
        longitude = planet_data.get("longitude", 0)
        return int(longitude / 30) % 12


def calculate_bindus_for_contributor(contributor_pos: int, benefic_houses: List[int]) -> List[int]:
    """
    Calculate bindus (0 or 1) for each zodiac sign from a single contributor.
    contributor_pos: sign index where contributor planet is located (0-11)
    benefic_houses: house numbers (1-12) where contributor gives bindus
    Returns: list of 12 values (0 or 1) for each sign
    """
    bindus = [0] * 12
    for house in benefic_houses:
        # Convert house number to sign index (house 1 = contributor's position)
        sign_idx = (contributor_pos + house - 1) % 12
        bindus[sign_idx] = 1
    return bindus


def get_bhinnashtakavarga(positions: Dict, houses: Dict) -> Dict[str, List[int]]:
    """
    Calculate Bhinnashtakavarga (individual Ashtakavarga) for each of 7 planets.
    Each planet gets points from 8 contributors (7 planets + Ascendant).
    Returns: dict mapping planet name to list of 12 bindu counts (0-8 per sign)
    """
    # Get positions of all 7 planets + Ascendant
    contributors = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    
    # Get sign positions
    contributor_positions = {}
    for planet in contributors:
        contributor_positions[planet] = get_planet_sign_index(positions, planet)
    
    # Add Ascendant position
    asc_longitude = houses.get("ascendant", 0)
    contributor_positions["ascendant"] = int(asc_longitude / 30) % 12
    
    # Calculate Bhinnashtakavarga for each of the 7 planets
    results = {}
    
    for planet in contributors:
        planet_bindus = [0] * 12  # Each sign can get 0-8 bindus total
        
        # Each contributor gives 0 or 1 bindu to each sign
        for contributor, contrib_pos in contributor_positions.items():
            benefic_houses = PLANET_BENEFIC_HOUSES[contributor]
            contributor_bindus = calculate_bindus_for_contributor(contrib_pos, benefic_houses)
            
            # Add contributor's bindus to planet's total
            for sign_idx in range(12):
                planet_bindus[sign_idx] += contributor_bindus[sign_idx]
        
        results[planet] = planet_bindus
    
    return results


def get_sarvashtakavarga(positions: Dict, houses: Dict) -> Dict[str, Any]:
    """
    Calculate Sarvashtakavarga (combined Ashtakavarga).
    Adds up bindus from all 7 Bhinnashtakavarga tables for each sign.
    Maximum possible: 56 points per sign (8 contributors × 7 planets).
    """
    bhinna = get_bhinnashtakavarga(positions, houses)
    sarva = [0] * 12
    
    # Sum up bindus across all 7 planets for each sign
    for planet_name, points in bhinna.items():
        for i in range(12):
            sarva[i] += points[i]
    
    # Analyze strength of each house
    house_analysis = []
    for i in range(12):
        points = sarva[i]
        if points >= 30:
            strength = "Very Strong"
            interpretation = "Excellent results when planets transit here"
        elif points >= 25:
            strength = "Average to Good" 
            interpretation = "Good results expected"
        else:
            strength = "Weak"
            interpretation = "Transits here may be difficult"
            
        house_analysis.append({
            "house": i + 1,
            "sign": ZODIAC_SIGNS[i],
            "total_points": points,
            "max_possible": 56,
            "strength": strength,
            "interpretation": interpretation
        })
    
    return {
        "bhinnashtakavarga": bhinna,
        "sarvashtakavarga": sarva,
        "total_points": sum(sarva),
        "max_total_points": 56 * 12,  # 12 signs × 56 max points
        "house_analysis": house_analysis,
        "calculation_method": "Classical Parashara Ashtakavarga"
    }

def get_transit_scoring(natal_positions: Dict[str, Any], natal_houses: Dict[str, Any], transit_positions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates how favorable current transits are based on the natal Ashtakavarga scores.
    Uses corrected Ashtakavarga calculation:
    - Sarvashtakavarga: >= 30 very strong, 25-29 average to good, < 25 weak
    - Bhinnashtakavarga: >= 4 good, < 4 challenging for each planet's transit
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
        house_idx = (t_sign_idx - asc_sign_idx) % 12
        actual_house = house_idx + 1
        
        # Get AV scores for that house
        planet_bav_score = bhinna.get(planet, [0]*12)[house_idx]
        total_sav_score = sarva[house_idx]
        
        # Scoring logic based on corrected Ashtakavarga
        # BAV: >= 4 is good, < 4 is challenging
        if planet_bav_score >= 4:
            bav_interp = "Favorable Transit"
            total_transit_score += 1
        else:
            bav_interp = "Challenging Transit"
            total_transit_score -= 1
            
        # SAV: >= 30 very strong, 25-29 average to good, < 25 weak
        if total_sav_score >= 30:
            sav_interp = "Very Strong Environmental Support"
            total_transit_score += 2
        elif total_sav_score >= 25:
            sav_interp = "Good Environmental Support"
            total_transit_score += 1
        else:
            sav_interp = "Weak Environmental Support"
            total_transit_score -= 1
            
        results[planet] = {
            "transit_sign": t_pos.get("sign"),
            "transit_house": actual_house,
            "bhinnashtakavarga_score": planet_bav_score,
            "bav_interpretation": bav_interp,
            "sarvashtakavarga_score": total_sav_score,
            "sav_interpretation": sav_interp,
            "combined_score": "Positive" if (planet_bav_score >= 4 and total_sav_score >= 25) else "Mixed" if (planet_bav_score >= 4 or total_sav_score >= 25) else "Challenging"
        }
    
    overall_interp = "Highly Favorable Phase" if total_transit_score > 5 else ("Positive Phase" if total_transit_score > 0 else ("Mixed Phase" if total_transit_score == 0 else "Challenging Phase"))
    
    return {
        "transit_scores": results,
        "overall_score": total_transit_score,
        "overall_interpretation": overall_interp,
        "calculation_note": "Using corrected classical Ashtakavarga method"
    }
