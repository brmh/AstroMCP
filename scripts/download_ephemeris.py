"""
Download Swiss Ephemeris data files from astro.com FTP.
"""

import os
import sys
import urllib.request
import hashlib

EPHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe")
BASE_URL = "https://www.astro.com/ftp/swisseph/ephe/"

FILES = [
    "semo_18.se1",   # Moon 1800-2400 CE
    "sepl_18.se1",   # Planets 1800-2400 CE
    "seas_18.se1",   # Asteroids 1800-2400 CE
    "sefstars.txt",  # Fixed stars
]


def download_file(filename: str):
    """Download a single file with progress."""
    url = BASE_URL + filename
    filepath = os.path.join(EPHE_DIR, filename)

    if os.path.exists(filepath):
        print(f"  ✓ {filename} already exists, skipping")
        return True

    print(f"  ↓ Downloading {filename}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, filepath)
        size = os.path.getsize(filepath)
        print(f"Done ({size / 1024 / 1024:.1f} MB)" if size > 1024*1024 else f"Done ({size / 1024:.0f} KB)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def main():
    print("=" * 60)
    print("Swiss Ephemeris Data File Downloader")
    print("=" * 60)
    print(f"\nTarget directory: {EPHE_DIR}")

    os.makedirs(EPHE_DIR, exist_ok=True)

    success_count = 0
    for f in FILES:
        if download_file(f):
            success_count += 1

    print(f"\n{'=' * 60}")
    print(f"Downloaded {success_count}/{len(FILES)} files")

    if success_count == len(FILES):
        print("✓ All required ephemeris files are present!")
    else:
        print("⚠ Some files failed to download. The API will fall back to Moshier ephemeris.")

    print(f"\nFor extended date range coverage, download additional files from:")
    print(f"  {BASE_URL}")
    print(f"\nFiles for other centuries:")
    print(f"  sepl_06.se1  — Planets 600-1200 CE")
    print(f"  sepl_12.se1  — Planets 1200-1800 CE")
    print(f"  sepl_24.se1  — Planets 2400-3000 CE")
    print(f"  semo_06.se1  — Moon 600-1200 CE")
    print(f"  semo_12.se1  — Moon 1200-1800 CE")
    print(f"  semo_24.se1  — Moon 2400-3000 CE")


if __name__ == "__main__":
    main()
