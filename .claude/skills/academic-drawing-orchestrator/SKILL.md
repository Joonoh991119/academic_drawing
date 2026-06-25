---
name: academic-drawing-orchestrator
description: "Orchestrates the Academic_Drawing agent team to produce a publication-grade GRAPHICAL ABSTRACT (first) and then ACADEMIC PRESENTATION SLIDES (second) for computational/cognitive-neuroscience work, with a generate -> review -> human-confirm loop. Use whenever the user wants to build/make/design a graphical abstract, visual summary figure, Cell/Nature-style abstract figure, an academic talk/seminar/defense deck, or an experimental-procedure schematic — and for ALL follow-ups: redo/다시/수정/보완/restyle the abstract or slides, re-run, update, fix the layout, change a color/condition, export, regenerate the deck, partial re-run of one section, 'improve the previous result', or 'apply my feedback'. Owns the cross-deliverable color/citation/tone consistency and the QC loop. Trigger on 'graphical abstract', '그래피컬 초록/그래픽 요약/요약 그림', 'academic slides/발표 슬라이드/세미나/디펜스 자료', 'experimental procedure figure', or any restyle/redo of these."
---

# Academic_Drawing Orchestrator

Coordinates a specialist agent team to deliver, in order, (1) a single-panel **graphical abstract**
and (2) an **academic presentation deck**, holding one palette / one voice / one citation style
across both, and gating every deliverable through mechanical QC → naive review → design review →
**human confirm**. The graphical abstract is produced first and then *reused* inside the deck.

## Execution mode: HYBRID
| Phase | Mode | Why |
|-------|------|-----|
| 2 Abstract generation | **agent team** | concept ↔ compositor ↔ plot-engineer co-design one locked layout; the compositor needs plot SVGs sized to reserved regions |
| 3 Abstract review | **sub-agents (parallel)** | qc-renderer / Codex / design-reviewer are independent passes; results collected by the Director |
| 4 Slides generation | **agent team** (rebuilt) | planner ↔ builder ↔ plot-engineer co-design the deck reusing the abstract |
| 5 Slides review | **sub-agents (parallel)** | same independent-review rationale |

One team is active at a time. Disband the abstract team (Phase 3 end) before building the slides
team (Phase 4) — abstract artifacts persist in `_workspace/` for the slides team to read.

## Agent roster
| Agent | Type | Role | Primary skills | Output |
|-------|------|------|----------------|--------|
| `drawing-director` | custom (lead) | owns style contract, sequences phases, runs review loops, holds human gate | ga-style-contract, overlap-qc | locks palette+label_map; final handoff |
| `concept-architect` | custom | designs the single-idea 3-act composition; pre-allocates whitespace + font sizes before placement | graphical-abstract, ga-style-contract | `_workspace/10_concept_layout.md` |
| `svg-compositor` | custom | emits the publication SVG from the kit; inserts placeholder regions | graphical-abstract, ga-style-contract | `_workspace/12_abstract.svg` |
| `plot-engineer` | custom | code-drawn matplotlib/seaborn figures, palette-locked, SVG/PDF + 300-dpi PNG | scientific-visualization, ga-style-contract | `_workspace/11_plot_*.svg` (or placeholders) |
| `slide-planner` | custom | deck structure to the fixed section template + action titles + outline | slide-rhetoric, ga-style-contract | `_workspace/20_outline.md` |
| `slide-builder` | custom | renders editable PPTX from the outline, palette/font reskinned, embeds abstract | pptx, slide-rhetoric | `_workspace/21_deck.pptx` |
| `slide-web-builder` | custom | *alternative* deck path: HTML/CSS slides (Claude-design web), show_widget preview, Chrome export | slide-rhetoric, ga-style-contract | `_workspace/21web_slide_*.html/.png` |
| `qc-renderer` | custom (general-purpose tools) | renders SVG/PPTX/HTML to images, runs overlap_check.py + pptx_style_lint.py + equation_qc.py, produces QC JSON + PNGs | overlap-qc | `_workspace/*_qc.json`, PNGs |
| `naive-reviewer` | custom | drives `mcp__codex__codex` (read-only) for text/equation/abbreviation/claim rule-check | (Codex MCP) | `_workspace/*_naive_review.json` |
| `design-reviewer` | custom | vision critique of the rendered image against the SciGA rubric | (vision + ga-style-contract) | `_workspace/*_design_review.md` |
| `logic-reviewer` | custom | reasoning/coherence lens: claim chain + over-claiming + title↔plot direction errors | (Opus + slide-rhetoric) | `_workspace/*_logic_review.md` |

All agents run `model: "opus"`. Reviews run three independent lenses in parallel (Codex rules /
vision design / Opus logic); the slide phase can build the PPTX deck, the HTML 'web' deck, or both.

## Workflow

### Phase 0 — Context check (follow-up support)
1. Check for `_workspace/`.
2. Decide mode:
   - **absent** → initial run → Phase 1.
   - **present + partial-fix request** (e.g. "fix the abstract's act C", "recolor condition B",
     "redo results slide") → **partial re-run**: re-invoke only the relevant agent(s), read the
     existing artifact, apply the change, re-run only the affected review. Do not rebuild everything.
   - **present + new input** → archive `_workspace/` → `_workspace_prev_<stamp>/`, then Phase 1.
3. For partial re-runs, pass the prior artifact path into the agent prompt so it edits rather than
   regenerates.

### Phase 1 — Prep & lock the style contract
1. Gather the user's material into `_workspace/00_input/` (paper text, data descriptions, the
   story/claim, condition names, author/year for citations). Ask for what's missing — do **not**
   fabricate facts, numbers, or citations.
2. **Director locks the palette + label_map.** Replace the `_template` in
   `ga-style-contract/assets/palette.json` → `label_map` with the project's real conditions, render
   the swatch (`python3 ga-style-contract/scripts/swatch.py`), and **show it to the user for
   sign-off** before producing anything. Record any palette/tone overrides in
   `_workspace/00_input/style_overrides.md`.
3. **Confirm venue + GA aspect with the operator (no fixed default).** Ask the target: Cell GA =
   square `--target cell` (1650², Arial 12–16 pt); a taller portrait `--target cell_portrait` only
   where the venue/use allows; or `nature1/2` / `pnas1/15/2`. Pass the chosen render target to the
   abstract team. For slides: 16:9; ask whether to build the editable-PPTX deck, the HTML 'web' deck,
   or **both**. Confirm deliverable order (abstract → slides).
4. Run the contrast/CVD gate (`contrast_check.py`) as part of the palette sign-off — a WCAG FAIL
   blocks the lock; condition-separation WARNs are acceptable because the contract mandates redundant
   coding (shape/weight/position), which is the operator's confirmed preference.

### Phase 2 — Graphical abstract: generate  (agent team)
1. `TeamCreate(team_name:"abstract-team", members:[drawing-director(lead), concept-architect,
   svg-compositor, plot-engineer], model:"opus")`.
2. `TaskCreate`:
   - concept-architect: design the 3-act (task→model→finding) layout, pre-allocate regions + font
     sizes, mark which regions are real vs placeholder → `10_concept_layout.md`.
   - plot-engineer: for any embedded data plot, either render it palette-locked, or (if data isn't
     in hand) define a placeholder spec → `11_plot_*.svg` / placeholder notes.
   - svg-compositor (depends on both): assemble `12_abstract.svg` from the kit, embed plots, insert
     placeholder rectangles, keep ≤5 colors and the locked label_map.
3. Team coordinates via SendMessage: compositor requests plot SVGs sized to the reserved regions;
   concept-architect arbitrates layout conflicts. Director monitors.

### Phase 2.5 — Live preview (steer before the costly gates)
Before spending the Chrome + Codex + design passes, the svg-compositor renders the current SVG inline
via `mcp__visualize__show_widget` (call `mcp__visualize__read_me` with modules `art,diagram` first;
use the 680px preview dialect). The operator steers layout/emphasis/wording in a fast
show→feedback→edit loop — this is the "claude design 연동" path. Lock the layout here, then proceed.

### Phase 3 — Graphical abstract: review loop  (parallel sub-agents → human)
Run up to **3 fix iterations**, then escalate to the human regardless.
1. **Mechanical QC (hard gate).** `qc-renderer`: run `overlap_check.py 12_abstract.svg` and
   `graphical-abstract/scripts/render.py` (font minima + oversize). Any `FAIL` → send specifics to
   svg-compositor, fix, re-run. Block until overlap = PASS and render validates.
2. In parallel once mechanical passes (three independent lenses):
   - **naive-reviewer (Codex)** on the SVG source + extracted text: tone/AI-slop, hallucinated
     abbreviations/jargon, undefined symbols, equation correctness, unsupported claims →
     `14_naive_review.json`.
   - **logic-reviewer (Opus)** on source + render: claim chain (gap→claim→hypothesis→metric→result),
     over-claiming, and direction/sign errors between action titles and what the plot shows →
     `16_abstract_logic_review.md`.
   - **design-reviewer** on the rendered PNG: SciGA rubric (visual coherence first), hierarchy,
     ≤5-color adherence, label-map consistency, "reads in <10 s", legibility → `15_design_review.md`.
3. Director triages both reports → actionable fixes → svg-compositor/plot-engineer apply → re-render
   → re-review the changed parts.
4. **Human confirm gate (once per deliverable).** Present the rendered abstract + both review
   summaries; ask for sign-off or adjustments. Apply adjustments (partial re-run) until approved.
5. On approval: export final via `render.py` → `abstract.svg` + `abstract.pdf` + `abstract.png`.
   `TeamDelete` the abstract team.

### Phase 4 — Slides: generate  (agent team, rebuilt)
1. `TeamCreate(team_name:"slides-team", members:[drawing-director(lead), slide-planner,
   slide-builder and/or slide-web-builder, plot-engineer], model:"opus")` — include whichever
   builder(s) the operator chose in Phase 1 (PPTX, HTML web, or both).
2. `TaskCreate`:
   - slide-planner: build the deck to the fixed section template (slide-rhetoric), action titles,
     Minto flow, mark result/plot/PDF-crop regions as placeholders, reuse `abstract.png` on the
     Experimental-Procedure slide → `20_outline.md`.
   - plot-engineer: presentation-styled versions of any ready plots (larger fonts, 300 dpi) →
     `21_plot_pres_*.png`; otherwise placeholders.
   - slide-builder (depends on planner): render `21_deck.pptx` via the pptx skill (pptxgenjs),
     palette/font reskinned to English + the locked map, embed the abstract and plots.
   - slide-web-builder (depends on planner, if chosen): author HTML/CSS slides from the SAME outline,
     preview via `show_widget`, export `21web_slide_*.png` — so the operator can compare both decks.

### Phase 5 — Slides: review loop  (parallel sub-agents → human)
Same loop as Phase 3, slide-flavored (max 3 iterations), applied to each built deck:
1. **Mechanical QC:** `qc-renderer` runs `pptx_style_lint.py` (palette/label-color/≤N-hue/font hard
   gate) then renders the PPTX deck (absolute-path `soffice --convert-to pdf` → `pdftoppm -jpeg
   -r 150`); for the HTML deck it runs the Chrome bbox overlap check per slide. Greps for leaked
   `PLACEHOLDER`.
2. **naive-reviewer (Codex):** outline text — tone, abbreviations, citation format, claim support,
   "no full sentences on result captions".
3. **logic-reviewer (Opus):** claim chain across the deck + title↔plot direction consistency.
4. **design-reviewer:** slide images — hierarchy, ≤5 colors, condition→color consistency with the
   abstract, action-title discipline, no Thank-You-only close.
5. Director triages all three reviews → slide-planner/slide-builder(s) fix → re-render → re-review.
6. **Human confirm** → finalize `deck.pptx` and/or `deck_web.*`. If both were built, the operator
   picks the preferred deck (or keeps both). `TeamDelete`.

### Phase 6 — Finalize
1. Copy approved deliverables to the user's chosen output path (`abstract.{svg,pdf,png}`,
   `deck.pptx`). Keep `_workspace/` (audit trail).
2. Report: what was produced, every region left as a PLACEHOLDER (and what each needs), and any
   review findings deferred by the user.
3. Invite feedback (harness evolution): anything to adjust in palette, layout grammar, or the loop?

## Data flow
```
00_input ─▶ Director locks palette+label_map ─▶ swatch sign-off
   │                                               │
   ▼                          (abstract team)      ▼
concept_layout ─▶ plot SVGs ─▶ 12_abstract.svg ─▶ [qc_renderer|Codex|design] ─▶ human ─▶ abstract.{svg,pdf,png}
                                                                                          │ (reused)
                                  (slides team)                                           ▼
                              20_outline ─▶ 21_deck.pptx ─▶ [qc_renderer|Codex|design] ─▶ human ─▶ deck.pptx
```
Conventions: numbered files in `_workspace/`; final deliverables only at the user's path; reviews are
JSON/MD so they're auditable; the locked palette is the one in `ga-style-contract/assets/palette.json`.

## Error handling
| Situation | Strategy |
|-----------|----------|
| overlap_check FAIL | hard gate — fix and re-run; never ship a known collision |
| Chrome measurement fails (exit 3) | fall back to render→vision pass; note the geometric check was skipped |
| Codex unavailable/errors | 1 retry; if still down, run review with an Opus subagent instead and note Codex was unavailable |
| review loop not converging | cap at 3 iterations, then surface the remaining findings to the human to decide |
| missing data/numbers/citation | leave a labeled PLACEHOLDER; never fabricate; ask the user |
| team member stalls | Director SendMessage to check, reassign, or restart |

## Test scenarios
**Normal:** user gives a study brief → Phase 1 locks palette (sign-off) → abstract team drafts SVG →
QC PASS, Codex + design clean (or fixed in ≤3 iters) → human approves → export → slides team builds
deck reusing the abstract → QC/review/approve → `deck.pptx` delivered. Placeholders listed.
**Error:** overlap_check FAILs on the abstract (label collides with an arrow) → Director routes the
specific finding to svg-compositor → relayout → re-render → PASS → continues. If still failing after
3 iterations, the human is shown the exact collision and decides.
