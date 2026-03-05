"""
Compatibility — Ashtakoot Guna Milan (8-fold scoring) + Western Synastry.
"""

from typing import Dict, List, Any
from api.core.ephemeris import (
    NAKSHATRAS, NAKSHATRA_GANAS, longitude_to_nakshatra, SIGNS,
    angular_difference,
)

# ── Varna (Caste) mapping: each sign's Varna ─────────────────────────────
# Brahmin=4, Kshatriya=3, Vaishya=2, Shudra=1
SIGN_VARNA = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4]  # Aries..Pisces

# ── Vashya Groups ────────────────────────────────────────────────────────
VASHYA_GROUPS = {
    "Aries": "Chatushpada", "Taurus": "Chatushpada", "Gemini": "Dwipad",
    "Cancer": "Jalachara", "Leo": "Vanachara", "Virgo": "Dwipad",
    "Libra": "Dwipad", "Scorpio": "Keeta", "Sagittarius": "Dwipad",
    "Capricorn": "Chatushpada", "Aquarius": "Dwipad", "Pisces": "Jalachara",
}

# ── Yoni Animal Pairs ────────────────────────────────────────────────────
NAKSHATRA_YONI = [
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep",
    "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger",
    "Deer", "Deer", "Dog", "Monkey", "Cow", "Monkey", "Lion", "Horse",
    "Lion", "Cow", "Elephant",
]

YONI_COMPATIBILITY = {
    ("Horse", "Horse"): 4, ("Horse", "Elephant"): 2,
    ("Elephant", "Elephant"): 4, ("Sheep", "Sheep"): 4,
    ("Serpent", "Serpent"): 4, ("Dog", "Dog"): 4,
    ("Cat", "Cat"): 4, ("Cat", "Rat"): 0, ("Rat", "Rat"): 4,
    ("Rat", "Cat"): 0, ("Cow", "Cow"): 4, ("Buffalo", "Buffalo"): 4,
    ("Tiger", "Tiger"): 4, ("Tiger", "Deer"): 1, ("Deer", "Deer"): 4,
    ("Deer", "Tiger"): 1, ("Monkey", "Monkey"): 4, ("Lion", "Lion"): 4,
    ("Lion", "Elephant"): 1, ("Elephant", "Lion"): 1,
}

# ── Nadi Groups ──────────────────────────────────────────────────────────
NAKSHATRA_NADI = [
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya",
]


def get_gun_milan(person1_moon_longitude: float, person2_moon_longitude: float) -> Dict[str, Any]:
    """
    Calculate Ashtakoot Guna Milan (8-fold compatibility, max 36 points).
    Uses sidereal Moon longitude for both persons.
    """
    nak1_name, nak1_num, _, _, _ = longitude_to_nakshatra(person1_moon_longitude)
    nak2_name, nak2_num, _, _, _ = longitude_to_nakshatra(person2_moon_longitude)

    sign1_idx = int(person1_moon_longitude / 30) % 12
    sign2_idx = int(person2_moon_longitude / 30) % 12

    kutas = {}
    total = 0

    # 1. Varna (max 1)
    v1 = SIGN_VARNA[sign1_idx]
    v2 = SIGN_VARNA[sign2_idx]
    varna_pts = 1 if v1 >= v2 else 0
    kutas["varna"] = {"points": varna_pts, "max": 1, "description": "Spiritual compatibility"}
    total += varna_pts

    # 2. Vashya (max 2)
    s1 = SIGNS[sign1_idx]
    s2 = SIGNS[sign2_idx]
    g1 = VASHYA_GROUPS.get(s1, "Dwipad")
    g2 = VASHYA_GROUPS.get(s2, "Dwipad")
    if g1 == g2:
        vashya_pts = 2
    elif (g1 == "Dwipad" and g2 in ["Chatushpada", "Jalachara"]) or \
         (g2 == "Dwipad" and g1 in ["Chatushpada", "Jalachara"]):
        vashya_pts = 1
    else:
        vashya_pts = 0
    kutas["vashya"] = {"points": vashya_pts, "max": 2, "description": "Dominance compatibility"}
    total += vashya_pts

    # 3. Tara (max 3)
    tara_diff = ((nak2_num - nak1_num) % 27)
    tara_group = (tara_diff % 9)
    tara_pts = 3 if tara_group in [0, 1, 2, 3, 5, 7] else 0
    kutas["tara"] = {"points": tara_pts, "max": 3, "description": "Birth star compatibility"}
    total += tara_pts

    # 4. Yoni (max 4)
    y1 = NAKSHATRA_YONI[nak1_num - 1] if nak1_num <= 27 else "Horse"
    y2 = NAKSHATRA_YONI[nak2_num - 1] if nak2_num <= 27 else "Horse"
    key = (y1, y2) if (y1, y2) in YONI_COMPATIBILITY else (y2, y1)
    yoni_pts = YONI_COMPATIBILITY.get(key, 2)
    kutas["yoni"] = {"points": yoni_pts, "max": 4, "description": "Sexual/physical compatibility"}
    total += yoni_pts

    # 5. Graha Maitri (max 5)
    from api.core.ephemeris import SIGN_RULERS, PLANETARY_FRIENDSHIP
    r1 = SIGN_RULERS[sign1_idx].lower()
    r2 = SIGN_RULERS[sign2_idx].lower()
    if r1 == r2:
        maitri_pts = 5
    elif r1 in PLANETARY_FRIENDSHIP and r2 in PLANETARY_FRIENDSHIP.get(r1, {}).get("friends", []):
        maitri_pts = 4
    elif r1 in PLANETARY_FRIENDSHIP and r2 in PLANETARY_FRIENDSHIP.get(r1, {}).get("neutral", []):
        maitri_pts = 2
    else:
        maitri_pts = 0
    kutas["graha_maitri"] = {"points": maitri_pts, "max": 5, "description": "Planetary friendship"}
    total += maitri_pts

    # 6. Gana (max 6)
    g1 = NAKSHATRA_GANAS[nak1_num - 1] if nak1_num <= 27 else "Deva"
    g2 = NAKSHATRA_GANAS[nak2_num - 1] if nak2_num <= 27 else "Deva"
    if g1 == g2:
        gana_pts = 6
    elif {g1, g2} == {"Deva", "Manushya"}:
        gana_pts = 3
    elif {g1, g2} == {"Manushya", "Rakshasa"}:
        gana_pts = 1
    else:
        gana_pts = 0
    kutas["gana"] = {"points": gana_pts, "max": 6, "description": "Temperament compatibility"}
    total += gana_pts

    # 7. Bhakoot (max 7)
    diff = abs(sign1_idx - sign2_idx)
    bad_combos = [1, 5, 7]  # 2-12, 6-8 patterns
    if diff in bad_combos or (12 - diff) in bad_combos:
        bhakoot_pts = 0
    else:
        bhakoot_pts = 7
    kutas["bhakoot"] = {"points": bhakoot_pts, "max": 7, "description": "Moon sign compatibility"}
    total += bhakoot_pts

    # 8. Nadi (max 8)
    n1 = NAKSHATRA_NADI[nak1_num - 1] if nak1_num <= 27 else "Aadi"
    n2 = NAKSHATRA_NADI[nak2_num - 1] if nak2_num <= 27 else "Aadi"
    nadi_pts = 0 if n1 == n2 else 8
    kutas["nadi"] = {"points": nadi_pts, "max": 8, "description": "Health/genetic compatibility"}
    total += nadi_pts

    # Doshas
    doshas = []
    if bhakoot_pts == 0:
        doshas.append({"name": "Bhakoot Dosha", "severity": "High",
                       "description": "6-8 or 2-12 Moon sign combination."})
    if nadi_pts == 0:
        doshas.append({"name": "Nadi Dosha", "severity": "Very High",
                       "description": "Same Nadi. Cancellations may apply."})

    # Assessment
    if total >= 26:
        assessment = "Excellent"
    elif total >= 21:
        assessment = "Very Good"
    elif total >= 18:
        assessment = "Good"
    elif total >= 14:
        assessment = "Average"
    else:
        assessment = "Below Average"

    return {
        "total_points": total, "max_points": 36, "assessment": assessment,
        "kutas": kutas, "doshas": doshas,
        "person1_nakshatra": nak1_name, "person2_nakshatra": nak2_name,
        "person1_moon_sign": SIGNS[sign1_idx], "person2_moon_sign": SIGNS[sign2_idx],
    }


def get_synastry_aspects(
    chart1_positions: Dict[str, Dict],
    chart2_positions: Dict[str, Dict],
    orb_settings: Dict = None,
) -> List[Dict]:
    """Calculate cross-chart aspects between two natal charts."""
    from api.core.calculations import ASPECT_DEFINITIONS
    defs = dict(ASPECT_DEFINITIONS)
    aspects = []
    for n1, p1 in chart1_positions.items():
        for n2, p2 in chart2_positions.items():
            diff = angular_difference(p1["longitude"], p2["longitude"])
            for asp_name, asp_data in defs.items():
                orb = abs(diff - asp_data["angle"])
                if orb <= asp_data["orb"]:
                    strength = round((1 - orb / asp_data["orb"]) * 100, 1)
                    aspects.append({
                        "person1_planet": n1, "person2_planet": n2,
                        "aspect_name": asp_name, "aspect_angle": asp_data["angle"],
                        "actual_angle": round(diff, 4), "orb": round(orb, 4),
                        "strength": strength,
                    })
    aspects.sort(key=lambda x: x["orb"])
    return aspects
