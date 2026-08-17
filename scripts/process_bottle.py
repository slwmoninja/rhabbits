"""Builds bottle.webp: a transparent-background cutout of the message-in-a-
bottle photo (Bottle.jpeg, source design asset, not committed), used as the
"The Story So Far" link icon on the Profile screen. Re-run whenever the
source photo changes, then re-run build_index.py to re-embed.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent


def remove_white_bg(im, thresh=238, feather=2.2):
    im = im.convert("RGB")
    arr = np.array(im).astype(np.float32)
    min_channel = arr.min(axis=2)
    # Fully opaque where clearly not background, fully transparent where
    # clearly near-white, smooth ramp across the antialiased edge pixels.
    alpha = np.clip((thresh - min_channel) / (thresh - 200), 0, 1) * 255
    alpha_img = Image.fromarray(alpha.astype(np.uint8), mode="L")
    alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(alpha_img)
    return out


def autocrop_alpha(im, pad=14):
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


def main():
    src = ROOT / "Bottle.jpeg"
    im = Image.open(src)
    im = remove_white_bg(im)
    im = autocrop_alpha(im)

    max_dim = 480
    scale = max_dim / max(im.size)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)

    out = ROOT / "bottle.webp"
    im.save(out, "WEBP", quality=88, method=6)
    print("wrote", out, im.size, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
