#!/usr/bin/env python3
"""Builds index.html by inlining the webp/png design assets as base64 data
URIs into the HTML template below. Run after editing HTML_TEMPLATE or after
regenerating any of the source images.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def b64(name, mime):
    data = (ROOT / name).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


ASSETS = {
    "__AVATAR_MALE__": b64("avatar_male.webp", "image/webp"),
    "__AVATAR_FEMALE__": b64("avatar_female.webp", "image/webp"),
    "__HOME_SCENE__": b64("home_scene.webp", "image/webp"),
    "__HOME_ICON__": b64("home_icon.webp", "image/webp"),
    "__CUTOUT_MALE__": b64("cutout_male.webp", "image/webp"),
    "__CUTOUT_FEMALE__": b64("cutout_female.webp", "image/webp"),
    "__SIGHTINGS_SPRITE__": b64("sightings_sprite.webp", "image/webp"),
    "__CHEST__": b64("chest.webp", "image/webp"),
    "__BOTTLE__": b64("bottle.webp", "image/webp"),
}

template = (ROOT / "scripts" / "index_template.html").read_text(encoding="utf-8")
for token, data_uri in ASSETS.items():
    template = template.replace(token, data_uri)

(ROOT / "index.html").write_text(template, encoding="utf-8")
print("wrote index.html:", (ROOT / "index.html").stat().st_size, "bytes")
