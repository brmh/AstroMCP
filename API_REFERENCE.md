# AstroConsultant API Reference

**Base URL (Local):** `http://localhost:8000`  
**Base URL (Production):** `https://ciirag-jyotishmcp.hf.space`  
**MCP SSE (ChatGPT):** `https://ciirag-jyotishmcp.hf.space/mcp/sse`  
**Interactive Docs:** `{base_url}/docs`

> All `POST` endpoints accept JSON bodies. Authentication is not required.

---

## Root

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server info, uptime, endpoint index |

---

## 🖼 Chart SVG (`/charts`) — NEW

| Method | Endpoint | Description | Response Type |
|--------|----------|-------------|---------------|
| `POST` | `/charts/north-indian` | North Indian Diamond D1 Kundli chart | `image/svg+xml` |
| `POST` | `/charts/south-indian` | South Indian Square D1 Kundli chart | `image/svg+xml` |
| `POST` | `/charts/north-indian/varga/{division}` | North Indian style for any Varga chart (D1–D60) | `image/svg+xml` |
| `POST` | `/charts/south-indian/varga/{division}` | South Indian style for any Varga chart (D1–D60) | `image/svg+xml` |

**Query Parameters (all 4 endpoints):**
- `theme` — `dark` (default) or `light`
- `size` — integer 200–800 (default 400), canvas width/height in px

**Usage Example:**
```
POST https://ciirag-jyotishmcp.hf.space/charts/north-indian?theme=dark&size=400
Body: { "birth_data": { ... } }
→ Returns SVG string directly embeddable as <img src="data:image/svg+xml,...">
```

**Common Varga divisions:** `9` (Navamsa), `10` (Dasamsa), `12` (Dwadasamsa), `3` (Drekkana), `7` (Saptamsa), `60` (Shashtiamsa)

---

## 🌟 Natal Chart (`/natal`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/natal/chart` | Complete Western natal chart (planets, houses, aspects, angles) |
| `POST` | `/natal/planets` | Planetary positions only |
| `POST` | `/natal/houses` | House cusps and lords |
| `POST` | `/natal/aspects` | Aspect grid between planets |
| `POST` | `/natal/dignities` | Essential dignities (domicile, exaltation, detriment, fall) |
| `POST` | `/natal/midpoints` | Natal midpoints table |
| `POST` | `/natal/arabic-parts` | Arabic/Hermetic lots (Fortune, Spirit, Love, etc.) |
| `POST` | `/natal/declinations` | Planet declinations and parallels |
| `POST` | `/natal/antiscia` | Antiscia and contra-antiscia positions |
| `POST` | `/natal/fixed-stars` | Fixed star conjunctions (Algol, Regulus, Spica, etc.) |

---

## 🪐 Vedic Astrology (`/vedic`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/vedic/kundli` | Complete Vedic Kundli (sidereal, Whole Sign houses) |
| `POST` | `/vedic/nakshatras` | All planet Nakshatra placements |
| `POST` | `/vedic/navamsa` | Navamsa (D9) divisional chart |
| `POST` | `/vedic/varga/{division}` | Any Varga chart: D1,D2,D3,D4,D7,D9,D10,D12,D16,D20,D24,D27,D30,D40,D45,D60 |
| `POST` | `/vedic/divisional-charts` | All major Varga charts at once |
| `POST` | `/vedic/bhava-chalit` | Bhava Chalit chart (Sripati house positions) |
| `POST` | `/vedic/ashtakavarga` | Bhinnashtakavarga + Sarvashtakavarga scores |
| `POST` | `/vedic/shadbala` | Shadbala planetary strength in Rupas |
| `POST` | `/vedic/yogas` | Detect Raj Yogas, Dhana Yogas, Doshas, etc. |
| `POST` | `/vedic/doshas` | Mangal Dosha, Kala Sarpa Dosha detection |
| `POST` | `/vedic/remedies` | Astrological remedies for detected yogas/doshas |
| `POST` | `/vedic/dashas/vimshottari` | Full Vimshottari Dasha timeline |
| `POST` | `/vedic/dashas/current` | Current Mahadasha, Antardasha, Pratyantardasha |
| `POST` | `/vedic/dashas/yogini` | Yogini Dasha system timeline |
| `POST` | `/vedic/dashas/chara` | Jaimini Chara Dasha timeline |
| `POST` | `/vedic/dashas/kalachakra` | Kalachakra Dasha (Nakshatra-based periods) |
| `POST` | `/vedic/dashas/interpretation` | AI-ready dasha interpretation with life areas |
| `POST` | `/vedic/jaimini-karakas` | Jaimini Chara Karakas (AK, AmK, BK, MK, PiK, GK, DK) |
| `POST` | `/vedic/atmakaraka` | Atmakaraka planet identification |
| `POST` | `/vedic/karakamsa` | Karakamsa lagna analysis |
| `POST` | `/vedic/arudha-padas` | Arudha Padas (AL, A2–A12) |
| `POST` | `/vedic/upagrahas` | Upagrahas: Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu |
| `POST` | `/vedic/gochar` | Vedic Gochar (transit) report against natal Moon |
| `POST` | `/vedic/sade-sati` | Sade Sati phase detection and timeline |
| `POST` | `/vedic/lagna-lord` | Lagna lord analysis (sign, house, strength, effects) |
| `POST` | `/vedic/varshaphal` | Varshaphal (Solar Return equivalent in Vedic) |
| `POST` | `/vedic/compatibility` | Vedic compatibility (Ashta Koota matching) |

---

## 🔄 Transits (`/transits`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/transits/now` | Current planetary positions (no birth data needed) |
| `POST` | `/transits/current` | Current sky transits against natal chart |
| `POST` | `/transits/aspects` | Transit-to-natal aspect hits |
| `POST` | `/transits/date-range` | All transit aspects over a date range |
| `POST` | `/transits/planet` | Single-planet transit tracking |
| `POST` | `/transits/ingresses` | Planet sign ingresses over a period |
| `POST` | `/transits/outer-planets` | Major outer planet (Jupiter/Saturn/Uranus/Neptune/Pluto) transits |
| `POST` | `/transits/eclipses` | Upcoming solar and lunar eclipses |
| `POST` | `/transits/eclipses/impacts` | Eclipse impact analysis on natal chart sensetive points |
| `POST` | `/transits/retrogrades` | Retrograde calendar for all planets |
| `POST` | `/transits/ashtakavarga-score` | Transit scoring using Vedic Ashtakavarga system |

---

## 🔗 Synastry (`/synastry`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/synastry/aspects` | Synastry aspect grid between two birth charts |
| `POST` | `/synastry/compatibility-score` | Composite compatibility score with interpretation |
| `POST` | `/synastry/composite` | Composite chart (midpoint method) |
| `POST` | `/synastry/davison` | Davison Relationship chart |

---

## 📅 Panchang (`/panchang`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/panchang/daily` | Full daily Panchang: Tithi, Vara, Nakshatra, Yoga, Karana, Muhurtas, Choghadiya |
| `POST` | `/panchang/monthly` | Month-long Panchang table |
| `POST` | `/panchang/tithi` | Current Tithi and % completion |
| `POST` | `/panchang/nakshatra` | Current Moon Nakshatra |
| `GET` | `/panchang/festivals` | List of major Hindu festivals |

---

## ⏱ Muhurta (`/muhurta`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/muhurta/quality` | Assess muhurta quality for a given date/time |

---

## 🌊 Progressions & Timing (`/progressions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/progressions/secondary` | Secondary Progressions (1 day = 1 year) |
| `POST` | `/progressions/solar-arc` | Solar Arc Directions |
| `POST` | `/progressions/solar-return` | Solar Return chart |
| `POST` | `/progressions/lunar-return` | Lunar Return chart |
| `POST` | `/progressions/profections` | Annual Profections (Annual Lords) |
| `POST` | `/progressions/firdaria` | Firdaria (Persian time lord system) |

---

## 🌏 Western Astrology (`/western`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/western/chart` | Full Western tropical chart |
| `POST` | `/western/dignities` | Western dignities (domicile, exaltation, terms, faces) |
| `POST` | `/western/midpoints/natal` | Natal midpoints |
| `POST` | `/western/midpoints/synastry` | Synastry midpoints |
| `POST` | `/western/composite` | Western composite chart |
| `POST` | `/western/progressions` | Secondary progressions (Western) |
| `POST` | `/western/progressions/solar-return` | Western Solar Return |
| `POST` | `/western/progressions/lunar-return` | Western Lunar Return |
| `POST` | `/western/acg` | Astrocartography — planetary power lines on world map |
| `POST` | `/western/receptions` | Mutual planetary receptions |

---

## ⭐ Fixed Stars (`/fixed-stars`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/natal/fixed-stars` | Fixed star conjunctions within orb |

---

## 🛠 Utilities (`/utilities`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/utilities/health` | Server health check |
| `GET` | `/utilities/ayanamsas` | List all supported Ayanamsa systems |
| `GET` | `/utilities/house-systems` | List all supported house systems |
| `GET` | `/utilities/planets` | Planet metadata (id, symbol, glyph) |
| `GET` | `/utilities/zodiac-signs` | Zodiac sign metadata |
| `GET` | `/utilities/nakshatras` | All 27 Nakshatras with lord and deity |
| `GET` | `/utilities/nakshatra/{number}` | Deep dive on a single Nakshatra (1–27) |
| `GET` | `/utilities/ephemeris-range` | Available ephemeris date range |
| `POST` | `/utilities/geocode` | Geocode city → latitude/longitude/timezone |
| `POST` | `/utilities/julian-day` | Convert date/time to Julian Day |
| `POST` | `/utilities/planetary-hours` | Planetary hour table for a given day |

---

## 🤖 MCP Tools (for Claude Desktop & ChatGPT)

The **MCP Server** exposes all 47 tools via:
- **Claude Desktop:** stdio script at `mcp/server.py`
- **ChatGPT / Remote:** SSE endpoint at `https://ciirag-jyotishmcp.hf.space/mcp/sse`

| Tool Name | Maps To |
|-----------|---------|
| `geocode_location` | `POST /utilities/geocode` |
| `get_natal_chart` | `POST /natal/chart` |
| `get_vedic_kundli` | `POST /vedic/kundli` |
| `get_varga_chart` | `POST /vedic/varga/{division}` |
| `get_bhava_chalit_chart` | `POST /vedic/bhava-chalit` |
| `get_ashtakavarga` | `POST /vedic/ashtakavarga` |
| `get_shadbala` | `POST /vedic/shadbala` |
| `get_yogas` | `POST /vedic/yogas` |
| `get_doshas` | `POST /vedic/doshas` |
| `get_remedies` | `POST /vedic/remedies` |
| `get_gemstones` | `POST /vedic/remedies` (gemstone filter) |
| `get_mantras` | `POST /vedic/remedies` (mantra filter) |
| `get_lagna_lord_analysis` | `POST /vedic/lagna-lord` |
| `get_dasha_timeline` | `POST /vedic/dashas/vimshottari` |
| `get_current_dasha` | `POST /vedic/dashas/current` |
| `get_dasha_interpretation` | `POST /vedic/dashas/interpretation` |
| `get_yogini_dasha` | `POST /vedic/dashas/yogini` |
| `get_kalachakra_dasha` | `POST /vedic/dashas/kalachakra` |
| `get_chara_dasha` | `POST /vedic/dashas/chara` |
| `get_jaimini_karakas` | `POST /vedic/jaimini-karakas` |
| `get_karakamsa` | `POST /vedic/karakamsa` |
| `get_arudha_padas` | `POST /vedic/arudha-padas` |
| `get_upagrahas` | `POST /vedic/upagrahas` |
| `get_gochar_report` | `POST /vedic/gochar` |
| `get_sade_sati` | `POST /vedic/sade-sati` |
| `get_varshaphal` | `POST /vedic/varshaphal` |
| `get_compatibility` | `POST /vedic/compatibility` |
| `get_current_transits` | `POST /transits/current` |
| `get_transit_scoring` | `POST /transits/ashtakavarga-score` |
| `get_eclipse_impacts` | `POST /transits/eclipses/impacts` |
| `get_retrograde_calendar` | `POST /transits/retrogrades` |
| `get_panchang` | `POST /panchang/daily` |
| `get_nakshatra_info` | `GET /utilities/nakshatra/{number}` |
| `get_moon_phase` | `GET /transits/now` (moon extraction) |
| `get_now` | `GET /transits/now` |
| `get_synastry` | `POST /synastry/aspects` |
| `get_composite_chart` | `POST /synastry/composite` |
| `get_synastry_midpoints` | `POST /western/midpoints/synastry` |
| `get_natal_midpoints` | `POST /western/midpoints/natal` |
| `get_solar_return` | `POST /progressions/solar-return` |
| `get_lunar_return` | `POST /progressions/lunar-return` |
| `get_secondary_progressions` | `POST /progressions/secondary` |
| `get_arabic_parts` | `POST /natal/arabic-parts` |
| `get_astrocartography` | `POST /western/acg` |
| `get_planetary_hours` | `POST /utilities/planetary-hours` |
| `get_muhurta` | `POST /muhurta/quality` |
| `find_auspicious_time` | `POST /muhurta/quality` |

---

## Common Request Body (Birth Data)

Most `POST` endpoints accept the following structure:

```json
{
  "birth_data": {
    "name": "Native",
    "year": 1997,
    "month": 4,
    "day": 8,
    "hour": 12,
    "minute": 40,
    "latitude": 27.553,
    "longitude": 76.634,
    "timezone": "Asia/Kolkata"
  },
  "options": {
    "house_system": "PLACIDUS",
    "zodiac_type": "TROPICAL",
    "ayanamsa": "LAHIRI"
  }
}
```

**Supported House Systems:** `PLACIDUS`, `WHOLE_SIGN`, `EQUAL`, `CAMPANUS`, `REGIOMONTANUS`, `PORPHYRY`, `MORINUS`, `ALCABITIUS`, `TOPOCENTRIC`

**Supported Ayanamsas:** `LAHIRI`, `RAMAN`, `KRISHNAMURTI`, `FAGAN_BRADLEY`, `TROPICAL`

---

*Auto-generated from live FastAPI schema — 87 endpoints across 10 route groups + 47 MCP tools*
