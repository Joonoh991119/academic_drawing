---
name: ga-style-contract
description: The canonical project-wide STYLE CONTRACT for the Academic_Drawing harness — the single source of truth for color palette + fixed label/condition/emphasis color map, restrained academic text/tone rules (no AI-slop, no hallucinated abbreviations or invented acronyms), the "Author et al., YYYY" citation format with Zotero-grounded resolution, the multi-stage equation render-QC policy, typography, contrast/CVD thresholds, and the placeholder-scope rule. Every agent that writes text, picks a color, places a citation, or renders an equation for a graphical abstract or slide MUST load this contract first. Use whenever building/reviewing/restyling any Academic_Drawing deliverable, when asked about the project palette, color consistency, citation format, tone, or "what color is condition X". Read this before authoring SVG, slides, or plots so color and wording stay consistent across abstract -> slides -> manuscript.
---

# Style Contract — Academic_Drawing

The one document every agent reads before writing a word of text, choosing a color, placing a
citation, or rendering an equation. It exists because the user's hardest requirements are
*consistency* and *restraint*: one palette and one voice across the graphical abstract, the slides,
and (later) the manuscript. Treat every rule here as binding unless the Director has overridden it
for a specific project and recorded the override in `_workspace/00_input/style_overrides.md`.

Several rules below are backed by **deterministic scripts** so they are checked, not just hoped for.
The scripts are the gate; the prose explains intent.

## 1. Color — tokens, never raw hex

The palette lives in `assets/palette.json`. **Reference colors by token name** (`ink`, `cond_a`,
`accent`, …), never by hardcoded hex, so the whole project restyles from one file.

Two sets, **both muted and harmonized** so a plot looks like it belongs next to the diagram:

| Set | Used for | Source |
|-----|----------|--------|
| `structural` | diagram lines, boxes, icons, arrows, slide chrome, layout | muted Nature/Cell-toned set |
| `data_series` | plotted DATA series (curves, bars, points) | **muted** categorical set whose first two entries ARE `cond_a`/`cond_b` |

**One color per condition, everywhere.** A *named* condition (in `label_map`) uses its mapped
structural token in BOTH the diagram and the plot — condition A is the SAME `cond_a` hue in the plot,
the diagram, and the slides. `data_series` only supplies extra muted hues for *unnamed* categorical
levels beyond the named conditions. **Do NOT use bright
Okabe-Ito hues for plots** — they read as "generic/AI" and break the toned-down Nature/Cell look
(this was a real defect). CVD safety comes from the **mandatory redundant coding** below (marker
shape + line type + label), not from saturated color. Every plot must call `academic_mpl.apply_style()`
so it inherits Arial + the muted prop-cycle deterministically (no DejaVu fallback, no bright hues).

**Rules (binding):**
- **≤5 structural hues** coexist on one slide/panel (`paper`/`bg`/`text` don't count). Read the cap
  from `palette.max_colors_per_slide`; the deck lint and the SVG review both enforce it.
- **One fixed label→color map per project.** The Director writes the project's conditions to
  `_workspace/00_input/label_map.json` (the scripts read it; do **NOT** edit the shipped `palette.json`
  `_template`), and *every* deliverable uses it identically. Never recolor a condition between figures.
  A **legend swatch must use the EXACT color of the marks it labels** (the condition's locked token) —
  never a generic gray for colored marks, or readers can't map the legend to the figure.
- **`accent` is rationed.** It marks the single key finding / core innovation — at most one
  emphasized region per panel.
- **Never color-alone (redundant coding).** Every color distinction is *also* carried by at least one
  of: marker **shape**, line **type**, **position**, or a **direct label**. Never encode meaning by
  red-vs-green alone. This keeps the figure legible in grayscale and for CVD readers. (`accent` vs
  `cond_a` can be confusable for some CVD types — that is *why* accent is always also
  bold/larger/labeled.)
- Plotted **named conditions** use their `label_map` token (= `data_series[0]`/`[1]` for the two
  locked conditions); additional *unnamed* levels take the next muted `data_series` entries in order.
  Same condition → same muted color in every figure (plot, diagram, slide).

**Contrast/CVD gate at palette-lock.** Before any deliverable is drawn, the Director runs the swatch
**and** the contrast check:
```
python3 .claude/skills/ga-style-contract/scripts/swatch.py            # visual swatch + current label map (human sign-off)
python3 .claude/skills/ga-style-contract/scripts/contrast_check.py    # WCAG text/bg ratios + CVD + grayscale separation of conditions
```
`contrast_check.py` is run for the record and **surfaced at the human gate** — it does **not** block
the initial draft (generate with the default palette). A WCAG text-on-bg FAIL blocks only a palette
**change** that would render text illegible; condition-separation WARNs are advisory (the contract's
mandatory redundant coding covers them).

## 2. Text & tone

The output is read by scientists; write like one.

- **Restrained academic register.** Declarative, specific, no hype. Banned: "revolutionary",
  "groundbreaking", "novel paradigm", "cutting-edge", "seamlessly", "leverage" (as a verb),
  "delve", "robust" used as filler, exclamation marks, rhetorical questions as headers.
- **No AI-slop.** No empty connective scaffolding ("It is important to note that…", "In the realm
  of…"), no triads-for-rhythm, no restating the heading in the first bullet.
- **No hallucinated abbreviations or invented acronyms.** Do **not** coin an abbreviation to save
  space. Use only abbreviations that (a) are standard in the field (e.g. fMRI, RT, SD, CI), or
  (b) the user has explicitly supplied, or (c) validate against the user's domain vocabulary via the
  `csnl-ontology` retriever (if wired) — a term present there counts as user-supplied. If a short
  form is genuinely needed and still unresolved, **do not invent one**: surface it to the operator
  through the **Director's inline human gate** as one focused, prediction-first question (the
  `interview` methodology — propose your best guess, ask "right? what's the preferred form?"), or
  leave `[PLACEHOLDER: short form TBD]` and raise it at the confirm step. Do **not** launch an async
  interview/DM campaign for an operator who is already in the loop.
- **No hallucinated facts, numbers, or citations.** Statistics, p-values, coefficients, author
  names, and years come only from user-supplied material or a resolved Zotero record (§3). If a value
  is needed and absent, leave a `[PLACEHOLDER: …]` marker — never fabricate.
- **Statistics stay minimal in prose.** Keep detailed stats (p-values, coefficients, exact
  equations) out of body text where possible; put a number in a figure caption, not a sentence.
  Captions on result figures use numbers/short math, **not full sentences**. Format any user-supplied
  statistic with correct APA typography (italic *p*, *r* without a leading zero, df) — the
  `statistical-analysis` skill formats; it never invents the value.

## 3. Citations — `Author et al., YYYY`, resolved from Zotero

At-a-glance attribution only (not a reference list). Format in `palette.json` → `citation`:

| Authors | Form | Example |
|---------|------|---------|
| 1 | `{First}, {YYYY}` | `Kim, 2024` |
| 2 | `{First} & {Second}, {YYYY}` | `Kim & Lee, 2024` |
| 3+ | `{First} et al., {YYYY}` | `Kim et al., 2024` |
| unpublished | `{First} et al., in prep` | `Park et al., in prep` |

**Citation resolution (never hand-author the string):**
1. Given a claim or a named author/title, resolve it against the user's **Zotero** library via the
   MCP: topic claim → `mcp__zotero__semantic_search`; named author/title → `mcp__zotero__search_library`.
2. Take the top hit's itemKey → `mcp__zotero__get_item_details`.
3. Run `python3 .claude/skills/ga-style-contract/scripts/format_citation.py <item.json>` to produce the contract-exact string
   deterministically (author lastNames in order; 4-digit year from the free-form date; refuses with a
   `[PLACEHOLDER]` if creators/year are missing).
4. **No confident hit** → `[PLACEHOLDER: citation — <claim>]` and the Director asks the operator at
   the confirm step. Never invent an author or year. Show the resolved title + DOI at the human gate
   so a wrong match is caught. Prefer the local Zotero MCP; `pyzotero` is a documented fallback only.

## 4. Equations — multi-stage QC (deterministic + cold-model + vision)

Equations are a top hallucination/render-failure risk, so they get four checks, not one. The author
(plot-engineer / svg-compositor) emits a structured `_workspace/eqs.json`
(`[{id, latex, declared_symbols, reference_latex?, invariants?}]`); the qc-renderer gates it:

1. **Render** offline, deterministically, with matplotlib mathtext (`text(..., r"$...$")` → `savefig`).
   **Do not** use the sci-ppt `formula_renderer` (broken) or the CodeCogs network path.
2. **Mathtext parse + sympy symbolic check** — `python3 overlap-qc/scripts/equation_qc.py eqs.json`:
   fails fast on broken markup, lists every free symbol and asserts each is in `declared_symbols`
   (the "every symbol must be defined" rule), and checks any stated `reference_latex` identity. This
   is the deterministic gate.
3. **Codex symbolic review** (naive-reviewer): model-appropriateness, notation/dimensional
   consistency — given the `equation_qc.py` JSON so Codex judges meaning, not algebra it can't see.
4. **Vision** (design-reviewer): the *rendering* is legible and unclipped at final size.

Every symbol that appears must be defined in a where-clause, a legend, or the adjacent text.

## 5. Typography & contrast

- One family project-wide: **Arial / Helvetica** (confirmed installed; the Cell/Nature default).
- **Sentence case** for everything except standard acronyms.
- Glyph/icon captions in the abstract: **≤7 words**.
- Respect font minima at *final rendered size* (`palette.json` → `typography.font_minima_pt`). The
  `graphical-abstract` `render.py`, `scientific-figure` `validate_fonts.py`, and the deck
  `pptx_style_lint.py` enforce this — do not bypass them.
- **Contrast floors** (checked by `contrast_check.py`): body text on its background ≥ WCAG 4.5:1
  (large text ≥ 3:1); any two conditions distinguishable under a deuteranopia/protanopia simulation
  *and* in grayscale (else add shape/position per §1).

## 6. Placeholder scope (do not fabricate content)

The harness lays out and **reserves space** for, but never invents the content of:
- **Result figures** produced elsewhere (Claude Code analysis, real data plots).
- **Code-based plots** whose data isn't in hand yet.
- **Regions that must be cropped from a PDF** (the `pdf` / `markitdown` skills can fill these once the
  user supplies the source; until then they stay reserved).

For each, emit a clearly marked placeholder rectangle: dashed `neutral` border, a centered label like
`[PLACEHOLDER — Fig 2: serial-dependence bias, x: Δθ, y: estimation bias]`, and the intended
dimensions. Never replace a placeholder with fabricated data to "complete" the figure.

## Files
- `assets/palette.json` — the locked palette, label map, citation rules, typography. Edit hex here only.
- `scripts/swatch.py` — render `palette_swatch.png` (swatches + token names + current label map) for human sign-off.
- `scripts/contrast_check.py` — WCAG + CVD + grayscale palette check; FAIL blocks sign-off.
- `scripts/format_citation.py` — Zotero item JSON → contract-exact `Author et al., YYYY` (or PLACEHOLDER).
- `scripts/academic_mpl.py` — shared matplotlib style (Arial + muted prop-cycle + ink axes) every plot must apply; `condition_color()` maps a named condition to its muted hex.
