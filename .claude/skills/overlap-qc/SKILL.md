---
name: overlap-qc
description: Mechanical RENDER + text/shape OVERLAP quality control for Academic_Drawing deliverables. Renders an SVG graphical abstract (or a PPTX deck) to images and runs deterministic bounding-box collision detection to catch the user's #1 layout failure — text overlapping shapes, overlapping other text, or running off the canvas — which render.py's font/size check does NOT cover. Use whenever a graphical-abstract SVG or a slide deck needs a layout/overlap QC pass, before any design or human review, or when asked to "check overlap", "QC the layout", "render and inspect", "is the text colliding". Produces an overlap report (JSON) + rendered PNG/JPG for the vision pass. Hard-fails on unambiguous collisions; the vision review corroborates the rest.
---

# Overlap QC — render then measure, don't eyeball

The user's most frequent failure is *text colliding with shapes*. Catching it reliably needs two
tracks that back each other up:

1. **Geometric (authoritative for the clear cases).** Measure the TRUE rendered bounding boxes and
   do rectangle-intersection math. Deterministic, repeatable, no opinion. This is the hard gate.
2. **Vision (corroborating + semantic).** A vision agent reads the rendered image to confirm what
   the math flagged and to catch crowding/contrast the math can't see (e.g. a label that's clear of
   shapes but still visually cramped, or dark-on-dark).

Never ship on the vision pass alone (it misses pixel-exact collisions) or the math alone (it misses
semantic crowding). Run both; the math gates, the vision corroborates.

## Graphical abstract (SVG)

**Step 1 — measure overlap (hard gate):**
```
python3 scripts/overlap_check.py ABSTRACT.svg --json ABSTRACT.overlap.json
```
Exit codes: `0` clean · `2` FAIL present (block) · `3` could not measure (Chrome failed → fall back
to the vision pass) · `4` WARN present under `--strict`. It loads the SVG in headless Chrome (the
same engine it'll be viewed in), reads every element's `getBoundingClientRect()`, and classifies:

| Result | Meaning | Gate |
|--------|---------|------|
| `text-text` | two labels overlap | **FAIL** |
| `text-spill` | text crosses the edge of a filled rect/circle/ellipse/polygon | **FAIL** |
| `text-clipped` | text runs past the SVG viewport | **FAIL** |
| `text-near-glyph` | text box overlaps a `<use>`/`image`/`path` bbox (coarse for icons) | WARN — vision confirms |
| (contained) | text fully inside one filled shape = intended label-on-card | OK |

Why only tight-bbox shapes (rect/circle/ellipse/polygon) hard-fail: `<use>` icon symbols, `<image>`,
and `<path>` have bounding boxes that overstate their inked area, so a caption sitting just under an
icon would false-positive. Those become WARNs for the vision pass to confirm.

**Step 2 — render for the vision pass.** Pick by need:
- Fidelity (what the viewer sees): headless Chrome —
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --screenshot=ABSTRACT.png --window-size=W,H file://ABS.svg`
- Fast/clean: `rsvg-convert -w 1600 ABSTRACT.svg -o ABSTRACT.png`
- True publication export (fonts embedded, exact size): the graphical-abstract skill's
  `scripts/render.py` (inkscape → rsvg → cairosvg), which ALSO checks font minima + oversize.
- `cairosvg` sizing gotcha: use `-s 2` (scale), not `-W/-H` (ignored).

Then `Read` the PNG so the vision agent reviews it.

## Slides (PPTX)

**Step 1 — deterministic style lint (hard gate, the deck's twin of `overlap_check`):**
```
python3 scripts/pptx_style_lint.py DECK.pptx --json DECK.stylelint.json
```
Reads `palette.json` and FAILs on: a structural fill not in the token set; a run matching a
`label_map` key not carrying that token's hex; more distinct structural hues on a slide than
`max_colors_per_slide`; or a font below the slide minima. Unresolved/theme colors → WARN (vision
confirms). Block on FAIL before spending a render.

**Step 2 — render for the vision pass** (both binaries confirmed present):
```
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf DECK.pptx --outdir OUT/
pdftoppm -jpeg -r 150 OUT/DECK.pdf OUT/slide      # -> slide-1.jpg, slide-2.jpg, ...
```
Then `Read` **only the slides that need a vision pass** (per `academic-drawing-orchestrator/references/routing-and-review.md`
§3): changed slides, slides with a mechanical WARN/FAIL, or user-flagged ones — **not all N**. For a
large deck, do a deck-level *sampled* quick-look (a few representative slides) unless Full mode. Check
overflow, text/figure overlap, contrast, leftover placeholder strings, ≤5-color adherence. `grep` the
source for `PLACEHOLDER`. The cheap mechanical lint runs on every slide; the expensive vision pass does not.

## Equations
Four-stage gate (see `ga-style-contract` §4). The author emits `_workspace/eqs.json`
(`[{id, latex, declared_symbols, reference_latex?}]`); then run the deterministic check:
```
python3 scripts/equation_qc.py eqs.json --json eqs.qc.json   # mathtext parse + sympy symbol/identity check
```
FAIL on broken markup or an undefined symbol. Then render each LaTeX offline with matplotlib mathtext
(`text(0,0,r"$...$"); savefig`), `Read` the PNG, and have both reviewers check it (Codex = model
appropriateness given `eqs.qc.json`, vision = legibility). Avoid CodeCogs and the sci-ppt
`formula_renderer` (broken).

## Files
- `scripts/overlap_check.py` — headless-Chrome geometry measurement + rectangle-intersection collision detection.
- `scripts/pptx_style_lint.py` — deterministic deck palette / label-color / ≤N-hue / font gate (python-pptx).
- `scripts/equation_qc.py` — mathtext parse + sympy symbolic/undefined-symbol gate for equations.
