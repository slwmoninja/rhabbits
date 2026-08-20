#!/usr/bin/env python3
"""Derives APP_VERSION in scripts/index_template.html (and the built
index.html) from a content hash of the template plus every embedded design
asset, so the version marker shown in Settings -> About actually changes
whenever the deployed app changes -- it used to be a hand-bumped comment
that nobody remembered to touch, so it sat frozen at "1.0.0" since day one.

Run automatically by the pre-commit hook (.githooks/pre-commit), before
verify_build.py -- it rewrites the template's version line and rebuilds
index.html from it, so verify_build.py's byte-for-byte check still passes.
Safe to run manually too; it's a no-op if nothing has changed.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index  # noqa: E402  (must come after sys.path setup above)

TEMPLATE_PATH = ROOT / "scripts" / "index_template.html"
INDEX_PATH = ROOT / "index.html"

VERSION_RE = re.compile(r'var APP_VERSION = "[^"]*";')


def compute_hash():
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    # Strip the version line itself so the hash doesn't depend on its own
    # previous output (which would make it self-referential / never settle).
    template_text = VERSION_RE.sub('var APP_VERSION = "";', template_text)

    hasher = hashlib.sha256()
    hasher.update(template_text.encode("utf-8"))
    for name, data_uri in sorted(build_index.assets().items()):
        hasher.update(name.encode("utf-8"))
        hasher.update(data_uri.encode("utf-8"))
    return hasher.hexdigest()[:8]


def main():
    if not VERSION_RE.search(TEMPLATE_PATH.read_text(encoding="utf-8")):
        sys.exit("Could not find APP_VERSION assignment in scripts/index_template.html")

    new_version = f"1.0+{compute_hash()}"
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    new_template_text = VERSION_RE.sub(f'var APP_VERSION = "{new_version}";', template_text, count=1)

    if new_template_text == template_text:
        print("APP_VERSION already up to date")
        return

    TEMPLATE_PATH.write_text(new_template_text, encoding="utf-8")

    built_html = build_index.render()
    INDEX_PATH.write_text(built_html, encoding="utf-8")

    subprocess.run(["git", "add", str(TEMPLATE_PATH), str(INDEX_PATH)], cwd=ROOT, check=True)
    print(f"APP_VERSION updated -> {new_version}")


if __name__ == "__main__":
    main()
