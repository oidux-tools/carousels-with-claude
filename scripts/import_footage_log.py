#!/usr/bin/env python3
"""Imports a footage log folder into the media bank.

The footage logging (done outside this repository) delivers:
    <source>/<Person or subject>/<Person>_<NNN>[_featured].<ext>
    <source>/catalog.csv   (separated by ;, one row per file, columns "file" and "folder")

The importer:
  - copies each photo in an optimized version (longer side 2400 px), with no metadata other than
    author and copyright; videos go as they are;
  - open area (default): media/open/<type>/<project>_<group>-<NNN>.<ext>, where <group> is the
    folder name (e.g. example-brand_beach-shoot-003.jpg);
  - restricted area (--area restricted): media/restricted/<project>/<type>/<project>_<code>-<NNN>.<ext>,
    where <code> is "r" + 6 random characters, stable per folder. The code → name translation stays
    in media/restricted/<project>/_key.json (only those with access to the area see it). The folder
    name is also replaced by the code in the texts that go into the catalog;
  - brings the footage log's columns into media/catalog.csv (except those that identify the source);
  - runs the indexer at the end to fill in the technical specifications.

The originals are never changed. Re-importing is safe: files already copied are kept and
the columns coming from the footage log are updated from it.

Usage:
    python scripts/import_footage_log.py <source> --project example-brand --dry-run
    python scripts/import_footage_log.py <source> --project example-brand --area restricted --folders "Person Name"
    python scripts/import_footage_log.py <source> --project other-brand --area restricted --no-code
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import secrets
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_media import COLUMNS, load_catalog, load_projects, generate_csv  # noqa: E402

PHOTOS = {"jpg", "jpeg", "png", "webp", "tif", "tiff", "heic"}
VIDEOS = {"mp4", "mov", "m4v"}
# footage log columns that do not go into the bank: they identify the source or the bank already calculates them
DO_NOT_IMPORT = {"file", "folder", "project", "number", "type", "orientation"}
MAX_SIDE = 2400


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def read_footage_log(source: Path) -> list[dict]:
    text = (source / "catalog.csv").read_text(encoding="utf-8-sig")
    first = text.split("\n", 1)[0]
    sep = ";" if first.count(";") > first.count(",") else ","
    return list(csv.DictReader(text.splitlines(), delimiter=sep))


ALPHABET = "23456789abcdefghjkmnpqrstuvwxyz"  # no 0/o, 1/l/i: they don't get confused when reading


def load_key(path: Path) -> dict:
    """{code: {"name": ..., ...}} of the project's restricted area."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_key(path: Path, key: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(key, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def new_code(used: set) -> str:
    while True:
        code = "r" + "".join(secrets.choice(ALPHABET) for _ in range(6))
        if code not in used:
            return code


def remove_name(value: str, folder: str, code: str) -> str:
    """Replaces the full name, the joined name (FirstLast) and each part of the name (first, last) with the code."""
    parts = [folder, folder.replace(" ", "")] + [p for p in folder.split() if len(p) >= 4]
    for name in parts:
        if len(name) >= 3:
            value = re.sub(r"\b" + re.escape(name) + r"\b", code, value, flags=re.IGNORECASE)
    return value


def copy_photo(orig: Path, dest: Path) -> None:
    with Image.open(orig) as img:
        exif = img.getexif()
        img = ImageOps.exif_transpose(img)
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        clean = Image.Exif()
        for tag in (315, 33432):  # author, copyright: credits stay; GPS, camera and XMP go
            if exif.get(tag):
                clean[tag] = exif[tag]
        img.convert("RGB").save(dest, "JPEG", quality=85, optimize=True, progressive=True, exif=clean)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Imports a footage log folder into the media bank.")
    ap.add_argument("source", type=Path, help="footage log folder (with catalog.csv)")
    ap.add_argument("--project", required=True, help="slug from media/projects.csv")
    ap.add_argument("--area", choices=["open", "restricted"], default="open",
                    help="open (default) or restricted: in the restricted area, each folder becomes a code and the name stays in _key.json")
    ap.add_argument("--no-code", action="store_true",
                    help="in the restricted area, keeps the folder name (use when the folders are not people, e.g. shoot dates)")
    ap.add_argument("--batch", default="", help="batch name, stored in the restricted area's key")
    ap.add_argument("--folders", nargs="+", help="imports only these folders (for testing)")
    ap.add_argument("--media-origin", default="", help="value of the origin column (own, client, stock:x…)")
    ap.add_argument("--media", type=Path, default=root / "media", help="bank folder (default: media/)")
    ap.add_argument("--dry-run", action="store_true", help="shows what it would do, without copying or writing")
    args = ap.parse_args()

    source, media = args.source.resolve(), args.media.resolve()
    if args.project not in load_projects(media / "projects.csv"):
        print(f"Project '{args.project}' is not in media/projects.csv.")
        return 1
    rows = read_footage_log(source)
    if args.folders:
        rows = [l for l in rows if l["folder"] in args.folders]

    restricted = args.area == "restricted"
    encode = restricted and not args.no_code
    base = media / "restricted" / args.project if restricted else media / "open"
    rel_prefix = f"restricted/{args.project}" if restricted else "open"
    key_file = base / "_key.json"
    key = load_key(key_file) if encode else {}
    catalog, extras = load_catalog(media / "catalog.csv")
    today = date.today().isoformat()
    warnings, copied, kept, names_replaced = [], 0, 0, 0
    new_columns = []

    # stable codes: the same folder keeps the code from previous imports
    folder_code = {}
    if encode:
        by_name = {v.get("name"): k for k, v in key.items()}
        for folder in sorted({l["folder"] for l in rows}):
            code = by_name.get(folder) or new_code(set(key))
            key.setdefault(code, {"name": folder, "batch": args.batch, "added_on": today})
            folder_code[folder] = code

    for l in rows:
        folder, name = l["folder"], l["file"]
        orig = source / folder / name
        if not orig.exists():
            warnings.append(f"{folder}/{name}: it is in the footage log catalog, but the file does not exist")
            continue
        ext = orig.suffix.lower().lstrip(".")
        parts = orig.stem.split("_")
        number = parts[1] if len(parts) > 1 else slug(orig.stem)
        group = folder_code[folder] if encode else slug(folder)
        if ext in PHOTOS:
            kind, dest_ext = "photo", "jpg"
        elif ext in VIDEOS:
            kind, dest_ext = "video", ext
        else:
            warnings.append(f"{folder}/{name}: format .{ext} not imported")
            continue
        rel = f"{rel_prefix}/{kind}/{args.project}_{group}-{number.lower()}.{dest_ext}"
        dest = media / rel

        if dest.exists():
            kept += 1
        else:
            copied += 1
            if not args.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if kind == "photo":
                    copy_photo(orig, dest)
                else:
                    dest.write_bytes(orig.read_bytes())

        row = catalog.setdefault(rel, {"file": rel, "added_on": today})
        row["projects"] = row.get("projects") or args.project
        if args.media_origin and not row.get("origin"):
            row["origin"] = args.media_origin
        row["group"] = group
        for col, value in l.items():
            if not col or col in DO_NOT_IMPORT:
                continue
            value = (value or "").strip()
            if encode and value:
                new = remove_name(value, folder, group)
                names_replaced += new != value
                value = new
            if col in COLUMNS:  # column the bank also has: only filled in if it is empty
                if value and not row.get(col):
                    row[col] = value
                continue
            row[col] = value
            if col not in extras and col not in new_columns:
                new_columns.append(col)

    for folder in sorted({p.name for p in source.iterdir() if p.is_dir()} & {l["folder"] for l in rows}):
        in_catalog = {l["file"] for l in rows if l["folder"] == folder}
        for a in sorted((source / folder).iterdir()):
            if a.is_file() and a.name not in in_catalog and a.name.lower() != "desktop.ini":
                warnings.append(f"{folder}/{a.name}: file without a row in the footage log catalog (not imported)")

    columns = COLUMNS + [c for c in extras if c != "group"]
    columns += ["group"] + [c for c in new_columns if c not in columns]

    print(f"Footage log: {source}")
    print(f"  {len(rows)} row(s) read: {copied} file(s) to copy, {kept} already in the bank")
    print(f"  Area: {rel_prefix}/")
    if encode:
        print(f"  {len(folder_code)} folder(s) with a code; key in {key_file} (only the restricted area sees it)")
        print(f"  {names_replaced} text field(s) had the folder name and received the code")
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for a in warnings[:15]:
            print(f"  ! {a}")
        if len(warnings) > 15:
            print(f"  … and {len(warnings) - 15} more")

    if args.dry_run:
        print("\nDry run: nothing was copied or written.")
        return 0
    if encode:
        save_key(key_file, key)
    (media / "catalog.csv").write_text(generate_csv([catalog[k] for k in sorted(catalog)], columns),
                                       encoding="utf-8", newline="")
    print("\nCatalog updated. Running the indexer…\n", flush=True)
    return subprocess.call([sys.executable, str(Path(__file__).with_name("index_media.py")),
                            "--media", str(media)])


if __name__ == "__main__":
    sys.exit(main())
