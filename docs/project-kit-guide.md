# Guide · how the AI creates the kit for a new project (A1)

Step by step for Claude to assemble the **production kit** of a new brand: the sheet (`project.md`), the design system in Figma and the carousel rules. It applies to any brand and sector.

- **Where it comes from:** this guide was written after assembling the kit of two real brands. Their names, files and styles are not here; only the **structure** and the mistakes that practice revealed remained. Copy the structure, never the style of another brand.
- **Where it sits in the process:** track A, step **A1 · System and style** (`docs/how-it-works.md`). The kit is what B4 (assembly) consumes later.
- **General rules** that apply here: `docs/decisions.md` and `docs/carousel-learnings.md`.

> ⚠️ **The brand's taste is not assumed.** Whatever is not clear in the references becomes a question for you (step 7). Build with the best reading, leave it marked as provisional and ask.

---

## Work order

| step | what | what comes out |
|---|---|---|
| 1 | Read and locate the sources | list of references and where they are |
| 2 | Extract the identity | notes on color, font, logo, tone, carousel |
| 3 | Fill in the sheet | `projects/<slug>/project.md` and `guides/` |
| 4 | Figma · Foundations | variables → styles → logos |
| 5 | Figma · Social Media | cover → content (+ list item) → final → contrast |
| 6 | Check | checklist with screenshot and new instance |
| 7 | Ask | list of taste questions for you |
| 8 | Record | decisions, journal, learnings |

**Priority when there is a deadline:** Foundations → cover → content unlock production. Final, collab and documentation come later.

---

## 1. What to read first and where to look

Read in this order, **only reading**, without changing anything in the sources:

1. **Repository:** `CLAUDE.md`, `README.md`, `projects/README.md`, `projects/_template/`, the project's sheet and learnings (even if empty), `docs/carousel-learnings.md`.
2. **Brandguide / brand manual** (PDF, site, branding Figma). Usually: guide, colors, typography, logos in SVG/PNG/PDF. Read the text and **render the pages** (PyMuPDF: `pymupdf.open(pdf)[i].get_pixmap(dpi=55)`); many guides have rules only in the image.
3. **Published posts:** the folder where the brand's deliveries are kept (e.g.: folders `YYYYMM_Carousel_<topic>` with `01.png`…) or Instagram itself. Build a **contact sheet** per carousel (all the slides side by side, in a single image) and look at the most recent ones first.
4. **Production file in Figma** (where the posts were made), if there is one. It is the most precise source: real fonts, sizes, gradients, effects, margins. Read by script (`use_figma` read-only) the layer tree of 2 or 3 recent carousels: type, position, size, fill, font of each piece of text.
5. **Ready-made kit**, if the brand already has one (for example, a Figma plugin made for it): read **also the plugin's code**, which keeps measurements that the documents don't say.
6. **Photos:** `media/catalog.csv` filtered by the slug, and the real photos in the bank. Build **contact sheets** (in the scratchpad, never in the repository) with a sample of the featured ones (`featured = yes`) and with the published posts, and describe what you see: light, color, texture, depth, setting, people, pose, framing. It is the basis of `photo-direction.md` (step 2).
7. **What the team has already recorded in Notion** about the client (briefings, meetings, photo guidelines, feedback). Run the prompt below in **Notion AI** (or in the tool where the team keeps this) and save the answer in `projects/<slug>/guides/notion-profile.md`. It is the source of the sheet's "Profile and image" block.

   ```
   Search the whole workspace for everything that exists about the client "<Name>": client pages, projects, briefings, meetings, proposals, content surveys, feedback and Social Media tasks. Build a summary using only what is written; where there is no information, write "not found".
   Profile: type; services; audience; what the Instagram needs to prove; tone of voice.
   Image: what the photos should show; what never to show; care with people (patients, children, team, data); photo sources mentioned; feedback on photos or artwork approved or rejected.
   Sources: the link for each piece of information.
   ```

**Order of authority when the sources diverge**
- For **post style** (layout, sizes, applied colors): **published posts and production file** win over the brandguide. Note the difference in the sheet (section "Divergences").
- For **brand rules** (logo, clear space, forbidden colors, tone): the brandguide wins.
- If the brandguide asks for a font that **is not available in Figma**, use the stand-in that the production file itself uses, and note it. *(In one of the cases, the brandguide's two fonts did not exist in Figma, and the posts used two others from Google Fonts.)*

> ⚠️ The official format for all projects is **1080 × 1440 (3:4)**. Build the components at that size, even if the brand's old posts use another.

## 2. What to extract

Build a note (it can be in `project.md` itself) with:

- **Colors:** hex of each color, **where** it appears in the posts (background, text on photo, text on light, gradient, detail) and what is forbidden. Separate *primitives* (the palette) from *roles* (text on photo, panel background…).
- **Fonts:** family and weight for each role (cover title, content title, highlight word, text, list, signature), size, line height, letter spacing, case (upper or normal). See whether the title mixes two fonts in one line (highlight): if so, the line height has to be in **pixels** (step 4).
- **Logos:** versions (full, symbol, wordmark, signature with tagline), allowed colors, minimum size, clear space, where each version appears in the carousel.
- **Graphic elements:** graphic motifs, watermark, halos, list markers, noise/grain, photo filter.
- **Tone of voice:** how it speaks and how it doesn't, with 3 real sentences from the posts.
- **Carousel structure:** typical number of slides, what the cover, middle and closing are, whether there is a signature-only slide, whether there are spreads, where the titles go, how the text gains contrast over the photo (shadow, gradient, veil, panel).
- **Measurements:** real margins (x/y position of the text in the posts), width of the text boxes, distance title → text, between paragraphs, between list items.
- **Photography:** light, color, treatment (filter), what to avoid. It becomes the sheet `projects/<slug>/photo-direction.md` (template in `_template/`): the yardstick per aspect, what gives away a "stock-photo look" in this project, "accept with a light adjustment × can't be saved" and **10 to 20 reference photos** from the bank (paths from `media/…`, preferably real featured ones), which `scripts/measure_coherence.py` uses as the yardstick. Mark each line with the source ([brandguide], [Notion], [observed]); whatever is only taste becomes a question (step 7).

## 3. How to fill in the sheet

1. Copy the brand material to `projects/<slug>/guides/` **without touching the original** (Git ignores this folder). Copy the brandguide, colors, typography and logos in SVG; do not copy video projects or concept files.
2. Fill in `projects/<slug>/project.md` following `_template/`, in the same order as the template:
   - header (slug, status, area, links, **design system and production Figma**, source of the summary);
   - About · Audience · Topics · Tone of voice (with real examples);
   - **Profile and image:** project type, what the feed proves, what the image shows and never shows, care with people and preferred photo source, based on `guides/notion-profile.md`. It is the basis of the B3 meaning criterion;
   - Visual identity: color table (name, hex, use), fonts (official × used in Figma), logos, elements, photos;
   - Carousel: format, structure, cover and content variants, typography (table of styles), spacing, widows, contrast, checklist;
   - **Divergences** between brandguide and posts;
   - **Open questions**: the questions from step 7.
3. Audience and tone that were inferred (and not written by the brand) get *(inferred; confirm)*.

## 4. Figma · Foundations

**File:** a `-<slug>` file only for the design system, with the **Design System** page. Inside it, two frames side by side:

```
Design System
├── Foundations — <Brand>        (x 0)
│   ├── Title
│   ├── Colors         (swatches + table of usage tokens)
│   ├── Typography     (families, styles, highlight rule, widows rule)
│   ├── Spacing        (bars with value, variable and use)
│   └── Logos          (components with color variants)
└── Social Media — <Brand>       (x 2400)
    ├── Title
    ├── 01 · Covers
    ├── 02 · Content
    ├── 03 · Final
    └── 04 · Contrast and legibility
```

Before creating: load the skills `figma-use` (and `figma-generate-library` for components), open a session (`create_session`) and **inspect the file** (pages, variables, existing styles).

### 4.1 Variables (first)

Three collections, one mode each:
- **Primitives:** the raw palette (`color/…`; if the brand already has names, use the brand's, e.g. `neutral/paper`, `accent/burgundy`). No scope (they don't appear in the pickers).
- **Brand:** roles, as an **alias** of the primitives: `text/on-photo`, `text/on-light`, `background/…`, `logo/…`, `highlight/…`. Explicit scope: `TEXT_FILL` for text, `FRAME_FILL`/`SHAPE_FILL` for background.
- **Spacing:** margin and every space that repeats (title → text, between paragraphs, between items, marker → text, panel padding). Scope `GAP` + `WIDTH_HEIGHT`. Description on each one.

> ⚠️ Figma has no "spacing style": spacing is a **variable**.
> ⚠️ Every new measurement in a component is born as a variable. Box widths and documentation measurements don't need to be.

### 4.2 Styles

- **Color:** one `Color/<Name>` style per primitive, **bound to the variable** (`setBoundVariableForPaint`, which returns a new paint: reassign it).
- **Text:** one style per role, named by slide (`Cover/Title`, `Cover/Highlight`, `Content/Title`, `Content/Highlight`, `Content/Text`, `Final/…`). Description on all of them.

> ⚠️ **Line height in pixels** when two styles share the line (title + highlight): the same fixed line height on both. In percentage, the line with the highlight ends up more open.
> ⚠️ Always adjust the **style**, never the loose text, and note where the design system departs from the kit.
> ⚠️ Weight names vary by family (`SemiBold` × `Semi Bold`): list them with `listAvailableFontsAsync()` before using.

### 4.3 Logos

- One **component set per version** (`Logo/Symbol`, `Logo/Wordmark`, `Logo/Signature`…), with the **Color** property as a variant (the colors allowed by the brand).
- Source: the **official SVGs** (`createNodeFromSvg`). If the version used in the posts only exists in the production Figma, export it from there as SVG (read) and recreate it.
- Crop the frame to the drawing (the SVGs usually come with a huge artboard) and bind the color to the `logo/…` variable.
- Each logo appears **once** in the Foundations, inside the frame; nothing loose on the page.

When the Foundations are done: **screenshot of the whole frame** and check (step 6) before moving on.

## 5. Figma · Social Media

### 5.1 Construction rules (apply to every `Social/*` component)

- **One component per slide type.** What changes the layout (position, style) is a **variant**; what only appears or disappears (subtitle, list, halo, darken) is an **on/off toggle** (decision "Slide components").
- Slide in **auto layout**, padding bound to the margin variable; **background in absolute position** (photo, veils, gradients, contrast, watermark).
- **Single-style** texts (subtitle, paragraph, sentence) get a text field in the panel. The **title does not**: it mixes fonts (highlight) and the text field would erase the mix.
- Photo layer: rectangle called **"Photo (swap image)"** with a provisional fill (gradient in the brand's tone) or a real photo of the brand.
- Variant names the same as those of the JSON/automation, when there are any (`top-left`, `bottom-right`…).
- Documentation frame next to each section: **properties**, **specifications per variant** and **rules**.

> ⚠️ **Layer opacity bound to a variable goes on the layer, not on the paint**: the paint opacity does not carry over to the instances.
> ⚠️ **No comma inside a variant value** ("F · Bottom right, aligned" breaks). The comma only separates properties.
> ⚠️ After **cloning a variant**, check whether the properties are still bound.
> ⚠️ In auto layout, set the height mode **after** any `resize()`.
> ⚠️ **Frames with text do not clip content** (`clipsContent = false`): the italic descender (g, j, p, ç) goes past the box. Only the slide clips.
> ⚠️ The shadow/darken effect **may cross over** to the neighboring slide in a spread; what it can't do is an abrupt cut at the seam.

### 5.2 Cover · `Social/Cover`

1. Discover the **logic** of the published covers before creating variations: for example, opposing corners (text in one corner, brand in the opposite one) or background styles with centered text.
2. Main variant = that logic (e.g.: Position A–F, or Style A–C).
3. On/off toggles for the optional ones (subtitle, watermark, halo, "swipe", darken).
4. Test with a **4-line title** in a new instance: the margin cannot be invaded.

### 5.3 Content · `Social/Content` and `Social/List item`

1. Survey the **real layouts** of the middle (where the title goes, where the text goes, how they gain contrast) and turn each one into a variant.
2. On/off toggles: Title, Paragraph 1, List, Item 4, Item 5, Paragraph 2, Highlight sentence, Darken, depending on the brand.
3. List with its own component (`Social/List item`): the brand's marker + text, gap by variable, numeric marker with **fixed width**. Figma's native list does not let you color the marker or use the variables.
4. Default texts already with the **last 3 words joined by a non-breaking space** (U+00A0), the widows rule.
5. If the brand uses spreads: an example of a spread with a continuous photo and the "fixed photo, free text" frame (decision "Spreads").

> ⚠️ **An example becomes a mold.** Every example that shows only one possibility needs a line saying what is fixed and what is free.

### 5.4 Final · `Social/Final`

- Variants based on the published closing models (panel, large sentence, signature-only slide…).
- **Collab:** only if it makes sense for the brand. Default: the brand becomes the reduced version and gives up space to up to 2 partners, by **instance swap** with a `Social/Partner logo (space)` component.
- An element that appears in a reference but not in the guide goes in **optional and turned off**, with a recorded question.

### 5.5 Contrast and legibility

Short section with the ladder from the decision "Contrast before shadow" adapted to the brand: which text color on photo, which contrast resource the brand uses (shadow, gradient, veil, panel) and the reference measurement (up to which gray the light text gives 4.5:1). And the "A rule is not a filter" frame.

## 6. What to check at the end

- [ ] **Screenshot** of each frame (Foundations, Covers, Content, Final) after creating it. Opacity and clipping defects only show up in the image, not in the data.
- [ ] **New instance** of each component, outside the main component, in each variant. Change text, turn each property on and off.
- [ ] **4-line** title and list with a **two-line** item in a new instance: margin intact, nothing overlapping.
- [ ] Highlight descenders (g, j, p, ç) whole in the screenshot.
- [ ] **Audit by script:** every padding and gap of the components bound to a variable; every text with a style; every color bound to a variable or style.
- [ ] Contrast of the text over the provisional background and over a real photo measured (target 4.5:1; minimum 3:1).
- [ ] Logos: once each in the Foundations, correct colors, nothing loose on the page.
- [ ] Sheet (`project.md`) with the Figma link, the styles and the divergences.

## 7. What to ask you (instead of assuming)

Ask, in a single list, whatever is taste and is not clear:

- divergences between brandguide and posts (which one applies from now on);
- official font × font available in Figma;
- post format (4:5 × 3:4) when the posts vary;
- elements that appear in some posts and not in others (halo, "swipe", seal, signature-only slide);
- whether there is a spread, collab, standard CTA;
- audience and tone, when inferred;
- colors that appear in the posts but not in the guide (e.g.: a darker burgundy only in the gradients).

Build with the best reading and leave the doubt written in the sheet ("Open questions") and in the Figma documentation ("provisional").

## 8. Record

- Structure decisions → `docs/decisions.md` (new entry at the end).
- The step → `docs/journal.md` (number = last + 1, read at the time).
- What is brand-specific → `projects/<slug>/learnings.md`; what applies to any project → `docs/carousel-learnings.md`.
- Did the process map change? Note it in "Pending in the visual" (`docs/how-it-works.md`).
- New problems that practice reveals → fix **this guide**.

---

## Pitfalls already seen, one line each

| pitfall | what to do |
|---|---|
| measurement that only exists in the plugin's code | read the code too |
| loose and repeated logos | one of each, inside the Foundations |
| color bound to a variable loses the opacity | reapply the opacity; check by screenshot |
| adjustment on the loose text | adjust the style and note the difference from the kit |
| cloned variant loses a property | rebind and check |
| variation made by position, without the logic | understand the logic first |
| comma in a variant name; opacity on the paint | parentheses; opacity on the layer; test with a new instance |
| uneven line height with highlight | fixed line height in px on both styles |
| overlapping list item; misaligned numbers | "hug" height after the resize; fixed width on the number |
| widows | non-breaking space in the last 3 words, at generation |
| shadow cut at the seam | it can cross over; it can't be cut |
| an example becomes a mold | write what is fixed and what is free |
| "there's X on everything" | survey where X appears before changing |
| space typed by hand | audit by script; create a variable |
| rule that locks things up | non-negotiable × recommended × recorded exception |
| element only from the reference | optional and turned off, with a question |
| pasted partner logo | instance swap |
| `imageHash` from another file comes out empty | export the image and send it with `upload_assets` |
| descender cut by a mask | text frame without clipping |

### Pitfalls seen in the second brand's kit

| pitfall | what to do |
|---|---|
| **gradient bound to a variable loses transparency**: Figma accepts the variable on the gradient stop, but forces the alpha to 100% | gradients with fixed hex; note in the documentation which variable each one represents |
| **Noise** effect (`NOISE`) rejects the `blendMode` key | create the effect without `blendMode` |
| noise on the **whole frame** creates moiré in the thumbnails | put the noise on a background layer (rectangle) and check the screenshot at real size |
| **Glass** effect (`GLASS`) "disappears" over a flat background | that's normal: it refracts what is behind it; check over a photo or gradient |
| element that only exists in the production Figma (vectorized signature, halo, marker) | read and export it from there (`exportAsync({format:'SVG_STRING'})`, read-only) and recreate it with `createNodeFromSvg`; a layer without fill (glass) exports empty: copy the `vectorPaths` |
| official SVG with a huge artboard | crop the component to the bounds of the vectors and only then rescale |
| changing `visible` on a layer bound to a property changes the **property default** for all variants | adjust the default with `editComponentProperty` and don't hide a bound layer |
| 3-variant component (3 × 1080) wider than the 2240 px frame | variants in a 2-column grid; examples in a reduced instance (66%) |
| changing the text of a title with two fonts leaves everything in a single style | document it in the cover rule: reapply the styles after changing the text |
| real photo in the examples: `upload_assets` only accepts the id of a simple node (not an instance layer) | upload into temporary rectangles, copy the `imageHash` to the instance's "Photo" layer and delete the temporary ones |
| three joined words don't fit in a narrow column | in the narrow column, join 2 words (see `docs/carousel-learnings.md`) |
| the audit found spaces typed by hand (cover footer, collab) | create the variable and bind it; run the audit again |
