"""
Vedic Aspects (Drishti) API Endpoints
=====================================
Exposes the complete Drishti analysis as REST endpoints.

POST /vedic/aspects         → Full Drishti analysis (all 3 systems)
POST /vedic/aspects/graha   → Graha Drishti (Parashari planetary aspects) only
POST /vedic/aspects/rashi   → Rashi Drishti (Jaimini sign aspects) only
POST /vedic/aspects/planet/{planet} → Aspects for a single planet
POST /vedic/aspects/house/{house}   → All aspects on a specific house
"""

from fastapi import APIRouter, HTTPException, Path as FPath
from api.models.request_models import NatalChartRequest
from api.dependencies import birth_data_to_jd
from api.core.charts import build_natal_chart
from api.core.aspects import (
    compute_full_aspects,
    get_all_aspects_in_chart,
    get_all_rashi_drishti,
    get_aspects_on_house,
    get_aspects_on_planet,
    get_graha_drishti,
    find_conjunctions,
    find_mutual_aspects,
    calculate_drik_bala,
    calculate_all_sphuta_drishti,
    get_house_aspect_summary,
    normalize_planet_name,
    house_from_sign,
    sign_from_house,
    GRAHA_DRISHTI,
    HOUSE_THEMES,
    PLANET_SIGNIFICATIONS,
    NATURAL_BENEFICS,
)

router = APIRouter(prefix="/vedic/aspects", tags=["Vedic Aspects (Drishti)"])


def _build_chart(request: NatalChartRequest) -> dict:
    """Build a whole-sign sidereal natal chart from a request."""
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    return build_natal_chart(
        jd, bd.latitude, bd.longitude,
        house_system="WHOLE_SIGN",
        zodiac_type="SIDEREAL",
        ayanamsa=request.options.ayanamsa.value,
    )


def _extract_positions(chart: dict) -> tuple[dict, dict, dict, str]:
    """
    Extract planet_positions {planet→house}, planet_signs {planet→sign},
    planet_longitudes {planet→longitude}, and lagna_sign from chart.
    """
    planets_raw = chart.get("planets", {})
    ascendant = chart.get("ascendant", {})
    lagna_sign = ascendant.get("sign", "Aries")

    positions = {}
    signs = {}
    longitudes = {}

    for name, data in planets_raw.items():
        p = normalize_planet_name(name)
        if p not in GRAHA_DRISHTI and p not in ("rahu", "ketu"):
            continue
        if not isinstance(data, dict):
            continue

        h = data.get("house")
        if h is None:
            s = data.get("sign", "Aries")
            h = house_from_sign(s, lagna_sign)
        positions[p] = int(h)
        signs[p] = data.get("sign", sign_from_house(int(h), lagna_sign))
        lon = data.get("full_degree") or data.get("longitude") \
              or data.get("sidereal_degree", 0)
        longitudes[p] = float(lon) if lon else 0.0

    return positions, signs, longitudes, lagna_sign


# ─── 1. Full Drishti Analysis ───────────────────────────────────────────

@router.post(
    "",
    summary="Full Vedic Drishti Analysis",
    description="""
Returns a **complete Drishti (aspect) analysis** covering all three classical systems:

1. **Graha Drishti** — Planetary aspects per BPHS Ch.9 (Parashari system)
2. **Sphuta Drishti** — Degree-based aspect strength in Virupas per BPHS Ch.28
3. **Rashi Drishti** — Sign aspects per Jaimini system (always full & mutual)

**Also includes:**
- Conjunctions (Yuti / Graha Samagama) with combustion check
- Mutual aspects (Paraspar Drishti) with bilateral strength
- Drik Bala — aspectual strength component of Shadbala (BPHS 27.19)
- House aspect summary — net benefic/malefic balance per house
- Planet-by-planet aspect breakdown (aspects cast + received)
- Yogakaraka aspect highlight (if applicable for this Lagna)

**Classical References:** BPHS Ch.9 (Graha Drishti), Ch.28 (Sphuta Drishti),
Phaladeepika, Jaimini Sutras (Rashi Drishti)
""",
)
async def vedic_full_aspects(request: NatalChartRequest):
    chart = _build_chart(request)
    result = compute_full_aspects(chart)
    result["birth_data"] = {
        "name": request.birth_data.name,
        "timezone": request.birth_data.timezone,
        "ayanamsa": request.options.ayanamsa.value,
    }
    return result


# ─── 2. Graha Drishti Only ─────────────────────────────────────────────

@router.post(
    "/graha",
    summary="Graha Drishti — Parashari Planetary Aspects",
    description="""
**Graha Drishti** (Planetary Aspects) per Brihat Parashara Hora Shastra Chapter 9.

**Rules applied:**
- All planets → 7th house (full aspect, 100%)
- Mars → also 4th & 8th (special full aspects)
- Jupiter → also 5th & 9th (special full aspects)
- Saturn → also 3rd & 10th (special full aspects)
- Rahu → 5th, 7th, 9th (Jupiter-like, modern practice)
- Ketu → 7th only (conservative)

Includes Pada (quarter) system for partial aspect strengths.
""",
)
async def vedic_graha_drishti(request: NatalChartRequest):
    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    aspects = get_all_aspects_in_chart(positions, lagna)

    # Group by aspecting planet for easy reading
    by_planet = {}
    for asp in aspects:
        p = asp["aspecting_planet"]
        if p not in by_planet:
            pinfo = PLANET_SIGNIFICATIONS.get(p, {})
            by_planet[p] = {
                "planet": p,
                "emoji": pinfo.get("emoji", ""),
                "name_sanskrit": pinfo.get("name", p.capitalize()),
                "nature": asp["nature"],
                "from_house": asp["from_house"],
                "from_sign": asp["from_sign"],
                "significations": pinfo.get("themes", ""),
                "aspects": [],
            }
        by_planet[p]["aspects"].append({
            "aspected_house": asp["aspected_house"],
            "aspected_sign": asp["aspected_sign"],
            "aspect_type": asp["aspect_type"],
            "strength_percent": asp["strength_percent"],
            "strength_pada": asp["strength_pada"],
            "planets_aspected": asp.get("planets_aspected", []),
            "house_themes": HOUSE_THEMES.get(asp["aspected_house"], ""),
        })

    return {
        "lagna": lagna,
        "system": "Graha Drishti — Parashari (BPHS Ch.9)",
        "total_aspects": len(aspects),
        "planets": by_planet,
        "aspect_rules_summary": {
            planet: {
                "aspects_houses_offset": offsets,
                "special_offsets": [o for o in offsets if o != 7],
            }
            for planet, offsets in GRAHA_DRISHTI.items()
        },
    }


# ─── 3. Rashi Drishti Only ────────────────────────────────────────────

@router.post(
    "/rashi",
    summary="Rashi Drishti — Jaimini Sign Aspects",
    description="""
**Rashi Drishti** (Sign Aspects) from the Jaimini system.

**Rules:**
- **Movable signs** (Aries, Cancer, Libra, Capricorn) aspect all Fixed signs
  except the immediately adjacent one
- **Fixed signs** (Taurus, Leo, Scorpio, Aquarius) aspect all Movable signs
  except the immediately adjacent one
- **Dual signs** (Gemini, Virgo, Sagittarius, Pisces) aspect all other Dual signs

All Rashi Drishti aspects are **full strength** and always **mutual**.
Planets inherit the sign's line of sight.

Used in Jaimini Chara Dasha, Arudha Pada analysis, and Karakamsha readings.
""",
)
async def vedic_rashi_drishti(request: NatalChartRequest):
    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    aspects = get_all_rashi_drishti(signs, lagna)

    by_sign = {}
    for asp in aspects:
        fs = asp["from_sign"]
        if fs not in by_sign:
            by_sign[fs] = {
                "sign": fs,
                "type": asp["from_sign_type"],
                "house": asp["from_house"],
                "planets_in_sign": [
                    p for p, s in signs.items() if s == fs
                ],
                "aspects": [],
            }
        by_sign[fs]["aspects"].append({
            "aspected_sign": asp["aspected_sign"],
            "aspected_sign_type": asp["aspected_sign_type"],
            "aspected_house": asp["aspected_house"],
            "planets_in_aspected": asp["planets_aspected"],
            "mutual": True,
            "strength": "Full (always)",
        })

    return {
        "lagna": lagna,
        "system": "Rashi Drishti — Jaimini System",
        "note": "All Rashi Drishti aspects are full strength and mutually bilateral.",
        "by_sign": by_sign,
    }


# ─── 4. Planet Aspect Detail ─────────────────────────────────────────

@router.post(
    "/planet/{planet_name}",
    summary="Aspects for a Single Planet",
    description="""
Get complete Drishti details for a **specific planet**:
- Houses and planets it aspects (Graha Drishti cast)
- Planets aspecting it (received aspects)
- Sphuta Drishti strength of received aspects
- Drik Bala net score
- Rashi Drishti from its sign
""",
)
async def vedic_planet_aspects(
    planet_name: str = FPath(description="Planet name: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu"),
    request: NatalChartRequest = ...,
):
    p = normalize_planet_name(planet_name)
    if p not in GRAHA_DRISHTI and p not in ("rahu", "ketu"):
        raise HTTPException(status_code=400, detail=f"Unknown planet: {planet_name}. "
                           f"Use: {list(GRAHA_DRISHTI.keys())}")

    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    if p not in positions:
        raise HTTPException(status_code=404, detail=f"{planet_name} not found in chart")

    phouse = positions[p]
    psign = signs.get(p, "")
    pinfo = PLANET_SIGNIFICATIONS.get(p, {})

    # Graha Drishti — what this planet aspects
    aspects_cast = get_graha_drishti(p, phouse, lagna)
    for asp in aspects_cast:
        asp["planets_in_target"] = [
            pn for pn, ph in positions.items()
            if ph == asp["aspected_house"] and pn != p
        ]
        asp["house_themes"] = HOUSE_THEMES.get(asp["aspected_house"], "")

    # Aspects received
    aspects_received = get_aspects_on_planet(p, positions, lagna)
    for ar in aspects_received:
        ar["house_themes"] = HOUSE_THEMES.get(phouse, "")

    # Sphuta Drishti received
    sphuta_received = []
    if longitudes.get(p):
        for op, olon in longitudes.items():
            if op == p:
                continue
            from api.core.aspects import calculate_sphuta_drishti
            vir = calculate_sphuta_drishti(op, olon, longitudes[p])
            if vir > 5:
                sphuta_received.append({
                    "from_planet": op,
                    "virupas": round(vir, 2),
                    "strength_percent": round(vir / 60 * 100, 1),
                    "nature": "benefic" if op in NATURAL_BENEFICS else "malefic",
                })

    # Drik Bala
    drik = calculate_drik_bala(longitudes).get(p, {})

    # Mutual aspects
    mutual = find_mutual_aspects(positions, lagna)
    my_mutual = [m for m in mutual if m["planet_1"] == p or m["planet_2"] == p]

    # Rashi Drishti from sign
    from api.core.aspects import get_rashi_drishti
    rashi_targets = get_rashi_drishti(psign)
    rashi_aspects = []
    for ts in rashi_targets:
        th = house_from_sign(ts, lagna)
        rashi_aspects.append({
            "aspected_sign": ts,
            "aspected_house": th,
            "planets_in_sign": [pn for pn, s in signs.items() if s == ts],
            "house_themes": HOUSE_THEMES.get(th, ""),
            "mutual": True,
            "strength": "Full",
        })

    return {
        "planet": p,
        "emoji": pinfo.get("emoji", ""),
        "name_sanskrit": pinfo.get("name", p.capitalize()),
        "nature": pinfo.get("nature", ""),
        "significations": pinfo.get("themes", ""),
        "position": {
            "house": phouse,
            "sign": psign,
            "longitude": round(longitudes.get(p, 0), 4),
        },
        "graha_drishti_cast": {
            "description": "Houses & planets this planet aspects",
            "count": len(aspects_cast),
            "aspects": aspects_cast,
        },
        "graha_drishti_received": {
            "description": "Planets aspecting this planet",
            "count": len(aspects_received),
            "aspects": aspects_received,
        },
        "sphuta_drishti_received": {
            "description": "Degree-based aspect strength received (Virupas)",
            "aspects": sorted(sphuta_received, key=lambda x: -x["virupas"]),
        },
        "rashi_drishti_cast": {
            "description": "Signs aspected via Jaimini Rashi Drishti",
            "from_sign": psign,
            "aspects": rashi_aspects,
        },
        "mutual_aspects": my_mutual,
        "drik_bala": drik,
    }


# ─── 5. House Aspect Detail ───────────────────────────────────────────

@router.post(
    "/house/{house_number}",
    summary="All Aspects on a Specific House",
    description="""
Get all Graha Drishti aspects falling on a specific house (1–12),
including benefic/malefic balance and interpretation context.
""",
)
async def vedic_house_aspects(
    house_number: int = FPath(ge=1, le=12, description="House number 1–12"),
    request: NatalChartRequest = ...,
):
    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    aspectors = get_aspects_on_house(house_number, positions, lagna)
    occupants = [p for p, h in positions.items() if h == house_number]
    house_sign = sign_from_house(house_number, lagna)

    benefic = [a for a in aspectors if a["nature"] in ("benefic",)]
    malefic = [a for a in aspectors if a["nature"] in ("malefic", "mild_malefic")]

    if len(benefic) > len(malefic):
        net = "net_benefic — This house is generally protected and strengthened"
    elif len(malefic) > len(benefic):
        net = "net_malefic — This house may face challenges or afflictions"
    elif not aspectors:
        net = "unaspected — This house's results depend mainly on its occupants and lord"
    else:
        net = "balanced — Mixed influences; context and dashas will determine timing"

    # Find which planets have special (full) aspects here
    special_aspects = [a for a in aspectors if "special" in a.get("aspect_type", "")]

    return {
        "house": house_number,
        "sign": house_sign,
        "themes": HOUSE_THEMES.get(house_number, ""),
        "occupants": occupants,
        "total_aspects_received": len(aspectors),
        "benefic_aspects": benefic,
        "malefic_aspects": malefic,
        "special_aspects": special_aspects,
        "net_assessment": net,
        "all_aspectors": aspectors,
        "interpretation_note": (
            "A benefic aspect can greatly improve even a damaged house. "
            "A malefic aspect tests the house's significations — but may not always "
            "give purely negative results, especially if it is a functional benefic for this Lagna."
        ),
    }


# ─── 6. Mutual Aspects Only ───────────────────────────────────────────

@router.post(
    "/mutual",
    summary="Mutual Aspects (Paraspar Drishti)",
    description="""
Find all **mutual aspects** in the chart — pairs of planets that aspect
each other simultaneously. Per BPHS, a full mutual aspect (Paraspar Drishti)
is one of the most powerful forms of planetary association (Sambandha).
""",
)
async def vedic_mutual_aspects(request: NatalChartRequest):
    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    mutual = find_mutual_aspects(positions, lagna)
    conjunctions = find_conjunctions(positions, longitudes, lagna)

    return {
        "lagna": lagna,
        "mutual_aspects": {
            "description": "Pairs of planets aspecting each other (Paraspar Drishti)",
            "count": len(mutual),
            "pairs": mutual,
        },
        "conjunctions": {
            "description": "Planets in same house (Yuti — most intimate association)",
            "count": len(conjunctions),
            "groups": conjunctions,
        },
        "classical_note": (
            "Per BPHS: 'The full aspect of a planet on another with that aspect returned "
            "in full is deemed a major kind of Sambandha (planetary association).' "
            "Conjunction > Full Mutual Aspect > Unilateral Special Aspect in intensity."
        ),
    }


# ─── 7. Drik Bala Only ────────────────────────────────────────────────

@router.post(
    "/drik-bala",
    summary="Drik Bala — Aspectual Strength (Shadbala Component)",
    description="""
Calculate **Drik Bala** — the aspectual strength component of Shadbala,
per BPHS Chapter 27 verse 19:

*"Reduce 1/4 of Drishti Pinda if a planet receives malefic aspects and add 1/4
if it receives benefic aspects. Super add the entire Drishti of Budha and Guru."*

Returns net Virupas for each planet (positive = benefic net, negative = malefic net).
Used in Shadbala total strength calculations.
""",
)
async def vedic_drik_bala(request: NatalChartRequest):
    chart = _build_chart(request)
    positions, signs, longitudes, lagna = _extract_positions(chart)

    drik = calculate_drik_bala(longitudes)

    # Sort by absolute strength
    ranked = sorted(
        [{"planet": p, **v} for p, v in drik.items()],
        key=lambda x: abs(x["drik_bala_virupas"]),
        reverse=True,
    )

    min_shadbala = {
        "sun": 390, "moon": 360, "mars": 300,
        "mercury": 420, "jupiter": 390, "venus": 330, "saturn": 300,
    }

    return {
        "lagna": lagna,
        "system": "Drik Bala — BPHS Ch.27 v19",
        "unit": "Virupas (0-60 per aspect; total can exceed 60 from multiple aspects)",
        "by_planet": drik,
        "ranked_by_strength": ranked,
        "reference_minimums": min_shadbala,
        "formula": (
            "Net Drik Bala = Σ(Benefic Sphuta Drishti × 1/4) "
            "+ Full Sphuta of Jupiter + Full Sphuta of Mercury "
            "- Σ(Malefic Sphuta Drishti × 1/4)"
        ),
    }
