# Routing & Review — how much to do, what to review, when

This file exists because the harness was **too eager**: full agent teams, palette sign-offs, and a
three-lens review on every artifact and every iteration — slow, token-heavy, and full of "should I
ask?" hesitation. This is the authoritative spec for **deciding scope**. Read it at the START of any
run, before touching the agent roster. The governing principle:

> **Default to action.** Pick a mode, apply the defaults, produce the artifact. Ask the human only
> at the single confirm gate — never up front, and only about things that change a *hard constraint*
> or that you genuinely cannot infer. A harness that dithers is worse than one that picks a sane
> default and shows its work.

---

## 1. Mode selection (do this first, in Phase 0)

Pick exactly one mode from the request. When unsure, pick **Standard**. Never ask the user which
mode — infer it.

| Mode | Trigger (infer from the request) | What runs |
|------|----------------------------------|-----------|
| **Fast** | input is already structured (a markdown/outline → slides; "just make the pptx"; "즉시/빨리/시간 없으니"; a re-export or recolor) | single builder, **mechanical QC only**, **one** combined quick-look review, **one** human gate at the very end (or none if the user said "skip review"/"just upload") |
| **Standard** (default) | a normal new deliverable from a brief | one builder/team, mechanical QC, **one pass** of the *applicable* reviews (see §3 routing), one human gate per deliverable |
| **Full** | explicitly asked: "thorough", "submission-grade", "review carefully", "for Cell submission", "be rigorous" | team generation, mechanical QC, **all applicable** reviews with up to the iteration caps, live preview, human gate(s) |

Downgrade signals always win: if the user says "skip QC", "just upload", "no time", obey — run the
minimum and finalize. Upgrade only on explicit request.

---

## 2. Don't-ask defaults (kills decision uncertainty)

These are the answers. Use them silently unless the user's message overrides them. Surface the
*resulting* choices at the single human gate, not as questions beforehand.

| Decision | Default — use without asking | Ask only if |
|----------|------------------------------|-------------|
| Palette | the locked `journal_presets.active_preset` (NPG) | the user mentions color / a different journal |
| GA venue + aspect | Cell square (`--target cell`, 1650²) for a GA; 16:9 for slides | the user names a different venue, or a venue's hard size differs and matters |
| `label_map` | infer condition names from the brief; 1–2 conditions → auto-map `cond_a`/`cond_b`, finding → `accent` | >3 conditions, or names are genuinely ambiguous → confirm at the gate (still don't block generation) |
| Citations | resolve from Zotero if reachable; else `[PLACEHOLDER]` | a citation can't resolve AND the user must supply it |
| Slide builder | PPTX (`pptxgenjs`) | the user asks for the web/HTML deck or "both" |
| Figures not supplied | reserve a labeled placeholder | — never fabricate, never block |
| Abbreviations/terms | standard-in-field or user-supplied only; unknown → validate via `csnl-ontology`, else `[PLACEHOLDER]` | a short form is required and unresolved → one inline question at the gate |

**Rule:** an unanswered default is never a reason to pause. Generate with the default, mark anything
uncertain as `[PLACEHOLDER]` or note it for the gate, and keep moving.

---

## 3. Review scope + routing (selective, NOT exhaustive)

The token sink was running every reviewer on every artifact every iteration. Instead, **route by
content and risk**, run each expensive review **once**, and never let cheap fix-loops re-trigger
expensive reviews.

| Check | Cost | Run it… | Scope | Max iters | SKIP when |
|-------|------|---------|-------|-----------|-----------|
| **Mechanical** (overlap_check / pptx_style_lint / render font+size) | cheap, deterministic | **always**, as the hard gate | only the changed artifact | loop until PASS | never (it's the gate) |
| **Equation QC** (`equation_qc.py` + render) | cheap | only if the artifact contains an equation | the equations | until PASS | no equations |
| **Naive / text (Codex)** | $$ (external model) | **once**, on the near-final TEXT | text of the whole artifact, one pass | 1 | Fast mode; pure-layout change; partial re-run that didn't touch text |
| **Logic (Opus)** | $$ | **once**, only if the deliverable makes CLAIMS / shows RESULTS | the claim chain | 1 | a pure schematic/methods figure with no claims; Fast mode; no text change |
| **Design (vision)** | $$ | **once**, on the near-final RENDER | the whole render | 1, +1 only if a must-fix was applied | Fast mode uses the combined quick-look instead |
| **Human gate** | — | **once per deliverable**, at the end | the rendered result + a short findings summary | — | only if the user said "skip"/"just upload" |

### Hard review rules
1. **Reviews run once, on the near-final artifact** — *after* mechanical QC passes. A mechanical
   fix-loop (moving a box to clear an overlap) does **not** re-run Codex/logic/design.
2. **Route by content.** Pure layout/recolor → mechanical only. Text-only slide → naive (+logic if
   it asserts a result). Figure-placeholder slide → design (layout) only, no logic (no claim yet).
   Equation present → equation QC. Don't run a reviewer that has nothing to review.
3. **Partial re-run = changed scope only.** If the user edits one slide/region, re-review *only that
   slide/region*, never the whole deck. Reference the prior review so resolved findings aren't
   re-raised (stable finding IDs = `hash(category+locus)`).
4. **One combined review in Fast mode.** Instead of three agents, one Opus pass that checks
   tone + layout + (if claims) coherence together, on the final render. Cheaper, good enough for
   pre-structured input.
5. **Cap the loop.** Per deliverable: mechanical (until PASS) + at most one pass each of the
   *applicable* expensive reviews + at most one fix iteration on confirmed must-fixes, then the
   human gate. No open-ended review loops. If still not clean, surface the residue to the human.
6. **Cheap before expensive.** Always run the deterministic checks first; they catch most issues for
   ~no tokens, and they shrink what the expensive reviewers must look at.

### Severity → action (don't fix everything)
- **FAIL (mechanical / equation):** hard gate, must fix before proceeding.
- **must-fix (reviewer):** fix once, re-render, done.
- **nice-to-have (reviewer):** record in the gate summary; do **not** spend an iteration on it unless
  the human asks.

---

## 4. Token / time budget

- Fast mode target: **one** generation + mechanical QC + **one** review pass. No teams, no preview.
- Standard target: generation + mechanical QC + the *applicable* one-pass reviews. Expect 0–1 fix
  iterations, then the gate.
- Only Full mode spends on teams, live preview, multi-iteration review — and only when asked.
- If a deliverable is large (e.g. a 13-slide deck), review at the **deck level once** for tone/logic
  and **per-slide only mechanically**; don't run a vision pass on all 13 unless a slide failed
  mechanically or the human flags it.

The measure of success is not "every possible check ran" — it's "the right checks ran on the right
scope, once, and the result is clean." Exhaustiveness is the failure mode this file prevents.
