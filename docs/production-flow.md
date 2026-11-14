# Production flow

**Status:** flow in use, validated in pilots and in real production.

From the request to the board ready in Figma for human review, and from approval to delivery. The groundwork track (system, footage logging, import, curation) runs in parallel and is not here; see [`how-it-works.md`](how-it-works.md).

---

## Steps

| # | step | in | out | tool | it worked if… |
|---|---|---|---|---|---|
| B1 | **Request** | the request in the source configured in the project sheet ("Requests and deliveries") | **standard request** (see below) or, in Notion, the task saved to a file | the project's source (Notion, spreadsheet, document, another tool, approved text) | the text is split by slide and the delivery folder is defined. In Notion: task in the tasks database with a ready-to-start status (in the original, Ready to Start) and the "Sequence / Art Text" table filled in; **do not filter by Asset Type** (carousels may show up with another type) |
| B1.1 | **Identify the project** | slug from the standard request, or the `Project` relation of the Notion task | project slug | `media/projects.csv` (column `slug`; in Notion, column `notion_project`) | the project has a registered slug; otherwise, stop and warn |
| B2 | **Structuring** | table per slide + project sheet | `projects/<slug>/production/<topic>.json` (cover, content slides, closing slide; title, text, list, bold, variant, position, line breaks) | **`scripts/structure_request.py`** (reads the standard request or the Notion task; Notion is read by Claude, through the MCP, read-only, and saved to a file; see `scripts/README.md`) + Claude for the exceptions | every slide has a role and a component; widows resolved; highlight on the last word; doubts marked as "review by hand" + reason |
| B2.1 | **Distribute into spreads** | number of slides | slide map (e.g.: 01 cover · 02–03 spread · 04 single photo · 05–06 spread with closing slide) | `scripts/structure_request.py` (1 spread, different from the project's last JSON) + spread rules | at least 1 spread; closing slide in the last spread; position compared with the previous carousel (no record yet) |
| B3 | **Photo selection** | structure + project catalog + learnings | 1 main + 2 alternatives per slide or spread, ordered, with measured contrast and reason | order: **meaning** (the photo shows the step in the text and what the project asks for in the sheet's "Profile and image") → non-negotiables → coherence with the photo direction (`projects/<slug>/photo-direction.md`; color and light measured by `scripts/measure_coherence.py`, which orders and explains; setting, people and "stock-photo look" stay by eye) → contrast measured per corner (`scripts/measure_contrast.py`) → format and uses. Checks `media/catalog.csv` + `media/uses.csv`: on a tie, prefers fewer `uses` and the ones not used recently **in the same project**. Sources, in this order: the client's real photos (`origin = footage-log:…`) → legacy (`legacy:figma`) → Pexels (browser) → Freepik (Magnific connector), these two when there are fewer than 2 good options in the bank; external ones come in as a preview and are only downloaded after approval in B6 (see decision "External photos in B3") | no slide without an option; nothing is eliminated, only ordered; a photo gap becomes a shot-list item; a photo chosen from an external source or from the legacy is downloaded and goes into `media/` with the `origin` marked |
| B4 | **Board assembly** (decision strip per slide: salmon = decision, white = nothing pending) | structure + photos | a **section** "<topic> · v1" on the single **"Review boards"** page of the project's Figma, with the carousel in `Social/*` components and the photos ordered below each slide | Figma: export the photo from the production file, send it to the design system file (`upload_assets`), apply it to the slide (spread with continuous crop) | slides in design system instances; real photos; texts from the request |
| B5 | **Check** | assembled board (screenshot) | table of exceptions per slide, on the board and in the JSON | measurement (`scripts/measure_contrast.py`) + looking at the screenshot (face, seam, block height) | each exception with a level (non-negotiable / review by hand / recommended), reason and suggestion; no non-negotiable without action |
| B6 | **Human review** | board + exceptions | carousel approved **or** feedback | person | — (outside the automation) |
| B6.1 | **Review cycle** | feedback | learnings recorded + board v2, v3… | Claude | each point of the feedback becomes a written criterion (brand-specific or general) **before** redoing; the previous version stays below, marked as replaced |
| B7 | **Delivery and record** | approved carousel | PNGs `01.png`…`NN.png` (**1080×1440**, official format for all projects) in the **request's delivery folder** (default: `projects/<slug>/deliveries/<topic>/`; in Notion, the task's `Link Location`, e.g.: `YYYYMM_SM_Carousel_<title>`, with `_editable-files/` next to it); delivered status in the request source, when it has a status; **one row in `media/uses.csv` per photo used** | Figma (export each slide), delivery folder, request source, usage log + indexer | only with human confirmation; only the photos of the delivered piece go into the log (alternatives don't), and the indexer recalculates `uses` and `last_used`; the folder must be empty (never overwrite); status in the source (e.g.: card in Notion) only with confirmation |

## Standard request (what B2 reads)

Each person receives requests in a different way. So that B2 does not depend on the tool, every request is converted, before B2, into a **standard request**: a `.md` file with four pieces of information. Full example: `scripts/examples/standard-request-example.md`.

```
# Carousel request

- project: example-brand
- topic: summer-care-routine
- title: Summer care routine
- delivery_folder: projects/example-brand/deliveries/summer-care-routine/
- source: content calendar spreadsheet
- id:

| Sequence | Art Text |
|---|---|
| Slide 1 | Cover title |
| Slide 2 | Title<br><br>Paragraph. |
| Slide 3 | Title<br>• item<br>• item<br>• item |
| Slide 4 | Title<br><br>Paragraph.<br><br>**Sentence in bold.** |
| Slide 5 | Closing line. |
```

| field | what it is |
|---|---|
| `project` | slug from `media/projects.csv` (required) |
| `topic` | becomes the name of the JSON (`production/<topic>.json`) and of the delivery folder |
| `title` | name of the content (optional) |
| `delivery_folder` | where the PNGs go in B7. Default, if the person has no other place: `projects/<slug>/deliveries/<topic>/` |
| `source` | where the request came from (optional) |
| `id` | ID of the request in the source, if any (optional) |

- **One row per slide**, in order. `<br>` breaks the line and `<br><br>` separates paragraphs. `**bold**` (or `<b>bold</b>`) marks the sentence in bold. Lines with `•`, `-` or `1.` become a list.
- The `+++` row and empty rows are ignored.
- The text goes **as the client sent it** (or as you approved it): the conversion to the standard request only changes the format, never the words.

## Where requests come from

The source is configured once per project, in the sheet (`projects/<slug>/project.md`, section "Requests and deliveries"): what the source is, how Claude accesses it (connector, folder, file) and which of its fields becomes each field of the standard request. In production, Claude reads the source and converts it to the standard request before B2.

**Example: Notion, as in the original process.** The script also reads the task directly (without converting):

| Notion field | becomes | note |
|---|---|---|
| tasks database, ready-to-start status (in the original, "Ready to Start") | when to pick up the request | Claude reads it through the connector, read-only, and saves the `notion-fetch` response to a file |
| `Project` relation | `project` | the ID of the project page goes in the `notion_project` column of `media/projects.csv` |
| "Sequence / Art Text" table in the page body | the table | one row per slide; `+++` is ignored |
| `Link Location` | `delivery_folder` | the folder where the PNGs are saved |
| `Name` | `title` | |
| unique ID (property "ID") | `id` | with the database prefix (`ID_PREFIX` in `scripts/structure_request.py`) |
| `Asset Type` | — | only generates a "recommended" warning if it is not "Social Media Carousel" |
| `Final Due Date`, `Client Delivery Date` | — | go into `origin` in the JSON |

Example of a saved task: `scripts/examples/notion-task-example.md`.

**Other sources** (spreadsheet, document, another tool): the mapping is written in the sheet, and Claude generates the standard request from it.

**AI-generated text** is a source like the others, and happens **before** B1: from a topic, Claude writes the text per slide, **you approve it** (or adjust it) and only then does it become a standard request. From there on the same rule as always applies: B2 organizes and does not rewrite.

## Time of each review board

Every board has a row in `projects/<slug>/production/timings.csv` (local time, `YYYY-MM-DD HH:MM`). Header:

```
board,notion_task,request_created,prep_start,board_ready,review_start,review_end,delivered,notes
```

| milestone | when | who records it |
|---|---|---|
| `request_created` | the task was created in Notion | Claude (reads it from Notion) |
| `prep_start` | started reading the task (B1) | Claude |
| `board_ready` | the board became ready for review (end of B5) | Claude |
| `review_start` | you started reviewing | Claude, when you say so ("I started reviewing") or from the first review message |
| `review_end` | you approved | Claude, when you approve |
| `delivered` | the piece was delivered (B7) | Claude, together with the delivery |

The times that matter come from there:
- **wait:** request created → start of prep;
- **prep:** start → board ready (the automatic part);
- **review queue:** board ready → start of review;
- **review:** start → end of review (the human part);
- **total cycle:** request created → delivered.

The board in Figma shows a card with these milestones, updated at each step. A milestone that was not recorded stays blank, with no estimate.

## Rules that apply at every step

- **A rule is not a filter:** non-negotiable blocks; recommended can give way with a reason; the rest becomes a recorded exception.
- **Nothing is published or changed in Notion** without human confirmation.
- **The request text belongs to the client:** structuring organizes and adjusts typography (widows, line breaks in titles), but does not rewrite the content. A change of meaning becomes "review by hand".

## How the request becomes structure

- **1st line of each slide** → title; the rest → paragraphs. Lines with `•` → list.
- **A 1-item list** does not fit the component (3 to 5): it becomes a paragraph and goes in as "review by hand".
- **More than 2 paragraphs** on a slide: the component only has 2 + a bold sentence. The 3rd goes to the bold and goes in as "review by hand" (it changes the emphasis).
- **Sentence that looks incomplete** ("Uma das importantes", i.e. "one of the important"): keep it and mark it.
- **Last slide** of the request → closing slide. The "+++" row and empty slides are ignored. The "+++" belongs to the request table template and does not go in even when it carries text; no slide is added to what the client sent (e.g.: signature).
- **Simple break** (`<br />`) joins the lines in the same paragraph; **blank line** separates paragraphs.
- **List after a sentence** ("…, such as:") stays paragraph + list, in the order of the request (field `order`).
- **Colored text** (yellow, italic) is a note for the designer: it leaves the art, goes to `production_notes` and becomes "review by hand".
- **Block with a link** (product, reference image) also leaves the art: it goes to `references` and becomes "review by hand".
- **Bold line** in the middle of the slide becomes the bold sentence. If it comes before other text, the slide comes out as "review by hand" ("comes before other text; check the order"), because the component shows the bold at the end.
- **Bold that spans lines** (`<b>Title<br><br>Sentence.<br></b>Text`) applies from where it opens to where it closes. **Bold at the end** also becomes `bold`.
- **Long 1st line** (more than 80 characters) is not a title: the slide is left without a title and becomes "review by hand". The script never invents a title.
- **Closing slide without a title** (only long paragraphs): variant A, last paragraph as the closing line. **Closing slide with a single sentence**: it becomes the title and, if it is long, "review by hand".
- **Title with a colon at the end** looks like the introduction of a list: "review by hand". Title with a period, highlight on a weak word ("are") or highlight repeated from another slide: "recommended".
- **Items separated by a blank line** (`• a<br><br>• b`) are **a single list**.
- **Slide that starts directly with the list** continues the list from the previous slide. The script puts the two in a spread and the exception says so ("decide whether to repeat the title").
- **Client typos** (".This" at the start of the paragraph, missing space after ":") pass through the script. Only "sentence without a period" is marked.
- **The text position from B2 is provisional:** B3 decides, by the contrast measurement and by the faces.

## Photos

- **Always measure.** The "tone" and "free space" written in the catalog were wrong in 3 of 4 choices in a pilot.
- **The measurement does not see faces.** Check in the board screenshot; text over a face is non-negotiable.
- **Text away from the seam.** Inside an instance it is not possible to draw the continuation of the shadow on the neighboring slide; a block with Darken next to the seam cuts off abruptly.
- **Every photo used lives in `media/`.** If it came from the Figma legacy or from a stock library, it is downloaded at the moment of the choice and goes in with an `origin` (`legacy:figma`, `stock:freepik`…). The use goes in the log `media/uses.csv`, and not in the catalog: the catalog says what the image is, and the log says where it was used.
- **Light photos dominate** stock libraries in some topics (e.g.: doctor's office). When nothing goes above 3:1, the board comes out with the best option, Darken turned on and the exception for a human decision.
- **The bank covers some topics well and others poorly.** When a topic needs an external photo on several slides, that is a finding: it becomes a gap for the shot list.
- **External ones also tend to be light.** Pexels and Freepik return a lot of studio light; measure before accepting.
- **The preview can be measured.** The public thumbnail (Pexels 1600 px, Freepik ~600 px) is enough to measure the contrast and assemble the board; nothing is downloaded or goes into `media/` before approval.
- **The face is what slips through most.** The screenshot at 30% shows text touching a face; at 15% it does not. Reframing (shifting the crop) usually solves it.
- **Restricted area** comes in as an alternative with the mark "RESTRICTED · caution" in the caption.

## What is worth turning into a script (priority)

Already a script (see `scripts/README.md`):
- the per-corner contrast measurement (`scripts/measure_contrast.py`);
- the color coherence measurement (`scripts/measure_coherence.py`);
- reading the Notion table → structure JSON (`scripts/structure_request.py`, B2 and B2.1).

Still missing:

1. **Assemble the board from the JSON** (instances, properties, texts with highlight, spread crop, photo cards, decision strips). Today Claude does this in Figma through the connector, one call per board from a "spec" taken from the JSON, plus sending the photos (`upload_assets` on the suggestion cards) and a call that copies the main photo to the slide, with the spread crop calculated.
2. **B3 candidate list** (search in the catalog by words from the slide, without the `restricted` ones for sensitivity, with uses and featured in the weight).
3. **Export and send the photos** from the production file to the board file (only for the Figma legacy; the local bank already uploads directly).

The choice of photo topic, the face check and the decision on exceptions remain with Claude and with the person.
