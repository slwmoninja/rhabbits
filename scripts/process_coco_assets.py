"""Builds the Coco Cannon game's real-photo sprites (cannon, crow, red
Captain Crow, flaming coconut) from Graphics/{Cannon,Crow,RedCrow,Coco}.jpeg
(source design assets, not committed) -- replaces the earlier hand-drawn
canvas-path placeholders in initCocoCannon() now that real art exists.
Re-run whenever a source photo changes, then re-run build_index.py.

Uses the same border-connected flood fill as process_carrot_juice.py
(not a fixed color threshold) so a photo's soft shadow doesn't survive
alongside the subject -- see that script for the full reasoning.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
GRAPHICS = ROOT / "Graphics"


def remove_white_bg(im, fg_thresh=150, feather=2.0):
    im = im.convert("RGB")
    arr = np.array(im).astype(np.int32)
    min_channel = arr.min(axis=2)
    not_fg = min_channel > fg_thresh
    labels, _ = ndimage.label(not_fg, structure=np.ones((3, 3)))
    border_labels = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))
    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)
    alpha_img = Image.fromarray(alpha, mode="L").filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(alpha_img)
    return out


def autocrop_alpha(im, pad=10):
    alpha = np.array(im.getchannel("A"))
    ys, xs = np.where(alpha > 12)
    if len(xs) == 0:
        return im
    l, r, t, b = xs.min(), xs.max(), ys.min(), ys.max()
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad + 1)
    b = min(im.height, b + pad + 1)
    return im.crop((l, t, r, b))


def process(name, max_dim, fg_thresh=150):
    src = GRAPHICS / (name + ".jpeg")
    im = Image.open(src)
    im = remove_white_bg(im, fg_thresh=fg_thresh)
    im = autocrop_alpha(im)
    scale = max_dim / max(im.size)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    out = GRAPHICS / (name.lower() + ".webp")
    im.save(out, "WEBP", quality=90, method=6)
    print("wrote", out, im.size, out.stat().st_size, "bytes")


def main():
    process("Cannon", 300)
    # Crow/RedCrow are already flat black/red silhouettes on pure white --
    # a much higher fg_thresh is safe (and desirable, to keep every bit of
    # the thin wingtip/feather detail near-white antialiasing would otherwise
    # shave off) since there's no shadow-vs-subject ambiguity like a real photo.
    process("Crow", 220, fg_thresh=245)
    process("RedCrow", 220, fg_thresh=245)
    process("Coco", 200)


if __name__ == "__main__":
    main()
