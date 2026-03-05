# 🔭 AstroConsultant — AI Astrology Consultant System

Professional-grade astrology API powered by **Swiss Ephemeris** (`pyswisseph`), supporting both **Western (Tropical)** and **Vedic/Jyotish (Sidereal)** traditions.

```
┌──────────────────────────────────────────────────┐
│              Claude Desktop (UI)                 │
│                      │                           │
│              MCP Protocol (stdio)                │
│                      │                           │
│           ┌──────────▼──────────┐                │
│           │   MCP Server        │                │
│           │  (fastmcp + httpx)  │                │
│           └──────────┬──────────┘                │
│                      │ HTTP/JSON                 │
│           ┌──────────▼──────────┐                │
│           │   FastAPI Backend   │                │
│           │   (10 routers,      │                │
│           │    60+ endpoints)   │                │
│           └──────────┬──────────┘                │
│                      │                           │
│           ┌──────────▼──────────┐                │
│           │  Swiss Ephemeris    │                │
│           │  (pyswisseph)       │                │
│           └─────────────────────┘                │
└──────────────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.10+**
- **pip** (or `uv`)
- ~50 MB disk space for ephemeris data files

## Quick Start

### 1. Install Dependencies

```bash
cd astrology-consultant
pip install -r requirements.txt
```

### 2. Download Ephemeris Files

```bash
python scripts/download_ephemeris.py
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work fine)
```

### 4. Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify

```bash
curl http://localhost:8000/utilities/health
# → {"status": "ok", "version": "1.0.0", ...}
```

## API Examples

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

### Muhurta Quality
```bash
curl -X POST http://localhost:8000/muhurta/quality \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2026, "month": 3, "day": 15,
    "hour": 10, "minute": 30,
    "latitude": 28.6139, "longitude": 77.209,
    "timezone": "Asia/Kolkata",
    "purpose": "marriage"
  }'
```

## Claude Desktop Integration

### 1. Start the FastAPI Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 2. Configure Claude Desktop

Copy the config to Claude Desktop's config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "astro-consultant": {
      "command": "python",
      "args": ["/FULL/PATH/TO/astrology-consultant/mcp/server.py"],
      "env": {
        "MCP_FASTAPI_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Quit and reopen Claude Desktop. The AstroConsultant tools should appear.

## API Reference

| Category | Endpoints | Description |
|----------|-----------|-------------|
| `/natal/*` | 10 | Natal chart, planets, houses, aspects, dignities, midpoints |
| `/vedic/*` | 17 | Kundli, dashas, yogas, shadbala, ashtakavarga, doshas |
| `/transits/*` | 9 | Current transits, retrogrades, eclipses, ingresses |
| `/synastry/*` | 4 | Cross-chart aspects, composite, Davison, compatibility |
| `/panchang/*` | 5 | Daily/monthly panchang, nakshatra, tithi, festivals |
| `/muhurta/*` | 4 | Quality assessment, auspicious time finder, hora |
| `/progressions/*` | 6 | Secondary, solar arc, solar/lunar return, profections |
| `/western/*` | 3 | Dignities, mutual receptions, Western chart |
| `/fixed-stars/*` | 3 | Star list, conjunctions, heliacal events |
| `/utilities/*` | 9 | Health, geocode, zodiac signs, nakshatras metadata |

**Total: 70+ endpoints**

## Running Tests

```bash
python scripts/test_calculations.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: swisseph` | `pip install pyswisseph` |
| Inaccurate positions | Run `python scripts/download_ephemeris.py` |
| Port 8000 in use | Change `API_PORT` in `.env` |
| MCP not connecting | Ensure FastAPI server is running first |
| Timezone errors | Use IANA format: `Asia/Kolkata`, `America/New_York` |

## License

This project uses **pyswisseph** which is licensed under **AGPL**. Please review the [Swiss Ephemeris license](https://www.astro.com/swisseph/) for commercial use requirements.

---

*Created by Team Magicmond*
# AstroMCP
