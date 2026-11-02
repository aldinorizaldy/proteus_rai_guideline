#!/usr/bin/env python3
"""Derive web-ready brand assets from the originals in docs/assets/.

Inputs (copied from the PROTEUS PowerPoint template):
    proteus-logo-white.png     white wordmark on black
    copernicus-agent-icon.png  favicon source
    hero-globe.png             title-slide globe

Outputs (all written next to the inputs, safe to re-run):
    proteus-logo-white-transparent.png  black turned into transparency
    proteus-wordmark-white.png          header logo (wordmark without tagline)
    favicon-32.png                      32 x 32 browser favicon
    apple-touch-icon-180.png            180 x 180 home-screen icon (opaque)
    hero-globe.webp                     resized, compressed hero image

Usage:  python scripts/prepare_assets.py
"""
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent.parent / "docs" / "assets"


def trim(im: Image.Image, pad: int = 0) -> Image.Image:
    """Crop away fully transparent borders, keeping `pad` px of margin."""
    box = im.getchannel("A").getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0),
                    min(r + pad, im.width), min(b + pad, im.height)))


def black_to_transparent(src: Path, dst: Path) -> None:
    """Treat black as the background: alpha = brightest channel, then
    un-premultiply so anti-aliased edges stay white rather than grey."""
    im = Image.open(src).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            alpha = max(r, g, b) * a // 255
            if alpha == 0:
                px[x, y] = (0, 0, 0, 0)
            else:
                k = 255 / max(r, g, b)
                px[x, y] = (min(255, round(r * k)), min(255, round(g * k)),
                            min(255, round(b * k)), alpha)
    trim(im, pad=4).save(dst, optimize=True)


def wordmark_only(im: Image.Image) -> Image.Image:
    """Keep the tallest horizontal band of content (the wordmark), dropping
    any tagline separated from it by a fully transparent gap."""
    alpha = im.getchannel("A")
    bands, start = [], None
    for y in range(im.height):
        filled = alpha.crop((0, y, im.width, y + 1)).getbbox() is not None
        if filled and start is None:
            start = y
        elif not filled and start is not None:
            bands.append((start, y))
            start = None
    if start is not None:
        bands.append((start, im.height))
    if len(bands) < 2:
        return im
    top, bottom = max(bands, key=lambda b: b[1] - b[0])
    return trim(im.crop((0, top, im.width, bottom)), pad=2)


def square(im: Image.Image, size: int, pad_ratio: float, bg=None) -> Image.Image:
    im = trim(im)
    side = round(max(im.size) * (1 + 2 * pad_ratio))
    canvas = Image.new("RGBA", (side, side), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def main() -> None:
    white = ASSETS / "proteus-logo-white.png"
    if white.exists():
        out = ASSETS / "proteus-logo-white-transparent.png"
        black_to_transparent(white, out)
        # Header logo: wordmark only (the tagline is unreadable at 24 px).
        wordmark_only(Image.open(out)).save(
            ASSETS / "proteus-wordmark-white.png", optimize=True)

    icon = ASSETS / "copernicus-agent-icon.png"
    if icon.exists():
        src = Image.open(icon).convert("RGBA")
        square(src, 32, 0.02).save(ASSETS / "favicon-32.png", optimize=True)
        # iOS ignores transparency (renders black), so use a white tile.
        square(src, 180, 0.12, bg=(255, 255, 255, 255)).convert("RGB").save(
            ASSETS / "apple-touch-icon-180.png", optimize=True)

    globe = ASSETS / "hero-globe.png"
    if globe.exists():
        im = Image.open(globe).convert("RGBA")
        im.thumbnail((1200, 1200), Image.LANCZOS)
        im.save(ASSETS / "hero-globe.webp", "WEBP", quality=82, method=6)

    for p in sorted(ASSETS.glob("*")):
        if p.is_file():
            print(f"{p.stat().st_size / 1024:8.1f} KB  {p.name}")


if __name__ == "__main__":
    main()
