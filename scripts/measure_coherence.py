#!/usr/bin/env python3
"""Measures the color coherence of candidate photos with the project's real photos (step B3).

The "yardstick" is the project's color signature, taken from the reference photos:
  1. the list of photos in projects/<slug>/photo-direction.md, if it exists;
  2. otherwise, the project's photos in the catalog with featured = yes and a real origin
     (footage log or legacy).

For each photo it measures six simple things, in the Lab space:
  brightness (mean of L*), contrast (deviation of L*), saturation (mean chroma),
  temperature (mean b*: + warm/yellow, - cool/blue), tint (mean a*: + pinkish,
  - greenish) and palette (hue distribution of the areas with color).

Each measure becomes a deviation relative to the yardstick (median of the references, in units
of the project's normal variation). The distance is the root mean square of these deviations.
Ranks the candidates; eliminates none (a rule is not a filter).

Does not see setting, people or the "stock-photo look": that remains a visual check.

Usage:
    python scripts/measure_coherence.py <photo or folder> --project example-brand
    python scripts/measure_coherence.py previews/ --project other-brand --json
    python scripts/measure_coherence.py photo.jpg --project example-brand --references <folder>

Requires Pillow; uses numpy if it is installed (faster, same result).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is missing. Run:  python -m pip install -r scripts/requirements.txt")

try:
    import numpy as np
except ImportError:  # numpy is optional
    np = None

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
CATALOG = MEDIA / "catalog.csv"
VERSION = 1                # changes when the calculation changes (invalidates the cache)

SIDE = 256                 # longer side of the measured thumbnail
COLOR_CHROMA = 8.0         # minimum chroma for a pixel to "have color" (goes into the palette)
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

# Measures, in display order: key, name, "minimum variation" unit (floor of the
# deviation, so a very homogeneous project does not turn a small difference into a big one),
# and the words for above / below the yardstick.
MEASURES = [
    ("temperature", "temperature", 3.0, "{p}warmer than the project", "{p}cooler than the project"),
    ("saturation", "saturation", 3.0, "saturation {p}above", "saturation {p}below (more washed out)"),
    ("brightness", "brightness", 4.0, "{p}lighter than the project", "{p}darker than the project"),
    ("contrast", "contrast", 2.5, "contrast {p}above", "contrast {p}below (flatter)"),
    ("tint", "tint", 2.0, "tint {p}pulled toward pinkish", "tint {p}pulled toward green"),
]
PALETTE_FLOOR = 0.06
Z_LIMIT = 4.0              # a huge deviation does not dominate the distance on its own

# Bands: |deviation| ≤ 1 inside; ≤ 2 slightly outside; > 2 outside.
BANDS = [(1.0, "inside"), (2.0, "slightly outside"), (math.inf, "outside")]
# Overall distance (root mean square of the deviations).
LEVELS = [(1.0, "coherent"), (2.0, "close"), (math.inf, "off")]

# Hue in Lab (degrees, 0 = +a*, 90 = +b*). Approximate bands, to explain the palette.
HUES = [(0, 30, "red/pink"), (30, 70, "orange/skin"), (70, 110, "yellow"),
        (110, 170, "green"), (170, 230, "cyan"), (230, 290, "blue"),
        (290, 330, "purple"), (330, 360, "magenta")]

VISUAL_WARNING = ("Measures only color and light. Setting, people (from the brand's audience, real), naturalness and "
                  "the \"stock-photo look\" remain a visual check, against the photo direction.")


# ---------------------------------------------------------------- color

def _linear(c8: int) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_LIN = [_linear(v) for v in range(256)]
# linear sRGB → XYZ (D65), already divided by the reference white.
_M = [(0.4124 / 0.95047, 0.3576 / 0.95047, 0.1805 / 0.95047),
      (0.2126, 0.7152, 0.0722),
      (0.0193 / 1.08883, 0.1192 / 1.08883, 0.9505 / 1.08883)]
_E = (6 / 29) ** 3


def _f(t: float) -> float:
    return t ** (1 / 3) if t > _E else t / (3 * (6 / 29) ** 2) + 4 / 29


def thumbnail(path: Path) -> Image.Image:
    with Image.open(path) as im:
        im.draft("RGB", (SIDE * 2, SIDE * 2))  # JPEG decodes already reduced
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((SIDE, SIDE), Image.BILINEAR)
        return im.copy()


def _lab_numpy(im: Image.Image):
    a = np.asarray(im, dtype=np.uint8).reshape(-1, 3)
    lin = np.array(_LIN)[a]
    xyz = lin @ np.array(_M).T
    f = np.where(xyz > _E, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    L = 116 * f[:, 1] - 16
    A = 500 * (f[:, 0] - f[:, 1])
    B = 200 * (f[:, 1] - f[:, 2])
    return L, A, B


def _lab_pure(im: Image.Image):
    px = im.tobytes()
    L, A, B = [], [], []
    for r, g, b in zip(px[0::3], px[1::3], px[2::3]):
        lr, lg, lb = _LIN[r], _LIN[g], _LIN[b]
        fx = _f(_M[0][0] * lr + _M[0][1] * lg + _M[0][2] * lb)
        fy = _f(_M[1][0] * lr + _M[1][1] * lg + _M[1][2] * lb)
        fz = _f(_M[2][0] * lr + _M[2][1] * lg + _M[2][2] * lb)
        L.append(116 * fy - 16)
        A.append(500 * (fx - fy))
        B.append(200 * (fy - fz))
    return L, A, B


def signature(path: Path) -> dict:
    """The six measures of a photo."""
    im = thumbnail(path)
    if np is not None:
        L, A, B = _lab_numpy(im)
        chroma = np.hypot(A, B)
        ang = np.degrees(np.arctan2(B, A)) % 360
        with_color = chroma > COLOR_CHROMA
        hist, _ = np.histogram(ang[with_color], bins=[m[0] for m in HUES] + [360],
                               weights=chroma[with_color])
        med = {"brightness": float(L.mean()), "contrast": float(L.std()),
               "saturation": float(chroma.mean()), "temperature": float(B.mean()),
               "tint": float(A.mean())}
        hist = [float(h) for h in hist]
    else:
        L, A, B = _lab_pure(im)
        n = len(L)
        mL = sum(L) / n
        hist = [0.0] * len(HUES)
        chroma_total = 0.0
        for a, b in zip(A, B):
            c = math.hypot(a, b)
            chroma_total += c
            if c > COLOR_CHROMA:
                ang = math.degrees(math.atan2(b, a)) % 360
                for i, (ini, end, _) in enumerate(HUES):
                    if ini <= ang < end:
                        hist[i] += c
                        break
        med = {"brightness": mL, "contrast": math.sqrt(sum((v - mL) ** 2 for v in L) / n),
               "saturation": chroma_total / n, "temperature": sum(B) / n, "tint": sum(A) / n}
    total = sum(hist)
    med["palette"] = [h / total for h in hist] if total else [0.0] * len(HUES)
    med["px"] = [im.width, im.height]
    return med


def palette_dist(p: list[float], q: list[float]) -> float:
    """0 = same hue distribution; 1 = nothing in common (1 - intersection)."""
    if not sum(p) or not sum(q):
        return 0.0  # photo with almost no color: the palette says nothing
    return 1.0 - sum(min(a, b) for a, b in zip(p, q))


# ---------------------------------------------------------------- statistics

def median(v: list[float]) -> float:
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def spread_of(v: list[float], floor: float) -> float:
    """The project's normal variation: 1.4826 × median absolute deviation (robust), with a floor."""
    m = median(v)
    return max(1.4826 * median([abs(x - m) for x in v]), floor)


def palette_name(p: list[float], n: int = 2) -> str:
    top = sorted(range(len(p)), key=lambda i: -p[i])[:n]
    return " and ".join(f"{HUES[i][2]} {p[i] * 100:.0f}%" for i in top if p[i] > 0.05) or "almost no color"


def build_yardstick(photos: list[Path], source: str) -> dict:
    sigs, errors = [], []
    for f in photos:
        try:
            sigs.append((f, signature(f)))
        except Exception as e:
            errors.append({"file": str(f), "error": str(e)})
    if not sigs:
        raise SystemExit("No reference photo could be read.")
    yardstick = {"source": source, "n": len(sigs), "measures": {}, "errors": errors}
    for key, _, floor, _, _ in MEASURES:
        v = [s[key] for _, s in sigs]
        yardstick["measures"][key] = {"median": median(v), "variation": spread_of(v, floor),
                                      "min": min(v), "max": max(v)}
    k = len(HUES)
    center = [sum(s["palette"][i] for _, s in sigs) / len(sigs) for i in range(k)]
    tot = sum(center) or 1.0
    center = [c / tot for c in center]
    dp = [palette_dist(s["palette"], center) for _, s in sigs]
    yardstick["palette"] = {"center": center, "median": median(dp), "variation": spread_of(dp, PALETTE_FLOOR)}
    # Distance of each reference to its own yardstick: calibrates what is "normal" in the project.
    yardstick["reference_distances"] = sorted(compare(s, yardstick)["distance"] for _, s in sigs)
    yardstick["references"] = [str(f) for f, _ in sigs]
    return yardstick


def band(z: float) -> str:
    for lim, name in BANDS:
        if abs(z) <= lim:
            return name
    return BANDS[-1][1]


def compare(sig: dict, yardstick: dict) -> dict:
    items, zs = [], []
    for key, name, _, above, below in MEASURES:
        r = yardstick["measures"][key]
        z = (sig[key] - r["median"]) / r["variation"]
        zs.append(max(-Z_LIMIT, min(Z_LIMIT, z)))
        f = band(z)
        if f == "inside":
            phrase = f"{name} inside"
        else:
            phrase = (above if z > 0 else below).format(p="slightly " if f == "slightly outside" else "")
        items.append({"measure": key, "value": round(sig[key], 1), "yardstick": round(r["median"], 1),
                      "deviation": round(z, 2), "band": f, "phrase": phrase})
    rp = yardstick["palette"]
    d = palette_dist(sig["palette"], rp["center"])
    zp = max(0.0, (d - rp["median"]) / rp["variation"])  # only "more different than normal" counts
    zs.append(min(Z_LIMIT, zp))
    fp = band(zp)
    phrase = ("palette inside" if fp == "inside"
              else f"{'slightly ' if fp == 'slightly outside' else ''}different palette "
                   f"({palette_name(sig['palette'])}; project: {palette_name(rp['center'])})")
    items.append({"measure": "palette", "value": round(d, 3), "yardstick": round(rp["median"], 3),
                  "deviation": round(zp, 2), "band": fp, "phrase": phrase})
    dist = math.sqrt(sum(z * z for z in zs) / len(zs))
    return {"distance": round(dist, 2), "items": items}


def level(d: float) -> str:
    for lim, name in LEVELS:
        if d <= lim:
            return name
    return LEVELS[-1][1]


# ---------------------------------------------------------------- references

PATH_PATTERN = re.compile(r"(?:media/)?((?:open|restricted)/[^\s`'\"()\[\]<>|,;]+?\.(?:jpe?g|png|webp|tiff?|bmp))",
                          re.IGNORECASE)


def refs_from_direction(slug: str) -> tuple[list[Path], list[str]] | None:
    """media/ paths cited in photo-direction.md (in the references section, if there is one)."""
    f = ROOT / "projects" / slug / "photo-direction.md"
    if not f.exists():
        return None
    txt = f.read_text(encoding="utf-8")
    # If there is a section whose title mentions "reference", read only that one.
    sections = re.split(r"(?m)^(#{1,6} .*)$", txt)
    excerpt = ""
    for i in range(1, len(sections) - 1, 2):
        if "refer" in sections[i].lower():
            excerpt += sections[i + 1]
    found = PATH_PATTERN.findall(excerpt or txt)
    seen, photos, missing = set(), [], []
    for c in found:
        if c in seen:
            continue
        seen.add(c)
        p = MEDIA / c
        (photos if p.is_file() else missing).append(p if p.is_file() else c)
    return photos, missing


def refs_from_catalog(slug: str) -> list[Path]:
    with open(CATALOG, encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        rows = list(csv.DictReader(f, delimiter=";" if sample.count(";") > sample.count(",") else ","))
    photos = []
    for l in rows:
        projects = {p.strip() for p in re.split(r"[,;]", l.get("projects", ""))}
        origin = l.get("origin", "").split(":")[0].strip()
        if (slug in projects and l.get("type") == "photo" and origin in ("footage-log", "legacy")
                and l.get("featured", "").strip().lower() == "yes"):
            p = MEDIA / l["file"]
            if p.is_file():
                photos.append(p)
    return photos


def cache_key(photos: list[Path], source: str) -> str:
    h = hashlib.sha1(f"v{VERSION}|{SIDE}|{COLOR_CHROMA}|{source}".encode())
    for f in sorted(photos):
        st = f.stat()
        h.update(f"{f}|{st.st_size}|{int(st.st_mtime)}".encode())
    return h.hexdigest()[:16]


def get_yardstick(slug: str, references: list[str] | None, cache_folder: Path | None) -> tuple[dict, list[str]]:
    warnings = []
    if references:
        photos, source = list_files(references), "--references"
    else:
        d = refs_from_direction(slug)
        photos = []
        if d is not None:
            photos, missing = d
            for c in missing:
                warnings.append(f"reference cited in photo-direction.md not found: {c}")
            if not photos:
                warnings.append("photo-direction.md exists, but does not cite photos from media/; used the catalog")
        source = f"projects/{slug}/photo-direction.md"
        if not photos:
            photos, source = refs_from_catalog(slug), "catalog: featured = yes, origin footage-log/legacy"
    if not photos:
        raise SystemExit(f"No reference photos for the project '{slug}'.")
    if len(photos) < 8:
        warnings.append(f"only {len(photos)} reference photos: the yardstick is fragile")
    yardstick = None
    cache_file = None
    if cache_folder is not None:
        cache_file = cache_folder / f"{slug}-{cache_key(photos, source)}.json"
        if cache_file.exists():
            try:
                yardstick = json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                yardstick = None
    if yardstick is None:
        yardstick = build_yardstick(photos, source)
        if cache_file is not None:
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(yardstick, ensure_ascii=False), encoding="utf-8")
            except OSError:
                pass
    else:
        yardstick["cache"] = str(cache_file)
    for e in yardstick.get("errors", []):
        warnings.append(f"could not read the reference {e['file']}: {e['error']}")
    return yardstick, warnings


# ---------------------------------------------------------------- input and output

def list_files(inputs: list[str]) -> list[Path]:
    files = []
    for e in inputs:
        p = Path(e)
        if p.is_dir():
            files += sorted(f for f in p.iterdir() if f.suffix.lower() in EXTENSIONS)
        elif p.is_file():
            files.append(p)
        else:
            print(f"warning: could not find {e}", file=sys.stderr)
    return files


def ref_percentile(d: float, dists: list[float]) -> int:
    """What share of the project's own photos is closer to the yardstick than the candidate."""
    return round(100 * sum(1 for x in dists if x < d) / len(dists)) if dists else 0


def summary(items: list[dict]) -> str:
    outside = [i for i in items if i["band"] != "inside"]
    outside.sort(key=lambda i: -abs(i["deviation"]))
    inside = [i["measure"] for i in items if i["band"] == "inside"]
    parts = [i["phrase"] for i in outside]
    if inside:
        parts.append(("inside: " if outside else "all inside: ") + ", ".join(inside))
    return "; ".join(parts)


def text_report(slug: str, yardstick: dict, results: list[dict], errors: list[dict], warnings: list[str]) -> str:
    m = yardstick["measures"]
    l = [f"Color coherence with the project {slug} · yardstick: {yardstick['n']} photos ({yardstick['source']})"
         + (" · from the cache" if yardstick.get("cache") else ""),
         "Yardstick (median ± normal variation): "
         + " · ".join(f"{name} {m[k]['median']:.1f}±{m[k]['variation']:.1f}" for k, name, *_ in MEASURES)
         + f" · palette {palette_name(yardstick['palette']['center'], 3)}",
         "Distance: root mean square of the deviations. <= 1 coherent · 1–2 close · > 2 off", ""]
    for i, r in enumerate(results, 1):
        l.append(f"{i}. {Path(r['file']).name}  distance {r['distance']:.2f}  {r['level']}"
                 f"  (farther than {r['ref_percentile']}% of the project's photos)")
        l.append(f"   {r['summary']}")
        l.append("   " + "  ".join(f"{it['measure'][:5]} {it['deviation']:+.1f}" for it in r["items"]))
    l.append("")
    for e in errors:
        l.append(f"could not read {e['file']}: {e['error']}")
    for a in warnings:
        l.append(f"warning: {a}")
    l.append("Order, not filter: no candidate is eliminated. " + VISUAL_WARNING)
    return "\n".join(l)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # accents in the Windows console
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Measures the color coherence of the candidates with the project's photos (B3).")
    ap.add_argument("inputs", nargs="+", help="candidate photos or folders")
    ap.add_argument("--project", required=True, help="project slug (e.g. example-brand)")
    ap.add_argument("--references", nargs="+", metavar="PHOTO_OR_FOLDER",
                    help="uses these photos as the yardstick, instead of the photo direction and the catalog")
    ap.add_argument("--json", action="store_true", help="output in JSON, for other steps")
    ap.add_argument("--cache", default=str(Path(tempfile.gettempdir()) / "carousel-coherence"),
                    help="yardstick cache folder (default: the system's temporary folder)")
    ap.add_argument("--no-cache", action="store_true", help="recalculates the yardstick without reading or writing the cache")
    a = ap.parse_args()

    if not (ROOT / "projects" / a.project).is_dir():
        print(f"warning: projects/{a.project}/ does not exist", file=sys.stderr)
    yardstick, warnings = get_yardstick(a.project, a.references, None if a.no_cache else Path(a.cache))

    files = list_files(a.inputs)
    if not files:
        print("No image found.", file=sys.stderr)
        return 1
    results, errors = [], []
    for f in files:
        try:
            sig = signature(f)
        except Exception as e:
            errors.append({"file": str(f), "error": str(e)})
            continue
        c = compare(sig, yardstick)
        results.append({"file": str(f), "distance": c["distance"], "level": level(c["distance"]),
                        "ref_percentile": ref_percentile(c["distance"], yardstick["reference_distances"]),
                        "summary": summary(c["items"]), "items": c["items"]})
    results.sort(key=lambda r: r["distance"])

    if a.json:
        print(json.dumps({
            "project": a.project,
            "yardstick": {"source": yardstick["source"], "n": yardstick["n"], "cache": yardstick.get("cache"),
                          "measures": {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in yardstick["measures"].items()},
                          "palette": palette_name(yardstick["palette"]["center"], 3)},
            "parameters": {"side": SIDE, "color_chroma": COLOR_CHROMA, "deviation_limit": Z_LIMIT,
                           "bands": {"inside": 1, "slightly outside": 2}, "levels": {"coherent": 1, "close": 2},
                           "numpy": np is not None},
            "photos": results, "errors": errors, "warnings": warnings, "warning": VISUAL_WARNING,
        }, ensure_ascii=False, indent=2))
    else:
        print(text_report(a.project, yardstick, results, errors, warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
