"""
Chart SVG API Router
Exposes endpoints that return ready-to-render SVG strings for:
  - North Indian (diamond) style chart
  - South Indian (grid) style chart
  - Any Varga (divisional) chart in either style
"""

from fastapi import APIRouter, Query
from fastapi.responses import Response

from api.models.request_models import NatalChartRequest
from api.dependencies import birth_data_to_jd
from api.core.calculations import get_all_planet_positions, get_houses, assign_houses_to_planets
from api.core.charts import build_divisional_chart
from api.core.chart_svg import (
    generate_north_indian_svg,
    generate_south_indian_svg,
    extract_positions_from_varga,
    extract_lagna_from_chart,
)

router = APIRouter(prefix="/charts", tags=["Chart SVG"])

SVG_MIME = "image/svg+xml"


def _build_base(request: NatalChartRequest):
    """Common setup: compute JD, positions, houses, lagna sign."""
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(
        jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value
    )
    houses = get_houses(
        jd, bd.latitude, bd.longitude,
        "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value
    )
    positions = assign_houses_to_planets(positions, houses)

    # Determine Lagna sign from the ascendant longitude
    asc_lon = houses.get("ascendant", 0)
    sign_idx = int(asc_lon / 30) % 12
    from api.core.chart_svg import SIGN_ORDER
    lagna_sign = SIGN_ORDER[sign_idx]

    return jd, positions, houses, lagna_sign


# ── North Indian D1 (Lagna / Birth Chart) ────────────────────────────────────

@router.post("/north-indian", summary="North Indian Diamond Kundli SVG (D1)")
async def north_indian_chart(
    request: NatalChartRequest,
    theme: str = Query("dark", enum=["dark", "light"]),
    size: int = Query(400, ge=200, le=800),
):
    """
    Generate a **North Indian Diamond** style Lagna (D1) birth chart as SVG.

    - Lagna sign always in the **top-centre** cell.
    - All 12 signs + planets placed clockwise.
    - Returns `image/svg+xml` — embed directly in `<img src="...">` or `<object>`.
    """
    jd, positions, houses, lagna_sign = _build_base(request)
    bd = request.birth_data
    title = f"{bd.name} · {lagna_sign} Lagna (D1)" if bd.name else f"{lagna_sign} Lagna (D1)"
    svg = generate_north_indian_svg(lagna_sign, positions, title=title, W=size, theme=theme)
    return Response(content=svg, media_type=SVG_MIME)


# ── South Indian D1 ───────────────────────────────────────────────────────────

@router.post("/south-indian", summary="South Indian Square Kundli SVG (D1)")
async def south_indian_chart(
    request: NatalChartRequest,
    theme: str = Query("dark", enum=["dark", "light"]),
    size: int = Query(400, ge=200, le=800),
):
    """
    Generate a **South Indian Square** style Lagna (D1) birth chart as SVG.

    - Signs are FIXED in cells (Aries always top-row, 2nd cell), going clockwise.
    - Lagna sign cell is highlighted.
    - Returns `image/svg+xml`.
    """
    jd, positions, houses, lagna_sign = _build_base(request)
    bd = request.birth_data
    title = f"{bd.name} · {lagna_sign} Lagna (D1)" if bd.name else f"{lagna_sign} Lagna (D1)"
    svg = generate_south_indian_svg(lagna_sign, positions, title=title, W=size, theme=theme)
    return Response(content=svg, media_type=SVG_MIME)


# ── North Indian Varga / Divisional Chart ─────────────────────────────────────

@router.post("/north-indian/varga/{division}", summary="North Indian Varga Chart SVG")
async def north_indian_varga_chart(
    division: int,
    request: NatalChartRequest,
    theme: str = Query("dark", enum=["dark", "light"]),
    size: int = Query(400, ge=200, le=800),
):
    """
    Generate a North Indian SVG for any **Divisional (Varga)** chart.

    - `division` = 1 (D1), 2, 3, 4, 7, 9 (Navamsa), 10 (Dasamsa), 12, 16, 20, 24, 27, 30, 40, 45, 60
    - Returns `image/svg+xml`.
    """
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    raw_positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_lon = houses.get("ascendant", 0)

    varga = build_divisional_chart(raw_positions, division, request.options.ayanamsa.value, jd, asc_lon)
    positions = extract_positions_from_varga(varga)
    lagna_sign = extract_lagna_from_chart(varga)

    title = f"{bd.name} · D{division} Chart" if bd.name else f"D{division} Chart"
    svg = generate_north_indian_svg(lagna_sign, positions, title=title, W=size, theme=theme)
    return Response(content=svg, media_type=SVG_MIME)


# ── South Indian Varga / Divisional Chart ─────────────────────────────────────

@router.post("/south-indian/varga/{division}", summary="South Indian Varga Chart SVG")
async def south_indian_varga_chart(
    division: int,
    request: NatalChartRequest,
    theme: str = Query("dark", enum=["dark", "light"]),
    size: int = Query(400, ge=200, le=800),
):
    """
    Generate a South Indian SVG for any **Divisional (Varga)** chart.

    - `division` = 9 for Navamsa, 10 for Dasamsa, etc.
    - Returns `image/svg+xml`.
    """
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    raw_positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_lon = houses.get("ascendant", 0)

    varga = build_divisional_chart(raw_positions, division, request.options.ayanamsa.value, jd, asc_lon)
    positions = extract_positions_from_varga(varga)
    lagna_sign = extract_lagna_from_chart(varga)

    title = f"{bd.name} · D{division} Chart" if bd.name else f"D{division} Chart"
    svg = generate_south_indian_svg(lagna_sign, positions, title=title, W=size, theme=theme)
    return Response(content=svg, media_type=SVG_MIME)
