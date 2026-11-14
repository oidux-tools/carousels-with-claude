# Media bank

A single place for all the raw material used in the content: photos, videos, icons, logos, soundtracks…

## Principle

- **The first folder level is the access boundary:** `open/` (whole team) or `restricted/<project>/` (only those who look after that project).
- **In the open area, each file lives in the folder for its type** and the link to projects is metadata (file name + catalog): a photo that serves three projects is still a single file.
- **In the restricted area, the project is a folder**, because the content belongs to a single client.
- **Catalog, usage log and projects are single** for both areas, at the root of `media/`.

## Structure

```
media/
├── _inbox/                inbox: what has arrived and hasn't been handled yet
├── open/                  whole team
│   ├── photo/ illustration/ icon/ logo/ background/ video/ audio/
├── restricted/            limited access, one folder per project
│   └── <project>/
│       ├── _key.json      code → name (only those with access to the area see it)
│       └── photo/ video/ …
├── catalog.csv     what each file is: one row per file, from both areas
├── uses.csv        what happened to it: one row per use in a delivered piece
└── projects.csv    list of valid projects (slugs)
```

Three parts, each with a role:

| part | answers | changes when |
|---|---|---|
| folders (area and type) | where the file is and who can open it | new media comes in |
| `catalog.csv` | what the image is (dimensions, description, origin, license) | new media comes in or someone completes the description |
| `uses.csv` | where, when and in which topic it was used | a piece is delivered |

## Types

| type           | what goes in                                   | common formats   | recommended minimum                 |
|----------------|------------------------------------------------|------------------|-------------------------------------|
| `photo`        | photographs: stock, shoots, product, people    | jpg, png, webp   | short side ≥ 1080 px                |
| `illustration` | illustrations, graphics, decorative elements   | svg, png         | vector (svg) whenever possible      |
| `icon`         | standalone icons                               | svg, png         | vector (svg)                        |
| `logo`         | logos of clients, partners and cited brands    | svg, png, pdf    | vector; png with transparent background |
| `background`   | backgrounds, textures, patterns                | jpg, png         | ≥ 1080 × 1350 px                    |
| `video`        | clips, b-roll, recordings                      | mp4, mov         | 1080p, mp4 (H.264)                  |
| `audio`        | soundtracks, effects, voice-overs              | mp3, wav         | wav or mp3 ≥ 192 kbps               |

Need a new type? Create the folder, add it to the table here and record it in `docs/decisions.md`.

## File name

```
<project>_<description>_<nn>.<ext>
```

- **project**: a slug from `projects.csv`. Use `general` when it serves any project.
- **description**: 2 to 5 words describing the content, separated by hyphens.
- **nn**: 2-digit sequence, only when there are variations of the same subject.
- All lowercase, no accents, no spaces. `_` separates fields, `-` separates words.

Examples:

```
open/photo/example-brand_team-meeting-office_01.jpg
open/photo/example-brand_team-meeting-office_02.jpg
open/logo/other-brand_horizontal-white.svg
open/video/general_city-timelapse-night.mp4
restricted/example-brand/photo/example-brand_rk7m2qx-014.jpg
```

**In the restricted area**, the description gives way to a **neutral code**: `r` + 6 random characters (lowercase letters and numbers, without 0/o, 1/l/i), stable per person or group. The code says nothing about the sector or about who it is; the translation lives in `restricted/<project>/_key.json`, which only those with access to the area can open and which never goes into Git. The importer generates the code and the key (`--area restricted`).

## Catalog (`catalog.csv`)

One row per file. CSV in UTF-8, comma-separated. Fields with several values use `|` (e.g.: `example-brand|other-brand`).

| column          | filled in     | example                            |
|-----------------|---------------|------------------------------------|
| `file`          | auto          | `open/photo/example-brand_team-meeting_01.jpg` (path inside `media/`; it is the key) |
| `area`          | auto (folder) | `open` or `restricted:example-brand` |
| `type`          | auto (folder) | `photo`                            |
| `format`        | auto (extension) | `jpg`                           |
| `width`         | auto          | `1080` (px)                        |
| `height`        | auto          | `1350` (px)                        |
| `aspect_ratio`  | auto          | `4:5`                              |
| `duration_s`    | auto          | `12.5` (video and audio only)      |
| `size_mb`       | auto          | `2.4`                              |
| `projects`      | auto from the name + manual | `example-brand\|other-brand` |
| `tags`          | manual        | `people\|office\|blue`             |
| `origin`        | manual (or by the importer) | `footage-log:202611_shoot`, `stock:freepik`, `legacy:figma` (see below) |
| `added_on`      | auto          | `2026-11-14`                       |
| `uses`          | auto (from the log) | `3`: rows in `uses.csv` for this file |
| `last_used`     | auto (from the log) | `2026-11-16`: the most recent date in the log |

"auto" = the indexer fills it in by reading the file itself or the log (`python scripts/index_media.py`, details in [`scripts/README.md`](../scripts/README.md)). "manual" = only a person knows; the indexer never overwrites what was filled in by hand. **`uses` and `last_used` are never typed in:** they are recalculated on every run from `uses.csv`, and any value written by hand is replaced.

## Origin

Where the image came from. One value per file, in the format `type:detail`:

| origin | when to use |
|---|---|
| `footage-log:<batch>` | the client's real material, coming from footage logging (e.g.: `footage-log:202611_shoot`) |
| `stock:freepik`, `stock:pexels`, `stock:adobe-stock`… | external stock library; the photo is only downloaded when it is chosen for a piece |
| `legacy:figma` | images a project already used before the bank (e.g.: the photos from a photo page in the production Figma and the originals in Drive), already imported into `open/photo/` |
| `own` | produced by your team |
| `ai` | AI-generated |

For external stock library images, it's worth also filling in the `license`, `author` and `original_link` columns (extra columns are preserved by the indexer).

## Usage log (`uses.csv`)

One row **per image, per delivered piece**. A suggested alternative that wasn't used doesn't go in; a rejected piece doesn't either. The one that records it is step B7 (Delivery), together with the human confirmation.

| column | example | notes |
|---|---|---|
| `date` | `2026-11-16` | delivery day (`YYYY-MM-DD`) |
| `file` | `open/photo/example-brand_appointment-01.jpg` | path inside `media/`, same as the catalog |
| `project` | `example-brand` | slug from `projects.csv` |
| `piece` | `summer-care-routine` | name of the review board or piece |
| `notion_task` | `TASK-101` | ID of the task in Notion, if any |
| `slide` | `04` or `02-03` | slide or spread where the image went in |
| `topic` | `summer care routine` | subject of the piece, in free text |

The log only grows: a recorded row is neither deleted nor edited. If something was recorded wrongly, it is corrected right away and explained in the journal. The indexer reads the log, counts the uses and warns when a row points to a file that isn't in the catalog.

## Intake flow

1. Drop the new material into `_inbox/`.
2. Rename it following the convention above.
3. Move it to `open/<type>/` (or `restricted/<project>/<type>/`, if it is sensitive).
4. Run the indexer (`python scripts/index_media.py`) and fix the warnings it shows.
5. In the catalog, complete `tags` and `origin`, and `projects` if the file serves more than one project.

`_inbox/` is a passage, not a storeroom: ideally it should be empty at the end of each triage session.

## How to find things

- **By project**: filter `projects` containing the slug, or look for files that start with `<project>_`.
- **By area**: filter `area` (`open` or `restricted:<project>`).
- **By post format**: filter `aspect_ratio` (`4:5` carousel/feed, `9:16` stories/reels, `1:1` square).
- **By subject**: filter `tags` or search by the description in the name.
- **Little used**: sort by `uses` (lowest first) and `last_used` (oldest first). To see where an image has already appeared, filter `uses.csv` by `file`.
- To filter comfortably, open `catalog.csv` in Google Sheets or Excel (Data → From Text/CSV).
