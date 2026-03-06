---
title: JyotishMCP
emoji: 🪐
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
---
# 🔭 AstroConsultant — AI Astrology MCP Server

Professional-grade astrology API + MCP Server powered by **Swiss Ephemeris** (`pyswisseph`), supporting both **Western (Tropical)** and **Vedic/Jyotish (Sidereal)** traditions. Exposes **48 MCP tools** and **70+ API endpoints** for comprehensive astrological consultation.

```
┌──────────────────────────────────────────────────┐
│              Claude Desktop (UI)                 │
│                      │                           │
│              MCP Protocol (stdio)                │
│                      │                           │
│           ┌──────────▼──────────┐                │
│           │   MCP Server        │                │
│           │  (48 tools)         │                │
│           └──────────┬──────────┘                │
│                      │ HTTP/JSON                 │
│           ┌──────────▼──────────┐                │
│           │   FastAPI Backend   │                │
│           │   (10 routers,      │                │
│           │    70+ endpoints)   │                │
│           └──────────┬──────────┘                │
│                      │                           │
│           ┌──────────▼──────────┐                │
│           │  Swiss Ephemeris    │                │
│           │  (pyswisseph)       │                │
│           └─────────────────────┘                │
└──────────────────────────────────────────────────┘
```

---

## ✨ Features at a Glance

### 🕉️ Vedic / Jyotish (Sidereal)
| Feature | Description |
|---------|-------------|
| **Kundli (Birth Chart)** | Full sidereal chart with Whole Sign houses |
| **Varga Charts (D1–D60)** | 16+ divisional charts (Navamsa, Dasamsa, etc.) |
| **Dasha Systems** | Vimshottari (Mahadasha → Sookshma), Yogini, Chara, Kalachakra |
| **Current Dasha** | Real-time Mahadasha / Antardasha / Pratyantardasha / Sookshma |
| **Dasha Interpretation** | AI-ready interpretation texts for any Dasha lord combination |
| **Yogas** | 30+ classical yogas (Raja, Dhana, Viparita, Pancha Mahapurusha…) |
| **Doshas** | Mangal Dosha, Kala Sarpa Dosha detection |
| **Shadbala** | Six-fold planetary strength analysis |
| **Ashtakavarga** | Sarvashtakavarga + Bhinnashtakavarga + Transit Scoring |
| **Sade Sati** | Complete 100-year Sade Sati timeline with peak dates |
| **Bhava Chalit** | Sripati house system shifted-planet chart |
| **Upagrahas** | Mandi, Gulika, Dhooma, Vyatipata, Parivesha, Indrachapa, Upaketu |
| **Jaimini System** | Chara Karakas (AK–DK), Arudha Padas, Karakamsa |
| **Lagna Lord Analysis** | Ascendant lord placement, dignity, and interpretation |
| **Gochar (Transit)** | Vedic transit report based on natal Moon sign |
| **Varshaphal** | Tajika annual horoscope (Solar year return) |
| **Nakshatra Deep Dive** | Detailed Nakshatra analysis with deity, syllable, compatibility |
| **Remedies** | Gemstones, Mantras, Charity, Fasting based on chart afflictions |

### 🌍 Western (Tropical)
| Feature | Description |
|---------|-------------|
| **Natal Chart** | Full tropical chart with Placidus / Koch / Equal houses |
| **Aspects** | 11 aspect types with configurable orbs |
| **Essential Dignities** | Domicile, Exaltation, Detriment, Fall, Term, Face |
| **Secondary Progressions** | Day-for-a-year progressed chart |
| **Solar Arc Directions** | Arc-directed planetary positions |
| **Solar Return** | Annual return chart |
| **Lunar Return** | Monthly return chart |
| **Synastry** | Cross-chart aspects for relationship analysis |
| **Composite Chart** | Midpoint composite chart |
| **Midpoint Analysis** | Natal & synastry midpoint trees |
| **Arabic Parts** | Part of Fortune, Spirit, Love, and 8 more |
| **Fixed Stars** | 31 major stars with conjunctions and parans |
| **Asteroids** | Chiron, Ceres, Pallas, Juno, Vesta |

### 📅 Timing & Prediction
| Feature | Description |
|---------|-------------|
| **Panchang** | Tithi, Nakshatra, Yoga, Karana, Sunrise/Sunset |
| **Muhurta** | Quality assessment for any activity + auspicious time finder |
| **Planetary Hours** | Hora chart for any day |
| **Eclipse Impacts** | Detect eclipses hitting natal planets (conjunction/opposition) |
| **Retrograde Calendar** | Mercury through Saturn retrograde periods for any year |
| **Transit Aspects** | Real-time transit-to-natal aspects |
| **Outer Planet Transits** | Jupiter, Saturn, Rahu/Ketu over natal chart |
| **Planetary Ingresses** | Sign-change dates for all planets |
| **Astro*Carto*Graphy** | ACG lines for relocation astrology |

---

## 🛠️ All 48 MCP Tools

Every tool is available to Claude Desktop (or any MCP client) via the `AstroConsultant` server.

<details>
<summary><b>Click to expand full tool list</b></summary>

| # | Tool Name | Category |
|---|-----------|----------|
| 1 | `get_natal_chart` | Core |
| 2 | `get_vedic_kundli` | Vedic |
| 3 | `get_varga_chart` | Vedic |
| 4 | `get_sade_sati` | Vedic |
| 5 | `get_bhava_chalit_chart` | Vedic |
| 6 | `get_upagrahas` | Vedic |
| 7 | `get_remedies` | Vedic |
| 8 | `get_gochar_report` | Vedic |
| 9 | `get_jaimini_karakas` | Vedic |
| 10 | `get_arudha_padas` | Vedic |
| 11 | `get_karakamsa` | Vedic |
| 12 | `get_yogas` | Vedic |
| 13 | `get_doshas` | Vedic |
| 14 | `get_gemstones` | Vedic Remedies |
| 15 | `get_mantras` | Vedic Remedies |
| 16 | `get_shadbala` | Vedic |
| 17 | `get_ashtakavarga` | Vedic |
| 18 | `get_lagna_lord_analysis` | Vedic |
| 19 | `get_transit_scoring` | Vedic / Transits |
| 20 | `get_current_dasha` | Dasha |
| 21 | `get_dasha_timeline` | Dasha |
| 22 | `get_dasha_interpretation` | Dasha |
| 23 | `get_yogini_dasha` | Dasha |
| 24 | `get_chara_dasha` | Dasha |
| 25 | `get_kalachakra_dasha` | Dasha |
| 26 | `get_varshaphal` | Predictive |
| 27 | `get_current_transits` | Transits |
| 28 | `get_eclipse_impacts` | Transits |
| 29 | `get_retrograde_calendar` | Transits |
| 30 | `get_now` | Transits |
| 31 | `get_panchang` | Timing |
| 32 | `get_muhurta` | Timing |
| 33 | `find_auspicious_time` | Timing |
| 34 | `get_planetary_hours` | Timing |
| 35 | `get_nakshatra_info` | Timing |
| 36 | `get_moon_phase` | Timing |
| 37 | `get_secondary_progressions` | Western |
| 38 | `get_solar_return` | Western |
| 39 | `get_lunar_return` | Western |
| 40 | `get_composite_chart` | Western |
| 41 | `get_synastry` | Relationships |
| 42 | `get_synastry_midpoints` | Relationships |
| 43 | `get_compatibility` | Relationships |
| 44 | `get_natal_midpoints` | Analysis |
| 45 | `get_arabic_parts` | Analysis |
| 46 | `get_astrocartography` | Analysis |
| 47 | `geocode_location` | Utility |
| 48 | `get_nakshatra_info` | Utility |

</details>

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd astrology-consultant
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Download Ephemeris Files

```bash
python scripts/download_ephemeris.py
```

### 3. Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify

```bash
curl http://localhost:8000/utilities/health
# → {"status": "ok", "version": "1.0.0", ...}
```

---

## 🤖 Claude Desktop Integration

### 1. Start the FastAPI Server
```bash
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "astro-consultant": {
      "command": "/FULL/PATH/TO/venv/bin/python",
      "args": ["/FULL/PATH/TO/astrology-consultant/mcp/server.py"],
      "env": {
        "MCP_FASTAPI_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Quit and reopen Claude Desktop. The **48 AstroConsultant tools** will appear automatically.

---

## 📡 API Examples

### Natal Chart
```bash
curl -X POST http://localhost:8000/natal/chart \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "name": "Test",
      "birth_year": 1990, "birth_month": 3, "birth_day": 15,
      "birth_hour": 14, "birth_minute": 30,
      "latitude": 28.6139, "longitude": 77.209,
      "timezone": "Asia/Kolkata"
    }
  }'
```

### Vedic Kundli
```bash
curl -X POST http://localhost:8000/vedic/kundli \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "birth_year": 1990, "birth_month": 3, "birth_day": 15,
      "birth_hour": 14, "birth_minute": 30,
      "latitude": 28.6139, "longitude": 77.209,
      "timezone": "Asia/Kolkata"
    },
    "options": {"ayanamsa": "LAHIRI"}
  }'
```

### Daily Panchang
```bash
curl -X POST http://localhost:8000/panchang/daily \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2026, "month": 3, "day": 6,
    "latitude": 28.6139, "longitude": 77.209,
    "timezone": "Asia/Kolkata"
  }'
```

### Current Dasha
```bash
curl -X POST http://localhost:8000/vedic/dashas/current \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "birth_year": 1990, "birth_month": 3, "birth_day": 15,
      "birth_hour": 14, "birth_minute": 30,
      "latitude": 28.6139, "longitude": 77.209,
      "timezone": "Asia/Kolkata"
    }
  }'
```

### Current Planetary Positions
```bash
curl http://localhost:8000/transits/now
```

---

## 📂 API Reference

| Category | Endpoints | Description |
|----------|-----------|-------------|
| `/natal/*` | 10 | Natal chart, planets, houses, aspects, dignities, midpoints, arabic parts |
| `/vedic/*` | 20 | Kundli, varga, dashas, yogas, shadbala, ashtakavarga, doshas, jaimini, lagna lord |
| `/transits/*` | 10 | Current transits, retrogrades, eclipses, ingresses, ashtakavarga scoring |
| `/synastry/*` | 4 | Cross-chart aspects, composite, Davison, compatibility |
| `/panchang/*` | 5 | Daily/monthly panchang, nakshatra, tithi, festivals |
| `/muhurta/*` | 4 | Quality assessment, auspicious time finder, hora |
| `/western/*` | 5 | Progressions, solar/lunar returns, composite chart |
| `/timing/*` | 4 | Solar/lunar returns, dasha interpretation, kalachakra |
| `/fixed-stars/*` | 3 | Star list, conjunctions, heliacal events |
| `/utilities/*` | 9 | Health, geocode, zodiac signs, nakshatras metadata |

**Total: 70+ endpoints · 48 MCP tools**

---

## 🔧 Configuration

### Supported Ayanamsas
`LAHIRI` · `RAMAN` · `KRISHNAMURTI` · `FAGAN_BRADLEY` · `TRUE_CHITRAPAKSHA` · `YUKTESHWAR` · `JN_BHASIN` · `SASSANIAN`

### Supported House Systems
`PLACIDUS` · `KOCH` · `WHOLE_SIGN` · `EQUAL` · `CAMPANUS` · `REGIOMONTANUS` · `PORPHYRY` · `ALCABITIUS` · `MORINUS` · `MERIDIAN` · `AZIMUTHAL` · `POLICH_PAGE`

### Zodiac Types
`TROPICAL` · `SIDEREAL`

---

## 🧪 Running Tests

```bash
source venv/bin/activate
python3 test_tools.py
```

Tests validate: Lagna Lord, Ashtakavarga Scoring, Dasha Interpretation, Kalachakra Dasha, Lunar Return, Eclipse Impacts, Retrogrades.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: swisseph` | `pip install pyswisseph` |
| Inaccurate positions | Run `python scripts/download_ephemeris.py` |
| Port 8000 in use | Change `API_PORT` in `.env` |
| MCP not connecting | Ensure FastAPI server is running first |
| Timezone errors | Use IANA format: `Asia/Kolkata`, `America/New_York` |
| Chiron warnings | Non-critical — Chiron ephemeris data not available for all dates |

---

## 📜 License

This project uses **pyswisseph** which is licensed under **AGPL**. Please review the [Swiss Ephemeris license](https://www.astro.com/swisseph/) for commercial use requirements.

---

*Created by Team Magicmond · Powered by Swiss Ephemeris*
