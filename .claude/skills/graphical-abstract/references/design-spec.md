# Graphical-abstract design spec — Cell / Nature / NN, computational neuroscience

The journal rules + the comp-neuro layout grammar. Load this before drawing. Numbers are the *delivered*
constraints; validate against them at FINAL rendered size (Step 3), not in the editor.

## 1. Journal target specs

### Cell Press (Neuron, Cell, Current Biology) — the default for comp-neuro
- **Single panel only.** No multi-part (no a/b/c). One continuous visual narrative.
- **Size:** width **min 1200 px, max 1323 px**; height **up to 1863 px**. Portrait or square. At 300 dpi that
  is ~11.2 cm wide. Author the SVG at a viewBox matching the aspect (e.g. `0 0 1100 1500` portrait) and export
  to the px target — vector source, raster/PDF output.
- **Resolution:** 300 dpi minimum at final size. Export **vector PDF** (text crisp) + a 300-dpi PNG/TIFF.
- **Font:** one sans-serif (Arial/Helvetica). Body legible at final size — keep ≥ ~12 pt equivalent; never
  below 8 pt. Consistent sizes (title / act-label / caption — three sizes max).
- **Reading order:** top→bottom (portrait) or left→right. The eye must find the entry point immediately.
- **No:** excessive text, multiple panels, watermarks, author names, journal logos, photos unless essential.

### Nature / Nature Neuroscience (when a summary figure is wanted)
- Graphical abstracts are optional, but the *figure* discipline applies: column widths **89 mm (single)** /
  **183 mm (double)**; min font **5 pt** (panel labels ~7–8 pt). Sans-serif. Square summary figures common.
- Same vector-first rule; CMYK-safe, perceptually-uniform colormaps for any embedded data.

### General (eLife, JNeurosci, PLoS, NN)
- Square 1:1 is the safest universal aspect. Vector PDF/SVG + 300-dpi PNG covers every portal.

## 2. The comp-neuro layout grammar — "3 acts, one arrow"

A graphical abstract for a perception/comp-neuro study almost always reads as **three stacked acts** connected
by flow arrows, with the finding given the most weight:

```
┌──────────────────────────────────────────┐
│  ACT A — TASK / STIMULUS                   │  what the subject (or model) did
│  grating/Gabor → delay → response dial      │  ≤7-word label
│                    │ (arrow)                │
│  ACT B — ANALYSIS / MODEL                   │  how you looked / the mechanism tested
│  ring attractor · tuning curve · observer   │  ≤7-word label
│                    │ (arrow)                │
│  ACT C — FINDING (the punchline)            │  the result, biggest visual weight
│  bias/DoG curve · decoded orientation       │  one crisp sentence
└──────────────────────────────────────────┘
```

Variants: **task → two competing hypotheses → which won** (good for strong-inference papers);
**stimulus → neural representation (cortex) → behavior** (links brain & behavior); **condition contrast**
(two mini-scenes side by side under one finding). Keep the spine vertical and the arrows unambiguous.

### Domain mapping for the OResti project (concrete)
- **A:** oriented grating (single-OR) / two gratings + cue (double-OR) / grating vs reference (BRL) →
  delay → circular response dial (+ confidence arc for double-OR; decision scale for BRL).
- **B:** the mechanism under test — ring/continuous attractor (drift toward prior), efficient-coding prior,
  Bayesian observer, serial-dependence kernel, visual-cortex channel/IEM (V1–hV4) if fMRI.
- **C:** the discovered phenomenon — e.g. attractive serial dependence (DoG bias curve), confidence-conditioned
  bias, post-decision repulsion (BRL), regression-to-the-mean. Show the signature curve.

## 3. Typography & color

- **Type:** ONE sans-serif. Three sizes: title (largest, the one-line message), act-labels, glyph captions.
  Sentence case everywhere. No italics except variable symbols (θ, θ̂, κ). No bold body; bold only the message.
- **Color:** ≤ **3 hues + 1 accent**. Encode meaning consistently (e.g. one hue = stimulus, one = response,
  accent = the finding). Pull from `assets/palettes.json` (Cell navy/red, Nature muted, Okabe-Ito colorblind).
  **Pair color with shape/position** (never color-alone) so it survives grayscale + colorblind readers.
- **No** gradients, drop shadows, 3-D bevels, glow, stock clipart, skeuomorphic textures. Flat vector only.

## 4. Visual weight & whitespace
- Finding (Act C) gets ~40% of the canvas; A and B ~30% each. The punchline should be the largest single element.
- Generous margins (≥5% each side). Don't fill every pixel — Cell penalizes clutter; one clear path beats density.
- One entry point (top-center). Arrows are thin (1–2 px at final size), single-headed, never crossing.

## 5. QC checklist (Step 4 gate — all must pass)
1. **<10-second read:** a naïve viewer states the finding within 10 s.
2. **Narrative arc obvious:** A→B→C spine + arrows unmistakable; one entry point.
3. **Every glyph captioned** (≤7 words) — no unlabeled icon.
4. **Colorblind-safe:** ≤3 hues+accent, each paired with shape/position; legible in grayscale.
5. **Font ≥ minimum at FINAL size** (Cell ≥ ~12 pt / never <8; Nature ≥5 pt). Validate post-export, not in editor.
6. **No overflow / no overlap:** no clipped text, no colliding elements (run render.py's validator).
7. **Vector export** (PDF) + 300-dpi raster; **exact dimensions** (Cell ≤1323 px wide / ≤1863 tall).
8. **Standalone:** understandable with zero caption; no jargon acronym undefined in-figure.
9. **Single panel** (Cell): no a/b/c subfigures.
10. **Honest:** the depicted finding matches the actual result (no implied effect you didn't measure).
