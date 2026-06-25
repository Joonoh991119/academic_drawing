---
name: graphical-abstract
description: Design and render a Nature/Cell-Press-grade GRAPHICAL ABSTRACT (visual summary figure) for a computational-neuroscience paper — orientation estimation, visual cortex, serial dependence, working memory, attractor models, Bayesian observers. Produces editable vector SVG with a comp-neuro icon library (grating/Gabor stimulus, neuron, tuning curve, ring attractor, brain + visual areas, response dial, distributions, decision scale), a Cell-Press single-panel layout grammar, and a two-target render pipeline: (1) LIVE PREVIEW + iteration inside the chat via Claude's design/visualize tool (mcp__visualize__show_widget), and (2) PUBLICATION EXPORT to exact-size PDF/PNG (Cell 1323px, Nature mm). USE THIS whenever the user asks to "make a graphical abstract", "graphical abstract / 그래피컬 초록 / 그래픽 요약", "visual summary figure", "Cell/Nature style figure", "논문 그래픽 abstract", "summary diagram of the study", "key-finding figure", "make the abstract figure", or to render/preview/iterate one — AND follow-ups "redo the graphical abstract", "다시/수정/보완", "restyle", "fix the layout", "export it", "preview it in chat". Pairs with scientific-figure (multi-panel journal figures) and sci-ppt (slides); this skill owns the single-panel visual-summary deliverable and its Claude-design integration.
license: MIT
---

# Graphical Abstract — computational-neuroscience, Nature/Cell grade

Author and render a **single-panel graphical abstract**: the one figure that tells the paper's story at a
glance. This skill is opinionated toward **computational neuroscience of perception** (orientation estimation,
visual cortex, serial dependence, confidence, working memory, attractor/observer models) because that is the
R3 project's domain. It is a **router, not a manual** — load the references below for the load-bearing detail;
do not synthesize a graphical abstract from this file alone.

## Why this skill exists
A graphical abstract is not a multi-panel results figure and not a slide. It is a **standalone visual
narrative** read in seconds, governed by journal rules (Cell Press *requires* one for Neuron; size/font/format
are strict). Two failure modes recur: (1) people draw it in a slide tool → wrong size, raster, unprofessional;
(2) people cram a results figure in → no narrative. This skill fixes both with a **vector-first** workflow, a
**comp-neuro icon library**, a **layout grammar**, and a **two-target render pipeline** so the same source
both previews live in chat (Claude design) and exports publication-grade.

## The two render targets (the core idea)
```
            author parametric SVG (assets/ template + icon library + palette)
                              │
        ┌─────────────────────┴──────────────────────┐
   (1) PREVIEW / ITERATE                         (2) PUBLICATION EXPORT
   Claude design tool                            scripts/render.py (uv)
   mcp__visualize__show_widget                   SVG → PDF + PNG at exact size
   - live in chat, dark-mode safe                - Cell 1323×(≤1863) px @300dpi
   - fast visual iteration with the user         - Nature panel mm, fonts embedded
   - CSS-variable themed SVG                      - cairosvg / rsvg-convert / inkscape
```
You almost always **iterate in target (1)** with the user, then **deliver in target (2)**. The two SVG
dialects differ slightly (see `references/claude-design-integration.md`): the preview SVG uses Claude's
CSS-variable color classes and 680px viewBox; the publication SVG uses the journal palette + exact mm/px and
embedded fonts. Keep ONE conceptual layout; the skill's helpers translate between dialects.

## Workflow

### Step 0 — Decide journal + aspect + story
Fix before drawing (see `references/design-spec.md`):
- **Target** — Cell Press graphical abstract OFFICIAL spec: **5.5 in SQUARE @ 300 dpi (= 1650 px),
  single panel, Arial 12–16 pt** (`--target cell`). This is the default for Neuron/comp-neuro.
  Nature/NN: square or 2-column-width, same vector discipline.
- **Aspect** — Cell's GA is **square** (read in a square frame, still A→B→C). A taller **portrait**
  (`--target cell_portrait`, ≤1323×1863 px) is available only where a venue/use explicitly allows it
  — confirm with the operator before using it, since it is off the official Cell spec.
- **Story (3 acts)** — the comp-neuro graphical-abstract grammar: **(A) task/stimulus → (B) analysis/model →
  (C) finding/mechanism**, flowing top→bottom with arrows. One sentence per act, ≤7 words. The finding (C)
  is the punchline — give it the most visual weight.

### Step 1 — Build the SVG from the kit
Start from `assets/template_oresti.svg` (a complete, renderable 3-act comp-neuro example) and the icon
library `assets/icons_compneuro.svg` (`<symbol>` glyphs: grating/Gabor, neuron, tuning curve, ring attractor,
brain+visual areas, eye, response dial, gaussian/distribution, decision scale, flow arrow). Recolor from
`assets/palettes.json` (Cell, Nature, Okabe-Ito colorblind-safe). Rules: ≤3 hues + 1 accent; one sans-serif
family; sentence case; every glyph captioned ≤7 words; generous whitespace; no gradients/shadows/3-D/clipart.

### Step 2 — Preview + iterate in chat (Claude design)
Render the SVG with `mcp__visualize__show_widget` so the user sees it inline and steers. See
`references/claude-design-integration.md` for the exact contract (call `mcp__visualize__read_me` with modules
`art,diagram` first; 680px viewBox; CSS-variable color classes; `role="img"`+`<title>`/`<desc>`; no gradients).
Loop: show → user feedback → edit SVG → show again. This IS the "claude design 연동" path.

### Step 3 — Export publication-grade
When the user approves the layout, run `scripts/render.py` (PEP 723 / `uv run`, no install) to write the
exact-size PDF (vector, fonts embedded) + 300-dpi PNG at Cell/Nature dimensions, with a font/min-size and
overflow validation pass. The script auto-selects `inkscape` → `rsvg-convert` → `cairosvg` by availability.

### Step 4 — QC gate (before handing over)
Run the checklist in `references/design-spec.md` §QC: reads in <10 s, narrative arc obvious, every glyph
labeled, colorblind-safe (or paired with shape/texture), font ≥ journal minimum at final size, no text
overflow/overlap, vector (not raster) export, correct dimensions. Optionally fold in the generate-N →
vision-judge selection pattern (render 2–3 variants, pick the clearest) noted in the figure references.

## Composition with other skills
- `scientific-figure` — multi-panel journal **results** figures at exact mm. Different deliverable; share the palette + export pipeline.
- `sci-ppt` — turns the approved graphical abstract into a title/summary **slide**.
- `publication-figure-standards` / `neuro-colormap-conventions` — analysis-plot rcParams + perceptually-uniform colormaps; reuse their palettes for any embedded data plot.
- `scientific-schematics` / `generate-image` — only if a *raster* illustration is explicitly wanted; default here is vector.

## Anti-patterns (do not)
- Do not build it in PowerPoint/Keynote and screenshot — raster, wrong size, unprofessional.
- Do not paste a results figure as the abstract — no narrative.
- Do not use gradients, drop shadows, 3-D bevels, stock clipart, or >4 colors.
- Do not let any text fall below the journal's minimum font at FINAL rendered size (validate in Step 3).
- Do not skip the live preview — iterate with the user in chat before exporting.

## Files
- `references/design-spec.md` — journal specs (Cell/Nature/NN), comp-neuro layout grammar, typography, palettes, QC checklist.
- `references/claude-design-integration.md` — exact `mcp__visualize__show_widget` contract + preview↔publication SVG translation.
- `references/iconography.md` — the comp-neuro glyph catalog and how to place/caption each.
- `assets/template_oresti.svg` — complete 3-act graphical-abstract example (orientation-estimation study).
- `assets/icons_compneuro.svg` — `<symbol>` icon library.
- `assets/palettes.json` — Cell / Nature / Okabe-Ito palettes.
- `scripts/render.py` — SVG → PDF/PNG at exact journal size (uv / PEP 723).
