#!/usr/bin/env python3
"""Fail the build if any slide's content is clipped by the slide edge.

Marp does not warn when a slide overflows — it just cuts the content off at
1280x720. Rendering one PNG per slide and looking for ink in the bottom band
is the cheapest reliable detector we have.

Usage:  python3 tools/check_overflow.py dist/png
"""
import sys
import pathlib

try:
    from PIL import Image
except ImportError:
    sys.exit(
        "check_overflow: Pillow is not installed, so nothing was checked.\n"
        "  A silent skip here would report a clean deck without looking at it.\n"
        "  Install it (pip install Pillow) or run via the repo venv:\n"
        "    ../.venv/bin/python tools/check_overflow.py dist/png"
    )

# Ink at all in the last few rows means something was cut off. A little ink
# just above that is legitimate — the citation footer lives there.
EDGE_ROWS = 6
FOOTER_BAND_TOP = 700
FOOTER_INK_BUDGET = 40
INK_THRESHOLD = 200  # 8-bit grey; below this counts as ink


def ink(pixels, width, y0, y1):
    return sum(
        1
        for y in range(y0, y1)
        for x in range(width)
        if pixels[x, y] < INK_THRESHOLD
    )


def main(directory):
    pngs = sorted(pathlib.Path(directory).glob("*.png"))
    if not pngs:
        sys.exit(f"check_overflow: no PNGs found in {directory}")

    failures = []
    for png in pngs:
        image = Image.open(png).convert("L")
        width, height = image.size
        pixels = image.load()
        if ink(pixels, width, height - EDGE_ROWS, height):
            failures.append((png.name, "content is clipped at the slide edge"))
        elif ink(pixels, width, FOOTER_BAND_TOP, height) > FOOTER_INK_BUDGET:
            failures.append((png.name, "content spills into the footer band"))

    if failures:
        for name, why in failures:
            print(f"  FAIL  {name} — {why}")
        sys.exit(f"check_overflow: {len(failures)} of {len(pngs)} slides overflow")

    print(f"check_overflow: {len(pngs)} slides, none clipped")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist/png")
