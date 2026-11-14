"""Structures the carousel request (step B2).

Reads the request in one of these two formats and writes `projects/<slug>/production/<topic>.json`:
- **standard request** (.md): project (slug), topic, delivery folder and the table
  "Sequence / Art Text". It is the neutral format: Claude converts into it the request
  that comes from any source (spreadsheet, document, another tool, approved text).
  Example: `scripts/examples/standard-request-example.md`;
- **Notion task**: the `notion-fetch` response, saved to a file by Claude.
  Example: `scripts/examples/notion-task-example.md`.

The script organizes; it does not rewrite. The client's text comes out the same, only with:
- the highlight word marked with *asterisks* (last word of the title);
- the last words of each paragraph and item joined by U+00A0 (widows);
- extra spaces at the ends removed.
Everything that calls for a decision becomes a "review by hand" (or "recommended") exception + reason.

The carousel text can be in Portuguese or in English: the list of weak words (which are
not used as highlight) has both languages.

Usage (from the repository root):
    python scripts/structure_request.py <request-file> [--topic summer-care-routine]
    python scripts/structure_request.py <file> --dry-run
See `scripts/README.md`.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Prefix of the unique ID of the task database in Notion (property "ID"). Replace with your database's.
ID_PREFIX = "TASK"
NBSP = "\u00a0"

# Words that are not used as highlight nor as file name.
# Portuguese (the carousel text can be in Portuguese) ...
WEAK_WORDS_PT = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos",
    "em", "na", "no", "nas", "nos", "e", "ou", "para", "pra", "por", "pelo", "pela",
    "que", "se", "com", "sem", "ao", "aos", "à", "às", "é", "são", "ser", "ter", "isso",
    "isto", "aqui", "ali", "já", "não", "sim", "mais", "menos", "muito", "como", "seu",
    "sua", "seus", "suas", "meu", "minha", "você", "ela", "ele", "lhe", "me", "te",
}
# ... and the English equivalent (or in English).
WEAK_WORDS_EN = {
    "a", "an", "the", "some", "of", "in", "on", "at", "to", "into", "and", "or", "for",
    "by", "with", "without", "from", "that", "if", "is", "are", "be", "have", "has",
    "this", "these", "those", "it", "here", "there", "already", "not", "no", "yes",
    "more", "less", "very", "as", "how", "your", "yours", "my", "mine", "our", "you",
    "she", "he", "her", "him", "his", "them", "their", "its", "me", "us", "so",
}
WEAK_WORDS = WEAK_WORDS_PT | WEAK_WORDS_EN

LIST_MARKERS = re.compile(r"^\s*(?:[•●▪◦·\-–*]|(\d{1,2})[.)])\s+")
URL = re.compile(r"https?://\S+")

LIMITS = {
    "words_slide": 45,             # project.md: up to ~45 words per slide
    "title_cover": 54,             # variant A: up to 3 lines of ~18 characters
    "title_content": 60,           # 2–3 short lines
    "title_final": 35,             # narrow cream panel (in the pilot, 42 → 4 lines)
    "title_max": 80,               # above this the 1st line is a sentence, not a title
    "list_min": 3,
    "list_max": 5,
}

REVIEW = "review by hand"
RECOMMENDED = "recommended"


# ---------------------------------------------------------------- utilities


def exception(level: str, reason: str) -> dict:
    return {"level": level, "reason": reason}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def words(text: str) -> list[str]:
    return text.replace(NBSP, " ").split()


def join_widow(text: str) -> str:
    """Joins the last words with U+00A0: 3 from 5 words up, 2 with 4 (decisions.md)."""
    p = words(text)
    if len(p) >= 5:
        n = 3
    elif len(p) == 4:
        n = 2
    else:
        return " ".join(p)
    return " ".join(p[:-n]) + " " + NBSP.join(p[-n:])


def clean_markdown(text: str) -> str:
    """Removes escapes and links from Notion's markdown, without changing the words."""
    text = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda m: m.group(2) if m.group(1).replace("\\", "") == m.group(2) else f"{m.group(1)} ({m.group(2)})", text)
    text = re.sub(r"\\([_*\[\]()#>`~|\\-])", r"\1", text)
    return text


def slug(text: str, max_words: int = 4) -> str:
    base = strip_accents(text.lower())
    base = re.sub(r"[^a-z0-9]+", " ", base)
    weak = {strip_accents(p) for p in WEAK_WORDS}
    p = [w for w in base.split() if w not in weak]
    return "-".join(p[:max_words]) or "carousel"


# ---------------------------------------------------------------- reading


STANDARD_FIELDS = ("project", "topic", "title", "delivery_folder", "id", "source")


def read_standard_request(raw: str) -> tuple[dict, str] | None:
    """Standard request: lines "- field: value" + markdown table "| Sequence | Art Text |".

    In the text cell, <br> breaks a line (<br><br> separates paragraphs) and **bold** or
    <b>bold</b> mark the bold sentence. Returns None if the file is not a standard request.
    """
    fields = {}
    for m in re.finditer(r"^[ \t]*-?[ \t]*([a-z_]+)[ \t]*:[ \t]*(.*?)[ \t]*$", raw, re.M):
        if m.group(1) in STANDARD_FIELDS and m.group(1) not in fields:
            fields[m.group(1)] = m.group(2)
    table_lines = [l.strip() for l in raw.splitlines() if l.strip().startswith("|")]
    if not fields.get("project") or not table_lines:
        return None
    trs = []
    for l in table_lines:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if len(cells) < 2 or re.fullmatch(r":?-{3,}:?", cells[0]):
            continue  # separator line of the markdown table
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", "|".join(cells[1:]))
        trs.append(f"<tr><td>{cells[0]}</td><td>{text}</td></tr>")
    props = {
        "_standard": True,
        "_slug": fields["project"],
        "_topic": fields.get("topic") or None,
        "_source": fields.get("source") or None,
        "Name": fields.get("title", ""),
        "Link Location": fields.get("delivery_folder") or None,
        "userDefined:ID": fields.get("id") or None,
    }
    return props, "<table>" + "".join(trs) + "</table>"


def read_export(path: Path) -> tuple[dict, str]:
    """Returns (properties, content html).

    Accepts: the standard request (see `read_standard_request`), the notion-fetch JSON response
    (with the "text" field) or the page text (<page>…<properties>{…}</properties>…<content>…</content>).
    """
    raw = path.read_text(encoding="utf-8")
    if "<properties>" not in raw and not raw.lstrip().startswith("{"):
        standard = read_standard_request(raw)
        if standard:
            return standard
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "text" in data:
            raw = data["text"]
    except json.JSONDecodeError:
        pass

    props: dict = {}
    m = re.search(r"<properties>\s*(\{.*?\})\s*</properties>", raw, re.S)
    if m:
        txt = m.group(1)
        # Notion sometimes returns markdown escapes that are not valid JSON (e.g. "\_").
        txt = re.sub(r"\\(.)", lambda m: m.group(0) if m.group(1) in '"\\/bfnrtu' else "\\\\" + m.group(1), txt)
        props = json.loads(txt)
    m = re.search(r"<content>(.*?)</content>", raw, re.S)
    content = m.group(1) if m else raw
    return props, content


def table_rows(content: str) -> list[tuple[str, str]]:
    """(label, html of the text cell) of each row of the slides table."""
    table = re.search(r"<table[^>]*>(.*?)</table>", content, re.S)
    if not table:
        raise SystemExit("Could not find the table \"Sequence / Art Text\" in the task content.")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(1), re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(cells) < 2:
            continue
        label = plain_text(cells[0])
        if strip_accents(label.lower()).startswith(("sequence", "sequencia")):
            continue  # header (English or Portuguese)
        rows.append((label, cells[1]))
    return rows


def plain_text(snippet: str) -> str:
    snippet = re.sub(r"<[^>]+>", "", snippet)
    return html.unescape(clean_markdown(snippet)).strip()


def split_notes(cell: str) -> tuple[str, list[str]]:
    """Removes from the cell the colored text (note for the designer), which does not go into the art."""
    notes = []

    def keep(m):
        note = plain_text(m.group(0).replace("<br />", " ").replace("<br/>", " "))
        if note:
            notes.append(re.sub(r"\s+", " ", note))
        return "<br /><br />"

    cell = re.sub(r"<i>\s*<span color=\"[^\"]+\">.*?</span>\s*</i>", keep, cell, flags=re.S)
    cell = re.sub(r"<span color=\"[^\"]+\">.*?</span>", keep, cell, flags=re.S)
    return cell, notes


def bold_line(raw: str, open_: bool) -> tuple[bool, bool]:
    """Is the whole line bold? Takes into account the <b> left open from the previous line.
    Returns (line in bold, bold still open at the end of the line)."""
    has_text, all_bold = False, True
    for piece in re.split(r"(</?b>)", raw):
        if piece == "<b>":
            open_ = True
        elif piece == "</b>":
            open_ = False
        else:
            t = plain_text(piece)
            if t and not re.fullmatch(r"[•●▪◦·\-–*\d.)\s]+", t):  # a list marker alone does not count
                has_text = True
                all_bold = all_bold and open_
    return has_text and all_bold, open_


def cell_blocks(cell: str) -> list[list[dict]]:
    """Blocks separated by a blank line; each line with text, bold and marker."""
    cell = re.sub(r"<br\s*/?>", "\n", cell.strip())
    blocks, current = [], []
    in_bold = False  # Notion's <b> can open on one line and close on another
    for raw in cell.split("\n"):
        bold, in_bold = bold_line(raw, in_bold)
        text = plain_text(raw)
        if not text:
            if current:
                blocks.append(current)
                current = []
            continue
        m = LIST_MARKERS.match(text)
        current.append({
            "text": text[m.end():].strip() if m else text,
            "item": bool(m),
            "number": bool(m and m.group(1)),
            "bold": bold,
            "url": bool(URL.search(text)),
        })
    if current:
        blocks.append(current)
    return blocks


# ---------------------------------------------------------------- structure


def title_with_highlight(title: str) -> tuple[str, str | None, list[dict]]:
    """Marks the last word with *asterisks*; the final punctuation stays outside."""
    exc = []
    p = title.strip().rsplit(" ", 1)
    last = p[-1]
    m = re.match(r"^(.*?)([.!?:;,…\"”’)]*)$", last)
    core, punct = m.group(1), m.group(2)
    if not core:
        return title, None, [exception(REVIEW, "title without a word for the highlight")]
    if strip_accents(core.lower()) in {strip_accents(w) for w in WEAK_WORDS} or len(core) <= 2:
        exc.append(exception(RECOMMENDED, f"highlight falls on a weak word (\"{core}\"); the rule asks for a title that ends in a strong word"))
    marked = (p[0] + " " if len(p) > 1 else "") + f"*{core}*{punct}"
    return marked, core, exc


def check_sentences(text: str, before_list: bool = False) -> list[dict]:
    """Signs of an incomplete sentence. Heuristic: flags, never corrects."""
    exc = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        p = words(sentence.rstrip(".!?"))
        # Portuguese-specific: "um dos / uma das" without a superlative after it.
        if len(p) >= 2 and p[0].lower() in {"um", "uma"} and p[1].lower() in {"dos", "das"}:
            following = p[2].lower() if len(p) > 2 else ""
            if following not in {"mais", "principais", "maiores", "melhores", "menores", "piores", "primeiros", "primeiras", "poucos", "poucas"}:
                exc.append(exception(REVIEW, f"\"{sentence.strip()}\" looks incomplete (missing \"mais\"?). Text kept; confirm with whoever wrote it"))
    for a, b in zip(words(text), words(text)[1:]):
        if a.lower() == b.lower() and a.isalpha():
            exc.append(exception(REVIEW, f"repeated word: \"{a} {b}\""))
    end = text.rstrip()
    if end.endswith(":") and not before_list:
        exc.append(exception(REVIEW, f"\"{end[-40:]}\" ends in a colon and nothing comes after it"))
    elif end and end[-1] not in ".!?…)\"”;:" and len(words(end)) > 6:
        exc.append(exception(RECOMMENDED, f"paragraph without final punctuation: \"…{end[-30:]}\""))
    return exc


def build_slide(number: int, label: str, role: str, cell: str) -> dict:
    cell, notes = split_notes(cell)
    blocks = cell_blocks(cell)
    exc: list[dict] = []
    slide = {"slide": f"{number:02d}", "role": role, "notion_row": label}

    # Block with a link: reference for the designer (product, icon…), not art text.
    references = []
    text_blocks = []
    for b in blocks:
        if any(l["url"] for l in b):
            references.append(" · ".join(l["text"] for l in b))
        else:
            text_blocks.append(b)
    blocks = text_blocks

    # Title: 1st line of the 1st block, if it is not a list item and looks like a title.
    starts_with_item = bool(blocks) and blocks[0][0]["item"]
    title = None
    if blocks and not blocks[0][0]["item"]:
        candidate = blocks[0][0]["text"]
        only_it = len(blocks) == 1 and len(blocks[0]) == 1
        if len(candidate) <= LIMITS["title_max"] or role == "cover" or (role == "final" and only_it):
            title = candidate
            blocks[0] = blocks[0][1:]
            blocks = [b for b in blocks if b]
    # Client's bold sentence (content and final): leaves the body and stays bold.
    # Before, a bold line attached to another line was merged into the paragraph without warning.
    uses_bold = role in ("content", "final")
    client_bold = [l for b in blocks for l in b if l["bold"] and not l["item"]] if uses_bold else []
    lines = [l for b in blocks for l in b]
    text_after_bold = bool(client_bold) and any(
        not l["bold"] for l in lines[lines.index(client_bold[0]) + 1:])

    # Body: paragraphs (consecutive lines become one paragraph) and lists, in order.
    body: list[tuple[str, object]] = []
    for b in blocks:
        par: list[str] = []
        lst: list[dict] = []
        for l in b:
            if uses_bold and l["bold"] and not l["item"]:
                if par:
                    body.append(("paragraph", " ".join(par)))
                    par = []
                if lst:
                    body.append(("list", lst))
                    lst = []
                continue
            if l["item"]:
                if par:
                    body.append(("paragraph", " ".join(par)))
                    par = []
                lst.append(l)
            else:
                if lst:
                    body.append(("list", lst))
                    lst = []
                par.append(l["text"])
        if par:
            body.append(("paragraph", " ".join(par)))
        if lst:
            body.append(("list", lst))

    # In Notion it is common to separate the items with a blank line ("• a<br><br>• b"): each item falls in a block.
    # Consecutive items, separated only by a blank line, are a single list (learned in a pilot).
    joined: list[tuple[str, object]] = []
    for kind, value in body:
        if kind == "list" and joined and joined[-1][0] == "list":
            joined[-1] = ("list", joined[-1][1] + value)
        else:
            joined.append((kind, value))
    body = joined

    # A 1-item list becomes a paragraph (the component asks for 3 to 5).
    final_body = []
    for kind, value in body:
        if kind == "list" and len(value) == 1:
            final_body.append(("paragraph", value[0]["text"]))
            exc.append(exception(REVIEW, f"\"{value[0]['text']}\" is a 1-item list in Notion; the component asks for {LIMITS['list_min']} to {LIMITS['list_max']}. It became a paragraph; decide whether it becomes bold or a subtitle"))
        else:
            final_body.append((kind, value))
    body = final_body

    paragraphs = [v for t, v in body if t == "paragraph"]
    lists = [v for t, v in body if t == "list"]

    # Bold sentence: the one the client marked in bold; otherwise, the 3rd paragraph (pilot rule).
    bold = None
    if client_bold:
        bold = " ".join(l["text"] for l in client_bold)
        if text_after_bold:
            exc.append(exception(REVIEW, f"bold sentence \"{bold}\" comes before other text in the request; the component shows the bold at the end. Check the order"))

    if title is not None:
        slide["title"], highlight, e = title_with_highlight(title)
        slide["highlight"] = highlight
        exc += e
    elif role != "final":  # the final without a title has its own exception (variant A)
        if starts_with_item:
            exc.append(exception(REVIEW, "slide without a title: it starts straight on the list, which continues the previous slide's. Decide with whoever wrote it whether to repeat the title or turn the two slides into a spread (do not invent)"))
        else:
            exc.append(exception(REVIEW, "slide without a title: the 1st line is too long for a title. All the text stayed as body; decide the title with whoever wrote it (do not invent)"))

    if role == "cover":
        slide["component"] = "Social/Cover"
        if paragraphs or lists:
            slide["variant"] = "B"
            slide["subtitle"] = join_widow(" ".join(paragraphs + [i["text"] for l in lists for i in l]))
            exc.append(exception(REVIEW, "cover with more than one line: the rest became a subtitle (variant B); check"))
        else:
            slide["variant"] = "A"
        if title and len(title) > LIMITS["title_cover"]:
            exc.append(exception(RECOMMENDED, f"cover title with {len(title)} characters; variant A holds ~3 lines of 18"))

    elif role == "final":
        slide["component"] = "Social/Final"
        texts = paragraphs + [i["text"] for l in lists for i in l]
        if title and len(title) <= LIMITS["title_max"] and not (len(texts) == 0 and len(title) > LIMITS["title_content"]):
            slide["variant"] = "B"
            if texts:
                slide["text"] = join_widow(" ".join(texts))
            if len(title) > LIMITS["title_final"]:
                exc.append(exception(RECOMMENDED, f"title of {len(title)} characters in the final's panel: it may go past 3 lines; check the height"))
            if not texts:
                exc.append(exception(REVIEW, "final with only one sentence: used as title; the panel has no supporting text"))
        elif title:
            # Only one long sentence: title too big for the panel.
            slide["variant"] = "B"
            exc.append(exception(REVIEW, f"final with only one sentence of {len(title)} characters, used as title; long for the panel. Decide whether it becomes text (variant A) and what the closing line would be"))
        else:
            # No title: variant A (support on top, big closing line at the bottom).
            slide["variant"] = "A"
            if len(paragraphs) >= 2:
                slide["text"] = join_widow(" ".join(paragraphs[:-1]))
                slide["closing"] = paragraphs[-1]
                exc.append(exception(REVIEW, "final without a title: variant A, with the last paragraph as the closing line (big) and the rest as support. Check that this is the highlight sentence"))
                f, d, e = title_with_highlight(paragraphs[-1])
                slide["closing"], slide["highlight"] = f, d
                exc += e
            else:
                slide["text"] = join_widow(" ".join(texts))
        if bold:
            slide["bold"] = join_widow(bold)
        for t in texts + ([bold] if bold else []):
            exc += check_sentences(t)

    else:
        slide["component"] = "Social/Content"
        if len(paragraphs) == 3 and bold is None:
            bold = paragraphs.pop()
            exc.append(exception(REVIEW, f"3 text blocks and the component has 2 paragraphs: \"{bold}\" went to the bold sentence, which changes the emphasis"))
        elif len(paragraphs) > 3 or (len(paragraphs) > 2 and bold is not None):
            exc.append(exception(REVIEW, f"{len(paragraphs)} paragraphs; the component has 2 + bold sentence. Nothing was cut: decide what gets merged or goes to another slide"))
        if paragraphs:
            slide["paragraphs"] = [join_widow(p) for p in paragraphs]
        if lists:
            items = lists[0]
            slide["list"] = {
                "marker": "Number" if all(i["number"] for i in items) else "Bullet",
                "items": [join_widow(i["text"]) for i in items],
            }
            n = len(items)
            if not LIMITS["list_min"] <= n <= LIMITS["list_max"]:
                exc.append(exception(REVIEW, f"list with {n} items; the component asks for {LIMITS['list_min']} to {LIMITS['list_max']}"))
            if len(lists) > 1:
                slide["extra_lists"] = [[join_widow(i["text"]) for i in l] for l in lists[1:]]
                exc.append(exception(REVIEW, f"{len(lists)} lists on the slide; the component has 1"))
            if paragraphs:
                slide["order"] = [t for t, _ in body]
        if bold:
            slide["bold"] = join_widow(bold)
        if title and len(title) > LIMITS["title_content"]:
            exc.append(exception(RECOMMENDED, f"title with {len(title)} characters; the standard is 2–3 short lines"))
        if title and title.rstrip().endswith(":"):
            exc.append(exception(REVIEW, "title ends in a colon: it looks like the introduction of the list, not a title"))
        elif title and title.rstrip().endswith(".") and not title.rstrip().endswith("..."):
            exc.append(exception(RECOMMENDED, "title ends in a period: check whether it is a title or a sentence"))
        introduces_list = {v for (t, v), (t2, _) in zip(body, body[1:]) if t == "paragraph" and t2 == "list"}
        for t in paragraphs + ([bold] if bold else []) + [i["text"] for l in lists for i in l]:
            exc += check_sentences(t, before_list=t in introduces_list)
        total = len(words(" ".join(paragraphs + ([bold] if bold else []) + [i["text"] for l in lists for i in l])))
        if total > LIMITS["words_slide"]:
            exc.append(exception(RECOMMENDED, f"{total} words in the body (standard: up to ~{LIMITS['words_slide']})"))

    if notes:
        slide["production_notes"] = notes
        exc.append(exception(REVIEW, "note for the designer in Notion (colored text), outside the art: " + " / ".join(notes)))
    if references:
        slide["references"] = references
        exc.append(exception(REVIEW, f"{len(references)} reference(s) with a link (product, image) outside the art: " + "; ".join(r.split(" · ")[0] for r in references)))

    slide["exceptions"] = exc
    return slide


POSITIONS = ["top-left", "bottom-right", "top-right", "bottom-left"]


def previous_spread(folder: Path, ignore_id: str | None, ignore_file: Path | None) -> str | None:
    """Slides of the 1st spread of the project's most recent carousel (to vary the position)."""
    candidates = []
    for f in folder.glob("*.json") if folder.is_dir() else []:
        if ignore_file and f.resolve() == ignore_file.resolve():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(d, dict) or not d.get("spreads"):
            continue
        if ignore_id and d.get("origin", {}).get("id") == ignore_id:
            continue
        when = (d.get("delivery") or {}).get("date") or d.get("generated_on") or ""
        candidates.append((when, f.stat().st_mtime, d["spreads"][0]["slides"]))
    if not candidates:
        return None
    return max(candidates)[2]


def distribute(slides: list[dict], previous: str | None) -> tuple[list[dict], list[dict]]:
    """One spread between content slides, in a position different from the previous carousel."""
    exc = []
    content = [s for s in slides if s["role"] == "content"]
    pairs = [(a, b) for a, b in zip(content, content[1:]) if int(b["slide"]) == int(a["slide"]) + 1]
    chosen = None
    for a, b in pairs:
        if f"{a['slide']}-{b['slide']}" != previous:
            chosen = (a, b)
            break
    if chosen is None and pairs:
        chosen = pairs[0]
        exc.append(exception(RECOMMENDED, f"only the spread {previous} fits, the same as the previous carousel's"))
    if chosen is None:
        exc.append(exception(REVIEW, "fewer than 2 consecutive content slides: the mandatory spread is not possible. Consider the spread with the final"))

    i = 0
    for s in slides:
        if s["role"] != "content":
            s["spread"] = None
            continue
        s["spread"] = None
        s["half"] = None
        if chosen and s in chosen:
            s["spread"] = f"{chosen[0]['slide']}-{chosen[1]['slide']}"
            s["half"] = "left" if s is chosen[0] else "right"
        s["position"] = POSITIONS[i % len(POSITIONS)]
        i += 1

    # Keys in the same order as the pilot.
    order = ("slide", "role", "spread", "half", "component", "variant", "position", "notion_row",
             "title", "highlight", "subtitle", "paragraphs", "list", "extra_lists", "order", "bold",
             "text", "closing", "production_notes", "references", "exceptions")
    for n, s in enumerate(slides):
        slides[n] = {k: s[k] for k in order if k in s} | {k: v for k, v in s.items() if k not in order}

    spreads = []
    if chosen:
        spreads.append({"slides": f"{chosen[0]['slide']}-{chosen[1]['slide']}", "photos": [], "exceptions": []})
    return spreads, exc


def structure_summary(slides: list[dict]) -> str:
    parts, seen = [], set()
    for s in slides:
        if s["slide"] in seen:
            continue
        if s.get("spread"):
            a, b = s["spread"].split("-")
            parts.append(f"{a}–{b} spread")
            seen.update({a, b})
        elif s["role"] == "cover":
            parts.append(f"{s['slide']} cover")
        elif s["role"] == "final":
            parts.append(f"{s['slide']} final (own photo)")
        else:
            parts.append(f"{s['slide']} single photo")
        seen.add(s["slide"])
    return " · ".join(parts)


def find_project(props: dict) -> tuple[str, str, str]:
    """(slug, id of the project's page in Notion, name).

    Standard request: by the slug, which must be in media/projects.csv.
    Notion task: by the Project relation, compared with the notion_project column.
    """
    if props.get("_standard"):
        with open(ROOT / "media" / "projects.csv", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("slug") == props["_slug"]:
                    return row["slug"], "", row.get("name", "")
        raise SystemExit(
            f"STOPPED: the request's project '{props['_slug']}' is not in media/projects.csv (slug column).\n"
            "  Register the project (see projects/README.md) and run again."
        )
    project = props.get("Project") or []
    if isinstance(project, str):
        try:
            project = json.loads(project)
        except json.JSONDecodeError:
            project = [project]
    ids = [re.sub(r"[^0-9a-f]", "", p.lower())[-32:] for p in project]
    with open(ROOT / "media" / "projects.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            target = re.sub(r"[^0-9a-f]", "", (row.get("notion_project") or "").lower())
            if target and target in ids:
                notes = row.get("notes") or ""
                name = notes.split("Notion:", 1)[1].strip() if "Notion:" in notes else row.get("name", "")
                return row["slug"], target, name
    raise SystemExit(
        "STOPPED: the task's project is not in media/projects.csv (notion_project column).\n"
        f"  Project in Notion: {project or '(empty)'}\n"
        "  Register the project (see projects/README.md) and run again."
    )


def structure(props: dict, content: str, previous_folder: Path | None, output: Path | None) -> dict:
    proj_slug, proj_id, proj_name = find_project(props)
    rows = table_rows(content)
    general: list[dict] = []

    valid = []
    for label, cell in rows:
        if label.strip() == "+++":
            general.append(exception(RECOMMENDED, "row \"+++\" of the request table ignored"))
            continue
        if not plain_text(re.sub(r"<br\s*/?>", " ", cell)):
            general.append(exception(RECOMMENDED, f"\"{label}\" empty in the request table: ignored"))
            continue
        valid.append((label, cell))
    if len(valid) < 3:
        raise SystemExit(f"STOPPED: the table has {len(valid)} slide(s) with text; a carousel needs a cover, content and a final.")
    if len(valid) > 10:
        general.append(exception(REVIEW, f"{len(valid)} slides; the carousel maximum is 10"))

    slides = []
    for i, (label, cell) in enumerate(valid, start=1):
        role = "cover" if i == 1 else "final" if i == len(valid) else "content"
        expected = f"slide {i}"
        if label.lower().strip() != expected:
            general.append(exception(RECOMMENDED, f"slide {i:02d} came from the request's row \"{label}\" (out of sequence)"))
        slides.append(build_slide(i, label, role, cell))

    # Highlight repeated on different slides.
    seen: dict[str, str] = {}
    for s in slides:
        d = (s.get("highlight") or "").lower()
        if d and d in seen:
            s["exceptions"].append(exception(RECOMMENDED, f"'{s['highlight']}' repeats the highlight of slide {seen[d]}"))
        elif d:
            seen[d] = s["slide"]

    task_id = props.get("userDefined:ID")
    if not props.get("_standard") and (isinstance(task_id, int) or (isinstance(task_id, str) and task_id.isdigit())):
        task_id = f"{ID_PREFIX}-{task_id}"
    previous = previous_spread(previous_folder, task_id, output) if previous_folder else None
    spreads, exc_spread = distribute(slides, previous)
    general += exc_spread

    asset = props.get("Asset Type")
    if asset and asset != "Social Media Carousel":
        general.append(exception(RECOMMENDED, f"the Notion task's Asset Type is \"{asset}\", not \"Social Media Carousel\""))

    url = (props.get("url") or "").split("?")[0]
    origin = {
        "source": props.get("_source") or ("standard request" if props.get("_standard") else "notion"),
        "notion_task": url,
        "id": task_id,
        "notion_project": proj_name,
        "notion_project_id": proj_id,
        "final_due_date": props.get("date:Final Due Date:start"),
        "client_delivery": props.get("date:Client Delivery Date:start"),
        "delivery_folder": props.get("Link Location"),
    }
    rules = [
        "client text without rewriting",
        "highlight = last word of the title (punctuation outside), marked with *asterisks*",
        "widows: last 3 words of each paragraph and item joined by U+00A0 (2 in 4-word texts)",
        "at least one spread, in a position different from the previous carousel" + (f" ({previous})" if previous else " (no previous carousel recorded)"),
        "provisional text position (alternating); the photo decides in B3/B5",
        "a rule is not a filter: doubts as exceptions",
    ]
    return {
        "name": clean_markdown(props.get("Name") or ""),
        "project": proj_slug,
        "origin": origin,
        "rules_applied": rules,
        "structure": structure_summary(slides),
        "slides": slides,
        "spreads": spreads,
        "general_exceptions": general,
        "status": "structured (B2); B3 onward pending",
        "version": 1,
        "generated_by": "scripts/structure_request.py",
        "generated_on": date.today().isoformat(),
    }


# ---------------------------------------------------------------- output


def report(d: dict) -> str:
    lines = [f"{d['origin']['id'] or d['origin']['source']} · {d['name']} → {d['project']}", f"  {d['structure']}"]
    for s in d["slides"]:
        head = s.get("title") or s.get("closing") or "(no title)"
        extra = []
        if s.get("paragraphs"):
            extra.append(f"{len(s['paragraphs'])} par.")
        if s.get("list"):
            extra.append(f"list {len(s['list']['items'])}")
        if s.get("bold"):
            extra.append("bold")
        if s.get("text"):
            extra.append("text")
        flagged = sum(1 for e in s["exceptions"] if e["level"] == REVIEW)
        lines.append(f"  {s['slide']} {s['role']:<8} {head[:50]:<52} {', '.join(extra):<22} review: {flagged}")
        for e in s["exceptions"]:
            lines.append(f"       - [{e['level']}] {e['reason']}")
    for e in d["general_exceptions"]:
        lines.append(f"  general [{e['level']}] {e['reason']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Structures the request (B2) into projects/<slug>/production/<topic>.json")
    ap.add_argument("request", type=Path, help="standard request (.md) or file with the task's notion-fetch response")
    ap.add_argument("--topic", help="file name (without .json); default: the request's topic or the cover title")
    ap.add_argument("--output", type=Path, help="writes to this path instead of projects/<slug>/production/<topic>.json")
    ap.add_argument("--overwrite", action="store_true", help="allows replacing a JSON that already exists")
    ap.add_argument("--dry-run", action="store_true", help="shows the JSON and the report, without writing")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    props, content = read_export(args.request)
    preview = structure(props, content, None, None)  # only to learn slug and topic
    proj_slug = preview["project"]
    cover = next((s.get("title") for s in preview["slides"] if s["role"] == "cover"), None) or preview["name"]
    request_topic = re.sub(r"[^a-z0-9]+", "-", strip_accents((props.get("_topic") or "").lower())).strip("-")
    topic = args.topic or request_topic or slug(cover.replace("*", ""))
    proj_folder = ROOT / "projects" / proj_slug / "production"
    target = args.output or (proj_folder / f"{topic}.json")

    d = structure(props, content, proj_folder, target)
    text = json.dumps(d, ensure_ascii=False, indent=2)

    if args.dry_run:
        print(text)
        print()
        print(report(d))
        print(f"\n(dry run) would write to {target}")
        return 0
    if target.exists() and not args.overwrite:
        print(f"STOPPED: {target} already exists. Use --topic, --output or --overwrite.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text + "\n", encoding="utf-8")
    print(report(d))
    print(f"\nwritten: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
