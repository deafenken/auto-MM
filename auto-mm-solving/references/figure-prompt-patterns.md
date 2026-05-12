# Figure prompt patterns

Three patterns, one per output channel. Pick the pattern, fill the slots from `brief.md`, save to `prompt.md`.

## Pattern A — matplotlib code prompt (for `type: data`)

```
You are generating a matplotlib script that plots a single figure for a
mathematical-modeling contest paper. Comply with the rules listed below.

# Brief
<paste brief.md verbatim>

# Style file (already on import path)
from src.style import PALETTE, apply_style
Call apply_style() at the top of the script.
Use chinese_friendly() additionally if the brief specifies language: zh or mixed.

# Required output
A single file named `plot.py` containing:
1. Imports and apply_style().
2. Loading code that reads from the brief's named data files (CSV / JSON / Parquet).
3. The plotting code.
4. fig.savefig("../output.pdf", bbox_inches="tight", pad_inches=0.05).
5. No __main__ guard — run as a script.

# Hard rules
- No plt.title() (caption is supplied by LaTeX).
- No plt.show().
- All colors via PALETTE indices specified in the brief — no hex literals.
- All axis labels include units.
- aspect ratio: figsize=(<from brief>).
- For PDF output: matplotlib backend "pdf" or default Agg with savefig to .pdf.
- For PNG (only if brief explicitly allows): dpi=300 and rasterize_above_dpi=200.
- Snapshot the actual data used into ../source/data_used.csv with df.to_csv(...).
- If the data file doesn't exist, raise FileNotFoundError with a clear message — do not fabricate data.

# Forbidden
- No "import matplotlib.pyplot as plt; plt.style.use('ggplot')" — use apply_style().
- No hardcoded fake data unless the brief explicitly marks the figure as illustrative.
- No 3D axes (mplot3d) unless the brief asks for it.
- No subplots() in this script unless the brief lists multiple panels — one figure per script.

# Output
Return only the Python code, no commentary, no markdown fences. The file
will be saved verbatim and run by `python plot.py` in the figure folder.
```

The slots in `<...>` are filled by the skill at prompt construction time.

## Pattern B — TikZ code prompt (for `type: schematic` with text labels)

```
You are generating a TikZ standalone document that draws a single figure
for a mathematical-modeling contest paper.

# Brief
<paste brief.md verbatim>

# Required output
A single file named `tikz.tex` containing:
1. \documentclass{standalone} with [convert={density=300}] or [tikz].
2. Required tikzlibraries (arrows.meta, positioning, calc, shapes.geometric).
3. The TikZ picture inside \begin{tikzpicture}...\end{tikzpicture}.
4. \end{document}.

# Hard rules
- All node positions explicit (use positioning library: right=of, below=of, etc.).
- Every node has a textual label per the brief (no empty nodes).
- Arrows: \draw[->, thick] (a) -- (b); — thin or normal, with arrowhead.
- Colors via xcolor: use the named colors from PALETTE
  (PALETTE0=2E5E8A, PALETTE1=D87A3D, PALETTE2=5A8A3D, PALETTE3=8A2E5E,
   PALETTE4=3D8A8A, PALETTE5=8A8A2E, PALETTE6=5A2E8A).
  Define them at the top:
    \definecolor{paletteA}{HTML}{2E5E8A}
    \definecolor{paletteB}{HTML}{D87A3D}
    ...
- Box style: \tikzset{box/.style={rectangle, draw, rounded corners=2pt,
                  align=center, minimum width=2cm, minimum height=1cm,
                  font=\small}}
- Text inside boxes: short English phrases (3-6 words) per the brief.
- No icon glyphs, no emoji, no fontawesome.
- No drop shadows.
- The standalone document compiles via:
    xelatex -interaction=nonstopmode tikz.tex
  and produces tikz.pdf which the skill renames to ../output.pdf.

# Forbidden
- No \usetikzlibrary{shadings,fadings,shadow} — flat colors only.
- No \begin{document} \maketitle — standalone class handles framing.
- No author / school names.

# Output
Return only the LaTeX source, no commentary, no markdown fences.
```

## Pattern C — Text-to-image prompt (for `type: schematic` where aesthetic dominates)

Use sparingly. Image models render text poorly; if your schematic has labels, prefer TikZ. Image is appropriate for:

- Conceptual covers / metaphorical illustrations (rare in 数模 papers).
- Abstract topology sketches where exact labels aren't critical.
- Background "scene" elements.

### Image request schema

Save to `source/image_request.json`:

```json
{
  "vendor": "<dalle3|imagen|midjourney|nanobanana|stable-diffusion>",
  "model": "<dall-e-3|imagen-3|...>",
  "size": "1024x768",
  "format": "png",
  "aspect_ratio": "4:3",
  "prompt": "<full positive prompt — see template below>",
  "negative_prompt": "<full negative prompt — see template below>",
  "guidance_scale": 7.5,
  "seed": 42
}
```

### Positive prompt template

```
A technical illustration for a mathematical-modeling academic paper.
<one or two sentences from brief.md Content section>.
Composition: <e.g. "left-to-right flow, balanced spacing, clear focal point on the central node">.
Style: flat 2D vector aesthetic, matte colors, restrained academic palette
(deep blue #2E5E8A, rust orange #D87A3D, olive green #5A8A3D), white background.
Reminiscent of figures in MIT Press / ACM journal papers.
No text labels inside the image (text will be added by LaTeX externally).
```

### Negative prompt template (always include)

```
no text, no captions, no titles, no labels, no watermarks, no logos,
no author names, no signatures, no school crests, no decorative icons,
no truck icons, no factory icons, no gear icons, no lightbulb icons,
no purple-blue gradient, no neon colors, no AI-flavored color scheme,
no rainbow gradient, no 3D rendering, no drop shadows, no glow effects,
no people, no faces, no hands, no cartoon characters, no anime style,
no photo-realism, no screenshot style, no PowerPoint style, no infographic icons.
```

### Vendor adapters

The skill emits `image_request.json` in this schema; the user runs whichever vendor they have access to:

```bash
# Adapter examples — user must implement one of these in their environment

# OpenAI DALL-E 3
python -c "
import json, openai, base64
req = json.load(open('source/image_request.json'))
resp = openai.images.generate(model='dall-e-3', prompt=req['prompt'],
                                size=req['size'], n=1)
# save resp.data[0].url to output.png
"

# Google Imagen via Vertex
gcloud ai generate-image --prompt-file=source/image_request.json --output=output.png

# Local Stable Diffusion (comfyui / a1111 / diffusers)
python local_sd.py --request source/image_request.json --output output.png
```

The skill writes the JSON; the user's wrapper picks the model. If no wrapper is configured, the skill escalates: "Text-to-image vendor not configured. Either configure one or switch the figure type to TikZ (`type: schematic` with code prompt)."

### Quality reality check

Text-to-image for technical figures is rarely the best choice in a 数模 paper because:

- Reviewer-visible AI tells are common (palette, composition, "AI-flavored" polish).
- Text rendering is unreliable — every label needs to be added in post.
- Vector output is hard (most models output PNG).
- Reproducibility is poor (seed + prompt + model version dependency).

The skill's default for `type: schematic` is TikZ. Text-to-image is opt-in via a brief field `prefer_image_gen: true`.

## Vendor-agnostic prompt scaffold

Independent of which channel, every prompt:

1. Quotes the brief (so the generator can re-read context if needed).
2. Names the exact output path.
3. Lists hard rules and forbidden elements.
4. Demands a single artifact (no exploratory variants).
5. Ends with "Return only the <code|image|JSON>, no commentary."

The orchestrator's gate verifies that each `prompt.md` contains: brief reference + output path + hard rules + forbidden + return instruction.

## Saving the prompt

`prompt.md` is saved verbatim. If a revision happens (loop iteration), save the new prompt with a header:

```markdown
# prompt.md — fig-route-map

## Revision 2 (2026-02-08T14:30Z)
<latest prompt>

## Revision 1 (2026-02-08T14:00Z)
<previous prompt>
```

The `self_check.md` for the figure references which revision was used. Cap at 3 revisions (`figure-workflow.md` § "Iteration discipline").

## Prompt tuning hints (when review fails)

| Review feedback | Prompt-level fix |
|---|---|
| "Palette is wrong" | Make PALETTE indices explicit in the prompt's color section, override the default. |
| "Labels overlap" | Add `tight_layout()` requirement or explicit `bbox_to_anchor` for legend in Pattern A; add `node distance=2cm` in Pattern B. |
| "In-figure title detected" | Add an explicit "No plt.title() / no in-figure title" line near the top of hard rules. |
| "Looks AI-generated (gradient/icons)" | Tighten the negative prompt; switch from image-gen to TikZ. |
| "Wrong aspect ratio" | Re-state figsize explicitly in the prompt; the brief value is sometimes ignored if buried. |
| "Data doesn't match brief" | Pattern A only — confirm the data file path is correct; rerun `data_used.csv` snapshot to verify upstream not the prompt. |
| "Schematic shape wrong" | Pattern B — be more explicit about positioning (e.g. "Node B is directly right of Node A with 2cm distance"). |
