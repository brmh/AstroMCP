"""
Western Essential Dignities & Reception
Domicile, Exaltation, Detriment, Fall, Term, Face, Reception.
"""

from typing import Dict, List, Any
from api.core.ephemeris import SIGNS, SIGN_RULERS, EXALTATION, DEBILITATION, MOOLATRIKONA


# Detriment = opposite of domicile
DETRIMENT = {
    "sun": "Aquarius", "moon": "Capricorn", "mercury": "Sagittarius",
    "venus": "Aries", "mars": "Taurus", "jupiter": "Gemini", "saturn": "Cancer",
}

# Fall = opposite of exaltation
FALL = {
    "sun": "Libra", "moon": "Scorpio", "mercury": "Pisces",
    "venus": "Virgo", "mars": "Cancer", "jupiter": "Capricorn", "saturn": "Aries",
}

# Domicile
DOMICILE = {
    "sun": ["Leo"], "moon": ["Cancer"],
    "mercury": ["Gemini", "Virgo"], "venus": ["Taurus", "Libra"],
    "mars": ["Aries", "Scorpio"], "jupiter": ["Sagittarius", "Pisces"],
    "saturn": ["Capricorn", "Aquarius"],
}

# Egyptian terms (Ptolemaic bounds)
TERMS = {
    "Aries": [("jupiter", 0, 6), ("venus", 6, 12), ("mercury", 12, 20), ("mars", 20, 25), ("saturn", 25, 30)],
    "Taurus": [("venus", 0, 8), ("mercury", 8, 14), ("jupiter", 14, 22), ("saturn", 22, 27), ("mars", 27, 30)],
    "Gemini": [("mercury", 0, 6), ("jupiter", 6, 12), ("venus", 12, 17), ("mars", 17, 24), ("saturn", 24, 30)],
    "Cancer": [("mars", 0, 7), ("venus", 7, 13), ("mercury", 13, 19), ("jupiter", 19, 26), ("saturn", 26, 30)],
    "Leo": [("jupiter", 0, 6), ("venus", 6, 11), ("saturn", 11, 18), ("mercury", 18, 24), ("mars", 24, 30)],
    "Virgo": [("mercury", 0, 7), ("venus", 7, 17), ("jupiter", 17, 21), ("mars", 21, 28), ("saturn", 28, 30)],
    "Libra": [("saturn", 0, 6), ("mercury", 6, 14), ("jupiter", 14, 21), ("venus", 21, 28), ("mars", 28, 30)],
    "Scorpio": [("mars", 0, 7), ("venus", 7, 11), ("mercury", 11, 19), ("jupiter", 19, 24), ("saturn", 24, 30)],
    "Sagittarius": [("jupiter", 0, 12), ("venus", 12, 17), ("mercury", 17, 21), ("saturn", 21, 26), ("mars", 26, 30)],
    "Capricorn": [("mercury", 0, 7), ("jupiter", 7, 14), ("venus", 14, 22), ("saturn", 22, 26), ("mars", 26, 30)],
    "Aquarius": [("mercury", 0, 7), ("venus", 7, 13), ("jupiter", 13, 20), ("mars", 20, 25), ("saturn", 25, 30)],
    "Pisces": [("venus", 0, 12), ("jupiter", 12, 16), ("mercury", 16, 19), ("mars", 19, 28), ("saturn", 28, 30)],
}


def get_basic_dignity(planet: str, sign: str) -> str:
    """Return a simple string summarizing the basic dignity of a planet in a sign."""
    p = planet.lower()
    if p in EXALTATION and EXALTATION[p][0] == sign:
        return "Exalted"
    if p in MOOLATRIKONA and MOOLATRIKONA[p][0] == sign:
        return "Moolatrikona"
    if p in DOMICILE and sign in DOMICILE[p]:
        return "Own Sign"
    if p in FALL and sign == FALL[p]:
        return "Debilitated (Fall)"
    if p in DETRIMENT and sign == DETRIMENT[p]:
        return "Detriment"
    return "Neutral/Enemy/Friend (requires deeper dignity check)"

def get_essential_dignities(positions: Dict) -> Dict[str, Dict]:
    """Calculate essential dignities for all planets."""
    results = {}
    skip = {"mean_node", "true_node", "ketu", "mean_apog", "oscu_apog", "chiron"}

    for name, pos in positions.items():
        if name in skip:
            continue
        sign = pos.get("sign", "")
        deg = pos.get("degree_in_sign", 0)
        dignities = []
        debilities = []

        # Domicile
        if name in DOMICILE and sign in DOMICILE[name]:
            dignities.append("Domicile (+5)")

        # Exaltation
        if name in EXALTATION and EXALTATION[name][0] == sign:
            dignities.append("Exaltation (+4)")

        # Moolatrikona
        if name in MOOLATRIKONA:
            mt_sign, mt_start, mt_end = MOOLATRIKONA[name]
            if sign == mt_sign and mt_start <= deg <= mt_end:
                dignities.append("Moolatrikona")

        # Detriment
        if name in DETRIMENT and sign == DETRIMENT[name]:
            debilities.append("Detriment (-5)")

        # Fall
        if name in FALL and sign == FALL[name]:
            debilities.append("Fall (-4)")

        # Term
        term_ruler = None
        if sign in TERMS:
            for ruler, start, end in TERMS[sign]:
                if start <= deg < end:
                    term_ruler = ruler
                    break
        if term_ruler == name:
            dignities.append("Own Term (+2)")

        # Face (Decan)
        decan = int(deg / 10)
        face_rulers_by_sign_element = {
            "Fire": ["mars", "sun", "venus"],
            "Earth": ["mercury", "moon", "saturn"],
            "Air": ["venus", "saturn", "mercury"],
            "Water": ["mars", "jupiter", "moon"],
        }
        from api.core.ephemeris import SIGN_ELEMENTS
        sign_idx = SIGNS.index(sign) if sign in SIGNS else 0
        element = SIGN_ELEMENTS[sign_idx]
        face_rulers = face_rulers_by_sign_element.get(element, [])
        if decan < len(face_rulers) and face_rulers[decan] == name:
            dignities.append("Own Face (+1)")

        # Peregrine (no essential dignity)
        is_peregrine = len(dignities) == 0 and len(debilities) == 0

        score = 0
        for d in dignities:
            if "+5" in d: score += 5
            elif "+4" in d: score += 4
            elif "+2" in d: score += 2
            elif "+1" in d: score += 1
        for d in debilities:
            if "-5" in d: score -= 5
            elif "-4" in d: score -= 4

        results[name] = {
            "dignities": dignities, "debilities": debilities,
            "is_peregrine": is_peregrine, "dignity_score": score,
            "term_ruler": term_ruler,
        }

    return results


def check_mutual_reception(positions: Dict) -> List[Dict]:
    """Check for mutual reception (two planets in each other's domicile signs)."""
    receptions = []
    planet_names = [n for n in positions if n not in {"mean_node", "true_node", "ketu", "mean_apog"}]

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]
            s1 = positions[p1].get("sign", "")
            s2 = positions[p2].get("sign", "")

            if p1 in DOMICILE and p2 in DOMICILE:
                if s1 in DOMICILE.get(p2, []) and s2 in DOMICILE.get(p1, []):
                    receptions.append({
                        "planet1": p1, "planet2": p2,
                        "type": "Mutual Reception by Domicile",
                        "sign1": s1, "sign2": s2,
                    })

    return receptions
