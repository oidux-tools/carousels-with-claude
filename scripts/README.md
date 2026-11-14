# Scripts

Repository automations. All of them run from the repository root (the folder that has `CLAUDE.md`).

## Setup (once per computer)

Requires Python 3.10+.

```bash
python -m pip install -r scripts/requirements.txt
```

## `index_media.py` — updates the media bank catalog

Walks through `media/` and keeps `media/catalog.csv` up to date.

```bash
python scripts/index_media.py
```

| option      | what it does                                                     |
|-------------|------------------------------------------------------------------|
| `--dry-run` | shows what would change, without saving anything                 |
| `--prune`   | removes from the catalog the rows of files that no longer exist  |
| `--media`   | points to another bank folder (useful for tests)                 |

**What it does**

- New file: creates the row with type, format, width, height, aspect ratio, duration, size and date added.
- File that already exists: updates only the technical columns.
- Empty `projects`: suggests the project from the start of the file name, if it is in `projects.csv`.
- Never touches what was filled in by hand (`projects`, `tags`, `origin` and any extra column you create).
- File deleted or renamed: the old row **stays** in the catalog and appears in the report, so you can carry the tags over to the new name. It only leaves with `--prune`.
- Ignores `_inbox/`, but warns how many files are waiting for triage.
- Reads the log `media/uses.csv` and recalculates `uses` (how many log rows) and `last_used` (most recent date) for each file. These two columns are never typed: a value written by hand is replaced.
- If the catalog was saved by Excel with `;`, it reads it anyway and writes it back in the standard (`,`).

**Warnings it gives (they don't block anything)**

- name outside the convention `<project>_<description>_<nn>.<ext>`;
- project in the name or in the `projects` column that is not in `projects.csv`;
- photo or background below the minimum size;
- file it could not read;
- usage log row that points to a file outside the catalog, with a date outside the `YYYY-MM-DD` format, with an unknown project or that repeats file + piece + slide.

**Formats it reads**

| specification      | formats                                           |
|--------------------|---------------------------------------------------|
| width × height     | jpg, png, webp, gif, bmp, tif, psd, svg, mp4, mov, m4v |
| duration           | mp4, mov, m4v, m4a, wav, mp3                       |

Other formats (pdf, ai, heic…) go into the catalog only with type, format and size.

## `import_footage_log.py` — brings a footage log into the bank

The footage logging (done outside this repository) delivers one folder per person or subject, files `Person_NNN[_featured].jpg` and a `catalog.csv`. The importer takes this to `media/`.

```bash
python scripts/import_footage_log.py "<footage log folder>" --project example-brand --dry-run
python scripts/import_footage_log.py "<footage log folder>" --project example-brand --area restricted --batch 202611_example-brand_shoot
```

| option           | what it does                                                              |
|------------------|---------------------------------------------------------------------------|
| `--project`      | slug from `media/projects.csv` (required)                                 |
| `--area`         | `open` (default) or `restricted`                                          |
| `--batch`        | batch name, kept in the restricted area key                               |
| `--no-code`      | in the restricted area, keeps the folder name (when the folders are not people, e.g.: shoot dates) |
| `--folders`      | imports only some folders (for testing)                                   |
| `--media-origin` | fills in the `origin` column (e.g.: `footage-log:202611_shoot`)           |
| `--dry-run`      | shows what it would do, without copying or saving                         |

**What happens**

- Photo: optimized copy (longer side 2400 px, JPEG 85), with only author and copyright in the metadata. Video: direct copy.
- **Open area:** `media/open/<type>/<project>_<folder>-<NNN>.jpg` (e.g.: `example-brand_shoot-003.jpg`).
- **Restricted area:** `media/restricted/<project>/<type>/<project>_<code>-<NNN>.jpg` (e.g.: `example-brand_rk7m2qx-003.jpg`). Each folder gets a random, stable code; the translation goes to `media/restricted/<project>/_key.json` (outside Git). The folder name is also replaced by the code in the texts that go into the catalog.
- The photo number is the same as in the footage log; the featured mark goes to the `featured` column, not in the name.
- The footage log columns go into the catalog, except `file`, `folder`, `project`, `number`, `type` and `orientation`. The `group` column keeps the folder (open) or the code (restricted).
- Reimporting is safe: what was already copied stays, the codes don't change and the footage log columns are updated.
- At the end, it runs the indexer.

**Finding the high-resolution original:** in the open area, the group is the folder; in the restricted area, `_key.json` translates the code. The photo number is the same as in the footage log.

## `measure_contrast.py` — measures the contrast of the text on each photo (B3)

For each photo and each position of the text block, it calculates the contrast ratio of the cream text color (`#F0EBDC`) against the lightest part of the background behind the block. It serves to **order** photos and positions in photo selection (B3) and in the check (B5). It doesn't eliminate anything.

```bash
python scripts/measure_contrast.py media/open/photo/example-brand_shoot-003.jpg
python scripts/measure_contrast.py "<folder>" --format spread
python scripts/measure_contrast.py "<folder>" --block 700x400 --json
```

| option               | what it does                                                                 |
|----------------------|------------------------------------------------------------------------------|
| inputs               | one or more images, or folders (reads jpg, png, webp, tif, bmp)              |
| `--format`           | `slide` (1080×1350, default) or `spread` (2160×1350, measured in two halves) |
| `--block WxH`        | approximate size of the text block (default `570x480`)                       |
| `--json`             | output in JSON, for other steps to use                                       |
| `--motion-limit`     | from what variation the background counts as busy (default 40)               |

**Text color:** the default is the cream `#F0EBDC` (constant `CREAM` at the start of the script), the text-on-photo color of the first brand the process ran on. Replace it with your brand's text-on-photo color before measuring.

**How it measures**

- Crops the photo the way the slide crops it (fill, centered). In the spread, it crops 2160×1350 and measures each half.
- Applies the Contrast layer (`#141414` at 10% in Linear Burn), which stays on in the slides.
- In each position (top-left, top-right, bottom-left, bottom-right, center), the block touches the 90 px margin. The measured area is the block + 40 px (20 on each side).
- Compares the cream with the **95th percentile** of the luminance of that area, using the WCAG contrast formula.
- "Variation" is the standard deviation of the gray in the area (0–255). Above the limit, the background counts as busy.

**Levels** (decisions "Contrast before shadow" and "A rule is not a filter")

| level     | when                                            |
|-----------|-------------------------------------------------|
| `ok`      | ≥ 4.5:1 and calm background                     |
| `review`  | between 3:1 and 4.5:1, or busy background       |
| `below`   | < 3:1 (non-negotiable: change corner, reframe or change the photo; Darken is the last resort) |

**Order**

- Positions of each photo: best level first, then away from the seam, then higher ratio. In the spread, the positions on the inner side of each half get the note "next to the seam".
- Photos: by the best position. In the spread, the worse of the two halves counts, because both usually have text.

**What it doesn't do**

- **It doesn't see faces or the seam.** Text over a face and an abrupt cut at the seam remain a visual check, in the board screenshot.
- It doesn't know the meaning of the photo: meaning comes before contrast in B3.
- It doesn't read the real framing in Figma: it assumes a centered crop. If the photo is reframed, measure the crop again.
- The "busy" limit (40) has not yet been calibrated with real photos.

Uses numpy if it is installed (full resolution); without numpy, it measures 1 in every 2 pixels, with the same result in the tests.

## `measure_coherence.py` — measures the color coherence of the photo with the project (B3)

Compares the color and light of each candidate with the project's **yardstick** (the color signature of the reference photos) and says, in words, where it departs from it. It serves to **order** candidates in the B3 criterion "coherence with the photo direction", mainly the external ones (Pexels, Freepik). It doesn't eliminate anything.

```bash
python scripts/measure_coherence.py "<previews folder>" --project example-brand
python scripts/measure_coherence.py photo1.jpg photo2.jpg --project other-brand --json
python scripts/measure_coherence.py "<folder>" --project example-brand --references "<other folder>"
```

| option          | what it does                                                                  |
|-----------------|-------------------------------------------------------------------------------|
| inputs          | one or more images, or folders (reads jpg, png, webp, tif, bmp); they can be previews in the scratchpad |
| `--project`     | project slug (required)                                                       |
| `--references`  | uses these photos or folders as the yardstick, instead of the direction and the catalog (tests) |
| `--json`        | output in JSON, for other steps                                               |
| `--cache`       | yardstick cache folder (default: system temporary folder, `carousel-coherence`) |
| `--no-cache`    | recalculates the yardstick without reading or writing the cache               |

**Where the yardstick comes from**

1. The list of photos in `projects/<slug>/photo-direction.md`, if the file exists. The script takes the `media/…` paths (e.g.: `media/restricted/example-brand/photo/example-brand_shoot-15-10-1555.jpg`) that are in a section whose title has "reference"; without that section, it takes all the paths in the file. A path that doesn't exist becomes a warning.
2. Otherwise, the project's photos in the catalog with `featured = yes` and a real origin (`footage-log:…` or `legacy:…`).

The yardstick is cached (it takes a few seconds for ~200 photos on a network drive) and is rebuilt on its own if the list or the files change. Nothing is written to `media/`.

**What it measures** (on a 256 px thumbnail, in Lab space)

| measure     | how                                    | words                                      |
|-------------|----------------------------------------|--------------------------------------------|
| temperature | mean of b* (+ yellow, − blue)          | warmer / cooler than the project           |
| saturation  | mean chroma                            | saturation above / below (more washed out) |
| brightness  | mean of L*                             | lighter / darker than the project          |
| contrast    | standard deviation of L*               | contrast above / below (flatter)           |
| tint        | mean of a* (+ pinkish, − green)        | tint pulled toward pinkish / toward green  |
| palette     | hue distribution of the colored areas (8 bands: red/pink, orange/skin, yellow, green, cyan, blue, purple, magenta) | different palette (with the predominant bands) |

**How it compares**

- For each measure, the yardstick is the **median** of the references and the project's **normal variation** (median absolute deviation × 1.4826, with a floor so that a very homogeneous project does not exaggerate small differences).
- The candidate's deviation is measured in that unit: up to 1 = **inside**, from 1 to 2 = **slightly** outside, above 2 = outside. In the palette, it only counts being more different than the references themselves usually are.
- **Distance** = root mean square of the six deviations (each one capped at 4). Up to 1 = `coherent`, from 1 to 2 = `close`, above 2 = `off`.
- It also says how many of the project's own photos the candidate is farther from ("farther than 41% of the project's photos"), for calibration.
- Order: smallest distance first.

**Tests (in the original process)**

- Variations of a real photo against the project's own yardstick: original 0.77 · more saturated 0.83 · slightly cooler 1.32 · darker 1.63 · black and white 1.63 · cooler 2.09. The words match the change made.
- Two projects, featured photos split in half (one half becomes the yardstick, the other half is the candidate): project 1 yardstick, same project 0.94 × other 1.71; project 2 yardstick, 1.00 × 1.21. It separates on average, but there is overlap when both projects have warm light and skin.
- Without numpy, the result is the same.

**What it doesn't do**

- **It doesn't see setting, people or "stock-photo look".** Brazilian, real people, naturalness, retouching, filter and stock scene remain a visual check, against the photo direction.
- It doesn't know the meaning of the photo: meaning comes before coherence in B3.
- It measures the whole photo, not the slide crop. The preview's watermark (Freepik) goes into the calculation.
- The yardstick is only as good as the references. When the references mix different lighting (e.g.: bedroom and living room), the brightness variation gets wide, and "darker" only shows up in large differences. The curated list in `photo-direction.md` should make the yardstick tighter.
- The bands (1 and 2) and the floors have not yet been calibrated with real choices from reviewers.

Uses numpy if it is installed; without numpy, it does the same calculation in pure Python (slower).

## `structure_request.py` — turns the request into the carousel structure (B2)

Reads the **standard request** (`.md`, format in `docs/production-flow.md`) or the **Notion task** (the "Sequence / Art Text" table and the properties) and writes `projects/<slug>/production/<topic>.json`, in the format described below (example input in `scripts/examples/`). The client's text **is not rewritten**: the script only organizes, marks the highlight and resolves widows. Whatever calls for a decision becomes an exception with a reason.

**Standard request:** just pass the file. The project comes from the `project` field (slug from `media/projects.csv`), and the topic, from the `topic` field.

```bash
python scripts/structure_request.py scripts/examples/standard-request-example.md --dry-run
```

**Notion task · step 1 — Claude fetches the task (the script doesn't talk to Notion)**

1. Through the Notion MCP, **read-only**: `notion-fetch` with the URL or the ID of the task page (Tasks database).
2. Saves the response to a file in the session scratchpad (e.g.: `<scratchpad>/notion/TASK-101.md`). Either of the two works:
   - the whole JSON that `notion-fetch` returns (with the `text` field);
   - only the page text, with the `<properties>{…}</properties>` and `<content>…</content>` blocks.
   The file is temporary: what matters from it (URL, ID, deadlines, folder) stays in `origin` in the generated JSON.

**Notion task · step 2 — run the script**

```bash
python scripts/structure_request.py "<scratchpad>/notion/TASK-101.md" --dry-run
python scripts/structure_request.py "<scratchpad>/notion/TASK-101.md"
```

| option           | what it does                                                                 |
|------------------|------------------------------------------------------------------------------|
| `--topic`        | file name without `.json` (default: the `topic` field of the standard request; otherwise, up to 4 strong words from the cover title) |
| `--output`       | writes to another path (useful for tests)                                    |
| `--overwrite`    | allows replacing a JSON that already exists (without it, the script stops)   |
| `--dry-run`      | shows the JSON and the report, without saving                                |

**Project:** in the standard request, the slug comes from the `project` field. In the Notion task, it comes from the `Project` relation, compared with the `notion_project` column of `media/projects.csv`. With no match, the script **stops** and warns.

**Notion ID:** the number of the "ID" property gets the prefix from `ID_PREFIX` (at the start of the script; default `TASK`). Replace it with your database's prefix.

**What it builds**

- **Role:** 1st slide with text = cover (`Social/Cover`, variant A; B if it has more than one line), last = final (`Social/Final`), the rest = content (`Social/Content`). The `+++` row and empty slides are ignored and noted.
- **Title:** 1st line of the slide. Highlight on the last word, with `*asterisks*` and the punctuation outside; the word also goes in `highlight`. Titles don't get U+00A0.
- **Body:** a blank line separates paragraphs; a simple break joins the lines. Lines with `•`, `-`, `*` or `1.` become a list (`marker` Bullet or Number). A bold line becomes `bold`, in the content and in the final, even when Notion's `<b>` opens on one line and closes on another; it leaves the paragraph.
- **Widows:** each paragraph, item, bold and final text comes out with the last 3 words joined by U+00A0 (2 in 4-word texts).
- **Language of the carousel text:** Portuguese or English. The weak words (which are not used as highlight nor in the file name) are a Portuguese list plus the English equivalent, used together (`WEAK_WORDS_PT` and `WEAK_WORDS_EN`). The header row of the table can be "Sequence" or "Sequência". See `docs/decisions.md`, "Repository in English; carousel text in Portuguese or English".
- **Spread:** one, in the first pair of content slides whose spread is **different** from the last JSON of the same project in `production/`. The text position alternates (top-left, bottom-right, top-right, bottom-left) and is **provisional**: the photo decides, in B3/B5.
- **Photos:** `spreads[].photos` comes out empty; B3 fills it in.

**Exceptions it marks**

| level          | when                                                                          |
|----------------|-------------------------------------------------------------------------------|
| review by hand | 1-item list (becomes a paragraph); list outside 3 to 5 items; more than one list |
| review by hand | 3 text blocks (the 3rd goes to the bold); more than that (nothing is cut)      |
| review by hand | client's bold sentence before other text (the component shows the bold at the end) |
| review by hand | slide without a title (1st line with more than 80 characters); title with `:` at the end |
| review by hand | sentence that looks incomplete (Portuguese pattern: "Uma das importantes", i.e. "one of the important"), repeated word, text with `:` at the end with nothing after it |
| review by hand | colored text in Notion (note for the designer) and blocks with a link: they leave the art and go to `production_notes` / `references` |
| review by hand | final with only one long sentence; final without a title (becomes variant A)   |
| recommended    | long title (cover > 54, content > 60, final > 35 characters); title with a period; highlight on a weak word; repeated highlight |
| recommended    | more than ~45 words in the body; paragraph without final punctuation; Asset Type different from "Social Media Carousel" |

**What it doesn't do**

- It doesn't choose photos, doesn't measure contrast, doesn't know whether the topic is medical (the technical review of the content and the photo exceptions come in B3–B5).
- It doesn't know whether the title "fits": the character counts are approximate, without measuring the font.
- The incomplete-sentence detection is a narrow heuristic (Portuguese pattern "um dos / uma das" without "mais", i.e. "one of the" without "most"; repeated word). Typos get through.
- It doesn't change anything in Notion.
