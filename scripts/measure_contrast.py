#!/usr/bin/env python3
"""Measures the contrast of the cream text over each photo, per text block position (step B3).

For each image, crops the way the slide would crop (fill, centered), applies the
Contrast layer (#141414 at 10% in Linear Burn) and compares the text cream (#F0EBDC)
with the 95th percentile of the luminance of the background behind the block (block + margin),
in five positions: top-left, top-right, bottom-left, bottom-right and center.

Ranks positions and photos; eliminates nothing (a rule is not a filter). Does not see faces or
the spread's seam: those remain a visual check.

Usage:
    python scripts/measure_contrast.py photo1.jpg photo2.jpg
    python scripts/measure_contrast.py <folder> --format spread
    python scripts/measure_contrast.py <folder> --block 700x400 --json

Requires Pillow; uses numpy if it is installed (faster and at full resolution).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageStat
except ImportError:
    sys.exit("Pillow is missing. Run:  python -m pip install -r scripts/requirements.txt")

try:
    import numpy as np
except ImportError:  # numpy is optional
    np = None

Image.MAX_IMAGE_PIXELS = None

# ---------------------------------------------------------------- brand parameters

W, H = 1080, 1350          # Instagram slide (4:5)
MARGIN = 90                # slide margin
DEFAULT_BLOCK = (570, 480) # approximate text block (width x height)
SLACK = 40                 # "block + 40 px": 20 px on each side
CREAM = (240, 235, 220)    # #F0EBDC
CONTRAST_RGB = 20          # #141414
CONTRAST_OPACITY = 0.10    # 10%, Linear Burn
PERCENTILE = 95

TARGET = 4.5               # recommended
MINIMUM = 3.0              # non-negotiable
MOTION_LIMIT = 40.0        # standard deviation of the gray (0–255) above which the background is "busy"

POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

VISUAL_WARNING = ("Face and seam are not measured: check in the review board screenshot "
                  "(text over a face and a hard cut at the seam are non-negotiable).")


# ---------------------------------------------------------------- color

def _linear(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


L_CREAM = luminance(CREAM)


def ratio(l_background: float) -> float:
    light, dark = max(L_CREAM, l_background), min(L_CREAM, l_background)
    return (light + 0.05) / (dark + 0.05)


def _contrast_layer(v: float) -> float:
    """Linear Burn of #141414 at 10% over a channel (0–255)."""
    burned = max(0.0, v + CONTRAST_RGB - 255)
    return (1 - CONTRAST_OPACITY) * v + CONTRAST_OPACITY * burned


# Table per channel: value 0–255 → linear contribution already with the Contrast layer.
_TAB = [_linear(_contrast_layer(v)) for v in range(256)]
_WEIGHTS = (0.2126, 0.7152, 0.0722)


# ---------------------------------------------------------------- image

def fill(im: Image.Image, w: int, h: int) -> Image.Image:
    """Centered FILL-type crop (how the photo goes into the slide)."""
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


class Luminances:
    """Luminance map of the slide, with numpy (full resolution) or without (1 every 2 px)."""

    def __init__(self, slide: Image.Image):
        if np is not None:
            tab = np.array(_TAB)
            a = np.asarray(slide, dtype=np.uint8)
            self.map = (_WEIGHTS[0] * tab[a[..., 0]] + _WEIGHTS[1] * tab[a[..., 1]]
                        + _WEIGHTS[2] * tab[a[..., 2]])
            self.step = 1
        else:
            self.step = 2
            red = slide.resize((slide.width // 2, slide.height // 2), Image.NEAREST)
            t = [[p * v for v in _TAB] for p in _WEIGHTS]
            px = red.tobytes()  # interleaved RGB
            data = [t[0][r] + t[1][g] + t[2][b] for r, g, b in zip(px[0::3], px[1::3], px[2::3])]
            self.width = red.width
            self.map = data

    def percentile(self, box, pct: float) -> float:
        x0, y0, x1, y1 = box
        if np is not None:
            return float(np.percentile(self.map[y0:y1, x0:x1], pct))
        p = self.step
        x0, y0, x1, y1 = x0 // p, y0 // p, x1 // p, y1 // p
        vals = []
        for y in range(y0, y1):
            base = y * self.width
            vals.extend(self.map[base + x0:base + x1])
        vals.sort()
        k = (len(vals) - 1) * pct / 100
        i = int(k)
        j = min(i + 1, len(vals) - 1)
        return vals[i] + (vals[j] - vals[i]) * (k - i)


def boxes(block: tuple[int, int]) -> dict[str, tuple[int, int, int, int]]:
    """Area measured in each position: the block against the margin, plus the slack, inside the slide."""
    bw, bh = block
    f = SLACK // 2
    xs = {"left": MARGIN, "right": W - MARGIN - bw, "middle": (W - bw) // 2}
    ys = {"top": MARGIN, "bottom": H - MARGIN - bh, "middle": (H - bh) // 2}
    pos = {"top-left": ("left", "top"), "top-right": ("right", "top"), "bottom-left": ("left", "bottom"),
           "bottom-right": ("right", "bottom"), "center": ("middle", "middle")}
    r = {}
    for name, (cx, cy) in pos.items():
        x, y = xs[cx], ys[cy]
        r[name] = (max(0, x - f), max(0, y - f), min(W, x + bw + f), min(H, y + bh + f))
    return r


def level(r: float, busy: bool) -> str:
    if r < MINIMUM:
        return "below"
    if r < TARGET or busy:
        return "review"
    return "ok"


LEVEL_ORDER = {"ok": 0, "review": 1, "below": 2}


def measure_slide(slide: Image.Image, block, half: str | None, limit: float) -> list[dict]:
    lum = Luminances(slide)
    gray = slide.convert("L")
    res = []
    for name, box in boxes(block).items():
        r = ratio(lum.percentile(box, PERCENTILE))
        deviation = ImageStat.Stat(gray.crop(box)).stddev[0]
        busy = deviation > limit
        notes = []
        if busy:
            notes.append("busy background")
        # In the spread, the inner side of each half is next to the seam.
        if (half == "left" and name.endswith("right")) or (half == "right" and name.endswith("left")):
            notes.append("next to the seam")
        res.append({"position": name, "ratio": round(r, 2), "level": level(r, busy),
                    "variation": round(deviation, 1), "notes": notes})
    # Best first: level, then away from the seam, then ratio.
    res.sort(key=lambda p: (LEVEL_ORDER[p["level"]], "next to the seam" in p["notes"], -p["ratio"]))
    return res


def analyze(path: Path, fmt: str, block, limit: float = MOTION_LIMIT) -> dict:
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    if fmt == "spread":
        s = fill(im, 2 * W, H)
        halves = {"left": measure_slide(s.crop((0, 0, W, H)), block, "left", limit),
                  "right": measure_slide(s.crop((W, 0, 2 * W, H)), block, "right", limit)}
    else:
        halves = {"slide": measure_slide(fill(im, W, H), block, None, limit)}
    # Photo score: the worst of the best positions (in the spread, both halves need text).
    best = [m[0] for m in halves.values()]
    worst = min(best, key=lambda p: (-LEVEL_ORDER[p["level"]], p["ratio"]))
    return {"file": str(path), "format": fmt, "source_px": list(im.size),
            "level": worst["level"], "best_ratio": worst["ratio"], "halves": halves}


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


def block_arg(txt: str) -> tuple[int, int]:
    try:
        w, h = (int(v) for v in txt.lower().split("x"))
    except ValueError:
        raise argparse.ArgumentTypeError("use WIDTHxHEIGHT, e.g. 570x480")
    if not (0 < w <= W - 2 * MARGIN and 0 < h <= H - 2 * MARGIN):
        raise argparse.ArgumentTypeError(f"the block must fit in the usable area ({W - 2 * MARGIN}x{H - 2 * MARGIN})")
    return w, h


def text_report(results: list[dict], block, errors: list[dict]) -> str:
    l = [f"Contrast of cream #F0EBDC · Contrast layer on · block {block[0]}x{block[1]} + {SLACK} px",
         f"ok >= {TARGET} · review {MINIMUM}–{TARGET} or busy background · below < {MINIMUM}", ""]
    for r in results:
        l.append(f"{Path(r['file']).name}  ({r['format']}, {r['source_px'][0]}x{r['source_px'][1]})")
        for half, positions in r["halves"].items():
            pre = "  " if half == "slide" else f"  [{half}] "
            for p in positions:
                notes = f"  · {', '.join(p['notes'])}" if p["notes"] else ""
                l.append(f"{pre}{p['position']:<12} {p['ratio']:>5.2f}:1  {p['level']:<8}"
                         f" variation {p['variation']:>5.1f}{notes}")
        l.append("")
    if results:
        l.append("Order of the photos (best first; nothing is eliminated):")
        for i, r in enumerate(results, 1):
            where = " / ".join(ps[0]["position"] if m == "slide" else f"{m} {ps[0]['position']}"
                               for m, ps in r["halves"].items())
            l.append(f"  {i}. {Path(r['file']).name:<40} {r['best_ratio']:>5.2f}:1  {r['level']:<8} {where}")
        l.append("")
    for e in errors:
        l.append(f"could not read {e['file']}: {e['error']}")
    l.append(VISUAL_WARNING)
    return "\n".join(l)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # accents in the Windows console
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Measures the contrast of the cream text per position, to rank photos (B3).")
    ap.add_argument("inputs", nargs="+", help="images or folders")
    ap.add_argument("--format", choices=["slide", "spread"], default="slide",
                    help="slide 1080x1350 (default) or spread 2160x1350 measured in two halves")
    ap.add_argument("--block", type=block_arg, default=DEFAULT_BLOCK,
                    help=f"approximate size of the text block, WxH (default {DEFAULT_BLOCK[0]}x{DEFAULT_BLOCK[1]})")
    ap.add_argument("--json", action="store_true", help="output in JSON, for other steps")
    ap.add_argument("--motion-limit", type=float, default=MOTION_LIMIT,
                    help=f"standard deviation of the gray above which the background counts as busy (default {MOTION_LIMIT:g})")
    a = ap.parse_args()

    files = list_files(a.inputs)
    if not files:
        print("No image found.", file=sys.stderr)
        return 1
    results, errors = [], []
    for f in files:
        try:
            results.append(analyze(f, a.format, a.block, a.motion_limit))
        except Exception as e:  # corrupted file or format Pillow cannot open
            errors.append({"file": str(f), "error": str(e)})
    results.sort(key=lambda r: (LEVEL_ORDER[r["level"]], -r["best_ratio"]))

    if a.json:
        print(json.dumps({
            "parameters": {"cream": "#F0EBDC", "layer": "#141414 10% Linear Burn", "percentile": PERCENTILE,
                           "slide": [W, H], "margin": MARGIN, "block": list(a.block), "slack": SLACK,
                           "target": TARGET, "minimum": MINIMUM, "motion_limit": a.motion_limit,
                           "numpy": np is not None},
            "photos": results, "errors": errors, "warning": VISUAL_WARNING,
        }, ensure_ascii=False, indent=2))
    else:
        print(text_report(results, a.block, errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
