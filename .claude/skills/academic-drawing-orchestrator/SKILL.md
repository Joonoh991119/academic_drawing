---
name: academic-drawing-orchestrator
description: "Orchestrates the Academic_Drawing agent team to produce a publication-grade GRAPHICAL ABSTRACT and/or ACADEMIC PRESENTATION SLIDES for ANY scientific/academic project (domain-agnostic; not just neuro), with a decisive, mode-based generate -> selective-review -> human-confirm loop. Use whenever the user wants to build/make/design a graphical abstract, visual summary figure, Cell/Nature-style abstract figure, an academic talk/seminar/defense deck, a slides-from-markdown build, or an experimental-procedure schematic — and for ALL follow-ups: redo/다시/수정/보완/restyle, re-run, update, fix the layout, change a color/condition, export, regenerate, partial re-run of one section, 'improve the previous result', or 'apply my feedback'. Picks a Fast/Standard/Full mode and sane defaults instead of asking; reviews selectively, not exhaustively. Trigger on 'graphical abstract', '그래피컬 초록/그래픽 요약/요약 그림', 'academic slides/발표 슬라이드/세미나/디펜스 자료', 'experimental procedure figure', 'markdown -> pptx', or any restyle/redo of these."
---

# Academic_Drawing Orchestrator

Coordinates a specialist agent team to deliver a **graphical abstract** and/or an **academic
presentation deck**, holding one palette / one voice / one citation style across both. Works for
**any scientific/academic project** — domain-agnostic core, with comp-neuro as one supported domain.
When both are requested, the graphical abstract is produced first and *reused* inside the deck.

## Decision discipline — READ FIRST  (`references/routing-and-review.md`)

Be **decisive and selective**, not exhaustive. The harness's failure mode is dithering and
over-reviewing. Before anything else:
1. **Pick a MODE** — **Fast** (pre-structured input, "즉시/빨리", "skip QC", a recolor/export),
   **Standard** (default — a normal brief), or **Full** (explicitly "thorough / submission-grade").
   Infer it from the request; **never ask which mode**.
2. **Apply the don't-ask DEFAULTS** — palette = the active journal preset (NPG), GA = Cell square,
   slides = 16:9 PPTX, conditions inferred from the brief, citations from Zotero-or-`[PLACEHOLDER]`.
   Generate with the default; surface the resulting choices at the **single** human gate, never as
   up-front questions.
3. **Review by ROUTING, once** — run only the *applicable* reviews on the *near-final* artifact, at
   the right scope. Cheap deterministic gates (overlap/lint/equation) always; expensive model
   reviews (Codex/logic/design) **once**, and only when there is something for them to judge. A
   mechanical fix-loop never re-triggers the expensive reviews. Partial re-run = review only the
   changed scope.

`references/routing-and-review.md` is the authoritative spec for *how much to do, what to review,
when*. This file governs *who does it*. When the two seem to conflict, routing-and-review.md wins on
scope/mode; this file wins on roster/sequence.

## Execution mode: HYBRID  (Full mode; Fast/Standard collapse the teams — see routing-and-review.md)
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
| `plot-engineer` | custom | code-drawn matplotlib/seaborn figures, palette-locked, SVG/PDF + 300-dpi PNG | ga-style-contract (+academic_mpl; *scientific-visualization* opt) | `_workspace/11_plot_*.svg` (or placeholders) |
| `slide-planner` | custom | deck structure to the fixed section template + action titles + outline | slide-rhetoric, ga-style-contract | `_workspace/20_outline.md` |
| `slide-builder` | custom | renders editable PPTX from the outline, palette/font reskinned, embeds abstract | slide-rhetoric (+pptxgenjs; *pptx* skill opt) | `_workspace/21_deck.pptx` |
| `slide-web-builder` | custom | *alternative* deck path: HTML/CSS slides (Claude-design web), show_widget preview, Chrome export | slide-rhetoric, ga-style-contract | `_workspace/21web_slide_*.html/.png` |
| `qc-renderer` | custom (general-purpose tools) | renders SVG/PPTX/HTML to images, runs overlap_check.py + pptx_style_lint.py + equation_qc.py, produces QC JSON + PNGs | overlap-qc | `_workspace/*_qc.json`, PNGs |
| `naive-reviewer` | custom | drives `mcp__codex__codex` (read-only) for text/equation/abbreviation/claim rule-check | (Codex MCP) | `_workspace/*_naive_review.json` |
| `design-reviewer` | custom | vision critique of the rendered image against the SciGA rubric | (vision + ga-style-contract) | `_workspace/*_design_review.md` |
| `logic-reviewer` | custom | reasoning/coherence lens: claim chain + over-claiming + title↔plot direction errors | (Opus + slide-rhetoric) | `_workspace/*_logic_review.md` |

All agents run `model: "opus"`. Reviews run three independent lenses in parallel (Codex rules /
vision design / Opus logic); the slide phase can build the PPTX deck, the HTML 'web' deck, or both.

## Workflow

### Phase 0 — Mode, defaults & context
0. **Pick the run MODE (Fast / Standard / Full)** and apply the don't-ask defaults —
   `references/routing-and-review.md` §1–§2. This decides how much of the workflow below runs: Fast
   collapses Phases 2–5 into one build + mechanical QC + one combined quick-look review + one gate;
   Standard runs the applicable one-pass reviews; Full runs teams + all applicable reviews.
1. Check for `_workspace/` (follow-up support).
2. Decide the run shape:
   - **absent** → initial run → Phase 1.
   - **present + partial-fix request** (e.g. "fix the abstract's act C", "recolor condition B",
     "redo results slide") → **partial re-run**: re-invoke only the relevant agent(s), read the
     existing artifact, apply the change, re-run only the affected review. Do not rebuild everything.
   - **present + new input** → archive `_workspace/` → `_workspace_prev_<stamp>/`, then Phase 1.
3. For partial re-runs, pass the prior artifact path into the agent prompt so it edits rather than
   regenerates.

### Phase 1 — Intake (non-blocking: infer + default, do NOT interrogate)

Gather what the user already gave into `_workspace/00_input/`. **Do not ask a checklist up front.**
Fill the **universal intake schema** by inference; leave the rest as `[PLACEHOLDER]`:

| Field | Get it from | If absent → |
|-------|-------------|-------------|
| topic / working title | the request | infer a working title |
| one core claim | the request | `[PLACEHOLDER: claim]` |
| 1–3 entities/conditions | the request | infer; map onto `cond_a` / `cond_b` / `accent` |
| known assets (data, figures, refs) | request / attached files | reserve labeled placeholders |
| target deliverable + venue | the request | **default: GA (Cell square) and/or PPTX 16:9** |

Then, **without pausing**:
1. Write the project label_map to `_workspace/00_input/label_map.json` (map the inferred conditions
   onto `cond_a/cond_b/...`). **Do NOT edit the shipped `palette.json` `label_map`** — the scripts
   read the project label_map from `00_input/`, falling back to palette.json `_template`.
2. Apply the **defaults** (`references/routing-and-review.md` §2): palette = active journal preset,
   GA = Cell square, slides = 16:9 PPTX, citations = Zotero-or-`[PLACEHOLDER]`.
3. Render the swatch + run `contrast_check.py` *for the record* — do **not** block on sign-off.
   Surface the palette + inferred label_map at the **single human gate**, with the draft.

**Only hard-block to ask** when source material is missing that cannot be placeholdered (e.g. there is
no claim at all). Everything else defaults or becomes a placeholder. A first user saying "make a
graphical abstract for my study" should get a *default draft*, not an interview.

---

## The DEFAULT path is Fast/Standard — Phases 2–5 below are the FULL-mode expansion

Do **not** reach for agent teams, live preview, or 3-lens review by default. Most runs are Standard
or Fast.

**Fast / Standard run (the default — no TeamCreate):**
1. **Generate directly.** Abstract: `concept-architect` picks an archetype skeleton (`ga-templates`)
   → `svg-compositor` fills it (+ `plot-engineer` for any plot). Slides: `slide-planner` →
   `slide-builder`. Call these as sub-agents (`Agent`) or inline — not a team.
2. **Mechanical gate.** `qc-renderer` runs overlap / pptx-lint / equation until PASS.
3. **Review once, applicable only** (`references/routing-and-review.md` §3). Standard = the lenses
   that have something to judge; **Fast = one combined quick-look** (tone+layout+claims in one Opus
   pass). Skip vision on unchanged slides.
4. **One human gate** with the render + a short findings summary. Done.

**Full run** — only when the user asks "thorough / submission-grade / review carefully / for
submission": use the team + live-preview + multi-iteration machinery in Phases 2–5.

---

### Phase 2 — Graphical abstract: generate  (FULL mode — team; Fast/Standard call the agents directly)
1. `TeamCreate(team_name:"abstract-team", members:[drawing-director(lead), concept-architect,
   svg-compositor, plot-engineer], model:"opus")`.
2. `TaskCreate`:
   - concept-architect: **pick the archetype** (`ga-templates`) by message type, start from its
     skeleton, pre-allocate regions + font sizes, mark real vs placeholder → `10_concept_layout.md`.
   - plot-engineer: for any embedded data plot, render it palette-locked, or (if data isn't in hand)
     define a placeholder spec → `11_plot_*.svg` / placeholder notes.
   - svg-compositor (depends on both): **fill the chosen skeleton** → `12_abstract.svg`, embed plots,
     insert placeholder rectangles, keep ≤5 colors and the project label_map.
3. Team coordinates via SendMessage: compositor requests plot SVGs sized to the reserved regions;
   concept-architect arbitrates layout conflicts. Director monitors.

### Phase 2.5 — Live preview (FULL mode / explicit "preview" request only — skip by default)
Only in Full mode or when the user explicitly asks to preview/iterate inline: the svg-compositor
renders the SVG via `mcp__visualize__show_widget` (call `mcp__visualize__read_me` with modules
`art,diagram` first; 680px preview dialect). **Requires the visualize MCP** — not guaranteed; if it's
absent, skip silently and go to QC. The operator steers in a fast show→feedback→edit loop (the
"claude design 연동" path). Never let this reintroduce an up-front gate in Fast/Standard runs.

### Phase 3 — Graphical abstract: review loop  (parallel sub-agents → human)
Iteration cap by mode (`references/routing-and-review.md` §3): **Full** = up to 3 fix iterations;
**Standard** = one review pass + at most one fix, then the gate; **Fast** = quick-look + gate (no fix
loop). Reviews never re-run on a mechanical fix-loop.
1. **Mechanical QC (hard gate).** `qc-renderer`: run `overlap_check.py 12_abstract.svg` and
   `graphical-abstract/scripts/render.py` (font minima + oversize). Any `FAIL` → send specifics to
   svg-compositor, fix, re-run. Block until overlap = PASS and render validates.
2. Once mechanical QC passes, run the **APPLICABLE reviews ONCE** (routing-and-review.md §3 — skip any
   lens with nothing to judge; **Fast mode = one combined quick-look pass** instead of three; reviews
   do NOT re-run on mechanical fix-loops):
   - **naive-reviewer (Codex)** on the SVG source + extracted text: tone/AI-slop, hallucinated
     abbreviations/jargon, undefined symbols, equation correctness, unsupported claims →
     `14_naive_review.json`. *(skip if no text changed / Fast mode)*
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

## Data flow  (FULL mode shown; Fast/Standard skip the teams + the up-front sign-off — see routing-and-review.md)
```
00_input ─▶ Director infers palette+label_map (surfaced at the final gate, not up front)
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
**Fast (default for pre-structured input):** "make slides from this markdown" → infer + default, no
questionnaire → build directly → mechanical QC + one combined quick-look → single human gate → delivered.
**Standard (default for a brief):** brief → infer palette + conditions (no up-front sign-off) → pick
archetype → draft → mechanical QC + the *applicable* review once → human gate (palette + draft
surfaced together) → export. Placeholders listed.
**Full (only if asked "thorough / submission-grade"):** Phase 1 → abstract team → live preview →
3-lens review (≤3 iters) → human → slides team → review → approve.
**Error:** overlap_check FAILs on the abstract (label collides with an arrow) → Director routes the
specific finding to svg-compositor → relayout → re-render → PASS → continues. If still failing after
3 iterations, the human is shown the exact collision and decides.
