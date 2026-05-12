# Sourcing figures from the web (channel `sourced`)

Some 数模 figures must come from the real world: a specific city's map, a policy document screenshot, a product photo, a satellite image, a historical artifact. AI must not generate these — a fabricated map of a real place is the same kind of integrity failure as a fabricated citation. This file is the protocol for finding, downloading, archiving, and citing them.

## When to enter this workflow

`brief.md` for the figure must declare `type: sourced`. If you find yourself drifting into image-gen for a figure whose subject is real (the problem says "the green delivery zone of Wuhan" — Wuhan is real), stop and switch to `sourced`.

## Folder layout (the contract)

```
stage2_solving/figures/<fig_id>/        # e.g. fig-wuhan-green-zone
├── brief.md                            # type: sourced, content list, claim
├── search_queries.md                   # the queries tried, the platforms hit, what filters
├── sources/                            # all candidates kept until one is chosen
│   ├── candidate_01.png
│   ├── candidate_01.meta.json          # url, date, license, attribution, dimensions
│   ├── candidate_02.png
│   ├── candidate_02.meta.json
│   └── ...
├── chosen.png                          # the selected candidate (may be cropped / annotated)
├── attribution.md                      # final citation form for references.bib + license note
└── self_check.md                       # legality, claim alignment, no overprocessing
```

After self-check passes, the chosen file lands at `stage2_solving/figures/<fig_id>.pdf|png` for LaTeX to pick up.

## Step-by-step

### 1. Write the brief

Same template as `figure-brief-template.md`, but the **claim** clarifies what real-world thing this figure depicts and why the paper needs the actual one (not an illustration):

- "Show the actual configuration of Wuhan's green-zone delivery boundary as defined by 武汉市生态环境局 in 2024-03." (not "a green zone in general")
- "Show the official Five-Year Plan policy document that mandates the carbon-price floor of 80 元/kg CO₂." (not "a policy paper looking like that")

### 2. Plan the search

Write `search_queries.md` BEFORE searching. This is the spec sheet for the search.

```markdown
# Search plan — <fig_id>

## Target
<one sentence: what real-world thing am I trying to find an image of>

## Acceptable sources (in priority order)
1. <Primary source — official publisher / authority of the depicted thing>
2. <Secondary source — Wikimedia Commons, OpenStreetMap, archive.org>
3. <Tertiary — news outlets with photo credit, academic databases>

## Queries to run
- Platform A: "<query 1>"
- Platform A: "<query 2 with site: filter>"
- Platform B: "<query 3>"

## License requirements
- Public domain / Creative Commons (preferred)
- Fair use (acceptable for policy screenshots, etc. — note rationale)
- Paid stock photo (avoid; use only if no alternative AND user-approved)

## Stop conditions
- Found a candidate from priority-1 source that matches the claim → done.
- Tried all queries on priority-2 sources and still nothing → escalate to user.
```

### 3. Run the searches and download candidates

For each match worth keeping, download to `sources/candidate_NN.png` and write the matching `.meta.json`:

```json
{
  "url": "https://commons.wikimedia.org/wiki/File:WuhanMap_GreenZone_2024.png",
  "retrieved_at_utc": "2026-02-08T11:30:00Z",
  "platform": "Wikimedia Commons",
  "title": "Wuhan green delivery zone, 2024 boundary",
  "creator": "User: WuhanMapper",
  "license": "CC BY-SA 4.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
  "dimensions_px": [1820, 1240],
  "file_bytes": 412330,
  "format": "PNG",
  "notes": "matches the boundary described in the problem statement; needs no cropping"
}
```

For platform-specific provenance:

- **OpenStreetMap** — record the `bbox` (min/max lat-lon), the zoom level, and the tile-server URL. Add the OSM contributor attribution line in `attribution.md`.
- **Wikimedia Commons** — copy the canonical Commons URL (not the thumbnail); record the license shortname (CC BY / CC0 / Public Domain).
- **Government policy site** — copy the document URL + the publication date; archive a snapshot at archive.org if the page might disappear.
- **Manufacturer site** — record the model number, retrieval URL; check the site's "Terms of use" for image republication.
- **News outlet** — record the photographer credit; many news photos are agency-owned (Reuters / AP) and not free to reuse — usually you can't use these.

### 4. Choose, optionally crop / annotate, save as `chosen.png`

The chosen file may be a light edit of the candidate:

- **Cropping** is fine — record the crop region in `attribution.md`.
- **Adding annotations** (arrows, circles, labels) is fine — say so.
- **Color adjustment for legibility** is fine — say so.
- **Anything that changes the depicted reality** (move boundaries, recolor regions, remove buildings) is **forbidden** — it crosses the line into fabrication.

Saved as `chosen.png` (or `chosen.pdf` if vector available). The file extension matches what `\includegraphics{img/<fig_id>}` expects — set the extension consistently.

### 5. Write `attribution.md`

The citation that will end up in the paper.

```markdown
# Attribution — <fig_id>

## Source
- URL: https://commons.wikimedia.org/wiki/File:WuhanMap_GreenZone_2024.png
- Retrieved: 2026-02-08
- License: CC BY-SA 4.0
- Creator: User: WuhanMapper (Wikimedia Commons)
- Modifications by us: cropped to focus on the central district; added two yellow
  arrows labeling the delivery checkpoints described in the problem.

## Citation in `references.bib`
```bibtex
@misc{wuhan_greenzone_2024,
  title  = {Wuhan green delivery zone, 2024 boundary},
  author = {{User: WuhanMapper}},
  year   = {2024},
  url    = {https://commons.wikimedia.org/wiki/File:WuhanMap_GreenZone_2024.png},
  note   = {Wikimedia Commons, CC BY-SA 4.0; retrieved 2026-02-08}
}
```

## Caption attribution line
The figure caption in the paper must end with:
"Source: Wikimedia Commons / WuhanMapper, CC BY-SA 4.0."
(or the equivalent for the specific license)

## License compliance checklist
- [x] CC BY-SA: attribution included in caption + bib entry
- [x] CC BY-SA: any derivative must inherit CC BY-SA (the cropped version we ship inherits)
- [x] No author asked us to remove the image (none did)
```

### 6. Self-check

`self_check.md` — same structure as for data/schematic figures, plus three extra rows specific to `sourced`:

```markdown
# self_check.md — <fig_id>

**Checked**: <UTC timestamp>
**Verdict**: ready | needs_revision

## Mechanical compliance
- [ ] chosen.png (or chosen.pdf) exists at expected path
- [ ] No in-figure title from the original source still visible (caption is LaTeX's job)
- [ ] No author / school / our team identifier visible
- [ ] Dimensions ≥ 1000 px on the long side (paper print legibility)

## Sourcing compliance
- [ ] attribution.md exists with URL + retrieved_at + license + creator
- [ ] License permits this use (paper publication, possibly modified)
- [ ] Modifications listed match what we actually did (no hidden alterations)
- [ ] Citation form in attribution.md is appendable to references.bib without edits
- [ ] If CC BY-SA: derivative obligations acknowledged

## Claim alignment
- [ ] The figure depicts the real-world subject named in brief.md
- [ ] No misleading representation (no relabeling, no false coloration, no fabricated boundary)

## Decision
ready | needs_revision
```

If any sourcing-compliance box is unchecked, the figure is **not** ready. Stage 3 will refuse it.

## Search tactics

### Geographic data

- **OpenStreetMap** (https://www.openstreetmap.org/export) — vector + raster, ODbL license. Use the export tool for bounded regions.
- **OpenStreetMap tile services**: cycle, transport, humanitarian themes via specialized tile providers.
- **国家地理信息公共服务平台 — 天地图** (https://www.tianditu.gov.cn) — authoritative for China. Free tier with attribution.
- **Mapbox / MapTiler** — paid; use only if the user has a license.
- **GIS portals**: 地方政府的 GIS / 数据开放平台 often have authoritative boundary shapefiles.

### Satellite imagery

- **NASA Earth Observatory** (https://earthobservatory.nasa.gov) — public domain.
- **Copernicus / Sentinel-Hub** (https://www.sentinel-hub.com) — free tier for academic use.
- **USGS Earth Explorer** (https://earthexplorer.usgs.gov) — public domain.
- **Bing Maps Aerial** — viewable but redistribution restrictions; check terms.

### Policy documents

- The **issuing authority's official site** is the only acceptable primary source. For Chinese policy: 国务院 / 国家发改委 / 工信部 / 生态环境部 etc.
- **Archive.org / archive.today** — for snapshots of pages that may disappear; record both the original URL and the archive URL.
- **NotebookLM** / OCR services — for parsing scanned PDFs into searchable text, BUT the cited figure must be the original scan, not the OCR'd derivative.

### Product / equipment photos

- **Manufacturer's official website** — most permissive when used in academic context, but check "Terms of Use" / "Media kit" page.
- **Wikimedia Commons** — search by model number and product class.
- **Academic databases** (IEEE Xplore, SpringerLink) — figures inside papers; cite the paper, do NOT re-screenshot without permission.

### Historical / cultural

- **Wikimedia Commons** — biggest single source.
- **Library of Congress** (https://www.loc.gov/free-to-use/) — public domain US-focused.
- **中国国家图书馆 / 各省图书馆数字资源** — Chinese historical materials.
- **Archive.org** — long-tail historical scans.

### Datasets and methodology screenshots

- **Source publisher's documentation page** — World Bank, CDC, FAO, NBS, FT.
- **Kaggle dataset pages** — for derived screenshots; record the dataset DOI.
- Cite the dataset itself, not just the screenshot, in `references.bib`.

## Bulk-download helper

`auto-mm-solving/assets/download_image.py` wraps `requests` + `Pillow` to:

1. Fetch a URL with a sane user-agent.
2. Verify the response is an image.
3. Save to `sources/candidate_NN.<ext>`.
4. Emit a starter `candidate_NN.meta.json` (URL + retrieved_at + dimensions + bytes). Other metadata fields the user fills in.

```bash
python auto-mm-solving/assets/download_image.py \
    --url "https://commons.wikimedia.org/wiki/Special:FilePath/WuhanMap.png" \
    --out runs/<slug>/stage2_solving/figures/fig-wuhan-green-zone/sources/candidate_01.png \
    --note "matches problem statement"
```

The helper does NOT auto-classify license — that requires reading the source page and is the human's call.

## What never goes into `sources/`

- Stock-photo agency previews with watermarks.
- Screenshots of another paper's figure (cite the paper; don't re-host the figure).
- Images downloaded behind a paywall where redistribution is forbidden.
- AI-generated images (those are channel `schematic`).
- Photos where personal identifiers are visible (faces, license plates) — blur or pick another candidate.

## Escalation triggers

Open an escalation block in `hand_off.md` if:

- After exhausting all priority-1 + priority-2 sources, no acceptable candidate exists. User decides: (a) reframe the figure (drop the real-world specificity), (b) substitute a schematic with the real-world ambiguity acknowledged, or (c) pay for a licensed stock photo.
- The only candidate available has unclear license. User decides whether to use it (with fair-use rationale) or drop the figure.
- The candidate's resolution is below the print threshold. User decides whether low-resolution + caveat is acceptable.

## Final delivery

After `status: ready`:

- Copy `chosen.png` (or .pdf) to `stage2_solving/figures/<fig_id>.png`.
- Append the `bibtex` block from `attribution.md` to the working `references.bib` collection.
- The writing stage appends the caption attribution line ("Source: ...") to the figure's `\caption{}` automatically.
