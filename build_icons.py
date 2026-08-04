#!/usr/bin/env python3
"""Generate platform-specific app icons from Rip-Tags.png."""

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parent
PNG_PATH = ROOT / "Rip-Tags.png"
ICO_PATH = ROOT / "Rip-Tags.ico"
ICNS_PATH = ROOT / "Rip-Tags.icns"


def main():
    if not PNG_PATH.exists():
        raise FileNotFoundError(f"Icon source not found: {PNG_PATH}")

    img = Image.open(PNG_PATH)

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Windows ICO with common sizes
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    img.save(ICO_PATH, format="ICO", sizes=[(s, s) for s in ico_sizes])
    print(f"Generated {ICO_PATH}")

    # macOS ICNS
    img.save(ICNS_PATH, format="ICNS")
    print(f"Generated {ICNS_PATH}")


if __name__ == "__main__":
    main()
