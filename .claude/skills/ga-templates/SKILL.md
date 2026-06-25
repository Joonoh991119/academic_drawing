---
name: ga-templates
description: Pre-built LAYOUT ARCHETYPE LIBRARY for graphical abstracts and summary schematics — domain-agnostic templates so the harness PICKS a proven layout (3-act pipeline, comparison A-vs-B, mechanism/forking, hub-and-spoke, cycle, quadrant, hierarchy/multi-scale, before-after, single-finding, zig-zag) by the paper's message type instead of designing from scratch. Also encodes the venue reality (graphical abstract = Cell/Neuron only; Nature Neuroscience = summary-schematic + cover; J Neurosci = cover/visual-abstract) and the SciGA evidence-based design rules (R1–R14, visual-coherence-first). Use whenever choosing or reviewing a graphical-abstract / visual-summary layout, deciding which artifact a venue wants, or picking a template. Read this BEFORE the concept-architect designs a layout — it removes the blank-page decision.
---

# GA Templates — pick a proven layout, don't invent one

The slowest, most uncertain step was the concept-architect designing a composition from zero. This
library removes that: **classify the message → pick the archetype → fill its slots**. The archetypes
are domain-agnostic (the comp-neuro icon kit is just one fill for them). Synthesized from SciGA-145k
(arXiv 2507.02212), Hullman & Bach "Picturing Science" (layout taxonomy + empirical frequencies),
PLOS "Ten Simple Rules", and Cell Press guidelines.

## Step 0 — Which artifact does the venue even want? (venue-awareness)

Do **not** assume "graphical abstract" for every venue:

| Venue | Artifact | Spec |
|-------|----------|------|
| **Cell Press / Neuron** | **Graphical abstract** (required) | **square, 5.5 in @300 dpi = 1650 px** (min 1200); Arial **rec 12–16 pt** (hard floor 9 pt; Neuron GA-label floor 18 pt); **one panel**, no data items |
| **Nature / Nature Neuroscience** | **Summary-schematic figure** (last main fig) + **cover** — *not* a GA | figure at column widths (89/120/183 mm); cover = portrait, image-led |
| **J Neurosci (SfN)** | **Cover image** / optional **visual abstract** — no GA requirement | cover = aesthetic, portrait, near-zero text |
| **default / unknown / talk** | graphical abstract (square) | Cell square is the safe default |

> **This table is the venue-spec SOURCE OF TRUTH.** `render.py` targets and `palette.json` font
> minima derive from it — do not re-state venue sizes/fonts elsewhere (any other prose is illustrative,
> this governs). Cell GA: square 1650 px, Arial rec 12–16 pt, hard floor 9 pt, one panel.

If the venue is Nat Neuro / J Neurosci, build a **summary-schematic** (uses the same archetypes but at
column-width, may include schematic data) or a **cover** (archetype #11, image-led), not a GA.

## Step 1 — Pick the archetype by message type

Classify the paper's core message, then take the matching archetype. Frequencies (% of real GAs,
Hullman & Bach n=54) are tie-breakers — prefer the more common pattern when two fit.

| If the message is… | Archetype | freq |
|--------------------|-----------|------|
| a method/process, sequential cause→effect | **1 Linear pipeline** (input→method→finding) | 35% |
| a long pipeline (5–7 steps) in a square | **2 Zig-zag** (folded pipeline) | 5.5% |
| a contrast: control vs treatment, WT vs KO, A vs B | **3 Comparison / parallel** | 37% |
| one system changed by one intervention | **4 Before→After** | — |
| a pathway/cascade that branches | **5 Mechanism / forking** | 18.5% |
| many inputs converging on one finding (no sequence) | **6 Hub-and-spoke / centric** | 7.4% |
| an iterative loop / feedback / cycle | **7 Cycle** | — |
| a 2×2 framework / typology / "where we sit" | **8 Quadrant / orthogonal** | 16.6% |
| macro→meso→molecular, multi-scale | **9 Hierarchy / nesting** (vertical) | 29.6% |
| one headline result, "the finding IS the figure" | **10 Single-finding / Q→A** | 14.4% |
| (Nat Neuro / J Neurosci) an issue cover | **11 Cover-art** (portrait, image-led) | — |

Comp-neuro note: the old default was the top-down **3-act (task→model→finding)** — that's archetype
**1 Linear pipeline** oriented vertically, and the **circuit→behavior** story is archetype 1/5 with the
comp-neuro icon kit. Use the general archetype + the domain icon set, not a neuro-only template.

Full slot structures, element counts, text density, and where the punchline goes are in
`references/archetypes.md`. Pre-built SVG skeletons (canvas + slots + flow arrows, palette-tokened) are
in `assets/skeletons/` — start from the matching skeleton and fill its slots.

## Step 2 — Fill the slots (rules that travel with every archetype)
- **≤7±2 top-level elements** (cognitive-load cap, R5). More → group by proximity or cut.
- **One reading order, one entry, one exit** (R3); arrows are the spine and encode time/causation.
- **Exactly one punchline**, visually dominant, `accent` color, at the archetype's punchline slot (R4).
- **Text = labels, not prose** (≤~60–80 words total; labels 1–3 words; keyword colored to match its
  element so text doubles as the legend) (R6).
- **≤5 structural colors**, fixed condition→color map, muted journal palette (R7); contrast ≥4.5:1 (R8).
- **Layout must match the message** (R9): don't put false arrows on a non-sequential set; don't use an
  orthogonal grid for a process. The archetype choice IS this rule.
- **Square-first** (R13); a long story folds into zig-zag (#2) rather than going wide.
- **Distinct from in-paper figures, no raw data items** in a GA (R10).

## Design rules R1–R14 (the design-reviewer gate, in priority order)

Apply in this order; a failure high in the list outranks polish below it:

1. **R1 Visual coherence** — one icon style, one palette, aligned grid; looks like one family. *SciGA:
   the single strongest predictor of human preference (r=0.421). If this fails, fix it first.*
2. **R3 Clear reading order** — one entry, one exit; arrows/enumeration resolve ambiguity.
3. **R4 One point, new finding emphasized** — single dominant punchline; background trimmed.
4. **R9 Layout matches message** — archetype fits the relationship type (process/comparison/typology…).
5. **R5 ≤7±2 elements** — else group or cut.
6. **R2 Consistent icon language** — same line-weight, palette, detail across glyphs.
7. **R6 Text sparse, denominative** — labels not paragraphs; no undefined abbreviations.
8. **R7/R8 Color encodes meaning, soft, CVD-safe, ≥4.5:1** — (overlap with `contrast_check.py`).
9. **R10 Distinct from paper figures; no raw data** (GA only).
10. **R11 Domain/context grounding** — a cue signals the field/system; match the field's visual idiom.
11. **R14 Reads in <10 s** — a naive viewer states the take-home at a glance.
12. **R12 Aesthetics** — tiebreaker only; polish after coherence + clarity are secured.

## Diagram conventions (apply)
**Connectors encode the relationship** — arrowheads = direction, dashed-vs-solid = link type, kept
consistent across every diagram in one deliverable; the contrast (e.g. hub-and-spoke vs mesh, or
report-up vs delegate-down) must read from the line treatment, not only a caption. **Role-bearing
icons are information** — keep them through a reskin; only purely decorative icons are optional.

## Anti-patterns (auto-flag)
Multi-panel collage in a GA · any data items/plots/numbers in a GA · too much / <12 pt text · heavily
saturated primaries / >5 colors · reusing the paper's model figure as the GA · background-literature
clutter · ambiguous reading order / false arrows on non-sequential content · mixed icon styles ·
red-green schemes · depicting the apparatus instead of the finding (neuro).

## Files
- `references/archetypes.md` — per-archetype slot structure, element/text/punchline specs, ASCII sketches.
- `assets/skeletons/` — pre-built domain-agnostic SVG layout skeletons (canvas + slots + arrows, palette-tokened).
