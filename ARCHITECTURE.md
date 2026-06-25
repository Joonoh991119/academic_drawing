# Architecture & routing

How the harness is wired — the agent ↔ skill ↔ script map, the decision flow, and where the
"source of truth" for each concern lives. (For *usage*, see [README](README.md); for *setup*, run
`python3 bin/preflight.py`.)

## Decision flow (what actually runs)

```
request ─▶ orchestrator
           │  Phase 0: pick MODE (Fast / Standard / Full) + apply don't-ask defaults
           │           └─ SoT: skills/academic-drawing-orchestrator/references/routing-and-review.md
           ▼
   ┌─────────────── GENERATE ───────────────┐
   │ abstract: concept-architect (pick archetype from ga-templates)            │
   │           → svg-compositor (+ plot-engineer)                              │
   │ slides:   slide-planner → slide-builder (PPTX) and/or slide-web-builder   │
   └──────────────────────────────────────────┘
           ▼
   ┌─────────── SELECTIVE REVIEW (once, by routing) ───────────┐
   │ ALWAYS  qc-renderer: overlap_check / pptx_style_lint / equation_qc (cheap, deterministic gate) │
   │ IF text/claims  naive-reviewer (Codex) · logic-reviewer (Opus)                                 │
   │ ON near-final   design-reviewer (vision, ga-templates R1–R14)                                  │
   │   (Fast mode = one combined quick-look pass; mechanical fix-loops never re-trigger these)       │
   └───────────────────────────────────────────────────────────┘
           ▼
   HUMAN CONFIRM (once per deliverable) ─▶ finalize
```

## Agents (`.claude/agents/`, all `model: opus`)

| Agent | Role | Loads skills | Output |
|-------|------|--------------|--------|
| `drawing-director` | lead: sequences, triages reviews, holds human gate | ga-style-contract, overlap-qc (reads orchestrator ref *routing-and-review.md*) | locked palette; final handoff |
| `concept-architect` | picks the **archetype** + pre-allocates the layout | **ga-templates**, graphical-abstract, ga-style-contract | `10_concept_layout.md` |
| `svg-compositor` | emits the publication SVG, embeds plots, reserves placeholders | graphical-abstract, ga-templates, ga-style-contract | `12_abstract.svg` |
| `plot-engineer` | code-drawn plots, palette-locked via `academic_mpl` | ga-style-contract (+ academic_mpl; *scientific-visualization* = external/opt) | `11_plot_*.svg` |
| `slide-planner` | deck structure → outline (fixed section template) | slide-rhetoric, ga-style-contract | `20_outline.md` |
| `slide-builder` | editable **PPTX** (pptxgenjs) | slide-rhetoric (+ pptxgenjs; *pptx* skill = external/opt) | `21_deck.pptx` |
| `slide-web-builder` | alt **HTML** deck (Claude-design web) | slide-rhetoric, ga-style-contract | `21web_slide_*` |
| `qc-renderer` | mechanical gate: render + overlap/lint/equation | overlap-qc | `*_qc.json`, PNGs |
| `naive-reviewer` | Codex rule-check (tone/abbrev/equation/citation) | (Codex MCP) | `*_naive_review.json` |
| `logic-reviewer` | claim-chain / over-claiming / title↔plot direction | (Opus) | `*_logic_review.md` |
| `design-reviewer` | vision critique vs ga-templates R1–R14 | ga-templates, ga-style-contract | `*_design_review.md` |

## Skills (`.claude/skills/`)

| Skill | Purpose | Scripts | Used by |
|-------|---------|---------|---------|
| `academic-drawing-orchestrator` | the pipeline + mode/routing | — (refs: routing-and-review.md) | director |
| `ga-style-contract` | **SoT** for palette / tone / citation / equation / contrast | swatch · contrast_check · format_citation · academic_mpl · render_presets | all |
| `ga-templates` | archetype library + venue logic + R1–R14 design rules | (assets: skeletons/) | concept-architect, design-reviewer |
| `overlap-qc` | render + collision / deck-lint / equation gates | overlap_check · pptx_style_lint · equation_qc | qc-renderer |
| `slide-rhetoric` | slide section template + action-title rules | — | slide-planner/builder |
| `graphical-abstract` | Cell-grade SVG kit (vendored) | render.py | compositor |
| `scientific-figure` | exact-mm multi-panel figures (vendored) | compose · export · validate_fonts | plot-engineer |

> **External / optional skills** — referenced by name but NOT in this repo (Claude Code global or
> built-in; the harness degrades gracefully without them): `scientific-visualization` (extra journal
> plot presets), `pptx` (Anthropic deck helpers), `statistical-analysis` (APA stat formatting),
> `csnl-ontology` (lab vocabulary), `interview`. Core plotting uses matplotlib via `academic_mpl`;
> core slides use `pptxgenjs` — neither requires an external skill. `bin/spec_lint.py` allowlists these
> and fails on any *other* unknown skill reference.

## Source-of-truth index (no duplication)

| Concern | Lives in |
|---------|----------|
| how much to do / mode / review routing | `academic-drawing-orchestrator/references/routing-and-review.md` |
| color / tone / citation / equation / contrast | `ga-style-contract/SKILL.md` + `assets/palette.json` |
| which layout / venue / design rules R1–R14 | `ga-templates/SKILL.md` + `references/archetypes.md` |
| slide structure / voice | `slide-rhetoric/SKILL.md` |
| who does it / sequence | `academic-drawing-orchestrator/SKILL.md` (this map mirrors it) |
| environment / deps | `bin/preflight.py` + `requirements.txt` + `CLAUDE.md` preflight block |
