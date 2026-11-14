# Instructions for Claude

- Reply in the language the person writes in (the repository is in English; many people will write in Portuguese), in simple language: whoever uses this repository may not be technical.
- **Guided implementation:** when the person says "help me implement" (or the Portuguese "me ajuda a implementar"), "I want to implement", "where do I start?", "set it up for me" or something similar, use the `implement` skill (`.claude/skills/implement/SKILL.md`) and follow its phases, one at a time.
- This project is built little by little, in conversation: process first, tool later. Do not create folders or areas "for the future" without the process being defined.
- The map of the process is `docs/how-it-works.md` (tracks A and B, steps A1–A4 and B1–B7). When talking about a process or step, use those names and codes.
- Visual version of the process: `docs/flow.html`. When changing `docs/how-it-works.md` or `docs/production-flow.md`, **do not** update the visual right away: note the change in "Pending in the visual", at the end of `how-it-works.md`. When closing a step or before a commit, if there is anything pending, ask the person whether to update the visual now or wait to accumulate more. When updating, empty the list and change the date (in `how-it-works.md` and at the top of `flow.html`).
- Before creating or moving something, read the root `README.md` and the one in the folder involved, and follow the naming conventions there.
- Every structure or process decision goes to `docs/decisions.md`.
- At the end of each step, add an entry to `docs/journal.md` (request → done → problems → lesson), including what went wrong. The number is always the **file's last + 1**, read at the time of writing (several sessions may write to it). Before each commit, check that the journal is up to date.
- When working on a project, first read `projects/<slug>/project.md` (with the Profile and image block), `projects/<slug>/learnings.md` and `projects/<slug>/photo-direction.md`, and also `docs/carousel-learnings.md`; when in doubt, the original guide in `guides/` wins.
- Review feedback becomes learning: what belongs to the brand goes to `projects/<slug>/learnings.md`; what applies to any project goes to `docs/carousel-learnings.md`.
- Media bank: rules in `media/README.md`. Never version media files; never delete anything from `media/` without confirmation.
- Nothing goes out without a person: publishing, delivering, downloading a paid photo and changing Notion (or another source of requests) only with confirmation.

## How to ask for a carousel

- The person indicates the request in their own way: a task link, "the next ready request", a file, or a topic for the AI to write about.
- The source, the access and the field mapping are in the project sheet, section "Requests and deliveries". Read the source (read-only) and convert it to the **standard request** (`docs/production-flow.md`): project, topic, delivery folder and the "Sequence / Art Text" table. For the Notion task, the script also reads the saved file directly.
- Text written by the AI from a topic only becomes a request after the person approves it. After that, nobody rewrites it: B2 only organizes.
- Follow B1 to B5 (`docs/how-it-works.md`, `docs/production-flow.md`) until the review board is ready and stop at the human review (B6).

## How the person receives it

- **Review:** a section "<topic> · v1" on the project's Figma "Review boards" page (carousel, decision strip, photo suggestions). Feedback becomes a written criterion before v2.
- **Delivery (B7), only with confirmation:** 1080 × 1440 PNGs `01.png`…`NN.png` in the request's `delivery_folder`; without another, `projects/<slug>/deliveries/<topic>/`. The folder must be empty (never overwrite). Record in `media/uses.csv` and `timings.csv`; status in the source only with confirmation.
