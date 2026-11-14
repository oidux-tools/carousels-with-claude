#!/usr/bin/env python3
"""Media bank indexer.

Walks media/, reads the technical specifications of each file and updates
media/catalog.csv. The manual columns (projects, tags, origin) are never
overwritten; `projects` is only suggested from the file name when it is empty.
The `uses` and `last_used` columns are always recalculated from the log
media/uses.csv (one row per image used in a delivered piece).

Usage:
    python scripts/index_media.py             updates the catalog
    python scripts/index_media.py --dry-run   shows what would change, without writing
    python scripts/index_media.py --prune     also removes from the catalog files that no longer exist

Requires Pillow:  python -m pip install -r scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is missing. Run:  python -m pip install -r scripts/requirements.txt")

Image.MAX_IMAGE_PIXELS = None  # large stock photos are normal; we only read the header

COLUMNS = ["file", "area", "type", "format", "width", "height", "aspect_ratio",
           "duration_s", "size_mb", "projects", "tags", "origin", "added_on",
           "uses", "last_used"]
USES_COLUMNS = ["date", "file", "project", "piece", "notion_task", "slide", "topic"]
VALID_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

IGNORE = {".gitkeep", "desktop.ini", "thumbs.db", ".ds_store"}
VALID_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*_[a-z0-9]+(?:-[a-z0-9]+)*(?:_\d{2})?\.[a-z0-9]+$")

RATIOS = {"1:1": 1.0, "4:5": 0.8, "5:4": 1.25, "3:4": 0.75, "4:3": 4 / 3, "2:3": 2 / 3,
          "3:2": 1.5, "9:16": 9 / 16, "16:9": 16 / 9, "1.91:1": 1.91}

MINIMUMS = {"photo": "shorter side >= 1080 px", "background": ">= 1080 x 1350 px"}


def below_minimum(kind: str, w: int, h: int) -> bool:
    if kind == "photo":
        return min(w, h) < 1080
    if kind == "background":
        return min(w, h) < 1080 or max(w, h) < 1350
    return False


def aspect_ratio(w, h) -> str:
    """Snaps to the closest common ratio (2% tolerance); otherwise, returns a decimal."""
    if not w or not h:
        return ""
    r = w / h
    for name, target in RATIOS.items():
        if abs(r - target) / target <= 0.02:
            return name
    return f"{r:.2f}:1"


# ---------------------------------------------------------------- readers

def read_image(path: Path) -> dict:
    with Image.open(path) as img:
        w, h = img.size
        try:
            if img.getexif().get(0x0112) in (5, 6, 7, 8):  # phone photo rotated via EXIF
                w, h = h, w
        except Exception:
            pass
    return {"width": w, "height": h}


def _px(value):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?|\.\d+)\s*(?:px)?\s*", value or "")
    return float(m.group(1)) if m else None


def read_svg(path: Path) -> dict:
    with open(path, "rb") as f:
        for _, root in ET.iterparse(f, events=("start",)):
            w, h = _px(root.get("width")), _px(root.get("height"))
            if not (w and h) and root.get("viewBox"):
                parts = re.split(r"[\s,]+", root.get("viewBox").strip())
                if len(parts) == 4:
                    w, h = float(parts[2]), float(parts[3])
            return {"width": round(w), "height": round(h)} if w and h else {}
    return {}


def _boxes(data: bytes, start: int = 0, end: int | None = None):
    """Iterates (type, content start, end) of the MP4/MOV boxes inside `data`."""
    end = len(data) if end is None else end
    pos = start
    while pos + 8 <= end:
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        head = 8
        if size == 1:
            size, head = struct.unpack(">Q", data[pos + 8:pos + 16])[0], 16
        elif size == 0:
            size = end - pos
        if size < head:
            return
        yield kind, pos + head, min(pos + size, end)
        pos += size


def _read_moov(f) -> bytes | None:
    """Finds the 'moov' box (metadata) without loading the whole video."""
    f.seek(0, 2)
    total, pos = f.tell(), 0
    while pos + 8 <= total:
        f.seek(pos)
        head = f.read(16)
        size, kind = struct.unpack(">I4s", head[:8])
        n = 8
        if size == 1:
            size, n = struct.unpack(">Q", head[8:16])[0], 16
        elif size == 0:
            size = total - pos
        if size < n:
            return None
        if kind == b"moov":
            f.seek(pos + n)
            return f.read(size - n)
        pos += size
    return None


def read_mp4(path: Path) -> dict:
    with open(path, "rb") as f:
        moov = _read_moov(f)
    if not moov:
        return {}
    info = {}
    for kind, ini, end in _boxes(moov):
        if kind == b"mvhd":
            if moov[ini] == 1:
                scale, dur = struct.unpack(">IQ", moov[ini + 20:ini + 32])
            else:
                scale, dur = struct.unpack(">II", moov[ini + 12:ini + 20])
            if scale:
                info["duration_s"] = dur / scale
        elif kind == b"trak" and "width" not in info:
            for t2, i2, _ in _boxes(moov, ini, end):
                if t2 != b"tkhd":
                    continue
                m = i2 + (52 if moov[i2] == 1 else 40)  # start of the transformation matrix
                a, _b, _u, _c, d = struct.unpack(">5i", moov[m:m + 20])
                w, h = (v >> 16 for v in struct.unpack(">II", moov[m + 36:m + 44]))
                if w and h:  # an audio track is 0 x 0
                    if a == 0 and d == 0:  # video recorded upright (90°/270° rotation)
                        w, h = h, w
                    info["width"], info["height"] = w, h
    return info


def read_wav(path: Path) -> dict:
    with open(path, "rb") as f:
        riff, _, wave = struct.unpack("<4sI4s", f.read(12))
        if riff != b"RIFF" or wave != b"WAVE":
            return {}
        bytes_per_s = None
        while True:
            head = f.read(8)
            if len(head) < 8:
                return {}
            cid, size = struct.unpack("<4sI", head)
            if cid == b"data":
                return {"duration_s": size / bytes_per_s} if bytes_per_s else {}
            if cid == b"fmt ":
                bytes_per_s = struct.unpack("<I", f.read(size)[8:12])[0]
            else:
                f.seek(size, 1)
            if size % 2:
                f.seek(1, 1)


_KBPS = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
         2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
_HZ = [44100, 48000, 32000]


def read_mp3(path: Path) -> dict:
    file_size = path.stat().st_size
    with open(path, "rb") as f:
        head = f.read(10)
        start = 0
        if head[:3] == b"ID3":  # skips the ID3v2 tag (cover, title…)
            start = 10 + ((head[6] & 0x7F) << 21 | (head[7] & 0x7F) << 14 | (head[8] & 0x7F) << 7 | (head[9] & 0x7F))
            if head[5] & 0x10:
                start += 10
        f.seek(start)
        block = f.read(64 * 1024)
    for i in range(len(block) - 4):
        if block[i] != 0xFF or (block[i + 1] & 0xE0) != 0xE0:
            continue
        version = (block[i + 1] >> 3) & 3  # 3 = MPEG1, 2 = MPEG2, 0 = MPEG2.5
        layer = (block[i + 1] >> 1) & 3  # 1 = Layer III
        br, hz = block[i + 2] >> 4, (block[i + 2] >> 2) & 3
        if version == 1 or layer != 1 or br in (0, 15) or hz == 3:
            continue
        mpeg1 = version == 3
        rate = _HZ[hz] // (1 if mpeg1 else 2 if version == 2 else 4)
        mono = (block[i + 3] >> 6) == 3
        xing = i + 4 + ((17 if mono else 32) if mpeg1 else (9 if mono else 17))
        if block[xing:xing + 4] in (b"Xing", b"Info"):  # VBR: the header carries the number of frames
            if struct.unpack(">I", block[xing + 4:xing + 8])[0] & 1:
                frames = struct.unpack(">I", block[xing + 8:xing + 12])[0]
                return {"duration_s": frames * (1152 if mpeg1 else 576) / rate}
        kbps = _KBPS[1 if mpeg1 else 2][br]  # CBR: estimate by size
        return {"duration_s": (file_size - start - i) * 8 / (kbps * 1000)}
    return {}


READERS = {
    **dict.fromkeys(["jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff", "psd"], read_image),
    "svg": read_svg,
    **dict.fromkeys(["mp4", "mov", "m4v", "m4a"], read_mp4),
    "wav": read_wav,
    "mp3": read_mp3,
}


# ---------------------------------------------------------------- catalog

def load_catalog(path: Path) -> tuple[dict, list]:
    """Returns (rows by file, extra columns someone created by hand)."""
    if not path.exists():
        return {}, []
    text = path.read_text(encoding="utf-8-sig")  # tolerates Excel's BOM
    first = text.split("\n", 1)[0]
    sep = ";" if first.count(";") > first.count(",") else ","  # Excel in some locales (e.g. pt-BR) saves with ;
    reader = csv.DictReader(io.StringIO(text), delimiter=sep)
    extras = [c for c in (reader.fieldnames or []) if c and c not in COLUMNS]
    rows = {}
    for row in reader:
        key = (row.get("file") or "").strip().replace("\\", "/")
        if key:
            row["file"] = key
            rows[key] = row
    return rows, extras


def load_projects(path: Path) -> set:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {(l.get("slug") or "").strip() for l in csv.DictReader(f)} - {""}


def load_uses(path: Path, valid_projects: set, warnings: list) -> dict:
    """Reads the usage log and returns {file: (count, most recent date)}."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig")
    first = text.split("\n", 1)[0]
    sep = ";" if first.count(";") > first.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=sep)
    missing = [c for c in USES_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        warnings.append(f"uses.csv: missing columns {', '.join(missing)}")
    count, seen = {}, set()
    for n, l in enumerate(reader, start=2):  # line 1 is the header
        file = (l.get("file") or "").strip().replace("\\", "/")
        when = (l.get("date") or "").strip()
        project = (l.get("project") or "").strip()
        if not any((v or "").strip() for v in l.values()):
            continue
        if not file:
            warnings.append(f"uses.csv line {n}: no file (ignored)")
            continue
        if not VALID_DATE.match(when):
            warnings.append(f"uses.csv line {n}: date '{when}' not in the YYYY-MM-DD format")
        if valid_projects and project and project not in valid_projects:
            warnings.append(f"uses.csv line {n}: project '{project}' is not in projects.csv")
        key = (file, (l.get("piece") or "").strip(), (l.get("slide") or "").strip())
        if key in seen:
            warnings.append(f"uses.csv line {n}: repeats file + piece + slide of a previous line")
        seen.add(key)
        qty, last = count.get(file, (0, ""))
        last = max(last, when) if VALID_DATE.match(when) else last
        count[file] = (qty + 1, last)
    return count


def generate_csv(rows: list, columns: list) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({c: row.get(c) or "" for c in columns})
    return buf.getvalue()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Updates media/catalog.csv from the files in the bank.")
    ap.add_argument("--media", type=Path, default=Path(__file__).resolve().parent.parent / "media",
                    help="bank folder (default: the repository's media/)")
    ap.add_argument("--dry-run", action="store_true", help="shows the result without writing the catalog")
    ap.add_argument("--prune", action="store_true", help="removes from the catalog files that no longer exist")
    args = ap.parse_args()

    media = args.media.resolve()
    if not media.is_dir():
        print(f"Folder not found: {media}")
        return 1
    catalog_file = media / "catalog.csv"
    catalog, extras = load_catalog(catalog_file)
    valid_projects = load_projects(media / "projects.csv")
    columns = COLUMNS + extras
    today = date.today().isoformat()

    new, changed, warnings, seen = [], [], [], set()
    in_inbox = 0
    uses = load_uses(media / "uses.csv", valid_projects, warnings)

    def list_files(folder: Path) -> list:
        return sorted(a for a in folder.rglob("*")
                      if a.is_file() and a.name.lower() not in IGNORE
                      and not a.name.startswith(("~$", "_")))

    def subfolders(folder: Path) -> list:
        return sorted(p for p in folder.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))

    # two areas: open/<type>/ and restricted/<project>/<type>/ (decision of 2026-11-14)
    groups = []  # (area, type, files)
    for folder in sorted(p for p in media.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if folder.name.startswith("_"):  # _inbox/ and the like do not go into the catalog
            in_inbox += len(list_files(folder))
        elif folder.name == "open":
            groups += [("open", t.name, list_files(t)) for t in subfolders(folder)]
        elif folder.name == "restricted":
            for proj in subfolders(folder):
                if valid_projects and proj.name not in valid_projects:
                    warnings.append(f"restricted/{proj.name}/: project is not in projects.csv")
                groups += [(f"restricted:{proj.name}", t.name, list_files(t)) for t in subfolders(proj)]
        else:
            warnings.append(f"{folder.name}/: folder outside the standard (use open/ or restricted/<project>/); not cataloged")

    for area, kind, files in groups:
        for f in files:
            rel = f.relative_to(media).as_posix()
            seen.add(rel)
            ext = f.suffix.lower().lstrip(".")

            tech = {}
            if ext in READERS:
                try:
                    tech = READERS[ext](f) or {}
                except Exception as e:
                    warnings.append(f"{rel}: could not read the specifications ({e.__class__.__name__})")
            w, h, dur = tech.get("width"), tech.get("height"), tech.get("duration_s")

            row = catalog.get(rel)
            is_new = row is None
            if is_new:
                row = {"file": rel, "added_on": today}
                catalog[rel] = row
                new.append(rel)
            before = {c: row.get(c) or "" for c in columns}

            row.update({
                "area": area,
                "type": kind,
                "format": ext,
                "width": str(w) if w else "",
                "height": str(h) if h else "",
                "aspect_ratio": aspect_ratio(w, h),
                "duration_s": f"{dur:.1f}" if dur else "",
                "size_mb": f"{f.stat().st_size / 1_048_576:.2f}",
                "uses": str(uses.get(rel, (0, ""))[0]),
                "last_used": uses.get(rel, (0, ""))[1],
            })

            prefix = f.name.split("_", 1)[0] if "_" in f.name else ""
            if not (row.get("projects") or "").strip():
                if area.startswith("restricted:"):
                    row["projects"] = area.split(":", 1)[1]  # in the restricted area, the project is the folder
                elif prefix in valid_projects:
                    row["projects"] = prefix  # suggestion from the name; whoever edits by hand rules

            if not is_new and before != {c: row.get(c) or "" for c in columns}:
                changed.append(rel)

            if not VALID_NAME.match(f.name):
                warnings.append(f"{rel}: name outside the convention <project>_<description>_<nn>.<ext>")
            elif valid_projects and prefix not in valid_projects:
                warnings.append(f"{rel}: project '{prefix}' is not in projects.csv")
            unknown = [s for s in (row.get("projects") or "").split("|")
                       if s.strip() and s.strip() not in valid_projects]
            if valid_projects and unknown:
                warnings.append(f"{rel}: projects column has an unknown slug: {', '.join(unknown)}")
            if w and h and below_minimum(kind, w, h):
                warnings.append(f"{rel}: {w}x{h} px, below the minimum for {kind} ({MINIMUMS[kind]})")

    absent = sorted(set(catalog) - seen)
    if args.prune:
        for rel in absent:
            del catalog[rel]
    for rel in absent:  # row kept without a file: the uses keep coming from the log
        if rel in catalog:
            catalog[rel]["uses"] = str(uses.get(rel, (0, ""))[0])
            catalog[rel]["last_used"] = uses.get(rel, (0, ""))[1]
    for file in sorted(set(uses) - set(catalog)):
        warnings.append(f"uses.csv: '{file}' is not in the catalog ({uses[file][0]} use(s) without a matching image)")

    new_text = generate_csv([catalog[k] for k in sorted(catalog)], columns)
    current_text = catalog_file.read_text(encoding="utf-8-sig") if catalog_file.exists() else ""

    # ---- report
    print(f"Media bank: {media}")
    print(f"  {len(seen)} file(s) cataloged: {len(new)} new, {len(changed)} changed")
    for rel in new:
        print(f"    + {rel}")
    for rel in changed:
        print(f"    ~ {rel}")
    if in_inbox:
        print(f"  {in_inbox} file(s) in _inbox/ waiting for triage")
    if absent:
        action = "removed from the catalog" if args.prune else "in the catalog without a file (use --prune to remove)"
        print(f"  {len(absent)} {action}:")
        for rel in absent:
            print(f"    - {rel}")
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for a in warnings:
            print(f"  ! {a}")

    if args.dry_run:
        print("\nDry run: nothing was written.")
    elif new_text == current_text:
        print("\nCatalog was already up to date.")
    else:
        tmp = catalog_file.with_name("catalog.csv.tmp")
        try:
            tmp.write_text(new_text, encoding="utf-8", newline="")
            os.replace(tmp, catalog_file)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            print("\nCould not write: the catalog is open in another program (Excel?). Close it and run again.")
            return 1
        print("\nCatalog updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
