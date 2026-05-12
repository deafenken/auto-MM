# Hero image prompt — auto-mm

The prompt below is what feeds an image-generation model (DALL-E 3 / Imagen 3 / Midjourney / Nano Banana / Stable Diffusion XL) to produce `docs/hero.png`. Save the resulting image into this directory; `README.md` references it as `docs/hero.png`.

The expected output size is **1254 × 1254 PNG** (matches the hero images in sister projects auto-kaggle and auto-research). Square aspect, transparent or pure white background is fine.

## Conceptual brief — what this image must convey

In a single still frame, the viewer should grasp three things in 5 seconds:

1. **A four-stage pipeline driving toward a deadline.** Mathematical-modeling contests are 72-96 hour sprints; the visual should feel like "structured motion under time pressure," not like a lazy infographic.
2. **The pipeline is built around a paper.** The artifact at the right is a stylized paper / LaTeX page — not a chart, not a robot, not a brain.
3. **Restrained academic aesthetic.** This is for a CS / applied-math audience that will close the page if it looks like AI-flavored marketing.

Anchors:
- 4 connected stages, left to right: 📂 triage → 📐 modeling → 🧪 solving → 📄 writing.
- A subtle "deadline countdown" cue (e.g., a thin clock arc, a dotted timeline, or a "72h / 96h" frame around the whole thing).
- Final artifact on the right: a stylized paper page with rectangles representing abstract / sections / a figure, but with **no readable text** (image models render text poorly).
- One human silhouette at the right side, hand on the paper — signaling "you ship it, not the agent."

## Positive prompt (vendor-agnostic)

```
A technical illustration for the hero banner of an open-source academic
tool, square 1:1 composition, 1254×1254 px.

Subject: a four-stage horizontal pipeline driving toward a published paper.
Left to right: (1) a stack of problem PDFs being scanned by a magnifying-
glass icon, (2) a blueprint with mathematical formulas and a notation
table, (3) a compute icon (a small server rack or a network of nodes)
with a Gantt-chart strip beneath it, (4) a stylized academic paper page
showing the silhouette of an abstract block and three section blocks and
one figure placeholder. A thin dotted timeline arcs over all four stages,
with subtle tick marks suggesting a 72-96 hour countdown. A simple human
silhouette stands on the right, hand resting on the paper, indicating the
human ships the final submission.

Style: flat 2D vector aesthetic, matte colors, restrained academic palette
of deep blue (#2E5E8A), rust orange (#D87A3D), olive green (#5A8A3D),
and warm gray (#6B6B6B) on an off-white background (#FAFAF7). Line weights
are crisp and uniform, similar to figures in MIT Press or ACM journal
papers. Generous white space, balanced spacing between stages, clear
visual hierarchy with the paper as the focal point. Composition has a
quiet, technical confidence — not playful, not corporate.

No text labels inside the image (any text on the paper or pipeline must
be abstract bars or wavy lines representing text, not actual letters).
Reminiscent of the cover of a research methods textbook or the hero image
of a static-site generator's docs page.
```

## Negative prompt (always include)

```
no text, no captions, no titles, no readable letters, no numbers as glyphs,
no watermarks, no logos, no signatures, no school crests, no author names,

no decorative icons (no trucks, no factories, no gears, no lightbulbs,
no robots, no brains, no rockets, no checkmarks-in-shields, no cartoon
mascots),

no purple-blue gradient, no neon colors, no rainbow gradient, no fluorescent
highlights, no "AI-flavored" high-saturation color schemes,

no 3D rendering, no isometric extrusion, no drop shadows, no glow effects,
no lens flare, no bokeh, no depth-of-field blur,

no photo-realism, no stock-photo aesthetic, no screenshot of an IDE, no
PowerPoint slide aesthetic, no generic infographic-template look,

no faces, no portrait, no eyes, no anime style, no cute mascots,

no overcrowding — leave generous white space; no more than 5-6 distinct
visual elements total.
```

## Vendor-specific notes

### DALL-E 3 (via OpenAI)

DALL-E 3 favors longer descriptive prompts; concatenate the positive prompt + negative prompt as one passage. Request size `1024x1024` (1254×1254 is not a native size; upscale after generation with an image editor if needed) and `quality: hd`.

### Imagen 3 (via Google Vertex)

Imagen 3 is more literal. Use the positive prompt as-is and pass the negative prompt via the `negative_prompt` field. Aspect ratio `1:1`.

### Midjourney v6

Append `--ar 1:1 --style raw --no text, neon, gradient, drop shadow, robot, gear, lightbulb` to the positive prompt. Use `--style raw` to suppress Midjourney's default decorative tendencies.

### Stable Diffusion XL (local)

Use `1024×1024` at base, then upscale to 1254×1254 with `R-ESRGAN x2` or similar. Negative prompt goes into the negative-prompt field. Recommended sampler: `DPM++ 2M Karras`, 30-40 steps, CFG 7.5. Seed: pick one you like, then save it in case you need to regenerate after touch-ups.

### Nano Banana (Google)

Treat as a stronger Imagen 3 variant. Same positive + negative prompt; supports prompt-driven inpainting if the first generation has one element you want to fix.

## After generation

1. Open the image. Check against the conceptual brief: do you see four stages, a timeline cue, a paper, a human silhouette? If not, regenerate.
2. Check for text artifacts (the most common failure mode). If any glyph that looks like text appears, regenerate with a stronger "no text" weight.
3. Check the palette — anything purple, neon, or gradient-heavy means the negative prompt didn't bite hard enough. Regenerate.
4. Resize to 1254×1254 PNG (Preview / ImageMagick / GIMP). Quantize palette if file size > 500KB.
5. Save as `docs/hero.png`. The README already references this path; nothing else needs to change.

## When you can ship without a hero image

If you don't have access to an image-gen tool, the README still renders cleanly without `docs/hero.png` — the surrounding badges + Mermaid flowchart carry the visual weight. The `<img>` tag in `README.md` (around line 10) can either be commented out or left in (GitHub shows a broken-image icon, mildly ugly but not fatal).

Suggested fallback: comment out the `<img>` line until you have the image. Patch is one line — see the README for the exact location.
