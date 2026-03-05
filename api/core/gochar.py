from typing import Dict, Any
from api.core.ephemeris import SIGNS

# Standard brief Gochar effects (From Natal Moon)
GOCHAR_EFFECTS = {
    "sun": {
        3: "Favorable: Courage, success, health",
        6: "Favorable: Victory over enemies, success in efforts",
        10: "Favorable: Career advancement, success in endeavors",
        11: "Favorable: Financial gains, fulfillment of desires"
    },
    "moon": {
        1: "Favorable: Good food, happiness, comfort",
        3: "Favorable: Good health, gains, meeting friends",
        6: "Favorable: Financial gains, comfort",
        7: "Favorable: Happiness, gains in partnership",
        10: "Favorable: Success, good deeds",
        11: "Favorable: Financial gains, fulfillment of desires"
    },
    "mars": {
        3: "Favorable: Courage, victory, good health",
        6: "Favorable: Success, overcoming obstacles",
        11: "Favorable: Unexpected gains, financial success"
    },
    "mercury": {
        2: "Favorable: Financial gains, good speech",
        4: "Favorable: Family happiness, comforts",
        6: "Favorable: Success in education or disputes",
        8: "Favorable: Unexpected gains, good health",
        10: "Favorable: Career success, intellectual growth",
        11: "Favorable: Financial gains, fulfillment of desires"
    },
    "jupiter": {
        2: "Favorable: Wealth, family expansion, good speech",
        5: "Favorable: Birth of child, divine grace, higher learning",
        7: "Favorable: Marriage prospects, gains from partnership",
        9: "Favorable: Spiritual progress, long travel, luck",
        11: "Favorable: Overall success, massive financial gains"
    },
    "venus": {
        1: "Favorable: Enjoyment, comforts",
        2: "Favorable: Wealth, good food",
        3: "Favorable: Prosperity, good relations",
        4: "Favorable: Vehicles, home comforts",
        5: "Favorable: Romance, children, investments",
        8: "Favorable: Unexpected material gains",
        9: "Favorable: Auspicious events, fortune",
        11: "Favorable: Financial gains, social success",
        12: "Favorable: Expenditures on luxuries, bed comforts"
    },
    "saturn": {
        3: "Favorable: Immense courage, success through effort",
        6: "Favorable: Crushing enemies, success in competition",
        11: "Favorable: Steady financial gains, fulfilling ambitions"
    },
    "rahu": {
        3: "Favorable: Boldness, success, travels",
        6: "Favorable: Victory over enemies",
        11: "Favorable: Material success, fulfillment of desires"
    },
    "ketu": {
        3: "Favorable: Courage, success, spiritual growth",
        6: "Favorable: Overcoming hurdles",
        11: "Favorable: Good financial gains"
    }
}

def get_relative_house(transit_sign: str, natal_moon_sign: str) -> int:
    try:
        t_idx = SIGNS.index(transit_sign)
        m_idx = SIGNS.index(natal_moon_sign)
        return (t_idx - m_idx) % 12 + 1
    except ValueError:
        return 1

def analyze_gochar(natal_positions: Dict, transit_positions: Dict) -> Dict[str, Any]:
    """Analyze current transits relative to natal Moon (Gochar)."""
    if "moon" not in natal_positions:
        return {"error": "Natal Moon position required for Gochar."}
        
    natal_moon_sign = natal_positions["moon"].get("sign")
    if not natal_moon_sign:
        return {"error": "Natal Moon sign not found."}
        
    report = {
        "natal_moon_sign": natal_moon_sign,
        "transits": []
    }
    
    for name, t_pos in transit_positions.items():
        if name in ["mean_apog", "oscu_apog", "chiron"]:
            continue
            
        t_sign = t_pos.get("sign")
        if not t_sign:
            continue
            
        house_from_moon = get_relative_house(t_sign, natal_moon_sign)
        
        # Check standard interpretations
        effect = GOCHAR_EFFECTS.get(name, {}).get(house_from_moon)
        is_favorable = effect is not None
        if not effect:
            if name == "saturn" and house_from_moon in [12, 1, 2]:
                effect = "Challenging: Sade Sati phase. Delays, hard work, mental stress."
            elif name == "jupiter" and house_from_moon in [3, 4, 6, 8, 10, 12]:
                effect = "Challenging: Lack of peace, financial hurdles, or health issues."
            elif name == "mars" and house_from_moon in [1, 2, 4, 5, 7, 8, 9, 10, 12]:
                effect = "Challenging: Aggression, quarrels, impulsiveness."
            else:
                effect = "Neutral or mixed results. Requires effort and patience."
                
        # Also check if transiting over natal planets
        conjunct_natal = []
        for n_name, n_pos in natal_positions.items():
            if n_pos.get("sign") == t_sign:
                conjunct_natal.append(n_name.title())
                
        conjunction_text = f"Transiting over natal {', '.join(conjunct_natal)}." if conjunct_natal else ""
        
        report["transits"].append({
            "planet": name.title(),
            "transit_sign": t_sign,
            "house_from_moon": house_from_moon,
            "is_favorable": is_favorable,
            "effect_summary": effect,
            "conjunction_notes": conjunction_text
        })
        
    return report
