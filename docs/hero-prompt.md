# Hero image prompt — auto-mm

Generates the 1254 × 1254 PNG referenced by `README.md` as `docs/hero.png`. The visual style matches the sister projects [`auto-kaggle`](https://github.com/deafenken/auto-kaggle/blob/main/docs/hero.png) and [`auto-research`](https://github.com/deafenken/auto-research/blob/main/docs/hero.png): hand-drawn watercolor + cartoon illustration, a central mascot, a big bubbly headline, and 5-7 isometric/semi-3D tool icons floating around — **not** flat vector, **not** corporate infographic.

## What the image must show (story, in 5 seconds)

A friendly studious mascot is the conductor of a mathematical-modeling contest run. Around it: the **input** (a problem PDF with A/B/C/D tabs), the **process** (a terminal running auto-mm, a LaTeX editor, math formulas being scribbled), a **time-pressure cue** (a 72-96h hourglass or countdown clock), and the **output** (a polished paper PDF + a `submit.zip` icon). A big bubbly headline on top says **"Drop a PDF. Get a Paper."** A tagline strip at the bottom says **"auto-mm · 72-96h · resume-safe · anonymity-gated"**.

It should read like an illustrated cover for a developer tool — playful, warm, dense with little tools and labels, NOT like an academic textbook figure.

## Reference images to feed the model

Strongly recommended: pass the two sister-project hero images as reference / style-anchor images to the generation model (Imagen 3 supports this directly; DALL-E 3 via the multimodal Vision API; Midjourney via `--cref` URL).

```
https://raw.githubusercontent.com/deafenken/auto-kaggle/main/docs/hero.png
https://raw.githubusercontent.com/deafenken/auto-research/main/docs/hero.png
```

If the model does not accept image references, copy the style cues into the prompt below verbatim — they are the same ones the sister projects' hero already encodes.

## Composition layout (top to bottom)

1. **Top third** — big bubbly cartoon headline: **"Drop a PDF."** in deep blue, **"Get a Paper."** in rust orange, each on its own line, comic-book-style outline + small shadow. The "P" letters can have a tiny LaTeX serif flourish.
2. **Just under headline** — small dot-separated tagline strip: **`auto-mm · 72-96h · resume-safe · anonymity-gated`** in dark gray.
3. **Center** — the mascot (see below) holding a LaTeX paper, surrounded by tool icons.
4. **Around the mascot, scattered** — 6 to 8 floating semi-3D tool icons (see icon list).
5. **Hand-drawn watercolor wash background** — warm cream / off-white (#FAF6EE) with very faint sky-blue cloudy splashes.

## The mascot

**A scholarly owl** wearing round black glasses, a graduation cap, and a dark blue scarf, sitting at a tiny wooden desk holding a freshly printed LaTeX paper in one wing and a pencil in the other. Expression: focused-but-friendly, slightly tired (this is hour 60 of 96). The owl is the visual anchor — centered, ~40% of canvas height.

Owl color: warm brown body, cream chest, large amber eyes behind glasses, soft feathered texture (hand-painted watercolor edges, not photoreal).

(If owl doesn't work, fallback mascot: a scholarly otter with the same accessories — round glasses, graduation cap, dark blue scarf. Same expression and pose.)

## Tool icons to scatter around (with text labels — text IS allowed and important)

Pick 6-8, distribute around the mascot in a clockwise or counterclockwise flow:

- **Problem PDFs** — a stack of three or four paper sheets with little tabs labeled `A`, `B`, `C`, `D` (one tab highlighted in orange — "the chosen one"). Top-left of mascot.
- **Terminal window** — a small terminal screenshot showing `> auto mm` in monospaced green text on a dark gray background, with a few cursor lines below. Top-right of mascot.
- **Math formula in a speech bubble** — a watercolor speech bubble with a hand-written-style formula like `min Σ c_v · y_v` or `δ_i = δ_0 + α·w_i` — illustrate as if scribbled on a napkin.
- **LaTeX paper page** — a clean A4 PDF rendering with `paper.tex → main.pdf` arrow underneath; the page shows the silhouette of an abstract block + section blocks + one figure placeholder. Right side, below mascot.
- **Hourglass with "72h" and "96h" labels** — a sand timer half-drained, with two small captions for the two contest durations. Above or beside the mascot.
- **submit.zip icon** — a small zip-file icon labeled `submit.zip` with a green checkmark. Bottom-right corner.
- **Anonymity stamp** — a small red rubber-stamp shape labeled `anonymized ✓`. Tucked near the LaTeX page.
- **Validation chart strip** — a tiny bar/line chart icon labeled `validation.md` or `Gap = 1.58%`. Beside the terminal or below the formula bubble.

Optional ninth icon: a **`/loop` rotating arrow** to hint at the supervisor pattern.

Connecting flow: thin watercolor arrows in soft orange, going `PDF stack → terminal → formula bubble → LaTeX page → submit.zip`, like a loose pipeline curved around the mascot. Not rigid; the arrows are slightly wobbly like ink-on-paper.

## Style adjectives

- hand-painted watercolor and ink, cartoon illustration
- cozy, friendly, slightly nostalgic, "indie game studio cover art" energy
- warm cream background with subtle paper texture
- color palette: deep blue (#2E5E8A) for the main headline and accents, rust orange (#D87A3D) for the second headline and the highlighted tab, warm brown (#8B6240) for the owl and the wood desk, soft cream (#FAF6EE) for the background, soft sky blue and pale yellow watercolor washes for atmosphere
- small, dense, but never cluttered — each icon has its own breathing room
- text inside the image is welcome wherever it carries information (file names, formulas, button labels, dates)
- mood is "studious nighttime sprint, but with warmth" — not corporate, not academic, not childish

## Positive prompt (one passage; paste into any model)

```
A hand-drawn watercolor cartoon hero illustration for an open-source
developer tool called "auto-mm" that helps students run mathematical-
modeling contests. Square 1:1 composition, 1254×1254 px, with a warm
cream off-white background (#FAF6EE) and soft sky-blue cloudy watercolor
splashes for atmosphere. Hand-painted watercolor and ink style, like an
illustrated cover for an indie developer tool — cozy, friendly, dense
with charming details, NOT flat vector, NOT corporate infographic.

CENTER: a scholarly cartoon owl with round black glasses, a graduation
cap, and a dark blue knitted scarf. The owl is sitting at a small wooden
desk, holding a freshly printed LaTeX paper in one wing and a pencil in
the other. Warm brown body, cream chest, large amber eyes behind glasses.
Expression: focused but friendly, slightly tired — this is hour 60 of 96.
The owl is the visual anchor, occupying about 40% of the canvas height,
slightly toward the lower center.

TOP HEADLINE: a big bubbly cartoon-style headline with comic-book outline
and small drop shadow. Line one says "Drop a PDF." in deep blue (#2E5E8A).
Line two says "Get a Paper." in rust orange (#D87A3D). Each line has a
playful tilt and the P letters have a tiny serif flourish hinting at LaTeX.

JUST UNDER HEADLINE: a small dot-separated tagline in dark gray text:
"auto-mm · 72-96h · resume-safe · anonymity-gated"

SURROUNDING the owl, distributed in a loose counterclockwise flow,
6 to 8 semi-3D hand-painted tool icons connected by thin wobbly orange
watercolor arrows:

  - upper left: a stack of 4 problem-PDF sheets with little colored tabs
    labeled A B C D, the C tab highlighted in orange.
  - upper right: a small terminal window showing "> auto mm" in green
    monospaced text on a dark gray background.
  - middle right: a speech bubble containing a hand-written formula like
    "min Σ c_v · y_v" scribbled in ink.
  - lower right: an A4 LaTeX paper page rendering, with the silhouette
    of an abstract block, three section blocks, and one figure inside;
    a small label "paper.tex → main.pdf" beneath it.
  - upper center, slightly behind the owl: an hourglass half-drained,
    with two small captions "72h" and "96h" next to it.
  - bottom right: a small zip-file icon labeled "submit.zip" with a
    green checkmark.
  - middle, near the LaTeX page: a small red rubber-stamp shape labeled
    "anonymized ✓".
  - middle left: a tiny bar chart icon labeled "Gap = 1.58%".

Color palette: deep blue (#2E5E8A) for headline and accents, rust
orange (#D87A3D) for the second headline and highlighted tab, warm
brown (#8B6240) for the owl and wood desk, soft cream (#FAF6EE) for
background, gentle sky blue and pale yellow watercolor washes for the
ambient wash. Texture: visible watercolor paper grain throughout.

Mood: studious nighttime sprint, but warm. Reads as an indie tool cover,
not an academic textbook figure.

Style anchors: hand-drawn watercolor, cartoon illustration, dense but
not cluttered, similar in style to the hero illustrations of "auto-kaggle"
(a scaly blue Kaggle dragon mascot surrounded by tools) and "auto-research"
(a bespectacled fox mascot at a writing desk). Match that aesthetic
exactly — same brushwork, same color warmth, same icon density.
```

## Negative prompt

```
no flat vector aesthetic, no corporate infographic style, no PowerPoint
slide look, no Material-Design icons, no clean line-art with no shading,

no purple-blue gradient, no neon, no fluorescent colors, no rainbow,
no AI-flavored over-saturated palette,

no photo-realism, no 3D rendering with hard ray-traced shadows, no
isometric extrusion with sharp edges, no metallic surfaces, no glow
effects, no lens flare, no bokeh, no depth-of-field blur,

no human faces, no human portraits, no eyes-on-cartoon-objects
(no eyes on the laptop, no eyes on the paper),

no anime aesthetic, no manga panels, no chibi style with oversized
heads, no Disney princess style,

no English typography errors in the visible labels (file names must
read correctly: "submit.zip", "paper.tex", "main.pdf", "anonymized ✓",
"auto mm", "72h", "96h", "A", "B", "C", "D"),

no overcrowding — keep each icon with breathing room,

no school crests, no university logos, no author signatures, no
copyright watermarks, no stock-photo watermarks, no Shutterstock label,

no political symbols, no national flags.
```

## Vendor notes

### DALL-E 3 (recommended for this style)

Paste positive + negative as one passage. Request `1024×1024` (DALL-E 3 doesn't support 1254 natively), `quality: hd`, `style: natural` (NOT `vivid` — vivid pushes toward neon AI palette). Upscale to 1254×1254 with Preview / ImageMagick after.

### Imagen 3 (Google)

Use the positive prompt in `prompt`, negative prompt in `negative_prompt`. Aspect `1:1`. Imagen 3 follows the "watercolor + cartoon" combination well.

### Midjourney v6

```
[positive prompt] --ar 1:1 --style raw --cref https://raw.githubusercontent.com/deafenken/auto-kaggle/main/docs/hero.png --cw 60 --no neon, gradient, 3D, photorealistic, infographic
```

`--cref` with `--cw 60` (character-weight 60%) anchors the style to the auto-kaggle hero. Drop `--style raw` if results feel too sketch-y.

### Stable Diffusion XL (local)

- Base model: `sd_xl_base_1.0` + a watercolor LoRA (`watercolor_v1` or similar).
- Sampler: `DPM++ 2M Karras`, 35-45 steps, CFG 6-8.
- Size: `1024×1024`, upscale 1.25× with `R-ESRGAN x2` afterward.
- Recommended LoRA: any "children's book illustration" / "indie game cover" / "watercolor cartoon" LoRA; weight 0.6-0.8.
- Seed: pick one you like and save it; this style depends heavily on seed luck.

### Nano Banana (Google Gemini image-gen)

Same as Imagen 3. Use the prompt verbatim. If first generation feels too "tech demo", run a second pass with the prompt prefixed by "in the warm hand-painted style of an indie game studio key visual".

## After generation — what to check

The most common failures and how to triage:

| Failure | What it looks like | Fix |
|---|---|---|
| Garbled text | "submit.zip" comes out as "subnit.iip" or "snnnit.zlp" | Regenerate. If it persists, manually inpaint the text labels in an editor (text-to-image text rendering is a known weak point). |
| AI-palette leak | Anything purple, neon teal, fluorescent | Negative prompt didn't bite — regenerate with stronger negative weighting; or post-process color grade in editor. |
| Too clean / corporate | Flat vector look, no brush texture | Re-run with positive prompt emphasizing "visible watercolor paper grain" and "hand-painted edges". |
| Mascot eyes feel wrong | Manga eyes / dead AI eyes / asymmetry | Inpaint the face area only. Or regenerate with seed change. |
| Too sparse | Big empty corners | Add more tool icons or scale up the existing ones; alternatively, fill the corners with watercolor wash atmosphere. |
| Reads like auto-kaggle | The dragon mascot appeared | Reference image confused the model. Drop `--cref` weight or remove the reference image; regenerate. |

## Final delivery

- Save as `docs/hero.png`. 1254×1254 PNG, sRGB, ≤ 800KB ideally.
- Uncomment the `<img>` tag at the top of `README.md` (around line 10) so GitHub renders it.
- Commit with a message like `docs: add hero banner`. Do NOT include the prompt + generation parameters in the commit — they live here.
