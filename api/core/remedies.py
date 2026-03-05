from typing import Dict, List, Any
from api.core.ephemeris import SIGNS, SIGN_RULERS

# Map of Planet to its corresponding Gemstone
GEMSTONES = {
    "sun": {"gem": "Ruby (Manik)", "finger": "Ring Finger", "metal": "Gold or Copper", "day": "Sunday morning"},
    "moon": {"gem": "Pearl (Moti)", "finger": "Little Finger", "metal": "Silver", "day": "Monday morning"},
    "mars": {"gem": "Red Coral (Moonga)", "finger": "Ring Finger", "metal": "Gold or Copper", "day": "Tuesday morning"},
    "mercury": {"gem": "Emerald (Panna)", "finger": "Little Finger", "metal": "Gold or Silver", "day": "Wednesday morning"},
    "jupiter": {"gem": "Yellow Sapphire (Pukhraj)", "finger": "Index Finger", "metal": "Gold", "day": "Thursday morning"},
    "venus": {"gem": "Diamond or White Sapphire", "finger": "Middle or Little Finger", "metal": "Gold or Platinum", "day": "Friday morning"},
    "saturn": {"gem": "Blue Sapphire (Neelam)", "finger": "Middle Finger", "metal": "Silver or Panchdhatu", "day": "Saturday evening"},
    "rahu": {"gem": "Hessonite (Gomed)", "finger": "Middle Finger", "metal": "Silver", "day": "Saturday evening"},
    "ketu": {"gem": "Cat's Eye (Lehsuniya)", "finger": "Middle Finger", "metal": "Silver", "day": "Tuesday or Thursday morning"}
}

MANTRAS = {
    "sun": "Om Hram Hreem Hroum Sah Suryaya Namah",
    "moon": "Om Shram Shreem Shroum Sah Chandraya Namah",
    "mars": "Om Kram Kreem Kroum Sah Bhaumaya Namah",
    "mercury": "Om Bram Breem Broum Sah Budhaya Namah",
    "jupiter": "Om Jhram Jhreem Jhroum Sah Gurave Namah",
    "venus": "Om Dram Dreem Droum Sah Shukraya Namah",
    "saturn": "Om Pram Preem Proum Sah Shanaischaraya Namah",
    "mean_node": "Om Bhram Bhreem Bhroum Sah Rahave Namah",
    "ketu": "Om Sram Sreem Sroum Sah Ketave Namah"
}

CHARITIES = {
    "sun": "Donate wheat, jaggery, and copper on Sundays.",
    "moon": "Donate milk, rice, and silver on Mondays.",
    "mars": "Donate red lentils (masoor dal) and copper on Tuesdays.",
    "mercury": "Donate green gram (moong) and green clothing on Wednesdays.",
    "jupiter": "Donate chana dal, yellow cloth, and turmeric on Thursdays.",
    "venus": "Donate sugar, rice, and white clothing on Fridays.",
    "saturn": "Donate mustard oil, black sesame, and iron on Saturdays.",
    "mean_node": "Donate black mustard, radish, and coal on Saturdays.",
    "ketu": "Donate multi-colored blankets or black/white sesame seeds to a temple."
}

def _get_house_lord(houses: Dict, house_num: int) -> str:
    cusp = houses.get("cusps", {}).get(f"house_{house_num}", {})
    sign = cusp.get("sign", "Aries")
    if sign not in SIGNS:
        return ""
    idx = SIGNS.index(sign)
    return SIGN_RULERS[idx].lower()

def get_remedies(positions: Dict, houses: Dict) -> Dict[str, Any]:
    """Calculate Gemstone and Mantra recommendations."""
    
    # Identify functional benefics (Lords of 1, 5, 9)
    lord_1 = _get_house_lord(houses, 1)
    lord_5 = _get_house_lord(houses, 5)
    lord_9 = _get_house_lord(houses, 9)
    
    # Identify functional malefics (Lords of 6, 8, 12, 3, 11)
    # If a planet rules a trine and a dusthana (e.g., Venus for Taurus ascendant rules 1 and 6), it's considered overall benefic for lagna, but mixed.
    dusthana_lords = [_get_house_lord(houses, h) for h in [6, 8, 12]]
    
    benefic_lords = [lord_1, lord_5, lord_9]
    
    gemstones = []
    
    for l_idx, (lord, role) in enumerate([
        (lord_1, "Life Stone (Lagna Lord)"),
        (lord_5, "Lucky Stone (5th Lord)"),
        (lord_9, "Fortune Stone (9th Lord)")
    ]):
        if not lord:
            continue
            
        gem_data = GEMSTONES.get(lord, {}).copy()
        
        # Check afflictions for warning
        warning = None
        if lord in positions:
            p_house = positions[lord].get("house", 0)
            if p_house in [6, 8, 12]:
                warning = f"{lord.title()} is situated in the {p_house}th house. Consult an astrologer before wearing, as wearing its gem may amplify dusthana effects."
        
        gemstones.append({
            "planet": lord.title(),
            "role": role,
            "gemstone": gem_data.get("gem"),
            "wearing_finger": gem_data.get("finger"),
            "metal": gem_data.get("metal"),
            "day": gem_data.get("day"),
            "warning": warning
        })
        
    # Mantras and charities for afflicted planets
    afflictions = []
    from api.core.ephemeris import DEBILITATION
    
    # 1. Check debilitation
    for planet, data in positions.items():
        if planet in ["mean_apog", "oscu_apog", "chiron"]:
            continue
        p_sign = data.get("sign")
        if planet in DEBILITATION and DEBILITATION[planet][0] == p_sign:
            afflictions.append({
                "planet": planet,
                "reason": f"Debilitated in {p_sign}",
                "mantra": MANTRAS.get(planet),
                "charity": CHARITIES.get(planet)
            })
            
        # 2. Check dusthana placement
        p_house = data.get("house", 0)
        if p_house in [6, 8, 12]:
            afflictions.append({
                "planet": planet,
                "reason": f"Placed in Dusthana house ({p_house})",
                "mantra": MANTRAS.get(planet),
                "charity": CHARITIES.get(planet)
            })
            
    # Removing duplicates from afflictions (same planet, multiple reasons)
    unique_afflictions = {}
    for aff in afflictions:
        p = aff["planet"]
        if p not in unique_afflictions:
            unique_afflictions[p] = aff
        else:
            unique_afflictions[p]["reason"] += f" AND {aff['reason']}"
            
    return {
        "gemstones": gemstones,
        "mantras_and_charities": list(unique_afflictions.values())
    }
