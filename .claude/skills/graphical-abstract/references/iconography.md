# Comp-neuro iconography — the glyph catalog

The icon library `assets/icons_compneuro.svg` defines reusable `<symbol>` glyphs (line-art, `stroke:currentColor`,
each on a 0 0 100 100 viewBox). Use them via `<use href="#id" x=".." y=".." width=".." height=".."/>` after
embedding the symbols (paste the `<defs>` from the library into your SVG, or `<use href="icons_compneuro.svg#id">`
when rendering locally). Set color by wrapping in a `c-*` class (preview) or `style="color:#.."` (publication) —
glyphs inherit `currentColor`.

## Catalog (id → meaning → typical act)
| id | glyph | use for | act |
|----|-------|---------|-----|
| `ic-grating` | circular oriented grating (Gabor) | the orientation stimulus | A |
| `ic-grating-pair` | two gratings flanking fixation | double-OR bilateral stimulus | A |
| `ic-fixation` | central fixation cross/dot | fixation / trial start | A |
| `ic-eye` | eye | eye-tracking / gaze / fixation | A |
| `ic-dial` | circular dial with a pointer | orientation response (report) | A/C |
| `ic-confidence-arc` | half-ring red↔blue arc | signed confidence scale (double-OR) | A/C |
| `ic-decision` | balance / 2-choice scale | binary decision (BRL: CW vs CCW of ref) | A |
| `ic-clock` | clock / hourglass | delay / working-memory retention | A→B |
| `ic-neuron` | soma + dendrites + axon | a neuron / population | B |
| `ic-tuning` | bell-shaped tuning curve | orientation tuning / channel | B |
| `ic-ring` | ring with a localized bump | continuous/ring attractor state | B |
| `ic-attractor-drift` | ring + curved arrow toward a well | attractor drift toward prior | B/C |
| `ic-brain` | lateral brain, occipital shaded | visual cortex (V1–hV4) | B |
| `ic-observer` | head + inward arrow | Bayesian observer / perception | B |
| `ic-prior` | skewed/peaked distribution | prior over orientation (efficient coding) | B |
| `ic-gaussian` | symmetric bell | likelihood / noise / distribution | B |
| `ic-dog` | derivative-of-Gaussian (S-shaped) curve | serial-dependence bias curve | C |
| `ic-bias-curve` | error-vs-stimulus curve | estimation bias signature | C |
| `ic-arrow` | flow arrow (down/right) | act→act flow | all |
| `ic-arrow-curved` | curved/return arrow | inter-trial history / feedback loop | B/C |

## Placement rules
- **One glyph = one idea.** Don't compose a glyph mosaic inside a single act; pick the one that carries the act.
- **Caption every glyph** (≤7 words) directly beneath it; the caption, not the glyph, carries precision.
- **Scale uniformly** — keep glyph stroke weight visually consistent across acts (use the same `width`/`height`,
  ~80–140 px at publication scale). A glyph that's 3× another reads as "more important" — only do that on purpose.
- **Color = encoding.** Reuse the same hue for the same role across acts (stimulus hue, response hue, finding
  accent). Don't recolor a glyph per act for decoration.
- **Data glyphs are schematic, not real plots.** `ic-tuning`/`ic-dog`/`ic-bias-curve` are *schematic*
  signatures. If you need the *actual* fitted curve, render it with matplotlib (publication-figure-standards /
  neuro-colormap-conventions) and embed the exported SVG/PNG in Act C instead of the schematic glyph.

## Extending the library
Add a new `<symbol id="ic-..." viewBox="0 0 100 100">…</symbol>` with `fill="none" stroke="currentColor"
stroke-width="4" stroke-linecap="round"`. Keep it readable at 24 px. Register it in the table above. Favor a
single clear metaphor over detail — a graphical-abstract glyph is recognized, not studied.
