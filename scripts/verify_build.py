#!/usr/bin/env python3
"""Fails the commit if index.html doesn't match what build_index.py would
produce from scripts/index_template.html right now.

Run automatically by the pre-commit hook (.githooks/pre-commit), whenever
either file is staged. Exists because index.html has, more than once, been
hand-edited directly instead of through the template -- which works fine
until the next build_index.py run (e.g. for an unrelated change) silently
regenerates index.html from the stale template and reverts every edit that
bypassed it. See git commit 308a7ba for the incident this caught after the
fact; this hook exists so the next one is caught before a commit ever lands.

The fix when this fails is never to hand-edit index.html: port the change
into scripts/index_template.html and rerun build_index.py instead.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index  # noqa: E402  (must come after sys.path setup above)


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout
    return set(out.splitlines())


def main():
    staged = staged_files()
    if "index.html" not in staged and "scripts/index_template.html" not in staged:
        return  # neither side of the build touched by this commit -- nothing to check

    expected = build_index.render()
    actual = (ROOT / "index.html").read_text(encoding="utf-8")
    if expected == actual:
        print("index.html matches scripts/index_template.html build output")
        return

    sys.exit(
        "index.html does not match building scripts/index_template.html.\n"
        "index.html must never be hand-edited -- edit the template and run\n"
        "`python scripts/build_index.py` instead, then stage the result."
    )


if __name__ == "__main__":
    main()
