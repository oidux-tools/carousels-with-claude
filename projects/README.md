# Projects

One folder per project (client or brand), with everything needed to produce content for it.

## Structure

```
projects/
├── _template/            copy this folder to create a new project
└── <slug>/               e.g. example-brand/
    ├── project.md        sheet: who it is, tone of voice, profile and image, visual identity, requests and deliveries
    ├── learnings.md      art direction learned in this brand's pilots and reviews
    ├── photo-direction.md  how the photo should look (B3's yardstick and reference photos)
    ├── guides/           application guides, brandbook, brand manual (as received)
    ├── kit/              production kit: templates, official logos, fonts, palettes
    ├── production/       the structure of each carousel (<topic>.json, from B2) and timings.csv
    └── deliveries/       default delivery folder for the PNGs (<topic>/01.png…), outside Git
```

## Three layers, each with a role

| layer          | what it is                                | who reads it                         |
|----------------|-------------------------------------------|--------------------------------------|
| `guides/`      | the original material, untouched (PDFs etc.) | people, when in doubt             |
| `project.md`   | the practical summary of the guides, in text | people and automations, day to day |
| `kit/`         | the production files ready to use         | whoever builds the pieces            |

`project.md` is the **quick reference source**: colors in hex, fonts, logo rules, tone of voice, what to avoid. If something in the summary conflicts with the original guide, the guide wins and the summary is corrected.

## Create a new project

1. Choose the slug (lowercase, no accents, hyphen between words) and add it to `media/projects.csv`.
2. Copy `_template/` to `projects/<slug>/`.
3. Put the guides in `guides/` and the kit in `kit/`, the way they came.
4. Fill in `project.md` from the guides.

## Project kit × media bank

- **`kit/`**: the project's official identity (logo, fonts, templates). It stays together, as a package.
- **`media/`**: reusable raw material (photos, videos, icons…), linked to the project by the slug in the file name.
