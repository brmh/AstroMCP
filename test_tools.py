import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000"

async def test_endpoint(name, endpoint, payload):
    print(f"\n--- Testing {name} ---")
    try:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=30) as client:
            if payload is None:
                res = await client.get(url)
            else:
                res = await client.post(url, json=payload)
            
            if res.status_code == 200:
                print(f"✅ Success! Length of output: {len(str(res.json()))}")
            else:
                print(f"❌ Failed: {res.status_code} {res.reason_phrase}")
                print(res.text)
    except Exception as e:
        print(f"❌ Failed: {e}")

async def main():
    birth_payload = {
        "birth_data": {
            "name": "Test Person",
            "birth_year": 1990,
            "birth_month": 5,
            "birth_day": 15,
            "birth_hour": 14,
            "birth_minute": 30,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        },
        "options": {
            "house_system": "PLACIDUS",
            "zodiac_type": "TROPICAL",
            "ayanamsa": "LAHIRI"
        }
    }

    await test_endpoint("Lagna Lord", "/vedic/lagna-lord", birth_payload)
    await test_endpoint("Ashtakavarga Scoring", "/transits/ashtakavarga-score", {"natal": birth_payload["birth_data"], "options": birth_payload["options"]})
    await test_endpoint("Dasha Interpretation", "/vedic/dashas/interpretation", {"mahadasha_lord": "Jupiter", "antardasha_lord": "Saturn"})
    await test_endpoint("Kalachakra Dasha", "/vedic/dashas/kalachakra", birth_payload)
    await test_endpoint("Lunar Return", "/western/progressions/lunar-return", {**birth_payload, "target_date": "2024-05-15"})
    await test_endpoint("Eclipse Impacts", "/transits/eclipses/impacts", {"natal": birth_payload["birth_data"], "year": 2024})
    await test_endpoint("Retrogrades", "/transits/retrogrades", {"natal": birth_payload["birth_data"], "start_date": "2024-01-01", "end_date": "2024-12-31", "options": {}})

    print("\nAll new tool endpoints checked against API.")

if __name__ == "__main__":
    asyncio.run(main())
