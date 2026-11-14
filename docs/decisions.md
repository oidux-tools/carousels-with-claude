# Decision log

One entry per structure or process decision: what was decided and why. New entries go at the end.

The decisions below come from the original process and explain the why behind each rule. When you decide something different in your project, add a new entry at the end saying what changed.

---

## Media bank organized by type; project is metadata

- **Decision:** in the open area of `media/`, each file lives in the folder for its type (photo, video, logo…). The project goes in the file name and in the catalog's `projects` column.
- **Why:** the same media can serve several projects. Folders per project would force duplicating files and losing track of which one is the right version.

## Media catalog in CSV

- **Decision:** `media/catalog.csv`, one row per file, with technical columns (filled in automatically) and context columns (projects, tags, origin).
- **Why:** it opens anywhere (Sheets, Excel, script), versions well in Git and doesn't lock you into any tool.

## Media outside Git

- **Decision:** Git versions structure, documentation, catalogs and scripts. Media files are ignored.
- **Why:** heavy files bloat the repository; Drive (or other storage) handles their backup and sync.

## Catalog indexer in Python, with Pillow only

- **Decision:** `scripts/index_media.py` fills in the catalog's technical columns. It depends only on Pillow; video (mp4/mov), wav and mp3 are read directly by the script, without installing ffmpeg.
- **Why:** it's the smallest install that covers all the common formats in the bank.
- **Rules:** the script never overwrites manual columns and never deletes rows on its own (only with `--prune`), so tags aren't lost when a file is renamed.

## Projects in three layers: guides, sheet and kit

- **Decision:** each project has `projects/<slug>/` with `guides/` (original material), `project.md` (practical summary in text) and `kit/` (production files). The slug is the same as in `media/projects.csv`.
- **Why:** guides are usually long PDFs. A text summary keeps the rules (colors, fonts, tone) at hand for people and automations, without losing the original as a reference.
- **Guides and kits stay outside Git**, like the media; only the `.md` files are versioned.

## Slide components in Figma: variant for position, on/off for optional elements, auto layout

- **Decision:** each slide type is **a single component**. What changes the layout (the position) becomes a **variant**; what only shows or hides (subtitle, watermark) becomes an **on/off property**. The slide uses auto layout with padding bound to the margin variable, and the background (photo, contrast, watermark) sits in absolute position.
- **Why:** it avoids multiplying variants (6 positions × 2 title types would be 12) and guarantees the margin when the text grows.
- **Rules:**
  - The title does **not** get a text field in the panel, because it would lose the highlight word (which uses another font). Single-style elements (subtitle) do get one.
  - Layer opacity bound to a variable goes on the **layer**, not on the paint: paint opacity doesn't carry over to instances.

## Widows: forbidden in body text and lists, solved with a non-breaking space

- **Decision:**
  - In running text and list items, the last line must have at least 3 words. In titles, a widow is tolerated, but avoided.
  - Every automation that generates text (scripts, Claude) joins the last 3 words of each paragraph and item with a non-breaking space (U+00A0). In 4-word paragraphs, it joins only the last 2.
- **Why:** Figma has no native widow control and no "balance text". Joining the last words is the solution that works in any tool and doesn't depend on who does the layout.

## Collab: reduced version of the brand + up to 2 partners in the closing slide footer

- **Decision:** in a collab with other brands, the closing slide swaps the full signature for the **reduced version** of the brand (monogram or symbol) and opens space for up to **2 partner logos** (3 brands in total), on the same line. In Figma, this is a signature variant of `Social/Final`, with instance swap for the logos.
- **Why:** the full signature takes up the width of the panel. With the reduced version, the brand stays present and the partners get equal space.
- **Closing slide badge:** optional, off by default.

## A rule is not a filter: three levels and a recorded exception

- **Decision:** every production rule fits into one of these levels:
  - **Non-negotiable:** never breaks. Text over a face, contrast below 3:1, a hard cut at the spread seam, a widow in body text or a list.
  - **Recommended:** always sought, but can give way with a reason. 4.5:1 without shadow, corner with free space, calm background, little-used photo.
  - **Recorded exception:** when nothing meets the recommended level, the best available option is used, the slide is marked "review by hand" and the reason is written down. A person decides whether to accept, adjust or swap.
- **Why:** rules that are too hard leave few "allowed" photos, and the feed gets repetitive. A well-made, visible exception is better than getting stuck or repeating.
- **In the automation:**
  - The scripts **rank** the options, they don't eliminate them.
  - The automation returns the result with the review marking and the reason, instead of failing.
  - Only the non-negotiable level blocks.

## Contrast before shadow

- **Decision:** legibility comes from the choice of photo and the position of the text. The shadow (Darken) is the last resort, off by default on covers and content slides.
- **Order:**
  1. Free, dark corner.
  2. Measure: the text color × the lightest part behind the text (block + 40 px), target 4.5:1.
  3. Between 3:1 and 4.5:1, or with a busy background: change the corner or reframe.
  4. Darken. Below 3:1, swap the photo.
- **Why:** the shadow makes the post heavier and repetitive. A well-chosen photo makes the shadow unnecessary.
- **Measure:** the criterion is objective (WCAG contrast ratio), so it can be automated by reading the photo. The 4.5:1 target sits above the minimum for large text (3:1) because the post is read on a phone.

## Spreads: at least one per carousel, in a varying position

- **Decision:**
  - Every carousel has at least one spread (horizontal photo across two consecutive slides). The position varies from one carousel to the next.
  - When assembling a carousel, check the previous one from the same project and choose a different spread and text position.
  - Slides outside a spread use their own photo.
- **Why:** it gives rhythm to the carousel and variety to the feed.
- **Consequence:** to vary from the previous one, the automation needs to know what the last carousel was like. The B2 script compares with the project's last JSON.
- **What the spread fixes and what it leaves free:**
  - **Fixed:** the photo is a single one and runs continuously across both slides, with no cut at the seam, shadow included.
  - **Free:** the text of each half. The format (paragraphs, bulleted or numbered list, title only, bold sentence only) comes from the content, and the position comes from the photo's free space.
- **For the automation:**
  - The generator's instruction must say explicitly that each half chooses its own format.
  - Give it several different examples, because a single example becomes a mold.

## Footage logging outside, import inside

- **Decision:** footage logging (organizing, renaming and cataloging raw material) is a separate process, used in any project. This repository only **imports** its result, with `scripts/import_footage_log.py`.
- **On import:**
  - The originals stay untouched in the footage log; the bank receives optimized copies (long side 2400 px, JPEG 85, only author and copyright in the metadata).
  - The name follows `<project>_<group>-<NNN>`: the group is the folder name, and the number is the same as in the footage log, so the original is easy to find.
  - The footage-log columns come into the catalog, except those that only describe the source folder. They are updated on each reimport; the bank's manual columns never are.
  - **No mandatory authorization layer:** usage authorization is requested before footage logging, so what arrives is already cleared.
- **Why:** footage logging is generic and serves any project; the bank only needs to receive the material in its format. A repeated check here would only slow the flow down.

## Catalog separate from where the file lives

- **Decision:** the files live in `media/`. The catalog's `file` column is a path **relative** to the bank (`open/photo/example-brand_shoot-003.jpg`), never a computer path.
- **Why:** the volume of media tends to grow a lot; separating "what exists" (catalog) from "where it is" (storage) lets you change the storage without redoing anything. Only the base address the automation pulls from and returns the file to changes.

## Notion request → project here via the Notion project

- **Decision:** each project here stores the ID of its project in Notion (column `notion_project` in `media/projects.csv`). When reading a task from the **Tasks** database, the automation follows the `Project` relation and finds the slug by that ID.
- **Why:**
  - The Notion **client** doesn't work: the same client can have more than one brand.
  - The **Asset Type** isn't reliable: carousels may be marked with another type.
  - Only the project identifies the brand safely.
- **Rule:** a task from a project with no registered slug doesn't enter the automation; it is flagged ("Notion project with no match").

## Every review board records its own timings

- **Decision:** each review board has a row in `projects/<slug>/production/timings.csv`, with six milestones: request created, prep start, board ready, review start, review end and delivery. The same goes as a card on the review board itself in Figma.
- **Why:** to separate machine time (prep) from human time (review) and idle time (waiting, queue). Only then can you know where the automation really saves time.
- **Rule:** only real times are recorded. An unrecorded milestone stays blank; no estimates. In a pilot, an estimated breakdown added up to 50 min, when the real figure was 13.

## Review board: versions, decision strip and feedback that becomes a criterion

- **Decision:**
  - The review board in Figma is versioned (v1, v2…). The current version sits at the top; the previous ones sit below, marked as superseded.
  - Each slide has a **decision strip**: salmon when it needs a human decision, white when nothing is pending. Alternative photos and reasons stay as support, on one line.
  - **Layout in three aligned bands:** on top the whole carousel, in order and side by side (ready to adjust the photos directly on the slides); below each slide, the comments; last, the suggested photos.
  - All review feedback is recorded as a criterion before redoing: what belongs to the brand goes to `projects/<slug>/learnings.md`; what is general goes to `docs/carousel-learnings.md`.
  - In choosing the photo, **meaning** comes before contrast.
- **Why:** whoever reviews looks, doesn't read. And the same mistake can't come back in the next carousel.

## Images: repository, catalog and usage log separate

- **Decision:** three pieces, each with a role.
  - **`media/` folders:** where the file lives. Every image used in a piece stays here, wherever it comes from.
  - **`media/catalog.csv`:** what the image is (dimensions, description, origin, license). One row per file.
  - **`media/uses.csv`:** what happened to it. One row per image, per **delivered** piece (date, file, project, piece, Notion task, slide, topic). A suggested alternative that wasn't used doesn't go in.
- **Standardized origin:** `footage-log:<batch>`, `stock:freepik` / `stock:pexels` / `stock:adobe-stock`…, `legacy:figma`, `own`, `ai`.
- **`uses` and `last_used`** in the catalog are calculated by the indexer from the log, never typed in.
- **External source or legacy:** the photo is downloaded when chosen and enters `media/` with the origin marked.
- **Why:** a counter typed into the catalog goes out of date and doesn't say where the image was used. The log records the fact once, and the count comes from it. B3 now prefers photos that are little used and not used recently in the same project.

## Bank in two areas: open and restricted, with a code key

- **Decision:** `media/` has two areas:
  - `media/open/<type>/`: whole team, organized by type;
  - `media/restricted/<project>/<type>/`: access limited per project.

  `catalog.csv`, `uses.csv` and `projects.csv` are **single**, at the root of `media/`, with an `area` column (`open` or `restricted:<slug>`).
- **First-level rule:** the top folder is always the access boundary. In the open area, the project is metadata (a photo can serve several projects); in the restricted area, the project is a folder (the content belongs to a single client).
- **Codes in the restricted area:**
  - the group (person, subject) becomes a neutral, random code: `r` + 6 characters of lowercase letters and numbers, without the ambiguous ones (0/o, 1/l/i). E.g.: `example-brand_rk7m2qx-014.jpg`;
  - it is stable, without repetition, and says nothing about the sector;
  - the code → name translation lives in `media/restricted/<project>/_key.json`, visible only to those with access to the area;
  - the catalog, which everyone sees, shows only the code.
- **Why:** the photo protected by the folder isn't enough if the catalog tells whose it is. The code keeps the catalog single and readable without identifying anyone.
- **Note:**
  - the restriction depends on your storage allowing a **folder with limited access** (in Google Drive, a folder with restricted access inside a shared drive). Test before putting sensitive material in;
  - it isn't encryption: the protection comes from the permission on the folder where the key lives.

## Legacy: original before Figma; extra columns in the catalog

- **Decision:** when bringing in a legacy photo (images the project already used before the bank), the source is the **original in Drive** when it exists. Figma only comes in for what isn't in Drive. The origin stays `legacy:figma`, and the real path goes in a `legacy_source` column.
- **Why:** Figma stores at most 4096 px and sometimes only a thumbnail. The originals are usually much larger.
- **Format:** JPEG is copied without recompression. PNG without transparency becomes JPG at quality 95 with the same color profile. PNG only stays PNG when there is real transparency.
- **Extra columns** (preserved by the indexer): `original_file`, `description`, `topics`, `tone`, `free_space`, `orientation`, `legacy_uses`, `legacy_source`.
  - "Format" (horizontal/vertical/square) becomes `orientation`, because `format` is already the extension.
  - An old "uses" becomes `legacy_uses`, because `uses` comes from the log.
- **Scope:** only what has a description goes in. An image without a description stays out until it is described.
- **Spread in the log:** a photo that fills a spread is a single row, with slide `02-03`, and not one per slide.

## Visual version of the process, updated in batches

- **Decision:** the process has a visual version in `docs/flow.html`. It draws tracks A and B and the connections between them, and each step opens its detail on click (goes in, comes out, tool, worked if, how it works inside, status).
- **Source:** the texts (`how-it-works.md` and `production-flow.md`) remain the source. The page only draws what they say and, if it diverges, the texts prevail.
- **Batch update:** the visual isn't redone at every change. Whoever changes the process notes the change in "Pending in the visual", at the end of `how-it-works.md`. With pending items, Claude asks whether to update now or wait to accumulate more.
- **Place:** `docs/`, next to the texts it draws. Single file, no dependencies: it opens directly in the browser.
- **Why:** the text map is hard to see as a flow. Updating the visual at every detail would mean rework, and forgetting to update it would leave the visual lying; the pending list solves both.

## Request structuring (B2) in a script; Notion stays with Claude

- **Decision:** `scripts/structure_request.py` turns the Notion task into the structure JSON. The one who reads Notion is Claude, through MCP and read-only; it saves the `notion-fetch` response to a temporary file and the script reads that file.
- **Why:** the script stays without credentials and without API dependencies, and can be tested with saved files. What matters from the task stays in `origin` in the JSON, so the exported file doesn't need to be kept.
- **Rules chosen** (detail in `docs/production-flow.md`):
  - a single line break joins lines in the same paragraph; a blank line separates;
  - colored text and blocks with a link are notes/references for the designer: they leave the art and become "review by hand";
  - the script never invents a title: a 1st line that is too long becomes "untitled slide";
  - widows: in 4-word texts it joins 2, as the widows decision says;
  - a single spread, on the first content pair different from the project's last JSON; provisional text position, decided by the photo in B3/B5;
  - it never overwrites an existing JSON without `--overwrite`; a project without a slug in `media/projects.csv` stops everything.

## Restricted area: code only when the folder is a person

- **Decision:** in the restricted area, the importer swaps the folder name for a code (`r` + 6 characters) **when the folder identifies a person** (e.g.: a patient). When the folder is something else (shoot date, event, setting), use `--no-code` and keep the name (e.g.: `example-brand_shoot-15-10.jpg`).
- **Why:** the code exists to hide **who**. Swapping a date for a code only removes useful information and would also erase common words from the descriptions.
- **Note:** names of the client's professionals may appear in the descriptions; they are public people of the project, not patients.

## External photos in B3 (Pexels and Freepik) and photo direction

**Context.** The own bank doesn't cover every topic. The external search uses Pexels and Freepik.

**Decisions**

1. **External sources, in this order, after the own bank:**
   - **Pexels** (free): manual search through the app's browser. At most 2 or 3 searches per slide.
   - **Freepik through the Magnific connector** (official server, with your account's login): only when Pexels doesn't solve it. Tools: `stock_search`, `stock_get`, `stock_show`, `stock_download`, `account_balance`.
   - Script straight to the API: postponed. Adobe Stock: out for now.
2. **No keys:** the connector uses your login; Claude never sees a credential. The connector only shows up in sessions opened after login (sometimes you need to restart the app).
3. **Cost on Freepik:**
   - search and details: 0 credits;
   - download: costs credits, according to the `creditCost` field (a premium photo costs more than a free one);
   - check the balance with `account_balance` before downloading.
4. **Download only after approval on the review board.**
   - Searching and viewing a preview is free; Claude does it without asking.
   - The download, from any source, only happens after you approve the photo in B6, and only of the approved photo. Never in batch.
   - On a quality tie, prefer the free option.
   - Generation, upscale, editing and video in Magnific: always with approval.
5. **How it enters B3:**
   - source order: own bank → Pexels → Freepik, when the slide is left with fewer than 2 good options;
   - search in English, portrait orientation, no AI (Freepik filter);
   - criteria order: meaning → non-negotiables → coherence with the photo direction → contrast → format and uses;
   - the slide crop is checked, because the "portrait" filter includes 2:3.
6. **On the review board:**
   - the external photo comes in as a preview, with a "Pexels" or "Freepik · preview" badge (the latter with the download cost);
   - the slide's decision strip turns salmon;
   - once approved, the photo is downloaded and replaces the preview with the high-res version before B7.
7. **Recording the downloaded photo:**
   - file in `media/open/photo/general_<description>.jpg`;
   - catalog: `origin = stock:pexels` (`license = pexels`) or `stock:freepik` (`license = freepik-premium`), plus `author`, `original_link` and ID;
   - Freepik: license PDF stored next to the photo;
   - indexer and `uses.csv` in B7.
8. **License:** read each stock library's current terms before the first use (commercial use, author credit, use for different clients, use in a logo or brand, people in a sensitive context).
9. **AI-generated photos:** filtered out for people in a sensitive scene (e.g.: medical scene). If any gets in, `origin = ai`.
10. **The restricted area never goes to Magnific.** Upscale of an open-area photo only with approval.
11. **When nothing works:** the gap becomes a shot-list item on the decision strip, with the possible ways out (produce with the client or another stock library). Generate with AI only for objects or backgrounds, with approval and `origin = ai`.
12. **Photo direction.** Each project has a sheet `projects/<slug>/photo-direction.md` (A1), built from the real photos and the published posts: light, color, texture, depth, setting, people, pose, framing, and what gives away a "stock-photo look".
    - **In B3:** an external photo that is off loses to another that tells the same stage and matches the real ones.
    - **On the review board:** the decision strip says when the best option is off ("cold light, stock-photo look").
    - **Supporting measurement:** `scripts/measure_coherence.py` compares the candidate's color, temperature, saturation and brightness with the project's reference photos. It doesn't replace visual judgment.
    - **Optional light treatment:** local adjustment of temperature, saturation and grain to bring an external photo closer. It doesn't save a photo that is off in the setting or the people.

## Photo source order: real, legacy, Pexels, Freepik

- **Decision:** in B3, the sources are checked in this order:
  1. **the client's real photos** (`origin = footage-log:…`);
  2. **legacy** (`origin = legacy:figma`);
  3. **Pexels**;
  4. **Freepik** (Magnific connector).

  The two external ones only come in when the slide is left with fewer than 2 good options in the bank.
- **Why:** the real photo is the most authentic and the one that best matches the brand. The legacy has already been used and tends to repeat in the feed. The external ones cost search, license and sometimes credits.
- **The criteria don't change:** meaning → non-negotiables → coherence → contrast → format and uses apply to all of them. The source order decides who is checked first and who has the edge in a tiebreak.

## Kit creation guide (A1)

- **Decision:** creating the kit for a new project (step A1) follows `docs/project-kit-guide.md`: read → extract → sheet → Figma Foundations (variables → styles → logos) → Figma Social Media (cover → content → closing → contrast) → checklist → questions → record. Each brand's design system file (`-<slug>`) always has the **same structure**: "Design System" page with the frames "Foundations — <Brand>" and "Social Media — <Brand>".
- **Why:** the same structure makes B4 (Assembly) the same for every brand, and the guide avoids repeating mistakes already seen.
- **Diverging sources:** for post style, the **published posts and the production file** prevail; for brand rules (logo, forbidden colors, tone), the brandguide prevails. The differences go in a "Discrepancies" table in the project sheet.
- **Font unavailable in Figma:** use the fallback font from the production file, noted in the project sheet and in the style description.
- **Gradients with fixed hex:** binding a variable to a gradient stop forces alpha to 100%; gradients keep a fixed hex and the documentation says which brand color they use.

## Profile and image in each project's sheet

- **Decision:** every project sheet (`projects/<slug>/project.md`) has the **"Profile and image"** block: project type, what the feed needs to prove, what the image shows, what it never shows, care with people and preferred photo source. It is the basis of the **meaning** criterion in B3.
- **Source:** a summary of what the team has already recorded about the client (in the original, made by Notion AI with a prompt that writes "not found" when there is no record), stored in `projects/<slug>/guides/notion-profile.md` with the links. The sheet block summarizes; the file is the proof.
- **Why:** the same topic calls for a different image in each project (in one brand, the patient; in another, the clinic and the team). Without this written down, the meaning criterion becomes taste.
- **Relation to photo direction:** "Profile and image" says **what** to show; the photo direction (`photo-direction.md`) says **how** the photo should look.

## Review boards on a single page; delivered ones on another

- **Decision:** in each project's Figma there are **two pages** for production, and not one page per piece of content:
  - **"Review boards":** everything in progress. Each piece of content is a **section** with the topic and the version (e.g.: "Topic · v2"), one below the other. The superseded versions sit right below the current one, marked.
  - **"Delivered":** when the content is approved and delivered (B7), the section leaves the review boards and comes here, with the delivery date in the title. Tests and pilots without a delivery come here marked as "test".
- **Why:** with one page per piece of content, the file fills up with pages and it gets hard to see what is open. The single review boards page shows the queue; the delivered ones stay as history, without getting in the way.

## Official format: 1080 × 1440 for all projects

- **Decision:** every carousel, from any project, comes out at **1080 × 1440 (3:4)**.
- **New project:** the components are born at 1080 × 1440 (spread of 2160 × 1440), even if the brand's old posts use another size.

## The request rules the structure

- **Decision:**
  - **No slide is added** to what the client sent (e.g.: signature slide). The component can stay in the design system.
  - **The "+++" row doesn't go in**, not even when it carries text: it belongs to the request's table template.
  - **The client's bold stays bold**, in the content and in the closing slide.
- **Why:** the structure corrected by hand on these points showed they were corrections that didn't need to be made.

## Flexible input and output: standard request, configured source and delivery folder

- **Decision:**
  - **Standard request.** Every request becomes, before B2, a neutral `.md` file with `project` (slug), `topic`, `delivery_folder` and the "Sequence / Art Text" table (format in `docs/production-flow.md`). `scripts/structure_request.py` reads that file and finds the project by its slug, without needing a Notion ID. Reading a Notion task directly still works.
  - **Source configured per project.** Where the requests come from (Notion, another tool, spreadsheet, documents, text written by the AI), how Claude accesses it and the mapping of fields to the standard request live in the project sheet, section "Requests and deliveries". Notion, with the fields from the original process, is documented as an example.
  - **AI-generated text** is a source like the others and happens before B1: the text only becomes a request after the person approves it. B2 keeps organizing without rewriting.
  - **Configurable output.** The delivery folder comes from the request. Without another one, the default is `projects/<slug>/deliveries/<topic>/`, outside Git. The PNG is still 1080 × 1440, `01.png`…, and is only written with confirmation.
- **Why:** Notion is the tool of whoever built the process, not one of its rules. Each person receives requests in a different way; with a neutral format in the middle, the rest of track B doesn't change.

## Repository in English; carousel text in Portuguese or English

- **Decision:**
  - **Everything in the repository is in English:** documents, the visual, the skill, folder and file names, scripts (messages, names, CSV headers and JSON keys). The glossary in the root `README.md` gives the English name of each process term.
  - **The skill answers in the language of whoever talks to it** and is triggered by "help me implement" and also by the Portuguese "me ajuda a implementar".
  - **The carousel text can be in Portuguese or in English.** `scripts/structure_request.py` keeps the Portuguese list of weak words (which are not used as highlight nor in the file name) and gained the English equivalent; the two lists are used together. The header row of the slides table is recognized as "Sequence" or "Sequência". The incomplete-sentence check ("um dos / uma das" without "mais") remains Portuguese only. This is the only change in the scripts' behavior that came with the translation.
- **Why:** the method is public and should be readable by anyone; the people who come from the Portuguese posts keep writing in Portuguese and producing carousels in Portuguese.
