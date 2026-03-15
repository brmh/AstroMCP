"""
Vedic Aspects (Drishti) Calculation Engine
==========================================
Implements all three classical Drishti systems from BPHS:
1. Graha Drishti (Planetary Aspects — Parashari)
2. Sphuta Drishti (Degree-Based Aspect Strength)
3. Rashi Drishti (Sign Aspects — Jaimini)

Plus: Conjunctions, Mutual Aspects, Drik Bala, and Interpretation.

Based on: Brihat Parashara Hora Shastra, Phaladeepika, Uttara Kalamrita
"""

from typing import List, Dict, Optional, Any
import math

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS & DATA TABLES
# ═══════════════════════════════════════════════════════════════════════════

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_TYPES = {
    "Aries": "movable", "Taurus": "fixed", "Gemini": "dual",
    "Cancer": "movable", "Leo": "fixed", "Virgo": "dual",
    "Libra": "movable", "Scorpio": "fixed", "Sagittarius": "dual",
    "Capricorn": "movable", "Aquarius": "fixed", "Pisces": "dual",
}

# Planet significations for interpretation
PLANET_SIGNIFICATIONS = {
    "sun":     {"nature": "mild_malefic", "emoji": "☀️", "name": "Surya",
                "themes": "authority, father, soul, vitality, career, fame"},
    "moon":    {"nature": "benefic", "emoji": "🌙", "name": "Chandra",
                "themes": "mind, mother, emotions, public, nourishment"},
    "mars":    {"nature": "malefic", "emoji": "♂", "name": "Mangala",
                "themes": "energy, courage, aggression, property, siblings"},
    "mercury": {"nature": "benefic", "emoji": "☿", "name": "Budha",
                "themes": "intellect, communication, commerce, writing"},
    "jupiter": {"nature": "benefic", "emoji": "♃", "name": "Guru",
                "themes": "wisdom, dharma, children, fortune, expansion"},
    "venus":   {"nature": "benefic", "emoji": "♀", "name": "Shukra",
                "themes": "love, beauty, luxury, arts, marriage, vehicles"},
    "saturn":  {"nature": "malefic", "emoji": "♄", "name": "Shani",
                "themes": "karma, discipline, delays, longevity, hard work"},
    "rahu":    {"nature": "malefic", "emoji": "☊", "name": "Rahu",
                "themes": "obsession, illusion, foreign, technology, amplification"},
    "ketu":    {"nature": "malefic", "emoji": "☋", "name": "Ketu",
                "themes": "spirituality, liberation, detachment, mysticism"},
}

# ── Graha Drishti Rules (BPHS Ch.9 v3-7) ────────────────────────────────
# Key = planet name, Value = list of house offsets (counted from planet position)
# Every planet has 7th. Mars adds 4,8. Jupiter adds 5,9. Saturn adds 3,10.
GRAHA_DRISHTI = {
    "sun":     [7],
    "moon":    [7],
    "mars":    [4, 7, 8],
    "mercury": [7],
    "jupiter": [5, 7, 9],
    "venus":   [7],
    "saturn":  [3, 7, 10],
    "rahu":    [5, 7, 9],   # Jupiter-like (most widely used modern practice)
    "ketu":    [7],          # Conservative: 7th only
}

# ── Pada (Quarter) Strength System (BPHS Ch.9) ──────────────────────────
# For standard planets (Sun, Moon, Mercury, Venus) — partial aspect strengths
PADA_STRENGTH = {
    3: 0.25,   # 1/4 pada
    4: 0.75,   # 3/4 pada
    5: 0.50,   # 2/4 pada
    7: 1.00,   # 4/4 pada (full) — all planets
    8: 0.75,   # 3/4 pada
    9: 0.50,   # 2/4 pada
    10: 0.25,  # 1/4 pada
}

# Special aspect overrides — these become FULL (1.0) instead of partial
SPECIAL_OVERRIDES = {
    "mars":    {4: 1.0, 8: 1.0},
    "jupiter": {5: 1.0, 9: 1.0},
    "saturn":  {3: 1.0, 10: 1.0},
}

# ── Rashi Drishti (Jaimini Sign Aspects) ─────────────────────────────────
RASHI_DRISHTI = {
    "Aries":       ["Leo", "Scorpio", "Aquarius"],
    "Taurus":      ["Cancer", "Libra", "Capricorn"],
    "Gemini":      ["Virgo", "Sagittarius", "Pisces"],
    "Cancer":      ["Scorpio", "Aquarius", "Taurus"],
    "Leo":         ["Libra", "Capricorn", "Aries"],
    "Virgo":       ["Gemini", "Sagittarius", "Pisces"],
    "Libra":       ["Aquarius", "Taurus", "Leo"],
    "Scorpio":     ["Capricorn", "Aries", "Cancer"],
    "Sagittarius": ["Gemini", "Virgo", "Pisces"],
    "Capricorn":   ["Taurus", "Leo", "Scorpio"],
    "Aquarius":    ["Aries", "Cancer", "Libra"],
    "Pisces":      ["Gemini", "Virgo", "Sagittarius"],
}

# ── House Significations (for interpretation) ───────────────────────────
HOUSE_THEMES = {
    1: "self, body, personality, health",
    2: "wealth, family, speech, food",
    3: "siblings, courage, communication, short travel",
    4: "home, mother, vehicles, happiness, education",
    5: "children, intelligence, romance, past merit (purva punya)",
    6: "enemies, debts, illness, service, litigation",
    7: "marriage, partnerships, business, public dealings",
    8: "death, transformation, longevity, occult, hidden matters",
    9: "fortune, father, dharma, higher learning, spirituality",
    10: "career, authority, status, karma, public life",
    11: "gains, friends, fulfillment of desires, income",
    12: "losses, foreign, spirituality, liberation, expenditure",
}

# ── Natural Benefics / Malefics ──────────────────────────────────────────
NATURAL_BENEFICS = {"jupiter", "venus", "mercury"}
NATURAL_MALEFICS = {"saturn", "mars", "sun", "rahu", "ketu"}

# ── Combustion Degrees (from Sun) ────────────────────────────────────────
COMBUSTION_DEGREES = {
    "moon": 12, "mars": 17, "mercury": 14, "jupiter": 11,
    "venus": 10, "saturn": 15,
}

# Yogakarakas by Lagna
YOGAKARAKAS = {
    "Aries": None, "Taurus": "saturn", "Gemini": None,
    "Cancer": "mars", "Leo": "mars", "Virgo": None,
    "Libra": "saturn", "Scorpio": None, "Sagittarius": None,
    "Capricorn": "venus", "Aquarius": "venus", "Pisces": None,
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def sign_index(sign_name: str) -> int:
    """Get 0-based index of a zodiac sign."""
    for i, s in enumerate(ZODIAC_SIGNS):
        if s.lower() == sign_name.lower():
            return i
    return 0

def house_from_sign(sign: str, lagna_sign: str) -> int:
    """Get house number (1-12) of a sign relative to the lagna (ascendant)."""
    return ((sign_index(sign) - sign_index(lagna_sign)) % 12) + 1

def sign_from_house(house: int, lagna_sign: str) -> str:
    """Get the zodiac sign corresponding to a house number."""
    idx = (sign_index(lagna_sign) + house - 1) % 12
    return ZODIAC_SIGNS[idx]

def normalize_planet_name(name: str) -> str:
    """Normalize planet names from various API formats."""
    n = name.lower().strip()
    aliases = {
        "true_node": "rahu", "mean_node": "rahu",
        "south_node": "ketu", "north_node": "rahu",
        "true node": "rahu", "mean node": "rahu",
    }
    return aliases.get(n, n)

def is_benefic(planet: str, moon_longitude: float = None) -> bool:
    """Check if planet is a natural benefic. Moon depends on phase."""
    p = normalize_planet_name(planet)
    if p == "moon" and moon_longitude is not None:
        # Waxing moon (Shukla Paksha) = benefic
        return True  # Simplified; precise phase needs Sun longitude
    return p in NATURAL_BENEFICS

def get_aspect_nature(planet: str) -> str:
    """Get the natural aspect quality of a planet."""
    p = normalize_planet_name(planet)
    info = PLANET_SIGNIFICATIONS.get(p, {})
    return info.get("nature", "neutral")


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM 1: GRAHA DRISHTI (Planetary Aspects — Parashari)
# ═══════════════════════════════════════════════════════════════════════════

def get_graha_drishti(planet_name: str, planet_house: int,
                      lagna_sign: str = "Aries") -> List[Dict]:
    """
    Calculate all houses aspected by a planet via Graha Drishti.
    Returns list of aspected houses with strength and type.
    """
    p = normalize_planet_name(planet_name)
    offsets = GRAHA_DRISHTI.get(p, [7])
    special_set = set(GRAHA_DRISHTI.get(p, [])) - {7}
    results = []

    for offset in offsets:
        # Count `offset` houses forward from planet (inclusive of planet's house = 1)
        # e.g. planet in house 1, offset=7 → house 7 ✓
        # e.g. planet in house 1, offset=4 → house 4 ✓
        target_house = ((planet_house - 1 + offset - 1) % 12) + 1
        target_sign = sign_from_house(target_house, lagna_sign)

        # Determine strength
        if offset == 7:
            strength = 1.0
            aspect_type = "standard_7th"
        elif offset in special_set:
            strength = 1.0
            aspect_type = f"special_{offset}th"
        else:
            strength = PADA_STRENGTH.get(offset, 0.25)
            aspect_type = f"partial_{offset}th"

        # Apply special overrides
        if p in SPECIAL_OVERRIDES and offset in SPECIAL_OVERRIDES[p]:
            strength = 1.0

        results.append({
            "aspected_house": target_house,
            "aspected_sign": target_sign,
            "aspect_offset": offset,
            "aspect_type": aspect_type,
            "strength_percent": int(strength * 100),
            "strength_pada": f"{int(strength * 4)}/4",
        })

    return results


def get_all_aspects_in_chart(planet_positions: Dict[str, int],
                             lagna_sign: str = "Aries") -> List[Dict]:
    """
    Calculate ALL Graha Drishti aspects for every planet in the chart.
    planet_positions: {"sun": 3, "moon": 7, ...} — house numbers
    """
    all_aspects = []
    for planet, house in planet_positions.items():
        p = normalize_planet_name(planet)
        if p not in GRAHA_DRISHTI:
            continue
        aspects = get_graha_drishti(p, house, lagna_sign)
        for asp in aspects:
            # Find planets receiving this aspect
            planets_in_target = [
                pname for pname, phouse in planet_positions.items()
                if phouse == asp["aspected_house"] and normalize_planet_name(pname) != p
            ]
            asp["aspecting_planet"] = p
            asp["from_house"] = house
            asp["from_sign"] = sign_from_house(house, lagna_sign)
            asp["planets_aspected"] = planets_in_target
            asp["nature"] = get_aspect_nature(p)
            all_aspects.append(asp)
    return all_aspects


def get_aspects_on_house(house: int, planet_positions: Dict[str, int],
                         lagna_sign: str = "Aries") -> List[Dict]:
    """Get all planets aspecting a specific house."""
    aspectors = []
    for planet, planet_house in planet_positions.items():
        p = normalize_planet_name(planet)
        aspects = get_graha_drishti(p, planet_house, lagna_sign)
        for asp in aspects:
            if asp["aspected_house"] == house:
                aspectors.append({
                    "planet": p,
                    "from_house": planet_house,
                    "from_sign": sign_from_house(planet_house, lagna_sign),
                    "aspect_type": asp["aspect_type"],
                    "strength_percent": asp["strength_percent"],
                    "nature": get_aspect_nature(p),
                })
    return aspectors


def get_aspects_on_planet(target_planet: str, planet_positions: Dict[str, int],
                          lagna_sign: str = "Aries") -> List[Dict]:
    """Get all planets aspecting a specific planet."""
    tp = normalize_planet_name(target_planet)
    target_house = planet_positions.get(tp)
    if target_house is None:
        return []
    aspectors = get_aspects_on_house(target_house, planet_positions, lagna_sign)
    # Remove self-aspect
    return [a for a in aspectors if normalize_planet_name(a["planet"]) != tp]


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM 2: SPHUTA DRISHTI (Degree-Based Aspect Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_sphuta_drishti(aspecting_planet: str,
                             asp_longitude: float,
                             aspected_longitude: float) -> float:
    """
    Calculate exact aspect strength in Virupas (0-60) using BPHS Ch.28.
    Based on longitudinal distance between two planets.
    60 Virupas = 1 Rupa = Full aspect.
    """
    angle = (aspected_longitude - asp_longitude) % 360

    # Full aspect points per planet
    full_angles = {
        "mars":    [90, 180, 210],    # 4th, 7th, 8th houses
        "jupiter": [120, 180, 240],   # 5th, 7th, 9th houses
        "saturn":  [60, 180, 270],    # 3rd, 7th, 10th houses
    }
    planet_fulls = full_angles.get(normalize_planet_name(aspecting_planet), [180])

    # Check for exact full aspect
    for fa in planet_fulls:
        if abs(angle - fa) < 1.0:
            return 60.0

    # BPHS interpolation between key points
    # Standard key points and their base virupas:
    key_points = [
        (30, 15), (60, 30), (90, 45), (120, 30),
        (150, 15), (180, 60), (210, 45), (240, 30),
        (270, 15), (300, 0), (330, 0), (360, 0),
    ]

    # Find surrounding key points and interpolate
    prev_angle, prev_vir = 0, 0
    for kp_angle, kp_vir in key_points:
        if angle <= kp_angle:
            # Linear interpolation
            if kp_angle == prev_angle:
                return float(kp_vir)
            ratio = (angle - prev_angle) / (kp_angle - prev_angle)
            virupas = prev_vir + ratio * (kp_vir - prev_vir)

            # Apply special planet overrides
            p = normalize_planet_name(aspecting_planet)
            if p in full_angles:
                for fa in full_angles[p]:
                    if prev_angle <= fa <= kp_angle:
                        # Boost toward 60 near special angle
                        dist = abs(angle - fa)
                        if dist < 30:
                            boost = (30 - dist) / 30 * (60 - virupas)
                            virupas += boost

            return min(60.0, max(0.0, virupas))

        prev_angle, prev_vir = kp_angle, kp_vir

    return 0.0


def calculate_all_sphuta_drishti(planet_longitudes: Dict[str, float]) -> List[Dict]:
    """
    Calculate Sphuta Drishti between all planet pairs.
    planet_longitudes: {"sun": 45.5, "moon": 120.3, ...}
    """
    results = []
    planets = list(planet_longitudes.keys())

    for i, p1 in enumerate(planets):
        for p2 in planets:
            if p1 == p2:
                continue
            virupas = calculate_sphuta_drishti(p1, planet_longitudes[p1], planet_longitudes[p2])
            if virupas > 5:  # Only include meaningful aspects
                angle = (planet_longitudes[p2] - planet_longitudes[p1]) % 360
                results.append({
                    "aspecting": normalize_planet_name(p1),
                    "aspected": normalize_planet_name(p2),
                    "angular_distance": round(angle, 2),
                    "virupas": round(virupas, 2),
                    "rupas": round(virupas / 60, 4),
                    "strength_percent": round(virupas / 60 * 100, 1),
                })

    return sorted(results, key=lambda x: x["virupas"], reverse=True)


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM 3: RASHI DRISHTI (Sign Aspects — Jaimini)
# ═══════════════════════════════════════════════════════════════════════════

def get_rashi_drishti(sign: str) -> List[str]:
    """Get all signs aspected by a given sign via Rashi Drishti (Jaimini)."""
    for s, targets in RASHI_DRISHTI.items():
        if s.lower() == sign.lower():
            return targets
    return []


def get_all_rashi_drishti(planet_signs: Dict[str, str],
                          lagna_sign: str = "Aries") -> List[Dict]:
    """
    Calculate all Rashi Drishti (sign-based aspects) for planets.
    planet_signs: {"sun": "Leo", "moon": "Cancer", ...}
    """
    results = []
    sign_to_planets = {}
    for planet, sign in planet_signs.items():
        p = normalize_planet_name(planet)
        if sign not in sign_to_planets:
            sign_to_planets[sign] = []
        sign_to_planets[sign].append(p)

    for planet, sign in planet_signs.items():
        p = normalize_planet_name(planet)
        aspected_signs = get_rashi_drishti(sign)
        for target_sign in aspected_signs:
            target_house = house_from_sign(target_sign, lagna_sign)
            planets_in_target = sign_to_planets.get(target_sign, [])
            results.append({
                "aspecting_planet": p,
                "from_sign": sign,
                "from_sign_type": SIGN_TYPES.get(sign, ""),
                "from_house": house_from_sign(sign, lagna_sign),
                "aspected_sign": target_sign,
                "aspected_sign_type": SIGN_TYPES.get(target_sign, ""),
                "aspected_house": target_house,
                "planets_aspected": planets_in_target,
                "strength": "full",
                "mutual": True,  # Rashi Drishti is always mutual
                "system": "jaimini_rashi_drishti",
            })

    return results


# ═══════════════════════════════════════════════════════════════════════════
# CONJUNCTIONS (Yuti)
# ═══════════════════════════════════════════════════════════════════════════

def find_conjunctions(planet_positions: Dict[str, int],
                      planet_longitudes: Dict[str, float] = None,
                      lagna_sign: str = "Aries") -> List[Dict]:
    """
    Find all planetary conjunctions (planets in same house).
    """
    house_groups = {}
    for planet, house in planet_positions.items():
        p = normalize_planet_name(planet)
        if house not in house_groups:
            house_groups[house] = []
        house_groups[house].append(p)

    conjunctions = []
    for house, planets in house_groups.items():
        if len(planets) < 2:
            continue

        # Check combustion
        combustion_info = []
        if planet_longitudes and "sun" in planets:
            sun_lon = planet_longitudes.get("sun", 0)
            for p in planets:
                if p != "sun" and p in COMBUSTION_DEGREES:
                    p_lon = planet_longitudes.get(p, 0)
                    dist = abs(sun_lon - p_lon)
                    if dist > 180:
                        dist = 360 - dist
                    if dist <= COMBUSTION_DEGREES[p]:
                        combustion_info.append({
                            "planet": p,
                            "distance_from_sun": round(dist, 2),
                            "combustion_limit": COMBUSTION_DEGREES[p],
                            "is_combust": True,
                        })

        # Classify conjunction nature
        all_benefic = all(is_benefic(p) for p in planets)
        all_malefic = all(not is_benefic(p) for p in planets)
        if all_benefic:
            quality = "highly_auspicious"
        elif all_malefic:
            quality = "severely_afflicted"
        else:
            quality = "mixed"

        conjunctions.append({
            "house": house,
            "sign": sign_from_house(house, lagna_sign),
            "planets": planets,
            "count": len(planets),
            "quality": quality,
            "combustion": combustion_info if combustion_info else None,
            "house_themes": HOUSE_THEMES.get(house, ""),
        })

    return conjunctions


# ═══════════════════════════════════════════════════════════════════════════
# MUTUAL ASPECTS
# ═══════════════════════════════════════════════════════════════════════════

def find_mutual_aspects(planet_positions: Dict[str, int],
                        lagna_sign: str = "Aries") -> List[Dict]:
    """
    Find all pairs of planets in mutual aspect (both seeing each other).
    """
    planets = list(planet_positions.keys())
    mutual = []
    seen = set()

    for i, p1 in enumerate(planets):
        p1n = normalize_planet_name(p1)
        h1 = planet_positions[p1]
        p1_aspects = {a["aspected_house"] for a in get_graha_drishti(p1n, h1, lagna_sign)}

        for j, p2 in enumerate(planets):
            if i >= j:
                continue
            p2n = normalize_planet_name(p2)
            h2 = planet_positions[p2]
            p2_aspects = {a["aspected_house"] for a in get_graha_drishti(p2n, h2, lagna_sign)}

            p1_sees_p2 = h2 in p1_aspects
            p2_sees_p1 = h1 in p2_aspects

            if p1_sees_p2 and p2_sees_p1:
                pair = tuple(sorted([p1n, p2n]))
                if pair in seen:
                    continue
                seen.add(pair)

                # Get aspect types
                p1_asp_type = "7th" if abs(h2 - h1) % 12 == 6 or abs(h1 - h2) % 12 == 6 else "special"
                p2_asp_type = "7th" if abs(h1 - h2) % 12 == 6 or abs(h2 - h1) % 12 == 6 else "special"

                offset_1_to_2 = ((h2 - h1) % 12) or 12
                offset_2_to_1 = ((h1 - h2) % 12) or 12

                # Strength lookup
                s1 = PADA_STRENGTH.get(offset_1_to_2, 0)
                if p1n in SPECIAL_OVERRIDES and offset_1_to_2 in SPECIAL_OVERRIDES[p1n]:
                    s1 = 1.0
                if offset_1_to_2 == 7:
                    s1 = 1.0

                s2 = PADA_STRENGTH.get(offset_2_to_1, 0)
                if p2n in SPECIAL_OVERRIDES and offset_2_to_1 in SPECIAL_OVERRIDES[p2n]:
                    s2 = 1.0
                if offset_2_to_1 == 7:
                    s2 = 1.0

                is_full_mutual = (s1 == 1.0 and s2 == 1.0)

                mutual.append({
                    "planet_1": p1n,
                    "planet_1_house": h1,
                    "planet_1_aspect_strength": int(s1 * 100),
                    "planet_2": p2n,
                    "planet_2_house": h2,
                    "planet_2_aspect_strength": int(s2 * 100),
                    "is_full_mutual": is_full_mutual,
                    "type": "full_mutual" if is_full_mutual else "mixed_mutual",
                    "significance": "Major planetary relationship (Sambandha)"
                        if is_full_mutual else "Partial mutual influence",
                })

    return mutual


# ═══════════════════════════════════════════════════════════════════════════
# DRIK BALA (Aspectual Strength in Shadbala)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_drik_bala(planet_longitudes: Dict[str, float]) -> Dict[str, Dict]:
    """
    Calculate Drik Bala (BPHS 27.19) for each planet.
    Positive = net benefic aspects; Negative = net malefic aspects.
    """
    results = {}

    for target_planet, target_lon in planet_longitudes.items():
        tp = normalize_planet_name(target_planet)
        benefic_total = 0.0
        malefic_total = 0.0
        details = []

        for asp_planet, asp_lon in planet_longitudes.items():
            ap = normalize_planet_name(asp_planet)
            if ap == tp:
                continue

            virupas = calculate_sphuta_drishti(ap, asp_lon, target_lon)
            if virupas < 1:
                continue

            quarter = virupas / 4.0

            if is_benefic(ap):
                benefic_total += quarter
                # Jupiter and Mercury get FULL addition (BPHS 27.19)
                if ap in ("jupiter", "mercury"):
                    benefic_total += virupas  # "Super add entire Drishti"
                details.append({
                    "from": ap, "virupas": round(virupas, 2),
                    "contribution": round(quarter, 2), "type": "benefic"
                })
            else:
                malefic_total += quarter
                details.append({
                    "from": ap, "virupas": round(virupas, 2),
                    "contribution": round(-quarter, 2), "type": "malefic"
                })

        net = benefic_total - malefic_total
        results[tp] = {
            "drik_bala_virupas": round(net, 2),
            "drik_bala_rupas": round(net / 60, 4),
            "benefic_contribution": round(benefic_total, 2),
            "malefic_contribution": round(malefic_total, 2),
            "net_balance": "benefic" if net > 0 else ("malefic" if net < 0 else "neutral"),
            "details": details,
        }

    return results


# ═══════════════════════════════════════════════════════════════════════════
# HOUSE ASPECT SUMMARY (Aspects on each house)
# ═══════════════════════════════════════════════════════════════════════════

def get_house_aspect_summary(planet_positions: Dict[str, int],
                             lagna_sign: str = "Aries") -> List[Dict]:
    """
    For each of the 12 houses, list all planets aspecting it and
    the net benefic/malefic balance.
    """
    summary = []
    for house in range(1, 13):
        aspectors = get_aspects_on_house(house, planet_positions, lagna_sign)
        occupants = [
            normalize_planet_name(p) for p, h in planet_positions.items()
            if h == house
        ]

        benefic_count = sum(1 for a in aspectors if a["nature"] in ("benefic",))
        malefic_count = sum(1 for a in aspectors if a["nature"] in ("malefic", "mild_malefic"))

        if benefic_count > malefic_count:
            net = "net_benefic"
        elif malefic_count > benefic_count:
            net = "net_malefic"
        elif len(aspectors) == 0:
            net = "unaspected"
        else:
            net = "balanced"

        summary.append({
            "house": house,
            "sign": sign_from_house(house, lagna_sign),
            "themes": HOUSE_THEMES.get(house, ""),
            "occupants": occupants,
            "aspected_by": aspectors,
            "aspect_count": len(aspectors),
            "benefic_aspects": benefic_count,
            "malefic_aspects": malefic_count,
            "net_influence": net,
        })

    return summary


# ═══════════════════════════════════════════════════════════════════════════
# MASTER FUNCTION: Complete Aspect Analysis
# ═══════════════════════════════════════════════════════════════════════════

def compute_full_aspects(chart_data: Dict) -> Dict[str, Any]:
    """
    Master function: takes a Kundli chart (from /vedic/kundli) and returns
    a complete Drishti analysis covering all three systems.

    Expected chart_data keys:
      - planets: {sun: {sign, house, full_degree, ...}, ...}
      - ascendant: {sign, ...}
    """
    planets_raw = chart_data.get("planets", {})
    ascendant = chart_data.get("ascendant", {})
    lagna_sign = ascendant.get("sign", "Aries")

    # Build lookup dicts
    planet_positions = {}  # planet → house number
    planet_signs = {}      # planet → sign name
    planet_longitudes = {} # planet → sidereal longitude

    for name, data in planets_raw.items():
        p = normalize_planet_name(name)
        if p in GRAHA_DRISHTI or p in ("rahu", "ketu"):
            if isinstance(data, dict):
                h = data.get("house")
                if h is None:
                    s = data.get("sign", "Aries")
                    h = house_from_sign(s, lagna_sign)
                planet_positions[p] = h
                planet_signs[p] = data.get("sign", sign_from_house(h, lagna_sign))
                lon = data.get("full_degree") or data.get("longitude") or data.get("sidereal_degree", 0)
                planet_longitudes[p] = float(lon) if lon else 0.0

    if not planet_positions:
        return {"error": "No planet positions found in chart data"}

    # ── Compute all systems ──
    graha_aspects = get_all_aspects_in_chart(planet_positions, lagna_sign)
    rashi_aspects = get_all_rashi_drishti(planet_signs, lagna_sign)
    sphuta_aspects = calculate_all_sphuta_drishti(planet_longitudes) if planet_longitudes else []
    conjunctions = find_conjunctions(planet_positions, planet_longitudes, lagna_sign)
    mutual_aspects = find_mutual_aspects(planet_positions, lagna_sign)
    drik_bala = calculate_drik_bala(planet_longitudes) if planet_longitudes else {}
    house_summary = get_house_aspect_summary(planet_positions, lagna_sign)

    # ── Planet-by-planet aspect detail ──
    planet_aspect_details = {}
    for p in planet_positions:
        aspects_cast = get_graha_drishti(p, planet_positions[p], lagna_sign)
        aspects_received = get_aspects_on_planet(p, planet_positions, lagna_sign)

        # Enrich cast aspects with planets in target houses
        for asp in aspects_cast:
            asp["planets_in_target"] = [
                pn for pn, ph in planet_positions.items()
                if ph == asp["aspected_house"] and pn != p
            ]
            asp["house_themes"] = HOUSE_THEMES.get(asp["aspected_house"], "")

        planet_aspect_details[p] = {
            "house": planet_positions[p],
            "sign": planet_signs.get(p, ""),
            "longitude": round(planet_longitudes.get(p, 0), 2),
            "nature": get_aspect_nature(p),
            "significations": PLANET_SIGNIFICATIONS.get(p, {}).get("themes", ""),
            "aspects_cast": aspects_cast,
            "aspects_cast_count": len(aspects_cast),
            "aspects_received": aspects_received,
            "aspects_received_count": len(aspects_received),
            "drik_bala": drik_bala.get(p, {}),
        }

    # ── Statistics ──
    total_aspects = len(graha_aspects)
    total_benefic = sum(1 for a in graha_aspects if a["nature"] in ("benefic",))
    total_malefic = sum(1 for a in graha_aspects if a["nature"] in ("malefic", "mild_malefic"))

    # ── Yogakaraka check ──
    yk = YOGAKARAKAS.get(lagna_sign)
    yogakaraka_info = None
    if yk and yk in planet_positions:
        yk_aspects = get_graha_drishti(yk, planet_positions[yk], lagna_sign)
        yogakaraka_info = {
            "planet": yk,
            "house": planet_positions[yk],
            "sign": planet_signs.get(yk, ""),
            "aspects": yk_aspects,
            "significance": f"{yk.capitalize()} is the Yogakaraka for {lagna_sign} Lagna — "
                           f"its aspects are extremely powerful benefic influences."
        }

    return {
        "lagna": lagna_sign,
        "system_1_graha_drishti": {
            "description": "Planetary Aspects (Parashari) — BPHS Ch.9",
            "total_aspects": total_aspects,
            "benefic_aspects": total_benefic,
            "malefic_aspects": total_malefic,
            "aspects": graha_aspects,
        },
        "system_2_sphuta_drishti": {
            "description": "Degree-Based Aspect Strength — BPHS Ch.28",
            "unit": "Virupas (0-60, where 60 = 1 Rupa = Full Aspect)",
            "aspects": sphuta_aspects[:30],  # Top 30 strongest
        },
        "system_3_rashi_drishti": {
            "description": "Sign Aspects (Jaimini) — Always full & mutual",
            "total_sign_aspects": len(rashi_aspects),
            "aspects": rashi_aspects,
        },
        "conjunctions": {
            "description": "Planets in same house (Yuti/Samagama)",
            "count": len(conjunctions),
            "groups": conjunctions,
        },
        "mutual_aspects": {
            "description": "Planets aspecting each other simultaneously (Paraspar Drishti)",
            "count": len(mutual_aspects),
            "pairs": mutual_aspects,
        },
        "drik_bala": {
            "description": "Aspectual Strength in Shadbala — BPHS Ch.27 v19",
            "planets": drik_bala,
        },
        "house_summary": {
            "description": "Aspect influence on all 12 houses",
            "houses": house_summary,
        },
        "planet_details": planet_aspect_details,
        "yogakaraka": yogakaraka_info,
        "meta": {
            "graha_drishti_rules": {
                p: offsets for p, offsets in GRAHA_DRISHTI.items()
            },
            "rahu_ketu_config": "Rahu: Jupiter-like (5th, 7th, 9th). Ketu: 7th only.",
            "reference": "BPHS (Brihat Parashara Hora Shastra), Phaladeepika, Uttara Kalamrita",
        },
    }
