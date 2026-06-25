# Archetype catalog — slot structures, specs, sketches

Per-archetype detail for the `ga-templates` selection table. Each entry: when-to-use, slot structure
+ reading order, ASCII sketch, element/text budget, and the punchline slot. Frequencies are the
empirical share of real GAs (Hullman & Bach, n=54) — use as a tie-breaker. Reading-flow legend:
`→` left-right · `↓` top-down · `⟳` cycle · `◎`/`★` center/punchline.

## Table of contents
1. Linear pipeline · 2. Zig-zag · 3. Comparison (parallel) · 4. Before→After · 5. Mechanism/forking
· 6. Hub-and-spoke · 7. Cycle · 8. Quadrant · 9. Hierarchy/multi-scale · 10. Single-finding/Q→A
· 11. Cover-art · Cross-archetype defaults.

---

## 1. Linear pipeline (input → method → finding) — Linear, 35%
- **Use:** process/method papers, sequential cause→effect, drug-discovery/analysis pipelines. The
  comp-neuro top-down **3-act (task→model→finding)** is this, oriented vertically.
- **Slots / order:** `[Context/Problem] → [Method/Approach] → [Key result ★] → [Implication]`, one
  reading order enforced by arrows (arrows = time in 72% of linear GAs).
- **Sketch:** `[ Input ] →→ [ Method ] →→ [ ★ Finding ] →→ [ Impact ]`
- **Budget:** 3–4 nodes + arrows; ≤80 words; 1–3-word node labels.
- **Punchline:** terminal/right (or bottom) node — larger, `accent`.

## 2. Zig-zag (folded pipeline) — Zig-zag, 5.5%
- **Use:** a linear story too long for one row (5–7 steps) inside a square canvas.
- **Slots / order:** rows read `→`, stacked `↓` (boustrophedon). Enumerate (i, ii, iii) if order is ambiguous.
- **Sketch:** `[1]→[2]→[3]┐` / `┌────────┘` / `[4]→[5]→[★6]`
- **Budget:** 5–7 nodes; 1–3-word labels.
- **Punchline:** final cell, bottom-right.

## 3. Comparison / A-vs-B (parallel) — Parallel, 37% (most common)
- **Use:** treatment vs control, WT vs mutant, method-A vs method-B, before/after as static contrast.
- **Slots / order:** two (or three) side-by-side columns with matched sub-structure; read each column
  `↓`, compare across. Identical styling per column so the difference pops; fixed condition→color.
- **Sketch:** `[ Condition A ] | [ Condition B ]` with `[result A]` / `[result B]` below each.
- **Budget:** 4 core elements (2 conditions × 2 results).
- **Punchline:** a center "verdict" strip or a Δ glyph **between** the columns naming the changed outcome.

## 4. Before → After (intervention transform) — Parallel/Linear
- **Use:** one system changed by one intervention (naive→trained, disease→treated, perturbation).
- **Slots / order:** `[State 0] —(intervention)→ [State 1]`; the arrow/center carries the manipulation
  (the only verb).
- **Sketch:** `[ Before ] ══[ intervention ]══▶ [ ★ After ]`
- **Budget:** 3 elements (2 states + 1 intervention label).
- **Punchline:** the "After" state, set as focal point.

## 5. Mechanism / pathway (forking) — Forking, 18.5%
- **Use:** molecular pathways, signaling cascades, branching causal chains.
- **Slots / order:** a backbone path that branches ≥once; directional arrows (activation ▸, inhibition ⊣).
  A small legend if ▸/⊣ notation is used (legends appear in ~20% of GAs).
- **Sketch:** `[A]→[B]→[C] ┬─▶ [outcome 1]` / `└─▶ [★ outcome 2]`
- **Budget:** 4–7 nodes + optional legend.
- **Punchline:** terminal node of the emphasized branch; thicken/recolor that path.

## 6. Hub-and-spoke / central concept (centric) — Centric, 7.4%
- **Use:** many inputs converge on one finding; integration/multi-omics/multi-method. Only when there
  is genuinely no sequence (reading order is ambiguous by nature).
- **Slots / order:** a **center** holding the core claim + a **periphery** of 3–4 facets radiating out;
  center read first, spokes in any order; keep spoke labels symmetric/parallel.
- **Sketch:** `[in1] [in2]` ↘↙ `(★ HUB)` ↗↖ `[in3] [out]`
- **Budget:** 4–5 elements (≥3 spokes + hub + outcome).
- **Punchline:** dead center, largest element, `accent`.

## 7. Cycle / loop (circular)
- **Use:** iterative processes, feedback loops, cyclical phenomena (cell cycle, train→eval→refine,
  perception-action).
- **Slots / order:** 3–5 stages on a ring, read clockwise `⟳`, closing to start; inner glyph can name
  the loop.
- **Sketch:** `[1] ⟳ [2] ⟳ [3] ⟳ [4] ⟳ (back to 1)`
- **Budget:** 3–5 stages, one short label each.
- **Punchline:** center of the ring (emergent property) or the novel stage, `accent`.

## 8. Quadrant / taxonomy (orthogonal) — Orthogonal, 16.6%
- **Use:** 2×2 conceptual frameworks, typologies, design spaces, "where our method sits". Deliberately
  **non-temporal** — implies equivalence, not sequence (so NO arrows).
- **Slots / order:** two labeled axes + four quadrant cells; rely on top-left-first convention.
- **Sketch:** `↑axisY` / `[Q1][Q2]` / `──┼──→axisX` / `[Q3][★Q4]`
- **Budget:** 2 axis labels + ≤4 cells, one icon/phrase per cell.
- **Punchline:** the claimed quadrant (often empty-before-now) or an "ours" labeled point.

## 9. Hierarchy / multi-scale (nesting, vertical) — Nesting, 29.6% (2nd most common)
- **Use:** systems biology, ecology, multi-scale models; macro→meso→molecular.
- **Slots / order:** stacked levels `↓` from whole to detail, often with a nested zoom-in inset
  ("footnoting" — a framed inset giving detail/context).
- **Sketch:** `[ ORGANISM ]` / `└▶[ TISSUE ]` / `└▶[ ★ MOLECULE ]`
- **Budget:** 3+ stacked levels + one zoom frame; label each scale.
- **Punchline:** the level where the discovery lives (often the innermost zoom), `accent`.

## 10. Single-finding / Question→Answer (single) — Single, 14.4%
- **Use:** one headline result, "the finding IS the figure," result-first papers, poster/tweet.
- **Slots / order:** optional top question banner → one dominant central visual → optional one-line
  answer (≤8 words). If a chart, strip axes/legends (high-level only — but in a GA use a schematic,
  not a real data plot; raw data stays a placeholder).
- **Sketch:** `[ "Does X cause Y?" ]` / `[ ★ big result ]` / `[ "Yes — by Z." ]`
- **Budget:** 1 hero visual + ≤2 text lines.
- **Punchline:** IS the central element.

## 11. Cover-art (Nat Neuro / J Neurosci covers — NOT a GA)
- **Use:** issue-cover submissions; chosen for aesthetic appeal + scientific interest.
- **Slots / order:** a single dominant hero image, **near-zero text** (editors add the title), portrait,
  full-bleed.
- **Budget:** 1 hero image; 0 captions.
- **Punchline:** the image itself; do not document findings — make it arresting.

---

## Cross-archetype defaults
- Total text ≈ **60–80 words max**; **≤7±2** top-level elements; **≤5** structural colors with a fixed
  condition→color map; **one** dominant focal element; **square (1:1)** canvas first (fold long stories
  into zig-zag rather than going wide).
- Arrows are the backbone: one unambiguous start, one end, one consistent arrowhead style.
- Labels sit adjacent to their element; color the keyword to match its element so text doubles as the
  legend. A GA carries **no caption and no data values**.
