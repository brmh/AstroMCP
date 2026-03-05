"""
Validation Script — Tests core astrological calculations against known data.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import swisseph as swe
from api.core.ephemeris import (
    get_julian_day, longitude_to_sign, longitude_to_nakshatra,
    get_ayanamsa_value, SIGNS, init_ephemeris,
)
from api.core.calculations import (
    get_all_planet_positions, get_houses, get_aspects, get_moon_phase,
    get_solar_eclipses, get_lunar_eclipses, assign_houses_to_planets,
)
from api.core.panchang import get_panchang
from api.core.dashas import get_current_dasha, get_mahadashas
from api.core.yogas import detect_all_yogas

PASS = 0
FAIL = 0


def check(test_name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {test_name}")
    else:
        FAIL += 1
        print(f"  ✗ {test_name} — {detail}")


def test_julian_day():
    print("\n── Test 1: Julian Day Conversion ──")
    # J2000.0 epoch: Jan 1, 2000, 12:00 TT ≈ 2451545.0
    jd = get_julian_day(2000, 1, 1, 12, 0, 0, "UTC")
    check("J2000.0 epoch", abs(jd - 2451545.0) < 0.01, f"Got {jd}")

    # Known date: March 6, 2026
    jd2 = get_julian_day(2026, 3, 6, 0, 0, 0, "UTC")
    check("Mar 6 2026 is valid JD", jd2 > 2460000, f"Got {jd2}")


def test_gandhi_chart():
    print("\n── Test 2: Mahatma Gandhi Natal Chart ──")
    # Born: October 2, 1869, 07:33 AM, Porbandar, India (21.6°N, 69.6°E)
    jd = get_julian_day(1869, 10, 2, 7, 33, 0, "Asia/Kolkata")
    check("Gandhi JD calculated", jd > 0, f"JD = {jd}")

    positions = get_all_planet_positions(jd, zodiac_type="TROPICAL")
    sun_sign = positions.get("sun", {}).get("sign", "")
    moon_sign = positions.get("moon", {}).get("sign", "")
    check("Gandhi Sun in Virgo/Libra (Tropical)", sun_sign in ("Virgo", "Libra"), f"Got {sun_sign}")
    check("Gandhi Moon in Leo (Tropical)", moon_sign == "Leo", f"Got {moon_sign}")

    houses = get_houses(jd, 21.6, 69.6, "PLACIDUS", "TROPICAL")
    asc_sign, _, _ = longitude_to_sign(houses["ascendant"])
    check("Gandhi Ascendant in Libra", asc_sign == "Libra", f"Got {asc_sign}")


def test_moon_phase():
    print("\n── Test 3: Moon Phase ──")
    # Test with a known full moon (approx): Feb 12, 2025
    jd = get_julian_day(2025, 2, 12, 12, 0, 0, "UTC")
    phase = get_moon_phase(jd)
    check("Moon phase has name", "phase_name" in phase)
    check("Illumination in range", 0 <= phase.get("illumination_percent", -1) <= 100)
    print(f"    Phase: {phase.get('phase_name')}, Illumination: {phase.get('illumination_percent')}%")


def test_eclipses():
    print("\n── Test 4: Eclipse Detection ──")
    start_jd = get_julian_day(2024, 1, 1, 0, 0, 0, "UTC")
    end_jd = get_julian_day(2025, 1, 1, 0, 0, 0, "UTC")
    solar = get_solar_eclipses(start_jd, end_jd)
    lunar = get_lunar_eclipses(start_jd, end_jd)
    check("Detected solar eclipses in 2024", len(solar) >= 1, f"Found {len(solar)}")
    check("Detected lunar eclipses in 2024", len(lunar) >= 1, f"Found {len(lunar)}")


def test_panchang():
    print("\n── Test 5: Panchang ──")
    jd = get_julian_day(2026, 3, 6, 6, 0, 0, "Asia/Kolkata")
    panchang = get_panchang(jd, 28.6139, 77.209, "Asia/Kolkata")
    check("Panchang has tithi", "tithi" in panchang)
    check("Panchang has vara", "vara" in panchang)
    check("Panchang has nakshatra", "nakshatra" in panchang)
    check("Panchang has yoga", "yoga" in panchang)
    check("Panchang has karana", "karana" in panchang)
    print(f"    Tithi: {panchang['tithi']['name']}, Nakshatra: {panchang['nakshatra']['name']}")
    print(f"    Vara: {panchang['vara']['name']}, Yoga: {panchang['yoga']['name']}")


def test_dashas():
    print("\n── Test 6: Vimshottari Dasha ──")
    jd = get_julian_day(1990, 3, 15, 14, 30, 0, "Asia/Kolkata")
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa="LAHIRI")
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    ayanamsa_val = get_ayanamsa_value(jd, "LAHIRI")
    moon_sid = (moon_lon - ayanamsa_val) % 360

    mahadashas = get_mahadashas(jd, moon_sid)
    check("Got 9 mahadashas", len(mahadashas) >= 9, f"Got {len(mahadashas)}")

    current = get_current_dasha(jd, moon_sid)
    check("Current dasha has mahadasha", "mahadasha" in current)
    if "mahadasha" in current:
        print(f"    Current Mahadasha: {current['mahadasha']['lord']}")
        if "antardasha" in current:
            print(f"    Current Antardasha: {current['antardasha']['lord']}")


def test_yogas():
    print("\n── Test 7: Yoga Detection ──")
    jd = get_julian_day(1990, 3, 15, 14, 30, 0, "Asia/Kolkata")
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa="LAHIRI")
    houses = get_houses(jd, 28.6139, 77.209, "WHOLE_SIGN", "SIDEREAL", "LAHIRI")
    positions = assign_houses_to_planets(positions, houses)
    yogas = detect_all_yogas(positions, houses)
    check("Detected at least one yoga", len(yogas) >= 1, f"Found {len(yogas)} yogas")
    for y in yogas[:5]:
        print(f"    {y['yoga_name']} ({y['category']})")


def test_sign_functions():
    print("\n── Test 8: Sign/Nakshatra Functions ──")
    sign, idx, deg = longitude_to_sign(45.5)
    check("45.5° is Taurus", sign == "Taurus", f"Got {sign}")
    check("Degree in sign ~15.5", abs(deg - 15.5) < 0.1, f"Got {deg}")

    nak, num, pada, lord, deity = longitude_to_nakshatra(23.0)
    check("Nakshatra calculated", nak != "", f"Got '{nak}'")
    check("Pada is 1-4", 1 <= pada <= 4, f"Got {pada}")


def main():
    print("=" * 60)
    print("AstroConsultant — Calculation Validation Tests")
    print("=" * 60)

    init_ephemeris()

    test_julian_day()
    test_gandhi_chart()
    test_moon_phase()
    test_eclipses()
    test_panchang()
    test_dashas()
    test_yogas()
    test_sign_functions()

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
    print("=" * 60)

    swe.close()
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
