"""
Muhurta (Auspicious Timing) Calculations
Evaluates quality of a given moment for various purposes.
"""

from typing import Dict, Any
from api.core.panchang import get_panchang

# Suitability tables for each purpose
# Higher score = more suitable. 0 = unsuitable.
TITHI_SUITABILITY = {
    "marriage": {2: 8, 3: 9, 5: 8, 7: 7, 10: 8, 11: 9, 12: 7, 13: 8},
    "travel": {2: 7, 3: 8, 5: 7, 6: 6, 7: 8, 10: 9, 11: 8, 12: 7, 13: 8},
    "business": {2: 7, 3: 8, 5: 8, 6: 7, 7: 7, 10: 8, 11: 9, 12: 7, 13: 8},
    "medical_surgery": {2: 6, 3: 7, 5: 6, 7: 8, 10: 7, 11: 8, 13: 7},
    "property_purchase": {2: 7, 3: 8, 5: 9, 7: 7, 10: 8, 11: 9, 12: 8, 13: 7},
    "education": {2: 7, 3: 8, 5: 9, 7: 8, 10: 7, 11: 8, 12: 7, 13: 8},
    "vehicle_purchase": {2: 7, 3: 8, 5: 7, 6: 6, 7: 7, 10: 8, 11: 9, 12: 7},
    "job_interview": {2: 7, 3: 8, 5: 8, 7: 7, 10: 9, 11: 8, 12: 7, 13: 8},
}

VARA_SUITABILITY = {
    "marriage": {"Monday": 8, "Wednesday": 7, "Thursday": 9, "Friday": 9},
    "travel": {"Monday": 7, "Wednesday": 8, "Thursday": 8, "Friday": 7, "Sunday": 7},
    "business": {"Monday": 7, "Wednesday": 9, "Thursday": 8, "Friday": 8},
    "medical_surgery": {"Tuesday": 6, "Saturday": 5, "Thursday": 7, "Monday": 7},
    "property_purchase": {"Thursday": 9, "Friday": 8, "Monday": 7, "Wednesday": 7},
    "education": {"Wednesday": 9, "Thursday": 8, "Monday": 7, "Friday": 7},
    "vehicle_purchase": {"Wednesday": 8, "Thursday": 7, "Friday": 8, "Monday": 7},
    "job_interview": {"Monday": 7, "Wednesday": 8, "Thursday": 9, "Friday": 7},
}

# Good nakshatras for general auspicious activities
GOOD_NAKSHATRAS = {
    "marriage": ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta", "Swati",
                  "Anuradha", "Mula", "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati"],
    "travel": ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Anuradha",
               "Shravana", "Dhanishta", "Revati"],
    "business": ["Ashwini", "Rohini", "Pushya", "Hasta", "Chitra", "Swati", "Shravana", "Revati"],
    "education": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                   "Chitra", "Swati", "Shravana", "Revati"],
}


def get_muhurta_quality(jd: float, latitude: float, longitude: float, purpose: str, timezone_str: str = "UTC") -> Dict[str, Any]:
    """
    Evaluate the auspiciousness of a given moment for a specific purpose.
    Returns a quality score (0-100) with detailed breakdown.
    """
    panchang = get_panchang(jd, latitude, longitude, timezone_str)
    scores = {}
    total_weight = 0

    # Tithi suitability (weight: 25)
    tithi_num = panchang["tithi"]["number"]
    tithi_table = TITHI_SUITABILITY.get(purpose, {})
    tithi_score = tithi_table.get(tithi_num, 5) * 10  # Out of 100
    scores["tithi"] = {"score": tithi_score, "weight": 25, "name": panchang["tithi"]["name"]}
    total_weight += 25

    # Vara suitability (weight: 15)
    vara_name = panchang["vara"]["name"]
    vara_table = VARA_SUITABILITY.get(purpose, {})
    vara_score = vara_table.get(vara_name, 5) * 10
    scores["vara"] = {"score": vara_score, "weight": 15, "name": vara_name}
    total_weight += 15

    # Nakshatra suitability (weight: 25)
    nak_name = panchang["nakshatra"]["name"]
    good_naks = GOOD_NAKSHATRAS.get(purpose, [])
    nak_score = 80 if nak_name in good_naks else 40
    scores["nakshatra"] = {"score": nak_score, "weight": 25, "name": nak_name}
    total_weight += 25

    # Yoga suitability (weight: 10)
    yoga_name = panchang["yoga"]["name"]
    bad_yogas = ["Vishkambha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vajra", "Vyatipata", "Parigha", "Vaidhriti"]
    yoga_score = 30 if yoga_name in bad_yogas else 70
    scores["yoga"] = {"score": yoga_score, "weight": 10, "name": yoga_name}
    total_weight += 10

    # Karana suitability (weight: 5)
    karana_name = panchang["karana"]["name"]
    bad_karanas = ["Vishti"]
    karana_score = 20 if karana_name in bad_karanas else 70
    scores["karana"] = {"score": karana_score, "weight": 5, "name": karana_name}
    total_weight += 5

    # Rahu Kalam check (weight: 10)
    rk = panchang.get("rahu_kalam")
    in_rahu_kalam = False
    if rk and rk.get("start_jd") and rk.get("end_jd"):
        in_rahu_kalam = rk["start_jd"] <= jd <= rk["end_jd"]
    rk_score = 0 if in_rahu_kalam else 80
    scores["rahu_kalam"] = {"score": rk_score, "weight": 10, "in_rahu_kalam": in_rahu_kalam}
    total_weight += 10

    # Yamaganda check (weight: 5)
    yg = panchang.get("yamaganda")
    in_yamaganda = False
    if yg and yg.get("start_jd") and yg.get("end_jd"):
        in_yamaganda = yg["start_jd"] <= jd <= yg["end_jd"]
    yg_score = 0 if in_yamaganda else 80
    scores["yamaganda"] = {"score": yg_score, "weight": 5, "in_yamaganda": in_yamaganda}
    total_weight += 5

    # Moon strength (weight: 5)
    paksha = panchang.get("paksha", "Shukla")
    moon_score = 70 if paksha == "Shukla" else 40
    scores["moon_strength"] = {"score": moon_score, "weight": 5, "paksha": paksha}
    total_weight += 5

    # Calculate weighted overall score
    weighted_sum = sum(s["score"] * s["weight"] for s in scores.values())
    overall_score = round(weighted_sum / total_weight, 1)

    # Assessment
    if overall_score >= 75:
        assessment = "Highly Auspicious"
    elif overall_score >= 60:
        assessment = "Auspicious"
    elif overall_score >= 45:
        assessment = "Average"
    elif overall_score >= 30:
        assessment = "Inauspicious"
    else:
        assessment = "Highly Inauspicious"

    recommendations = []
    if in_rahu_kalam:
        recommendations.append("Avoid this time — falls during Rahu Kalam.")
    if in_yamaganda:
        recommendations.append("Avoid this time — falls during Yamaganda.")
    if karana_name == "Vishti":
        recommendations.append("Vishti Karana is inauspicious for new beginnings.")

    return {
        "purpose": purpose,
        "overall_score": overall_score,
        "assessment": assessment,
        "breakdown": scores,
        "recommendations": recommendations,
        "panchang_summary": {
            "tithi": panchang["tithi"]["name"],
            "vara": panchang["vara"]["name"],
            "nakshatra": panchang["nakshatra"]["name"],
            "yoga": panchang["yoga"]["name"],
            "karana": panchang["karana"]["name"],
        },
    }


def find_auspicious_times(
    jd_start: float, jd_end: float,
    latitude: float, longitude: float,
    purpose: str, timezone_str: str = "UTC",
    min_score: float = 65, step_hours: float = 2,
) -> list:
    """Find auspicious times within a date range for a given purpose."""
    step_jd = step_hours / 24.0
    jd = jd_start
    results = []

    while jd <= jd_end:
        try:
            quality = get_muhurta_quality(jd, latitude, longitude, purpose, timezone_str)
            if quality["overall_score"] >= min_score:
                results.append({
                    "julian_day": jd,
                    "score": quality["overall_score"],
                    "assessment": quality["assessment"],
                    "panchang_summary": quality["panchang_summary"],
                })
        except Exception:
            pass
        jd += step_jd

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:20]  # Top 20 results
