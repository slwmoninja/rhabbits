#!/usr/bin/env python3
"""Builds index.html by inlining the webp/png design assets as base64 data
URIs into the HTML template below. Run after editing HTML_TEMPLATE or after
regenerating any of the source images.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def b64(name, mime):
    data = (ROOT / "Graphics" / name).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def assets():
    return {
        "__AVATAR_MALE__": b64("avatar_male.webp", "image/webp"),
        "__AVATAR_FEMALE__": b64("avatar_female.webp", "image/webp"),
        "__HOME_SCENE__": b64("home_scene.webp", "image/webp"),
        "__HOME_ICON__": b64("home_icon.webp", "image/webp"),
        "__CUTOUT_MALE__": b64("cutout_male.webp", "image/webp"),
        "__CUTOUT_FEMALE__": b64("cutout_female.webp", "image/webp"),
        "__SIGHTINGS_SPRITE__": b64("sightings_sprite.webp", "image/webp"),
        "__CHEST__": b64("chest.webp", "image/webp"),
        "__BOTTLE__": b64("bottle.webp", "image/webp"),
        "__TREASURE_MAP__": b64("treasure_map.webp", "image/webp"),
        "__CARROT_JUICE__": b64("carrot_juice.webp", "image/webp"),
        "__COCO_CANNON_IMG__": b64("cannon.webp", "image/webp"),
        "__COCO_CROW__": b64("crow.webp", "image/webp"),
        "__COCO_CROW_RED__": b64("redcrow.webp", "image/webp"),
        "__COCO_COCONUT__": b64("coco.webp", "image/webp"),
    }


def render():
    """Returns the built index.html text, without writing anything -- used
    both by main() below and by verify_build.py's stale-index.html check."""
    template = (ROOT / "scripts" / "index_template.html").read_text(encoding="utf-8")
    for token, data_uri in assets().items():
        template = template.replace(token, data_uri)
    return template


def main():
    html = render()
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html:", (ROOT / "index.html").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
