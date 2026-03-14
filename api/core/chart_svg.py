"""
SVG Chart Generator for Vedic Astrology Charts.

Generates:
  - North Indian Diamond (Uttara Bhartiya) style Kundli
  - South Indian Square (Dakshina Bhartiya) style Kundli
  - Any Divisional (Varga) chart in North or South style

North Indian Layout:
  - Outer square with 2 diagonals (corner-to-corner) + inner diamond (midpoint-to-midpoint)
  - Creates 12 houses: 4 trapezoidal (1,4,7,10), 4 corner triangles (2,3,5,6,8,9,11,12)
  - House 1 (Ascendant) is always the top-center diamond.
  - Signs placed clockwise from Lagna.
"""

from typing import Dict, List, Optional

# ─── Sign Abbreviations ──────────────────────────────────────────────────────
SIGN_ABBR = {
    "Aries": "Ar", "Taurus": "Ta", "Gemini": "Ge", "Cancer": "Ca",
    "Leo": "Le", "Virgo": "Vi", "Libra": "Li", "Scorpio": "Sc",
    "Sagittarius": "Sg", "Capricorn": "Cp", "Aquarius": "Aq", "Pisces": "Pi",
}

PLANET_ABBR = {
    "sun": "Su", "moon": "Mo", "mars": "Ma", "mercury": "Me",
    "jupiter": "Ju", "venus": "Ve", "saturn": "Sa", "rahu": "Ra",
    "ketu": "Ke", "mean_node": "Ra", "true_node": "Ra",
    "uranus": "Ur", "neptune": "Ne", "pluto": "Pl",
}

SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Vedic charts only show the 9 Navagrahas — exclude outer planets, Lilith, etc.
# mean_node / true_node are both Rahu — only show one.
VEDIC_PLANET_KEYS = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu", "mean_node"}
SKIP_IN_VEDIC = {"true_node", "uranus", "neptune", "pluto", "chiron", "mean_apog", "oscu_apog", "earth", "pholus", "ceres", "pallas", "juno", "vesta"}


def _build_sign_planets(positions: Dict) -> Dict[str, List[str]]:
    """
    Build a sign → list-of-abbreviated-planet-names mapping.
    Filters to Vedic Navagrahas only, deduplicates Rahu (mean_node vs rahu vs true_node).
    """
    sign_planets: Dict[str, List[str]] = {}
    seen_abbrs_per_sign: Dict[str, set] = {}  # prevents "Ra Ra"
    for planet, data in positions.items():
        if not isinstance(data, dict):
            continue
        # Skip non-Vedic planets
        if planet.lower() in SKIP_IN_VEDIC:
            continue
        sign = data.get("sign", "")
        if not sign:
            continue
        abbr = PLANET_ABBR.get(planet.lower(), None)
        if abbr is None:
            continue
        if sign not in seen_abbrs_per_sign:
            seen_abbrs_per_sign[sign] = set()
        # Deduplicate (e.g. "Ra" from both rahu and mean_node)
        if abbr not in seen_abbrs_per_sign[sign]:
            seen_abbrs_per_sign[sign].add(abbr)
            sign_planets.setdefault(sign, []).append(abbr)
    return sign_planets



def _sign_index(sign_name: str) -> int:
    try:
        return SIGN_ORDER.index(sign_name)
    except ValueError:
        return 0


def _house_sign(lagna_sign: str, house_num: int) -> str:
    lagna_idx = _sign_index(lagna_sign)
    return SIGN_ORDER[(lagna_idx + house_num - 1) % 12]


# ─── North Indian (Diamond) Chart ────────────────────────────────────────────
#
# Geometry: A square of size W×W.
#
# Key points:
#   Corners:  TL(0,0)  TR(W,0)  BR(W,W)  BL(0,W)
#   Midpoints: T(W/2,0)  R(W,W/2)  B(W/2,W)  L(0,W/2)
#   Center:   C(W/2, W/2)
#
# Lines drawn:
#   Diagonal 1: TL → BR  (y = x)
#   Diagonal 2: TR → BL  (y = -x + W)
#   Diamond:    T → R → B → L → T  (connecting midpoints)
#
# The diagonals intersect the diamond edges at 4 points:
#   NW(W/4, W/4)   NE(3W/4, W/4)   SE(3W/4, 3W/4)   SW(W/4, 3W/4)
#
# This creates 12 houses (CLOCKWISE from top):
#   1  = Top diamond (Ascendant)
#   2  = Top-right △    3 = Right-upper △    4 = Right diamond
#   5  = Right-lower △  6 = Bottom-right △   7 = Bottom diamond
#   8  = Bottom-left △  9 = Left-lower △    10 = Left diamond
#  11  = Left-upper △  12 = Top-left △

def _ni_polygons(W: int) -> Dict[int, str]:
    """Return correct North Indian house polygons for a W×W SVG."""
    TL = (0, 0);      TR = (W, 0)
    BR = (W, W);      BL = (0, W)
    T = (W/2, 0);     R = (W, W/2)
    B = (W/2, W);     L = (0, W/2)
    C = (W/2, W/2)
    NW = (W/4, W/4);    NE = (3*W/4, W/4)
    SE = (3*W/4, 3*W/4); SW = (W/4, 3*W/4)

    def pts(*p):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)

    return {
        1:  pts(T, NE, C, NW),
        2:  pts(T, TR, NE),
        3:  pts(TR, R, NE),
        4:  pts(NE, R, SE, C),
        5:  pts(R, BR, SE),
        6:  pts(BR, B, SE),
        7:  pts(SE, B, SW, C),
        8:  pts(B, BL, SW),
        9:  pts(BL, L, SW),
        10: pts(SW, L, NW, C),
        11: pts(L, TL, NW),
        12: pts(TL, T, NW),
    }


def _centroid(pts_str: str):
    coords = [(float(p.split(",")[0]), float(p.split(",")[1]))
              for p in pts_str.strip().split()]
    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    return cx, cy


def generate_north_indian_svg(
    lagna_sign: str,
    positions: Dict,
    title: str = "",
    W: int = 400,
    theme: str = "dark",
) -> str:
    """Generate a North Indian diamond Kundli chart as SVG string."""
    if theme == "dark":
        bg = "#0B0C1A"; stroke = "#C5A880"; text_c = "#F0E6D3"
        lagna_fill = "#1A1040"; cell_fill = "#0F1030"; sign_c = "#9370DB"
        planet_c = "#FFD700"
    else:
        bg = "#FFFBF0"; stroke = "#8B6914"; text_c = "#1A0A00"
        lagna_fill = "#FFF0C8"; cell_fill = "#FFFFF0"; sign_c = "#7B2D8B"
        planet_c = "#8B0000"

    polygons = _ni_polygons(W)
    house_signs = {h: _house_sign(lagna_sign, h) for h in range(1, 13)}

    # Use the filtered Vedic planet builder (no outer planets, no duplicate Rahu)
    sign_planets = _build_sign_planets(positions)

    title_h = 24 if title else 0
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W + title_h}" '
        f'viewBox="0 0 {W} {W + title_h}">',
        f'<rect width="{W}" height="{W + title_h}" fill="{bg}"/>',
    ]

    if title:
        lines.append(
            f'<text x="{W//2}" y="18" text-anchor="middle" font-family="Georgia,serif" '
            f'font-size="14" fill="{text_c}" font-weight="bold">{title}</text>'
        )

    lines.append(f'<g transform="translate(0,{title_h})">')

    # Draw outer border
    lines.append(
        f'<rect x="0" y="0" width="{W}" height="{W}" fill="{cell_fill}" '
        f'stroke="{stroke}" stroke-width="2"/>'
    )

    # Draw all structural lines (diagonals + diamond)
    mid = W / 2
    # Diagonals
    lines.append(f'<line x1="0" y1="0" x2="{W}" y2="{W}" stroke="{stroke}" stroke-width="1.2"/>')
    lines.append(f'<line x1="{W}" y1="0" x2="0" y2="{W}" stroke="{stroke}" stroke-width="1.2"/>')
    # Diamond (midpoint connections)
    lines.append(
        f'<polygon points="{mid},0 {W},{mid} {mid},{W} 0,{mid}" '
        f'fill="none" stroke="{stroke}" stroke-width="1.2"/>'
    )

    # Highlight House 1 (Ascendant)
    lines.append(
        f'<polygon points="{polygons[1]}" fill="{lagna_fill}" fill-opacity="0.6" '
        f'stroke="none"/>'
    )

    # Place sign abbreviations and planets in each house
    for house_num, pts_str in polygons.items():
        sign = house_signs[house_num]
        sign_abbr = SIGN_ABBR.get(sign, sign[:2])
        planets_here = sign_planets.get(sign, [])
        cx, cy = _centroid(pts_str)

        # Sign abbreviation
        lines.append(
            f'<text x="{cx:.1f}" y="{cy - 4:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="10" fill="{sign_c}" '
            f'font-weight="bold">{sign_abbr}</text>'
        )

        # Planets
        if planets_here:
            planet_str = " ".join(planets_here)
            lines.append(
                f'<text x="{cx:.1f}" y="{cy + 12:.1f}" text-anchor="middle" '
                f'font-family="Georgia,serif" font-size="11" font-weight="bold" '
                f'fill="{planet_c}">{planet_str}</text>'
            )

    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


# ─── South Indian (Square Grid) Chart ────────────────────────────────────────
_SI_SIGN_CELLS = {
    "Pisces":      (0, 0), "Aries":       (0, 1), "Taurus":  (0, 2), "Gemini":    (0, 3),
    "Aquarius":    (1, 0),                                             "Cancer":    (1, 3),
    "Capricorn":   (2, 0),                                             "Leo":       (2, 3),
    "Sagittarius": (3, 0), "Scorpio":     (3, 1), "Libra":   (3, 2), "Virgo":     (3, 3),
}

def generate_south_indian_svg(
    lagna_sign: str,
    positions: Dict,
    title: str = "",
    W: int = 400,
    theme: str = "dark",
) -> str:
    """Generate a South Indian 4×4 grid Kundli chart as SVG string."""
    if theme == "dark":
        bg = "#0B0C1A"; stroke = "#C5A880"; text_c = "#F0E6D3"
        lagna_fill = "#2A1060"; cell_fill = "#0F1030"; sign_c = "#9370DB"
        planet_c = "#FFD700"; inner_fill = "#080811"
    else:
        bg = "#FFFBF0"; stroke = "#8B6914"; text_c = "#1A0A00"
        lagna_fill = "#FFF0C8"; cell_fill = "#FFFFF0"; sign_c = "#7B2D8B"
        planet_c = "#8B0000"; inner_fill = "#F5F5DC"

    cell = W / 4
    # Use the filtered Vedic planet builder
    sign_planets = _build_sign_planets(positions)

    title_h = 24 if title else 0
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W + title_h}" '
        f'viewBox="0 0 {W} {W + title_h}">',
        f'<rect width="{W}" height="{W + title_h}" fill="{bg}"/>',
    ]
    if title:
        lines.append(
            f'<text x="{W//2}" y="18" text-anchor="middle" font-family="Georgia,serif" '
            f'font-size="14" fill="{text_c}" font-weight="bold">{title}</text>'
        )

    lines.append(f'<g transform="translate(0,{title_h})">')
    lines.append(f'<rect x="0" y="0" width="{W}" height="{W}" fill="{bg}" stroke="{stroke}" stroke-width="2"/>')
    lines.append(f'<rect x="{cell:.1f}" y="{cell:.1f}" width="{cell*2:.1f}" height="{cell*2:.1f}" fill="{inner_fill}" stroke="{stroke}" stroke-width="1"/>')

    for sign, (row, col) in _SI_SIGN_CELLS.items():
        x = col * cell
        y = row * cell
        is_lagna = (sign == lagna_sign)
        fill = lagna_fill if is_lagna else cell_fill
        planets_here = sign_planets.get(sign, [])
        cx = x + cell / 2
        cy = y + cell / 2

        lines.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        )
        if is_lagna:
            # Draw diagonal line to mark Lagna
            lines.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x+cell/3:.1f}" y2="{y+cell/3:.1f}" stroke="#FF6666" stroke-width="1.5"/>')

        sign_abbr = SIGN_ABBR.get(sign, sign[:2])
        lines.append(
            f'<text x="{cx:.1f}" y="{cy - 6:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="10" fill="{sign_c}" font-weight="bold">{sign_abbr}</text>'
        )
        if planets_here:
            planet_str = " ".join(planets_here)
            lines.append(
                f'<text x="{cx:.1f}" y="{cy + 10:.1f}" text-anchor="middle" '
                f'font-family="Georgia,serif" font-size="11" font-weight="bold" fill="{planet_c}">{planet_str}</text>'
            )

    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


# ─── Utilities ────────────────────────────────────────────────────────────────

def extract_positions_from_varga(varga_data: Dict) -> Dict:
    positions = {}
    planets_raw = varga_data.get("planets", {})
    if not planets_raw:
        planets_raw = {k: v for k, v in varga_data.items() if isinstance(v, dict) and "sign" in v}
    for planet, data in planets_raw.items():
        if isinstance(data, dict):
            positions[planet] = {"sign": data.get("sign", "")}
    return positions


def extract_lagna_from_chart(chart_data: Dict) -> str:
    if "ascendant" in chart_data:
        asc = chart_data["ascendant"]
        if isinstance(asc, dict):
            return asc.get("sign", "Aries")
        if isinstance(asc, str):
            return asc
    if "lagna" in chart_data:
        return chart_data["lagna"]
    houses = chart_data.get("houses", {})
    if houses:
        h1 = houses.get("house_1", houses.get("1", {}))
        if isinstance(h1, dict):
            return h1.get("sign", "Aries")
    cusps = chart_data.get("cusps", {})
    if cusps:
        h1 = cusps.get("house_1", {})
        if isinstance(h1, dict):
            return h1.get("sign", "Aries")
    return "Aries"
