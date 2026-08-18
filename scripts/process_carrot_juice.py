"""Builds carrot_juice.webp: a transparent-background cutout of the real
Carrot Juice barrel photo (Graphics/CarrotJuice.jpeg, source design asset,
not committed), plus the derived icon-192.png/icon-512.png (real deployed
PWA icons, project root) and home_icon.webp (onboarding logo) square-padded
from the same cutout -- replaces the earlier hand-drawn placeholder
(scripts/build_barrel_icon.py, now unused) now that a real product photo
exists. Re-run whenever the source photo changes, then re-run
build_index.py to re-embed.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
GRAPHICS = ROOT / "Graphics"


def remove_white_bg(im, thresh=238, feather=2.2, shadow_cutoff=90):
    im = im.convert("RGB")
    arr = np.array(im).astype(np.float32)
    min_channel = arr.min(axis=2)
    alpha = np.clip((thresh - min_channel) / (thresh - 200), 0, 1) * 255
    # The source photo casts a soft studio shadow on the white backdrop --
    # those pixels are pale gray, not pure white, so the ramp above gives
    # them a faint partial alpha that survives as a visible smudge on any
    # background darker than white (see the app's teal theme). Real subject
    # edges jump alpha sharply over 1-2px; the shadow stays low and gradual,
    # so a hard floor cuts the shadow without visibly notching the subject.
    alpha[alpha < shadow_cutoff] = 0
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


def square_pad_transparent(im):
    w, h = im.size
    s = max(w, h)
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    canvas.paste(im, ((s - w) // 2, (s - h) // 2), im)
    return canvas


def main():
    src = GRAPHICS / "CarrotJuice.jpeg"
    im = Image.open(src)
    im = remove_white_bg(im)
    im = autocrop_alpha(im)

    max_dim = 480
    scale = max_dim / max(im.size)
    cutout = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)

    out = GRAPHICS / "carrot_juice.webp"
    cutout.save(out, "WEBP", quality=88, method=6)
    print("wrote", out, cutout.size, out.stat().st_size, "bytes")

    squared = square_pad_transparent(im)

    logo = squared.resize((320, 320), Image.LANCZOS)
    logo_path = GRAPHICS / "home_icon.webp"
    logo.save(logo_path, "WEBP", quality=90, method=6)
    print("wrote", logo_path, logo.size)

    for size, name in ((192, "icon-192.png"), (512, "icon-512.png")):
        icon = squared.resize((size, size), Image.LANCZOS)
        out_path = ROOT / name
        icon.save(out_path)
        print("wrote", out_path, icon.size)


if __name__ == "__main__":
    main()
