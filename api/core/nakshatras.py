from typing import Dict, Any
from api.core.ephemeris import NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_DEITIES, NAKSHATRA_GANAS

# Deep dive data for all 27 nakshatras
NAKSHATRA_DETAILS = {
    "Ashwini": {"symbol": "Horse's head", "animal": "Male Horse", "dosha": "Vata", "nature": "Light/Swift (Kshipra)", "purpose": "Dharma"},
    "Bharani": {"symbol": "Yoni (female organ)", "animal": "Male Elephant", "dosha": "Pitta", "nature": "Fierce/Severe (Ugra)", "purpose": "Artha"},
    "Krittika": {"symbol": "Razor, Axe, or Flame", "animal": "Female Sheep", "dosha": "Kapha", "nature": "Mixed (Mishra)", "purpose": "Kama"},
    "Rohini": {"symbol": "Chariot or Oxcart", "animal": "Male Serpent", "dosha": "Kapha", "nature": "Fixed/Steady (Dhruva)", "purpose": "Moksha"},
    "Mrigashira": {"symbol": "Deer's head", "animal": "Female Serpent", "dosha": "Pitta", "nature": "Soft/Mild (Mridu)", "purpose": "Moksha"},
    "Ardra": {"symbol": "Teardrop or Diamond", "animal": "Female Dog", "dosha": "Vata", "nature": "Fierce/Severe (Ugra)", "purpose": "Kama"},
    "Punarvasu": {"symbol": "Quiver of Arrows", "animal": "Female Cat", "dosha": "Vata", "nature": "Movable (Chara)", "purpose": "Artha"},
    "Pushya": {"symbol": "Cow's udder or Lotus", "animal": "Male Goat", "dosha": "Pitta", "nature": "Light/Swift (Kshipra)", "purpose": "Dharma"},
    "Ashlesha": {"symbol": "Coiled Serpent", "animal": "Male Cat", "dosha": "Kapha", "nature": "Sharp/Dreadful (Tikshna)", "purpose": "Dharma"},
    "Magha": {"symbol": "Royal Throne", "animal": "Male Rat", "dosha": "Kapha", "nature": "Fierce/Severe (Ugra)", "purpose": "Artha"},
    "Purva Phalguni": {"symbol": "Front legs of a bed/cot", "animal": "Female Rat", "dosha": "Pitta", "nature": "Fierce/Severe (Ugra)", "purpose": "Kama"},
    "Uttara Phalguni": {"symbol": "Back legs of a bed/cot", "animal": "Male Cow", "dosha": "Vata", "nature": "Fixed/Steady (Dhruva)", "purpose": "Moksha"},
    "Hasta": {"symbol": "Hand or Fist", "animal": "Female Buffalo", "dosha": "Vata", "nature": "Light/Swift (Kshipra)", "purpose": "Moksha"},
    "Chitra": {"symbol": "Pearl or Gem", "animal": "Female Tiger", "dosha": "Pitta", "nature": "Soft/Mild (Mridu)", "purpose": "Kama"},
    "Swati": {"symbol": "Shoot of plant or Sword", "animal": "Male Buffalo", "dosha": "Kapha", "nature": "Movable (Chara)", "purpose": "Artha"},
    "Vishakha": {"symbol": "Triumphal Arch or Potter's wheel", "animal": "Male Tiger", "dosha": "Kapha", "nature": "Mixed (Mishra)", "purpose": "Dharma"},
    "Anuradha": {"symbol": "Lotus or Staff", "animal": "Female Deer", "dosha": "Pitta", "nature": "Soft/Mild (Mridu)", "purpose": "Dharma"},
    "Jyeshtha": {"symbol": "Circular amulet or Umbrella", "animal": "Male Deer", "dosha": "Vata", "nature": "Sharp/Dreadful (Tikshna)", "purpose": "Artha"},
    "Mula": {"symbol": "Tied bunch of roots", "animal": "Male Dog", "dosha": "Vata", "nature": "Sharp/Dreadful (Tikshna)", "purpose": "Kama"},
    "Purva Ashadha": {"symbol": "Elephant's tusk or Winnowing basket", "animal": "Male Monkey", "dosha": "Pitta", "nature": "Fierce/Severe (Ugra)", "purpose": "Moksha"},
    "Uttara Ashadha": {"symbol": "Planks of a bed", "animal": "Female Mongoose", "dosha": "Kapha", "nature": "Fixed/Steady (Dhruva)", "purpose": "Moksha"},
    "Shravana": {"symbol": "Ear or Three footprints", "animal": "Female Monkey", "dosha": "Kapha", "nature": "Movable (Chara)", "purpose": "Artha"},
    "Dhanishta": {"symbol": "Drum or Flute", "animal": "Female Lion", "dosha": "Pitta", "nature": "Movable (Chara)", "purpose": "Dharma"},
    "Shatabhisha": {"symbol": "Empty circle or thousand flowers", "animal": "Female Horse", "dosha": "Vata", "nature": "Movable (Chara)", "purpose": "Dharma"},
    "Purva Bhadrapada": {"symbol": "Swords or two front legs of funeral cot", "animal": "Male Lion", "dosha": "Vata", "nature": "Fierce/Severe (Ugra)", "purpose": "Artha"},
    "Uttara Bhadrapada": {"symbol": "Twins or back legs of funeral cot", "animal": "Female Cow", "dosha": "Pitta", "nature": "Fixed/Steady (Dhruva)", "purpose": "Kama"},
    "Revati": {"symbol": "Fish or drum", "animal": "Female Elephant", "dosha": "Kapha", "nature": "Soft/Mild (Mridu)", "purpose": "Moksha"},
}

def get_nakshatra_info(nakshatra_number: int) -> Dict[str, Any]:
    """Retrieve detailed properties for a given nakshatra."""
    if not (1 <= nakshatra_number <= 27):
        return {"error": "Nakshatra number must be between 1 and 27."}
        
    idx = nakshatra_number - 1
    name = NAKSHATRAS[idx]
    details = NAKSHATRA_DETAILS.get(name, {})
    
    return {
        "number": nakshatra_number,
        "name": name,
        "lord": NAKSHATRA_LORDS[idx],
        "deity": NAKSHATRA_DEITIES[idx],
        "gana": NAKSHATRA_GANAS[idx],
        "symbol": details.get("symbol"),
        "animal": details.get("animal"),
        "dosha": details.get("dosha"),
        "nature": details.get("nature"),
        "purpose": details.get("purpose"),
    }
