# How It Works · how the automation works

The reference map of the process. When we talk about a step ("this is B3", "this is track A"), this is the map we mean. The detail of each production step (input, output, criterion) is in [`production-flow.md`](production-flow.md).

**Visual version:** [`flow.html`](flow.html), which opens in the browser and has clickable steps.

---

## Two tracks, the same importance

The process is not a single queue. There are two tracks that run together:

- **Track A · Groundwork:** continuous, independent of requests. Gets the system, media and rules ready.
- **Track B · Production:** runs for each request, supported by track A.

### Track A · Groundwork

| code | step | who | what it is |
|---|---|---|---|
| A1 | System and style | you + Claude | project sheet, design system, components, rules and learnings (the brand's and general ones, fed by the reviews). Step by step for a new brand: [`project-kit-guide.md`](project-kit-guide.md) |
| A2 | Footage logging | you + Claude | organize and catalog the raw material; a separate process, delivers a ZIP |
| A3 | Import | Claude | from the footage log ZIP to the media bank and the catalog: **open** area (whole team) or **restricted** per project, with a code instead of the name |
| A4 | Curation | you + Claude | highlights, contrast, history: the bank gets ready for choosing. The uses of each image come from the log `media/uses.csv` |

### Track B · Production

| code | step | who | what it is |
|---|---|---|---|
| B1 | Request | client or you | the request arrives from the **source configured in the project** (Notion, another tool, spreadsheet, document or text written by the AI and approved by you) with the text **already split per slide**, and Claude converts it into the **standard request** (project, topic, delivery folder and the "Sequence / Art Text" table). In the original process, the source is a task in Notion and the project comes from the `Project` relation |
| B2 | Structuring | Claude | the text becomes the carousel structure (cover, contents, final, position, highlight, widows) and is distributed into slides, with **at least one spread** (not all). It organizes, **does not rewrite** |
| B3 | Photo selection | Claude | 1 main + 2 alternatives per slide, in this order: **meaning** (follows the project sheet's "Profile and image"; the photo tells the same stage as the text, the cover shows the topic directly, the photos follow an arc) → non-negotiables (face, minimum contrast, seam) → **coherence with the project's photo direction** → measured contrast → format and uses. Lack of the right photo becomes a **shot-list item**, not a photo that "just passes". It consults the catalog + usage log and prefers the least used ones and those not used recently in the project. Sources, in this order: **the client's real photos** (footage log) → **legacy** (`legacy:figma`) → **Pexels** (browser) → **Freepik** (Magnific connector); the external ones only when the slide has fewer than 2 good options in the bank. An external photo goes onto the review board as a **preview**; it is only downloaded after approval in B6 and goes into `media/` with origin and license |
| B4 | Assembly | Claude | the **review board** in Figma: a single **"Review boards"** page per project, with one section per piece of content in progress; with the `Social/*` components, in three bands aligned per slide: carousel on top, **decision strip** (salmon = your decision, white = nothing pending) and the photo suggestions below |
| B5 | Check | Claude | measured contrast + screenshot (face, seam, cut-off text); exceptions with level, reason and suggestion |
| B6 | Adjustment and approval | you + client | human review of the review board. Whoever reviews **looks, doesn't read**: what needs a decision appears in the image or on the strip |
| B6.1 | Review cycle | Claude | each point of the feedback becomes a **written criterion** (the brand's or general) **before** redoing; the review board gets v2, v3… and the previous one stays below, marked as replaced |
| B7 | Delivery | you + Claude | **1080 × 1440** PNGs (official format for all projects) named `01.png`, `02.png`… in the **request's delivery folder** (default: `projects/<slug>/deliveries/<topic>/`; in Notion, the `Link Location` folder), status in the request's source when there is one, and record (one row in `media/uses.csv` per photo used, history, timings). Only with confirmation |

## How the tracks connect

- **B3 pulls from A** the catalog and the photos.
- **B4 pulls from A** the design system components.
- **B7 returns to A4** the uses of the photos, the carousel history and the timings. This closes the loop: each delivery improves the next one.
- **B6.1 returns to A1** the criteria learned in the review (`learnings.md`). Each review makes the next review board better from the first version.

## What already comes ready in this repository

- **Project template (A1):** `projects/_template/` (sheet with Tone of voice and Profile and image, learnings, photo direction). Step by step to put together a brand's kit: `docs/project-kit-guide.md`.
- **Media bank (A3, A4):** structure in `media/` (open and restricted area, catalog, usage log).
- **Standard request:** the neutral format B2 reads, described in `docs/production-flow.md` ("Standard request"), with an example in `scripts/examples/standard-request-example.md`.
- **Already a script:** import (A3, `import_footage_log.py`), catalog (A4, `index_media.py`), request structuring (B2, `structure_request.py`, which reads the standard request or a Notion task), contrast (B3/B5, `measure_contrast.py`) and color coherence (B3, `measure_coherence.py`).
- **External photos (B3):** Pexels through the browser and Freepik through the Magnific connector, only as a preview until approval.
- **Not a script yet:** review board assembly (B4; Claude builds it in Figma following `production-flow.md`) and the B7 record.

## Principles that run through everything

- **A rule is not a filter:** only the non-negotiable blocks; the rest becomes an exception with a reason for a human decision.
- **Nothing goes out without a person:** publishing, delivering and changing Notion (or another source of requests) only with confirmation.
- **The request text is not rewritten:** B2 organizes. If the text was written by the AI from a topic, that happens **before** B1 and it only becomes a request after you approve it.
- **Time is measured:** every review board records its milestones in `projects/<slug>/production/timings.csv`.
- **Feedback becomes learning:** it goes to `projects/<slug>/learnings.md` or `docs/carousel-learnings.md`.

## Visual version

[`flow.html`](flow.html) draws this map and [`production-flow.md`](production-flow.md): the two tracks, the connections and, when you click a step, how it works inside. It opens directly in the browser; `flow.html#B3` opens B3 directly. The texts are the source: if the visual diverges, they win.

**Batch update.** The visual is not redone at each change. Whoever changes this map or `production-flow.md` notes the change in the list below. When the list has something, Claude asks whether it can update the visual now or wait for more changes. When updating, the list is emptied and the date changes.

- **Visual updated on:** 2026-11-14
- **Pending in the visual:** nothing.
