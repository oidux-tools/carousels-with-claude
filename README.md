# Carousels with Claude

**To get started:**
1. Download this folder (on GitHub: **Code → Download ZIP**, or `git clone`).
2. Open the folder in **Claude Code** (app or terminal).
3. Write: **"help me implement"** (in Portuguese, "me ajuda a implementar" also works). Claude shows the phases and guides you through one at a time.

---

## What it is

A process to produce Instagram carousels with Claude, from the request to the delivery of the PNGs. It was put together and used in real production; here is the method, without client data.

The process has **two tracks** that run together:

- **Track A · Groundwork** (A1–A4): the brand sheet (tone of voice, profile and image, visual identity), the design system in Figma, the cataloged photo bank and the rules.
- **Track B · Production** (B1–B7): for each request, Claude structures the text into slides, chooses the photos, builds a **review board** in Figma and checks contrast and faces. You review by looking, approve, and only then does it deliver.

The full map is in [`docs/how-it-works.md`](docs/how-it-works.md). The visual version, with clickable steps, is [`docs/flow.html`](docs/flow.html) (opens in the browser).

## How to ask for a carousel

After implementing (phase 7 of the skill agrees on where your requests come from):

1. **Tell Claude what the request is.** Examples: "make the carousel for the task <link>", "take the next ready request from the spreadsheet", "make the request from the file <path>" or "write a carousel about <topic> for <brand>".
2. If the AI wrote the text, **you approve it first**. From then on, the text is not rewritten.
3. Claude converts the request into the **standard request** (project, topic, delivery folder and the text per slide) and follows track B:
   - **B2** organizes the text into slides (cover, contents, final, at least one spread), without rewriting;
   - **B3** chooses 1 main photo and 2 alternatives per slide;
   - **B4** builds the review board in Figma;
   - **B5** checks contrast, faces and seam and flags what needs your decision.

Format of the standard request and examples: [`docs/production-flow.md`](docs/production-flow.md) ("Standard request") and `scripts/examples/`.

## How you receive it

1. **To review:** a new section on the project's Figma **"Review boards"** page, with the carousel on top, one strip per slide (salmon = your decision) and the suggested photos below. You look, approve or give feedback; each point of the feedback becomes a written rule before the new version.
2. **After approval and only with your confirmation:** the **1080 × 1440** PNGs, `01.png`, `02.png`…, in the request's delivery folder. If you don't have another place, the default is `projects/<slug>/deliveries/<topic>/`. If the request's source has a status (e.g. Notion), it only changes with your confirmation.

## What you need

- **Claude Code** and a Claude account.
- **Python 3.10+** (for the catalog, contrast and structure scripts).
- **Figma**, with the Figma connector turned on in Claude (design system and review board).
- **A source of requests**: the one you already use (Notion, another tool, spreadsheet, documents) or none, if the AI is going to write the text from a topic. A tool with a connector needs the connector turned on in Claude.
- For external photos (optional): **Pexels** (through the browser) and **Freepik** through the Magnific connector.

The `implement` skill checks all of this in the first phase.

## Map

| folder     | what for                                          |
|------------|---------------------------------------------------|
| `projects/`| one folder per project (brand): sheet, learnings, photo direction, guides, kit and production. Start by copying `projects/_template/` |
| `media/`   | media bank: raw photos and videos, catalog and usage log. New material comes in through `media/_inbox/` |
| `docs/`    | the process, the decisions, the general learnings and the journal |
| `scripts/` | automations (catalog, import, request structure, contrast, color coherence) |
| `.claude/skills/implement/` | the step-by-step guide Claude uses to help you implement |

Every main folder has a `README.md` saying what goes in it.

## General conventions

- **Names** of folders and files: lowercase, no accents, no spaces. `_` separates fields, `-` separates words.
- **Folders with `_` in front** are for special use (e.g. `media/_inbox/`).
- **Dates** inside files: `YYYY-MM-DD`.
- **Lists and catalogs** in CSV (UTF-8, comma): they open in Sheets/Excel and are read by any script.
- **Structure decisions** are recorded in [`docs/decisions.md`](docs/decisions.md).
- **The history of your process** (what was done, what went wrong, what you learned) is in [`docs/journal.md`](docs/journal.md).

## Glossary

The process was born in Portuguese; these are the English names used throughout the repository.

| term | what it is |
|---|---|
| **carousel** | an Instagram post with several slides (carrossel) |
| **review board** | the Figma section where a carousel is reviewed: carousel on top, decision strip, photo suggestions below (mesa). All boards live on one **"Review boards"** page per project |
| **decision strip** | the bar under each slide on the review board: salmon = your decision, white = nothing pending (tarja de decisão) |
| **spread** | one photo across two consecutive slides |
| **seam** | where the two halves of a spread meet (emenda) |
| **footage logging** | organizing and cataloging the raw material outside this repository; its output is the **footage log** (decupagem) |
| **standard request** | the neutral request format that B2 reads (pedido padrão) |
| **project sheet** | `project.md`, the practical summary of a brand (ficha) |
| **widow** | a word left alone on the last line of a paragraph (viúva) |
| **highlight** | the word of the title marked to stand out (destaque) |
| **yardstick** | the reference a photo is measured against (régua) |

## Git

- Git versions only text: processes, sheets, catalogs and scripts. Media, guides and kits stay out (`.gitignore`); keep them on a drive that has backups.
- If the repository is inside a synced folder (Google Drive, OneDrive), it works well with one person running Git at a time.
- **Careful when publishing yours:** sheets, catalogs and the usage log may have names of clients and people. If you are going to share your version, keep the repository private.
