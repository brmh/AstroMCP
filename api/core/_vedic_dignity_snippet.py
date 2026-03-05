from api.core.ephemeris import EXALTATION, DEBILITATION, MOOLATRIKONA, PLANETARY_FRIENDSHIP, SIGN_RULERS, SIGNS

def get_vedic_dignity(planet: str, sign: str) -> str:
    """Calculate the Vedic dignity of a planet in a sign."""
    if planet not in PLANETARY_FRIENDSHIP and planet not in ["rahu", "ketu"]:
        return "Neutral"
    
    # Exaltation
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return "Exalted"
    
    # Debilitation
    if planet in DEBILITATION and DEBILITATION[planet][0] == sign:
        return "Debilitated"
        
    # Moolatrikona
    if planet in MOOLATRIKONA and MOOLATRIKONA[planet][0] == sign:
        return "Moolatrikona"
        
    # Own Sign (Domicile)
    sign_idx = SIGNS.index(sign)
    if SIGN_RULERS[sign_idx].lower() == planet:
        return "Own Sign"
        
    # Friend / Enemy / Neutral
    ruler = SIGN_RULERS[sign_idx].lower()
    if planet in PLANETARY_FRIENDSHIP:
        if ruler in PLANETARY_FRIENDSHIP[planet]["friends"]:
            return "Friendly"
        elif ruler in PLANETARY_FRIENDSHIP[planet]["enemies"]:
            return "Enemy"
            
    return "Neutral"
