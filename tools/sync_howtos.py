"""Copy the partner guides from the public toolkit into the how-to section, so they never go out of date.

    python tools/sync_howtos.py            # from GitHub (main)
    python tools/sync_howtos.py --from ../ceh-biomonitoring    # from a local copy

Runs before every build on GitHub. The copies are committed too, so the site still builds if GitHub
can't be reached. Edit the guides in the toolkit (docs/), never here.
"""
from __future__ import annotations

import argparse
import re
import urllib.request
from datetime import date
from pathlib import Path

REPO = "https://github.com/NERC-CEH/ceh-biomonitoring"
RAW = "https://raw.githubusercontent.com/NERC-CEH/ceh-biomonitoring/main/"
HERE = Path(__file__).resolve().parent.parent / "how-to"

# toolkit guide -> how-to page
GUIDES = {
    "docs/upload-guide.md": ("upload.qmd", "Send us your data", 3),
    "docs/setting-up-sites.md": ("sites.qmd", "Set up your sites", 2),
}
PAGES = {Path(k).name: v[0] for k, v in GUIDES.items()}


def fetch(path: str, local: Path | None) -> str:
    if local:
        return (local / path).read_text(encoding="utf-8")
    with urllib.request.urlopen(RAW + path, timeout=30) as r:
        return r.read().decode("utf-8")


def link(target: str) -> str:
    """A link in a toolkit guide, made to work on the website."""
    if re.match(r"^(https?:|mailto:|#)", target):
        return target
    page, _, anchor = target.partition("#")
    name = Path(page).name
    if name in PAGES:
        return PAGES[name] + (f"#{anchor}" if anchor else "")
    where = (Path("docs") / page).as_posix()
    while "/../" in where or where.startswith("../"):
        where = re.sub(r"[^/]+/\.\./", "", where, count=1).removeprefix("../")
    return f"{REPO}/blob/main/{where}" + (f"#{anchor}" if anchor else "")


def convert(text: str, title: str, order: int, source: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    body = "\n".join(l for l in lines if not l.startswith("**Use R?**")).strip()
    body = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + link(m.group(1)) + ")", body)
    return (f'---\ntitle: "{title}"\norder: {order}\n'
            f'# Copied from {REPO}/blob/main/{source} by tools/sync_howtos.py. Edit it there, not here.\n---\n\n'
            f'::: {{.callout-note appearance="minimal"}}\nThis guide is the same as the one in our '
            f'[toolkit]({REPO}/blob/main/{source}), and is updated automatically (last copied {date.today():%d %B %Y}).\n:::\n\n'
            f"{body}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="local", type=Path, help="a local copy of the toolkit repository")
    a = ap.parse_args()
    HERE.mkdir(exist_ok=True)
    for src, (out, title, order) in GUIDES.items():
        try:
            new = convert(fetch(src, a.local), title, order, src)
        except OSError as e:
            print(f"couldn't fetch {src} ({e}); keeping the copy already here")
            continue
        p = HERE / out
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        strip = lambda t: re.sub(r"last copied [^)]*\)", "", t)
        if strip(old) != strip(new):
            p.write_text(new, encoding="utf-8")
            print(f"updated how-to/{out} from {src}")
        else:
            print(f"how-to/{out} already up to date")


if __name__ == "__main__":
    main()
