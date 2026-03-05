"""
Vedic Yoga Detection Engine
Detects Raja Yogas, Dhana Yogas, Doshas, Pancha Mahapurusha, and more.
"""

from typing import Dict, List, Any
from api.core.ephemeris import (
    SIGNS, SIGN_RULERS, EXALTATION, DEBILITATION,
    MOOLATRIKONA, angular_difference, longitude_to_sign,
)


KENDRAS = [1, 4, 7, 10]
TRIKONAS = [1, 5, 9]
DUSTHANAS = [6, 8, 12]
UPACHAYAS = [3, 6, 10, 11]

def _get_sign_lord(sign_name: str) -> str:
    idx = SIGNS.index(sign_name)
    return SIGN_RULERS[idx].lower()

def _planet_in_houses(positions: Dict, planet: str, houses: list) -> bool:
    return positions.get(planet, {}).get("house") in houses

def _planet_sign(positions: Dict, planet: str) -> str:
    return positions.get(planet, {}).get("sign", "")

def _planet_house(positions: Dict, planet: str) -> int:
    return positions.get(planet, {}).get("house", 0)

def _house_lord(houses_data: Dict, house_num: int) -> str:
    cusp = houses_data.get("cusps", {}).get(f"house_{house_num}", {})
    sign = cusp.get("sign", "Aries")
    return _get_sign_lord(sign)


def detect_all_yogas(positions: Dict, houses: Dict) -> List[Dict]:
    """Detect all major yogas in the chart."""
    yogas = []
    yogas.extend(detect_pancha_mahapurusha(positions))
    yogas.extend(detect_gaja_kesari(positions))
    yogas.extend(detect_budha_aditya(positions))
    yogas.extend(detect_raja_yogas(positions, houses))
    yogas.extend(detect_dhana_yogas(positions, houses))
    yogas.extend(detect_viparita_raja_yogas(positions, houses))
    yogas.extend(detect_chandra_yogas(positions))
    yogas.extend(detect_kala_sarpa_dosha(positions))
    yogas.extend(detect_mangal_dosha(positions))
    yogas.extend(detect_guru_chandal(positions))
    yogas.extend(detect_neecha_bhanga(positions, houses))
    yogas.extend(detect_vargottama(positions))
    return yogas


def detect_pancha_mahapurusha(positions: Dict) -> List[Dict]:
    """Detect the 5 Pancha Mahapurusha Yogas."""
    yogas = []
    checks = [
        ("Ruchaka", "mars", ["Aries", "Scorpio", "Capricorn"]),
        ("Bhadra", "mercury", ["Gemini", "Virgo"]),
        ("Hamsa", "jupiter", ["Sagittarius", "Pisces", "Cancer"]),
        ("Malavya", "venus", ["Taurus", "Libra", "Pisces"]),
        ("Shasha", "saturn", ["Capricorn", "Aquarius", "Libra"]),
    ]
    for name, planet, strong_signs in checks:
        sign = _planet_sign(positions, planet)
        house = _planet_house(positions, planet)
        if sign in strong_signs and house in KENDRAS:
            yogas.append({
                "yoga_name": f"{name} Yoga", "category": "Pancha Mahapurusha",
                "is_present": True, "strength": "Strong",
                "participating_planets": [planet],
                "houses_involved": [house],
                "description": f"{planet.title()} in own/exaltation sign in a Kendra house.",
                "effects": f"Confers power and authority through {planet.title()} qualities.",
                "remedies": None,
            })
    return yogas


def detect_gaja_kesari(positions: Dict) -> List[Dict]:
    """Jupiter in Kendra (1,4,7,10) from Moon."""
    jup_house = _planet_house(positions, "jupiter")
    moon_house = _planet_house(positions, "moon")
    if moon_house == 0 or jup_house == 0:
        return []
    diff = ((jup_house - moon_house) % 12) + 1
    if diff in [1, 4, 7, 10]:
        return [{"yoga_name": "Gaja Kesari Yoga", "category": "Raja Yoga",
                 "is_present": True, "strength": "Strong",
                 "participating_planets": ["jupiter", "moon"],
                 "houses_involved": [jup_house, moon_house],
                 "description": "Jupiter in Kendra from Moon.",
                 "effects": "Fame, wisdom, wealth, and respect.",
                 "remedies": None}]
    return []


def detect_budha_aditya(positions: Dict) -> List[Dict]:
    """Sun + Mercury in the same house."""
    sun_h = _planet_house(positions, "sun")
    mer_h = _planet_house(positions, "mercury")
    if sun_h and sun_h == mer_h:
        return [{"yoga_name": "Budha-Aditya Yoga", "category": "Raja Yoga",
                 "is_present": True, "strength": "Moderate",
                 "participating_planets": ["sun", "mercury"],
                 "houses_involved": [sun_h],
                 "description": "Sun and Mercury in same house.",
                 "effects": "Intelligence, communication skill, authority.",
                 "remedies": None}]
    return []


def detect_raja_yogas(positions: Dict, houses: Dict) -> List[Dict]:
    """Detect Raja Yogas: lord of Kendra + lord of Trikona in conjunction."""
    yogas = []
    kendra_lords = set()
    trikona_lords = set()
    for h in KENDRAS:
        kendra_lords.add(_house_lord(houses, h))
    for h in TRIKONAS:
        trikona_lords.add(_house_lord(houses, h))

    common = kendra_lords & trikona_lords
    for lord in common:
        if lord in positions:
            yogas.append({
                "yoga_name": "Raja Yoga (Kendra-Trikona)", "category": "Raja Yoga",
                "is_present": True, "strength": "Strong",
                "participating_planets": [lord],
                "houses_involved": [],
                "description": f"{lord.title()} is lord of both Kendra and Trikona.",
                "effects": "Power, authority, success, recognition.",
                "remedies": None,
            })

    # Check conjunction of different Kendra and Trikona lords
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl != tl and kl in positions and tl in positions:
                if _planet_house(positions, kl) == _planet_house(positions, tl):
                    yogas.append({
                        "yoga_name": "Raja Yoga (Conjunction)", "category": "Raja Yoga",
                        "is_present": True, "strength": "Moderate",
                        "participating_planets": [kl, tl],
                        "houses_involved": [_planet_house(positions, kl)],
                        "description": f"Kendra lord {kl.title()} conjunct Trikona lord {tl.title()}.",
                        "effects": "Power and authority.",
                        "remedies": None,
                    })
    return yogas


def detect_dhana_yogas(positions: Dict, houses: Dict) -> List[Dict]:
    """Detect wealth yogas."""
    yogas = []
    wealth_houses = [2, 5, 9, 11]
    lords = [_house_lord(houses, h) for h in wealth_houses]
    for i in range(len(lords)):
        for j in range(i+1, len(lords)):
            if lords[i] in positions and lords[j] in positions:
                if _planet_house(positions, lords[i]) == _planet_house(positions, lords[j]):
                    yogas.append({
                        "yoga_name": "Dhana Yoga", "category": "Dhana Yoga",
                        "is_present": True, "strength": "Moderate",
                        "participating_planets": [lords[i], lords[j]],
                        "houses_involved": [_planet_house(positions, lords[i])],
                        "description": f"Lords of houses {wealth_houses[i]} and {wealth_houses[j]} conjunct.",
                        "effects": "Wealth and financial prosperity.",
                        "remedies": None,
                    })
    return yogas


def detect_viparita_raja_yogas(positions: Dict, houses: Dict) -> List[Dict]:
    yogas = []
    checks = [
        ("Harsha Yoga", 6, [6, 8, 12]),
        ("Sarala Yoga", 8, [6, 8, 12]),
        ("Vimala Yoga", 12, [6, 8, 12]),
    ]
    for name, house_num, valid_houses in checks:
        lord = _house_lord(houses, house_num)
        if lord in positions and _planet_house(positions, lord) in valid_houses:
            yogas.append({
                "yoga_name": name, "category": "Viparita Raja Yoga",
                "is_present": True, "strength": "Moderate",
                "participating_planets": [lord],
                "houses_involved": [_planet_house(positions, lord)],
                "description": f"{house_num}th lord in a Dusthana house.",
                "effects": "Gains through adversity and reversal of fortune.",
                "remedies": None,
            })
    return yogas


def detect_chandra_yogas(positions: Dict) -> List[Dict]:
    yogas = []
    moon_h = _planet_house(positions, "moon")
    if not moon_h:
        return yogas

    planets_2nd = [n for n, p in positions.items()
                   if n not in ("moon", "mean_node", "true_node", "ketu") and p.get("house") == ((moon_h) % 12) + 1]
    planets_12th = [n for n, p in positions.items()
                    if n not in ("moon", "mean_node", "true_node", "ketu") and p.get("house") == ((moon_h - 2) % 12) + 1]

    if planets_2nd and not planets_12th:
        yogas.append({"yoga_name": "Sunafa Yoga", "category": "Chandra Yoga",
                      "is_present": True, "strength": "Moderate",
                      "participating_planets": ["moon"] + planets_2nd,
                      "houses_involved": [moon_h], "description": "Planet(s) in 2nd from Moon.",
                      "effects": "Wealth gained through own effort.", "remedies": None})
    if planets_12th and not planets_2nd:
        yogas.append({"yoga_name": "Anafa Yoga", "category": "Chandra Yoga",
                      "is_present": True, "strength": "Moderate",
                      "participating_planets": ["moon"] + planets_12th,
                      "houses_involved": [moon_h], "description": "Planet(s) in 12th from Moon.",
                      "effects": "Good personality, self-made success.", "remedies": None})
    if planets_2nd and planets_12th:
        yogas.append({"yoga_name": "Durudhura Yoga", "category": "Chandra Yoga",
                      "is_present": True, "strength": "Strong",
                      "participating_planets": ["moon"] + planets_2nd + planets_12th,
                      "houses_involved": [moon_h], "description": "Planets in both 2nd and 12th from Moon.",
                      "effects": "Wealth, vehicles, fame.", "remedies": None})
    if not planets_2nd and not planets_12th:
        yogas.append({"yoga_name": "Kemadruma Yoga", "category": "Chandra Yoga (Adverse)",
                      "is_present": True, "strength": "Moderate",
                      "participating_planets": ["moon"],
                      "houses_involved": [moon_h], "description": "No planets in 2nd or 12th from Moon.",
                      "effects": "Poverty, difficulties (check cancellations).", "remedies": "Worship Moon, wear Pearl."})
    return yogas


def detect_kala_sarpa_dosha(positions: Dict) -> List[Dict]:
    rahu_lon = positions.get("mean_node", {}).get("longitude")
    ketu_lon = positions.get("ketu", {}).get("longitude")
    if rahu_lon is None or ketu_lon is None:
        return []
    skip = {"mean_node", "true_node", "ketu"}
    all_between = True
    for name, pos in positions.items():
        if name in skip:
            continue
        lon = pos.get("longitude", 0)
        if rahu_lon < ketu_lon:
            if not (rahu_lon <= lon <= ketu_lon):
                all_between = False
                break
        else:
            if ketu_lon < lon < rahu_lon:
                all_between = False
                break
    if all_between:
        return [{"yoga_name": "Kala Sarpa Dosha", "category": "Dosha",
                 "is_present": True, "strength": "Strong",
                 "participating_planets": ["rahu", "ketu"],
                 "houses_involved": [],
                 "description": "All planets hemmed between Rahu and Ketu.",
                 "effects": "Karmic challenges, delays, obstacles.",
                 "remedies": "Kala Sarpa pooja, Rahu-Ketu remedies."}]
    return []


def detect_mangal_dosha(positions: Dict) -> List[Dict]:
    mars_h = _planet_house(positions, "mars")
    if mars_h in [1, 2, 4, 7, 8, 12]:
        return [{"yoga_name": "Mangal Dosha", "category": "Dosha",
                 "is_present": True, "strength": "Moderate",
                 "participating_planets": ["mars"],
                 "houses_involved": [mars_h],
                 "description": f"Mars in {mars_h}th house.",
                 "effects": "Delays/difficulties in marriage.",
                 "remedies": "Mangal pooja, wear Red Coral, Hanuman worship."}]
    return []


def detect_guru_chandal(positions: Dict) -> List[Dict]:
    jup_h = _planet_house(positions, "jupiter")
    rahu_h = _planet_house(positions, "mean_node")
    if jup_h and jup_h == rahu_h:
        return [{"yoga_name": "Guru Chandal Yoga", "category": "Dosha",
                 "is_present": True, "strength": "Moderate",
                 "participating_planets": ["jupiter", "rahu"],
                 "houses_involved": [jup_h],
                 "description": "Jupiter conjunct Rahu.",
                 "effects": "Unorthodox thinking, may challenge traditions.",
                 "remedies": "Jupiter remedies, donate yellow items on Thursday."}]
    return []


def detect_neecha_bhanga(positions: Dict, houses: Dict) -> List[Dict]:
    yogas = []
    for planet, (deb_sign, deb_deg) in DEBILITATION.items():
        if planet not in positions:
            continue
        if _planet_sign(positions, planet) == deb_sign:
            deb_lord = _get_sign_lord(deb_sign)
            if deb_lord in positions and _planet_house(positions, deb_lord) in KENDRAS:
                yogas.append({"yoga_name": "Neecha Bhanga Raja Yoga", "category": "Raja Yoga",
                              "is_present": True, "strength": "Strong",
                              "participating_planets": [planet, deb_lord],
                              "houses_involved": [_planet_house(positions, planet)],
                              "description": f"Debilitation of {planet.title()} cancelled by {deb_lord.title()} in Kendra.",
                              "effects": "Rise after initial struggles, great success.",
                              "remedies": None})
    return yogas


def detect_vargottama(positions: Dict) -> List[Dict]:
    yogas = []
    for name, pos in positions.items():
        if pos.get("sign") == pos.get("navamsa_sign"):
            yogas.append({"yoga_name": "Vargottama", "category": "Strength",
                          "is_present": True, "strength": "Strong",
                          "participating_planets": [name],
                          "houses_involved": [pos.get("house", 0)],
                          "description": f"{name.title()} in same sign in D1 and D9.",
                          "effects": f"{name.title()} is extra strong and auspicious.",
                          "remedies": None})
    return yogas


def detect_sade_sati(natal_moon_sign_idx: int, transit_saturn_sign_idx: int) -> Dict:
    diff = (transit_saturn_sign_idx - natal_moon_sign_idx) % 12
    if diff == 11:
        return {"sade_sati": True, "phase": "Rising (12th from Moon)", "severity": "Moderate"}
    elif diff == 0:
        return {"sade_sati": True, "phase": "Peak (Over Moon)", "severity": "Strong"}
    elif diff == 1:
        return {"sade_sati": True, "phase": "Setting (2nd from Moon)", "severity": "Moderate"}
    return {"sade_sati": False, "phase": None, "severity": None}


def get_atmakaraka(positions: Dict) -> Dict:
    """Find the Atmakaraka (planet with highest degree in sign), excluding Rahu/Ketu."""
    skip = {"mean_node", "true_node", "ketu", "rahu", "mean_apog", "oscu_apog"}
    candidates = {n: p["degree_in_sign"] for n, p in positions.items()
                  if n not in skip and "degree_in_sign" in p}
    if not candidates:
        return {}
    ak = max(candidates, key=candidates.get)
    return {"atmakaraka": ak, "degree": candidates[ak]}


def get_amatyakaraka(positions: Dict) -> Dict:
    skip = {"mean_node", "true_node", "ketu", "rahu", "mean_apog", "oscu_apog"}
    candidates = {n: p["degree_in_sign"] for n, p in positions.items()
                  if n not in skip and "degree_in_sign" in p}
    if len(candidates) < 2:
        return {}
    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    return {"amatyakaraka": sorted_c[1][0], "degree": sorted_c[1][1]}
