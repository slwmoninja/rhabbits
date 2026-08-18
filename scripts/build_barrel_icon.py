#!/usr/bin/env python3
"""Draws the Carrot Juice barrel -- rHabbits' emerging brand icon -- as a
transparent-background vector-style illustration, matching the app's
existing hand-drawn-icon convention (see chestIconSvg() in
scripts/index_template.html, used because no chest emoji exists either).
No source photo exists for this one, unlike the other build_*.py scripts,
so everything below is drawn directly with PIL primitives at high
resolution and downsampled for crisp edges.

Writes:
  Graphics/home_icon.webp -- the onboarding welcome-screen logo
  icon-192.png / icon-512.png (project root) -- the real deployed PWA icons
"""
import math
import os
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHICS = os.path.join(BASE, "Graphics")

S = 1024  # draw large, downsample later for antialiasing
WOOD = (107, 69, 38, 255)       # --wood
WOOD_DARK = (62, 39, 20, 255)   # --wood-dark
WOOD_LIGHT = (150, 108, 68, 255)
WOOD_MID_SHADOW = (85, 54, 29, 255)
GOLD = (198, 153, 47, 255)      # --gold
GOLD_DARK = (150, 110, 30, 255)
CARROT = (224, 123, 46, 255)    # --carrot
CARROT_DEEP = (184, 90, 27, 255)
LEAF = (92, 122, 63, 255)       # --leaf


def half_width(t, rim, bulge):
    return rim + bulge * math.sin(math.pi * t)


def barrel_polygon(cx, y0, y1, rim, bulge, steps=48):
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge)
        left.append((cx - hw, y))
        right.append((cx + hw, y))
    return left + right[::-1]


def band_polygon(cx, y0, y1, rim, bulge, t_center, band_h, steps=24):
    pts_top, pts_bot = [], []
    half_span = (band_h / (y1 - y0)) / 2
    for i in range(steps + 1):
        t = t_center - half_span + (2 * half_span) * (i / steps)
        t = max(0.0, min(1.0, t))
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge) + 3
        pts_top.append((cx - hw, y))
        pts_bot.append((cx + hw, y))
    return pts_top + pts_bot[::-1]


def draw_barrel(size=S):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = size / 2
    y0, y1 = size * 0.16, size * 0.90
    rim, bulge = size * 0.195, size * 0.075

    # Body
    d.polygon(barrel_polygon(cx, y0, y1, rim, bulge), fill=WOOD, outline=WOOD_DARK)
    # Left highlight streak (cheap cylinder shading)
    hl = []
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge)
        hl.append((cx - hw * 0.55, y))
    for i in range(steps, -1, -1):
        t = i / steps
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge)
        hl.append((cx - hw * 0.15, y))
    # ImageDraw.polygon overwrites pixels rather than alpha-blending them, so
    # these shading strips must be fully opaque themselves -- a semi-
    # transparent fill would erase the wood body drawn underneath instead of
    # tinting it, revealing whatever's behind the whole image (transparent
    # canvas) rather than blending with the barrel.
    d.polygon(hl, fill=WOOD_LIGHT)
    # Right shadow streak
    sh = []
    for i in range(steps + 1):
        t = i / steps
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge)
        sh.append((cx + hw * 0.25, y))
    for i in range(steps, -1, -1):
        t = i / steps
        y = y0 + t * (y1 - y0)
        hw = half_width(t, rim, bulge)
        sh.append((cx + hw * 0.75, y))
    d.polygon(sh, fill=WOOD_MID_SHADOW)

    # Hoops/bands
    for t_center in (0.12, 0.5, 0.88):
        d.polygon(band_polygon(cx, y0, y1, rim, bulge, t_center, size * 0.045),
                   fill=GOLD, outline=GOLD_DARK)

    # Body outline redrawn on top so the bands don't overhang the silhouette edge
    d.polygon(barrel_polygon(cx, y0, y1, rim, bulge), outline=WOOD_DARK, width=max(2, size // 200))

    # Top lid (flat ellipse cap)
    lid_rx, lid_ry = rim * 0.98, size * 0.028
    d.ellipse([cx - lid_rx, y0 - lid_ry, cx + lid_rx, y0 + lid_ry],
              fill=WOOD_LIGHT, outline=WOOD_DARK, width=max(2, size // 220))

    # Bunghole, filled with carrot juice
    hole_r = size * 0.05
    hole_cy = y0 - lid_ry * 0.15
    d.ellipse([cx - hole_r, hole_cy - hole_r * 0.65, cx + hole_r, hole_cy + hole_r * 0.65],
               fill=CARROT_DEEP, outline=WOOD_DARK, width=max(2, size // 260))

    # A carrot used as the cork/stopper -- little in-joke matching the app's
    # carrot-currency theme, not just a generic barrel.
    carrot_w, carrot_h = size * 0.05, size * 0.11
    carrot_top_y = hole_cy - carrot_h * 0.6
    d.polygon([
        (cx - carrot_w, carrot_top_y),
        (cx + carrot_w, carrot_top_y),
        (cx, carrot_top_y + carrot_h),
    ], fill=CARROT, outline=CARROT_DEEP)
    leaf_y = carrot_top_y - size * 0.01
    for dx in (-1, 0, 1):
        lx = cx + dx * size * 0.022
        d.polygon([
            (lx - size * 0.012, leaf_y),
            (lx + size * 0.012, leaf_y),
            (lx, leaf_y - size * 0.05),
        ], fill=LEAF)

    return im


def main():
    art = draw_barrel(S)

    # In-app onboarding logo -- transparent, matches home_icon.webp's
    # existing 320x320 convention exactly.
    logo = art.resize((320, 320), Image.LANCZOS)
    logo_path = os.path.join(GRAPHICS, "home_icon.webp")
    logo.save(logo_path, "WEBP", quality=90, method=6)
    print("wrote", logo_path, logo.size)

    # Real deployed PWA icons -- transparent background matches the
    # existing icon-192/512.png convention already in place (verified via
    # pixel-sampling the previous tree-cutout icons before overwriting).
    for size, name in ((192, "icon-192.png"), (512, "icon-512.png")):
        out = art.resize((size, size), Image.LANCZOS)
        out_path = os.path.join(BASE, name)
        out.save(out_path)
        print("wrote", out_path, out.size)


if __name__ == "__main__":
    main()
