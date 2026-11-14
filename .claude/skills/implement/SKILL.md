---
name: implement
description: Guides the person, phase by phase, to implement this repository's carousel process in their own work (prerequisites, first project, material and footage logging, curation, design system in Figma, tone of voice and photo direction, request source and delivery folder, first test carousel). Use when the person says "help me implement" (or the Portuguese "me ajuda a implementar"), "I want to implement", "where do I start?", "set it up for me" or asks for help getting the process running.
---

# Implement the carousel process

You will lead the person through implementing the process described in `docs/how-it-works.md`, **one phase at a time**. They may not be technical: speak simply, explain the why in one sentence, and do yourself whatever is a command, file or script.

## Conversation rules

- **Use only what exists in this repository.** Each phase points to the files that say how to do it. Do not invent a step, rule, field or tool. If the person asks for something the process does not have, say it is not part of the process and record the idea in `docs/journal.md`.
- **One phase at a time.** At the start of each phase, say in 2–3 lines what will happen and what you will need from them. At the end, show what is ready (files) and ask whether you can move on.
- **Ask in a batch, not one thing per message.** Gather the phase's questions into a short list. Whatever you can find out on your own (reading files, running a script), find out.
- **You fill in the files.** The person answers; you write in the sheets, the CSVs and the JSONs.
- **Nothing goes out without confirmation:** publishing, delivering, downloading a paid photo, changing Notion and deleting anything from `media/`.
- **Record when closing each phase:** an entry in `docs/journal.md` (request → done → problems → lesson; number = last + 1). A decision different from the original process goes to `docs/decisions.md`.
- **Reply in the language the person writes in.**
- Also follow the root `CLAUDE.md`.

## First: show the phases and find out where the person is

Show this list (with ✅ on what is already done) and say which one is next:

| phase | what | process step |
|---|---|---|
| 1 | Prepare the computer and the tools | — |
| 2 | Create the first project (the brand sheet) | A1 |
| 3 | Upload the material and do the footage logging and the import | A2 and A3 |
| 4 | Curation of the photo bank | A4 |
| 5 | Basic design system in Figma | A1 |
| 6 | Tone of voice, profile and image, and photo direction | A1 |
| 7 | Where requests come from and where deliveries go | B1 and B7 |
| 8 | First test carousel, from request to delivery | B1 to B7 |

**How to know what is already done** (check it yourself, without asking):

| phase | it is done when… |
|---|---|
| 1 | `python --version` answers 3.10 or higher, `python -c "import PIL"` works, and the Figma connector appears in your tools (search for "figma"); the request source connector only matters in phase 7 |
| 2 | `projects/<slug>/project.md` exists (outside `_template/`) with About, Audience and Visual identity filled in, and the slug has a row in `media/projects.csv` |
| 3 | `media/catalog.csv` exists and has rows for this project, and `media/_inbox/` is empty |
| 4 | the project's rows in the catalog have `tags` and `origin`, and some have `featured = yes` |
| 5 | the project sheet has the link to the design system file in Figma (ask if it does not) |
| 6 | the sheet has **Tone of voice** and **Profile and image** filled in, and `projects/<slug>/photo-direction.md` has the yardstick and 10 to 20 reference photos |
| 7 | the **Requests and deliveries** section of the sheet has source, access, mapping and delivery folder filled in |
| 8 | `projects/<slug>/production/<topic>.json` exists and there is a row in `projects/<slug>/production/timings.csv` |

The person can skip to a specific phase. Just tell them what they will miss (e.g. without photos in the bank, phase 6 has no reference photos).

---

## Phase 1 · Prepare the computer and the tools

**Goal:** everything installed and connected.

1. **Python 3.10+:** run `python --version`. Without Python, explain how to install it (official Python site; on Windows, check "Add Python to PATH") and wait.
2. **Libraries:** run `python -m pip install -r scripts/requirements.txt` (just Pillow). numpy is optional and makes the photo scripts faster.
3. **Connectors in Claude:**
   - **Figma** (required for phases 5 and 8): design system and review board.
   - **Request source** (phase 7): if it is Notion or another tool with a connector, turn the connector on; read-only in the normal flow. A spreadsheet or document in a folder does not need a connector.
   - **Pexels** has no connector: the search is done through the app's browser.
   - **Freepik** (optional): through the Magnific connector, with the person's login. Claude never sees the password.
   If a connector does not appear, ask the person to turn it on in Claude's connector settings and open a new session.
4. **Where to keep it:** if the folder is on a synced drive, that is fine; remember that media never goes into Git (`.gitignore`).

**Supporting files:** `README.md`, `scripts/README.md` ("Setup" section).

---

## Phase 2 · Create the first project (A1: the sheet)

**Goal:** `projects/<slug>/` created, with the brand sheet.

1. Ask for the brand name and agree on the **slug** (lowercase, no accents, hyphen between words).
2. Copy `projects/_template/` to `projects/<slug>/` and add the row in `media/projects.csv` (`slug,name,notion_project,notes`). `notion_project` can stay empty until phase 7.
3. Ask for the **brand material** (brandguide, colors, typography, logos in SVG) and put it in `projects/<slug>/guides/`, without touching the original. Production logos, fonts and templates go in `kit/`.
4. Follow `docs/project-kit-guide.md`, steps **1 to 3**: read the sources (including published posts and the Figma production file, if there is one), extract the identity and fill in `project.md` (About, Audience, Topics, Visual identity, Carousel, Divergences, Open items).
5. Whatever is inferred, and not written by the brand, gets *(inferred; to confirm)*. A question of taste becomes a question (step 7 of the guide).

**Tone of voice** and **Profile and image** can wait for phase 6, which is where they are reviewed calmly.

**Supporting files:** `projects/README.md`, `projects/_template/project.md`, `docs/project-kit-guide.md`.

---

## Phase 3 · Upload the material, log the footage and import (A2 and A3)

**Goal:** the brand's raw photos and videos in the bank, cataloged.

1. **Where the person uploads the material:** `media/_inbox/`. It is a passage, not a storage place: at the end of the phase it is empty.
2. **Open or restricted area?** Ask whether the material has people who need protection (patients, children, clients). If so, it goes to the project's **restricted** area, and the person's name becomes a code. Explain the rule in `media/README.md` and the decision "Bank in two areas" (`docs/decisions.md`). The restriction depends on the folder having limited access on the drive: ask the person to test it first.
3. **Footage logging (A2)** is a separate process. This repository does not include its step by step; it only knows the format the importer expects:
   - one folder per person or subject: `<source>/<Person or subject>/<Person>_<NNN>[_featured].<ext>`;
   - a `<source>/catalog.csv` separated by `;`, one row per file, with the columns `file` and `folder` (the other columns are carried into the catalog).
   If the person does not have a ready footage log, use the **manual intake flow** in `media/README.md` ("Intake flow"): rename by the convention, move to `open/<type>/` or `restricted/<project>/<type>/` and run the indexer.
4. **Import (A3):** run it first with `--dry-run` and show the result; then run it for real.
   ```
   python scripts/import_footage_log.py "<footage log folder>" --project <slug> --dry-run
   python scripts/import_footage_log.py "<footage log folder>" --project <slug> --batch YYYYMM_<slug>_<subject>
   ```
   Restricted area: `--area restricted` (code per person) or `--area restricted --no-code` (when the folders are dates or events, not people).
5. Check the indexer report and fix the warnings.

**Supporting files:** `media/README.md`, `scripts/README.md` (import_footage_log, index_media), `docs/decisions.md` ("Footage logging outside, import inside", "Bank in two areas", "Restricted area: code only when the folder is a person").

---

## Phase 4 · Curation of the bank (A4)

**Goal:** the bank ready for photo selection.

1. Run `python scripts/index_media.py` and show a summary (how many files, warnings).
2. With the person, fill in the manual columns in `media/catalog.csv`: `tags`, `origin` (`footage-log:<batch>`, `legacy:figma`, `stock:pexels`, `own`…), `projects` when it serves more than one, and `featured = yes` on the best ones. The indexer never overwrites these columns.
3. To look at the photos, build contact sheets in a temporary folder (never inside the repository).
4. If the brand already has photos used before (legacy), follow the "Legacy" decision in `docs/decisions.md`.
5. Explain the log `media/uses.csv`: it only grows, and B7 is what writes to it, at delivery.

**Supporting files:** `media/README.md` (Catalog, Origin, Usage log, How to find things), `scripts/README.md`.

---

## Phase 5 · Basic design system in Figma (A1)

**Goal:** the brand's design system file with the components the assembly uses.

1. Follow `docs/project-kit-guide.md`, steps **4 to 6**:
   - **Foundations:** variables (Primitives, Brand, Spacing) → color and text styles → logos;
   - **Social Media:** `Social/Cover`, `Social/Content` + `Social/List item`, `Social/Final` and the contrast section;
   - everything in **1080 × 1440** (spread of 2160 × 1440), which is the official format;
   - check with a screenshot and a new instance.
2. Before touching Figma: load the Figma skills listed in the guide, open the file and **inspect** what already exists.
3. Priority when there is a deadline: Foundations → cover → content. Closing slide, collab and documentation later.
4. In the project's Figma, create the two production pages: **"Review boards"** and **"Delivered"** (decision "Review boards on a single page").
5. Write down the Figma links (design system and production) in the sheet header.
6. Take the questions of taste to the person in a single list (step 7 of the guide) and mark as provisional whatever stays open.

**Supporting files:** `docs/project-kit-guide.md` (steps 4 to 8 and the pitfall tables), `docs/decisions.md` ("Slide components in Figma", "Widows", "Contrast before shadow", "Spreads", "Collab", "Official format").

---

## Phase 6 · Tone of voice, profile and image, and photo direction (A1)

**Goal:** write down how the brand speaks and what (and how) the photo should show. This is what gives meaning to the photo selection in B3.

1. **Tone of voice** (section of `project.md`): how it speaks, how it does not speak, the brand's words, with **3 real sentences** from the posts (guide, step 2).
2. **Profile and image** (section of `project.md`): type of project, what the feed needs to prove, what the image shows and never shows, care with people, preferred photo source. Source: what the team has already recorded about the client. If the team uses Notion, ask them to run the guide's prompt in Notion AI (step 1, item 7) and save the answer in `projects/<slug>/guides/notion-profile.md`.
3. **Photo direction** (`projects/<slug>/photo-direction.md`, from the template): the yardstick per aspect (light, color, texture, depth, setting, people, pose, framing), what gives away the "stock-photo look", "accept with a light adjustment × can't be saved" and **10 to 20 reference photos** from the bank (paths from `media/…`, preferably real featured ones). Mark the source of each line ([brandguide], [Notion], [sheet], [observed]). Do not invent a style: whatever is taste becomes a question.
4. Test the yardstick: run `python scripts/measure_coherence.py "<a folder with 3 or 4 photos>" --project <slug>` and show whether the words match what the person sees.

**Supporting files:** `projects/_template/project.md`, `projects/_template/photo-direction.md`, `docs/project-kit-guide.md` (steps 1, 2 and 3), `docs/decisions.md` ("Profile and image", "External photos in B3", item 12), `scripts/README.md` (measure_coherence).

---

## Phase 7 · Where requests come from and where deliveries go (B1 and B7)

**Goal:** agree once on how the request arrives and where the finished carousel is delivered, and write this in the **"Requests and deliveries"** section of the sheet (`projects/<slug>/project.md`).

1. **Explain the standard request** in 2 lines: everything that arrives becomes a file with project, topic, delivery folder and the text per slide ("Sequence / Art Text" table). Show `scripts/examples/standard-request-example.md`.
2. **Ask where the requests come from.** Examples: Notion, another task tool, a spreadsheet, documents in a folder, or "I ask the AI to write from a topic".
3. **Find out how to access it** and test with a real request, read-only:
   - tool with a connector (Notion and others): turn the connector on and read a request;
   - spreadsheet or documents: agree on the folder or the file and read one;
   - text written by the AI: agree on where the person gives the topic. Make it clear that the text **only becomes a request after they approve it**, and that from then on nobody rewrites it (B2 only organizes).
4. **Build the mapping** of each source field to the standard request (`project`, `topic`, `title`, `delivery_folder`, table, `id`) and say when a request is ready to start (e.g. a status). Write it all in the "Requests and deliveries" section of the sheet.
5. **If the source is Notion** (as in the original process), today's fields are in `docs/production-flow.md`, "Where requests come from": task database with a ready-to-start status, `Project` relation, "Sequence / Art Text" table in the page body (one row per slide; `+++` is ignored), `Link Location` (delivery folder), `Name`, unique ID and `Asset Type`. Register the ID of the project's page in the `notion_project` column of `media/projects.csv` and replace `ID_PREFIX` in `scripts/structure_request.py` with the database's prefix. Use the person's own names, never the example's.
6. **Delivery:** ask where the PNGs should go. If the source does not say and the person has no other place, the default is `projects/<slug>/deliveries/<topic>/` (outside Git). The PNGs are always 1080 × 1440, `01.png`, `02.png`…, and are only written with confirmation. If the source has a status (e.g. "delivered"), note which one, to change it only with confirmation.
7. **Test the conversion:** generate the standard request from a real request and run `python scripts/structure_request.py "<request>.md" --dry-run`. Show the structure and the exceptions.

**Supporting files:** `docs/production-flow.md` ("Standard request", "Where requests come from", B1 and B7), `projects/_template/project.md` ("Requests and deliveries"), `scripts/examples/standard-request-example.md`, `scripts/examples/notion-task-example.md`, `scripts/README.md` (structure_request), `docs/decisions.md` ("Flexible input and output").

---

## Phase 8 · First test carousel (B1 to B7)

**Goal:** run the whole track B once, stopping at the human review.

1. **B1 · Request:** read a request from the source configured in phase 7 and convert it to the standard request (or, in Notion, save the task to a temporary file, read-only). Text written by the AI only comes in after it is approved.
2. **B2 · Structuring:** `python scripts/structure_request.py "<request>" --dry-run`, then without `--dry-run`. Show the exceptions ("review by hand", "recommended").
3. **B3 · Photos:** 1 main + 2 alternatives per slide, in the order of criteria and of sources in `docs/how-it-works.md`; `measure_coherence.py` and `measure_contrast.py` to rank. External ones only as a preview.
4. **B4 · Review board:** a "<topic> · v1" section on the "Review boards" page, with the `Social/*` components, in three bands (carousel, decision strip, photo suggestions). See `docs/production-flow.md` (B4 and "What is worth turning into a script").
5. **B5 · Check:** measured contrast + screenshot (face, seam, cut-off text), exceptions with level, reason and suggestion.
6. **B6 and B6.1 · Review:** the person looks at the review board. Each feedback point becomes a written criterion **before** redoing (`projects/<slug>/learnings.md` or `docs/carousel-learnings.md`); the review board gets a v2 and the v1 stays below, marked.
7. **B7 · Delivery (only with confirmation):** 1080 × 1440 PNGs `01.png`…`NN.png` in the request's delivery folder (empty: never overwrite), one row per photo used in `media/uses.csv`, indexer, section moved to "Delivered", status at the source if there is one.
8. **Time:** record the milestones in `projects/<slug>/production/timings.csv` from B1 on (header in `docs/production-flow.md`, "Time of each review board"). Real time only.

**Supporting files:** `docs/how-it-works.md`, `docs/production-flow.md`, `scripts/README.md` (structure_request, measure_contrast, measure_coherence), `docs/carousel-learnings.md`, `media/README.md` (Usage log).

---

## When the 8 phases are done

Tell the person that, from now on, each request follows track B (phase 8; summary in "How to request a carousel" and "How you receive it", in `README.md`) and that each review makes the next review board better. Remind them what is still done by hand by Claude (review board assembly in B4 and the B7 logging) and where to see the process: `docs/flow.html`.
