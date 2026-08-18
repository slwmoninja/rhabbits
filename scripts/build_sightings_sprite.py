#!/usr/bin/env python3
"""Builds sightings_sprite.webp: a single 10x10 grid combining the 100
individual "New Discovery" collectible icons from Rewards1.jpeg and
Rewards2.jpeg (two 10x5 sprite sheets, https://.../rHabbits/Rewards1.jpeg /
Rewards2.jpeg -- source design assets, not committed). Re-run this whenever
those source sheets change, then re-run build_index.py to re-embed.

One combined sprite (rather than 100 separate embedded images) both keeps
file size down and compresses better than many tiny images would.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

TILE = 96
COLS, ROWS_PER_SHEET = 10, 5
PAD_CELL = 6  # inset per grid cell to avoid picking up seam/grid-line artifacts
BG = (241, 228, 194)  # --parchment


def autocrop_cell(cell, thresh=245, pad=4):
    arr = np.array(cell.convert("L"))
    ys, xs = np.where(arr < thresh)
    if len(xs) == 0:
        return cell
    l, r, t, b = xs.min(), xs.max(), ys.min(), ys.max()
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(cell.width, r + pad + 1)
    b = min(cell.height, b + pad + 1)
    return cell.crop((l, t, r, b))


def make_tile(cell):
    cell = autocrop_cell(cell)
    w, h = cell.size
    s = max(w, h)
    canvas = Image.new("RGB", (s, s), BG)
    canvas.paste(cell, ((s - w) // 2, (s - h) // 2))
    return canvas.resize((TILE, TILE), Image.LANCZOS)


def main():
    sheets = [Image.open(ROOT / "Graphics" / "Rewards1.jpeg"), Image.open(ROOT / "Graphics" / "Rewards2.jpeg")]
    sw, sh = sheets[0].size
    cw, ch = sw / COLS, sh / ROWS_PER_SHEET

    total_rows = ROWS_PER_SHEET * len(sheets)
    sprite = Image.new("RGB", (TILE * COLS, TILE * total_rows), BG)

    for sheet_i, sheet in enumerate(sheets):
        for row in range(ROWS_PER_SHEET):
            for col in range(COLS):
                x0, y0 = int(col * cw) + PAD_CELL, int(row * ch) + PAD_CELL
                x1, y1 = int((col + 1) * cw) - PAD_CELL, int((row + 1) * ch) - PAD_CELL
                tile = make_tile(sheet.crop((x0, y0, x1, y1)))
                out_row = sheet_i * ROWS_PER_SHEET + row
                sprite.paste(tile, (col * TILE, out_row * TILE))

    out = ROOT / "Graphics" / "sightings_sprite.webp"
    sprite.save(out, "WEBP", quality=82, method=6)
    print("wrote", out, sprite.size, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
