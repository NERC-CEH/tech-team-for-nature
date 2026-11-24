"""Build map/deployments.json and map/photos/ for the "Where we work" map.

    python tools/build_map.py --deployments <deployments_info.csv> --summary <summary.json> --photos <photos dir>
                              [--counts <deployment_*.csv> ...] [--bucket-counts <bucket_media_summary.csv>]
                              [--setup-photos <setup.json>] [--as-of "November 2026"]

Inputs stay private: the team's deployment list (ceh-biomonitoring-internal/upload_api/deployments_info.csv)
and the summary + night photos picked from the data store on JASMIN (summary.json, photos/<dep>/*.jpg).
Photo counts come from the team's media summaries (--counts per deployment, --bucket-counts per
country); where a system has no count, none is shown. --setup-photos is an optional {deployment_id: path} of photos of a system in place.

What comes out is public, so it holds NO coordinates, site names or deployment IDs: one marker per
country (at the middle of the country), and per system only a number, what it records, the months
it ran, its photo count and a few photos (renamed, resized, EXIF removed).
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import date
from pathlib import Path

import numpy as np
from scipy import ndimage
from PIL import Image

SITE = Path(__file__).resolve().parents[1]
OUT_JSON, OUT_PHOTOS = SITE / "map" / "deployments.json", SITE / "map" / "photos"

# The middle of each country (rounded). Never a site's location.
CENTRES = {
    "Anguilla": (18.22, -63.05), "Argentina": (-34.0, -64.0), "Costa Rica": (9.75, -83.75), "Cyprus": (35.0, 33.2),
    "Ghana": (7.9, -1.0), "Japan": (36.2, 138.25), "Kenya": (0.0, 37.9), "Madagascar": (-19.0, 46.7),
    "Namibia": (-22.5, 17.0), "Nigeria": (9.1, 8.7), "Panama": (8.5, -80.0), "Singapore": (1.35, 103.82),
    "Thailand": (15.0, 101.0), "Uganda": (1.4, 32.3), "United Kingdom": (54.0, -2.0),
}
BUCKET_COUNTRY = {"aia": "Anguilla", "cri": "Costa Rica", "cyp": "Cyprus", "gbr": "United Kingdom", "jpn": "Japan",
                  "ken": "Kenya", "nam": "Namibia", "nga": "Nigeria", "pan": "Panama", "sgp": "Singapore",
                  "tha": "Thailand", "mdg": "Madagascar", "uga": "Uganda", "gha": "Ghana",
                  "saltmarsh-soundscapes": "United Kingdom"}
KINDS = {"snapshot_images": "moths", "motion_images": "moths", "audible_recordings": "sound",
         "terrestrial_recordings": "sound", "aquatic_recordings": "sound", "ultrasound_recordings": "bats"}
FIRST_MONTH = "202301"           # earlier dates are cameras whose clock wasn't set
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def month(d: str) -> str:
    return f"{MONTHS[int(d[4:6]) - 1]} {d[:4]}" if len(d) >= 6 else ""


def when(first: str, last: str) -> str:
    a, b = month(first), month(last)
    return a if a == b else f"{a} to {b}" if a and b else a or b


def busy(src: Path) -> float:
    """How many separate insects are on the screen: small dark specks on the bright background.

    Big dark shapes (an insect right in front of the lens, a cable) don't count, and a photo that is
    mostly dark scores low, so sharp, busy screens come first.
    """
    g = np.asarray(Image.open(src).convert("L").resize((480, 270)), dtype=float)
    med = np.median(g)
    if med < 90:
        return 0.0
    dark = g < med * 0.7
    labels, n = ndimage.label(dark)
    if not n:
        return 0.0
    sizes = np.bincount(labels.ravel())[1:]
    specks = int(((sizes >= 6) & (sizes <= 900)).sum())
    return specks * (1.0 - min(1.0, dark.mean() * 4))


def save_photo(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")       # convert() drops EXIF and any GPS
    img.thumbnail((800, 800))
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "JPEG", quality=72, optimize=True, progressive=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deployments", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--photos", required=True)
    ap.add_argument("--counts", nargs="*", default=[])
    ap.add_argument("--bucket-counts")
    ap.add_argument("--setup-photos")
    ap.add_argument("--as-of", default=date.today().strftime("%B %Y"))
    a = ap.parse_args()

    rows = {r["deployment_id"]: r for r in csv.DictReader(open(a.deployments, encoding="utf-8-sig"))}
    summary = json.loads(Path(a.summary).read_text(encoding="utf-8"))
    setup = ({d: str(Path(a.setup_photos).parent / p) for d, p in json.loads(Path(a.setup_photos).read_text(encoding="utf-8")).items()}
             if a.setup_photos else {})        # paths in setup.json are relative to it
    photos_in = Path(a.photos)
    counts = {r["deployment_id"]: int(float(r["image_count"] or 0))
              for f in a.counts for r in csv.DictReader(open(f, encoding="utf-8-sig"))}
    bucket_counts = ({r["bucket"]: int(float(r["image_count"] or 0)) for r in csv.DictReader(open(a.bucket_counts, encoding="utf-8-sig"))}
                     if a.bucket_counts else {})
    this_month = date.today().strftime("%Y%m")

    systems = {}
    for dep in sorted(set(rows) | set(summary)):
        r, s = rows.get(dep, {}), summary.get(dep, {})
        country = (r.get("country") or BUCKET_COUNTRY.get(s.get("bucket", ""), "")).split(" (")[0]
        if s.get("bucket") == "saltmarsh-soundscapes":
            country = "United Kingdom"
        if country not in CENTRES:
            print("skipped (no country centre):", dep, country)
            continue
        kinds = s.get("kinds", {})
        if not kinds and r.get("status") != "active":
            continue                                 # never used
        records = sorted({KINDS[k] for k, n in kinds.items() if n and k in KINDS}, key=["moths", "sound", "bats"].index)
        if not records:
            records = ["sound"] if "soundscape" in (r.get("country", "") + s.get("bucket", "")) else ["moths"]
        months = sorted(m for m in (s.get("months") or [s.get("first", "")[:6], s.get("last", "")[:6]])
                        if m and FIRST_MONTH <= m <= this_month)
        folder = photos_in / dep
        scored = sorted(((busy(p), p) for p in (folder.glob("*.jpg") if folder.is_dir() else [])), reverse=True)
        if scored and scored[0][0] >= 3:
            scored = [t for t in scored if t[0] >= 3]     # leave out near-empty screens if there's better
        night = [p for _, p in scored]
        systems.setdefault(country, []).append({
            "dep": dep, "bucket": s.get("bucket", r.get("country_code", "")), "first": months[0] if months else "",
            "last": months[-1] if months else "", "records": records, "images": counts.get(dep) or next((n for k, n in kinds.items() if k == "snapshot_images" and type(n) is int), None),
            "photos": ([Path(setup[dep])] if dep in setup else []) + night,
            "best": (1000.0 if dep in setup else 0.0) + (scored[0][0] if scored else -1.0),
        })

    if OUT_PHOTOS.exists():
        shutil.rmtree(OUT_PHOTOS)
    countries = []
    for country in sorted(systems):
        code = country.lower().replace(" ", "-")
        deps = sorted(systems[country], key=lambda d: (-d["best"], d["first"] or "9", d["dep"]))   # best photos first
        out = []
        for i, d in enumerate(deps, 1):
            ph = []
            for k, src in enumerate(d["photos"], 1):
                if src.exists():
                    rel = f"photos/{code}/{i}-{k}.jpg"
                    save_photo(src, SITE / "map" / rel)
                    ph.append(rel)
            out.append({"label": f"System {i}", "records": d["records"], "when": when(d["first"], d["last"]),
                        "images": d["images"] or 0, "photos": ph})
        kinds = {k: sum(k in d["records"] for d in out) for k in ("moths", "sound", "bats")}
        lat, lon = CENTRES[country]
        total = max(sum(d["images"] for d in out), sum(n for b, n in bucket_counts.items()
                                                         if BUCKET_COUNTRY.get(b) == country and b != "saltmarsh-soundscapes"))
        countries.append({"country": country, "lat": lat, "lon": lon, "systems": len(out),
                          "images": total, "kinds": kinds, "deployments": out})
    OUT_JSON.write_text(json.dumps({"as_of": a.as_of, "countries": countries}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(countries)} countries, {sum(c['systems'] for c in countries)} systems, "
          f"{sum(len(d['photos']) for c in countries for d in c['deployments'])} photos -> {OUT_JSON}")


if __name__ == "__main__":
    main()
