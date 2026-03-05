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
                contrib_sign_idx = positions.get(contributor, {}).get("sign_index", 0)

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
