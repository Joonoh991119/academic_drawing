---
name: slide-rhetoric
description: The CONTENT contract for Academic_Drawing presentation slides — the fixed section template (Background, Research Gap, Main Claim, Experimental Procedure, Hypothesis & Prediction, Metric & Axis, Main Results, Discussion, Summary) plus academic-talk rhetoric rules: action titles, Minto top-down argument flow, restrained tone, "Author et al., YYYY" citations, one annotated exhibit per result, short numeric/equation captions (no full sentences on result figures), and a Conclusions (not Thank-You) close. Use when planning a deck's structure, writing slide titles/bullets, deciding what goes on each slide, or reviewing whether a talk follows the section template and academic register. Read before writing slide text so structure and voice are correct; the pptx skill renders, this skill decides what to say.
---

# Slide Rhetoric — what each slide says, and how

This is the **content** layer for the deck. The `pptx` skill renders; this decides structure and
wording. Pair it with `ga-style-contract` (color/tone/citation) and `overlap-qc` (render check).

## The fixed section template

Every deck follows this skeleton (the user's template). One idea per slide; add slides within a
section rather than crowding one. The graphical abstract (already produced) is reused on the
Experimental-Procedure / overview slide — do not redraw it.

| # | Section | Must contain | Notes |
|---|---------|--------------|-------|
| 1 | **Background** | the prior-work theoretical foundation the study builds on, each claim with a short citation `OO et al., 20xx` | state what is *established*, not everything known |
| 2 | **Research Gap** | the unexplained piece: "*X* is known, but *Y* is not explained" | one sentence; this motivates everything |
| 3 | **Main Claim** | "to address *Y* in the *Z* domain, we propose *W*" | the thesis of the talk; everything downstream connects here |
| 4 | **Experimental Procedure** | block/session-level sequence + the per-trial time-series schematic (Stimulus → mask → delay → response); **reuse the graphical abstract** | this is structure, not results |
| 5 | **Hypothesis & Prediction** | connected to the Main Claim: "if hypothesis *H* holds, then in *result R* we expect *E*" | predictions must be falsifiable and tied to a specific plot |
| 6 | **Metric & Axis** | define the quantitative measure *M*, its equation (render-QC'd), and the plot conventions: what x/y axes are, how color/condition is assigned (from the locked label map) | sets up how to *read* the result plots |
| 7 | **Main Results** | figure + short caption; numbers/short math only, **never full sentences** | one annotated exhibit per slide; the action title carries the takeaway |
| 8 | **Discussion** | interpretation, relation back to the gap/claim, limits, alternatives | this is where prose is allowed |
| 9 | **Summary (+α)** | 3–4 takeaways mirroring claim→evidence; then Conclusions/next-steps — **not** a "Thank You" slide | optional appendix slides after |

Result figures, code-based plots, and PDF-crop regions stay **placeholders** (per `ga-style-contract`
§6) until the real assets exist — reserve the region, label what goes there.

## Rhetoric rules

- **Action titles.** Every slide title is a complete sentence stating the takeaway, not a topic
  label. Not "Results" → "Estimation bias grows with stimulus uncertainty." The title is the
  message; the body is the evidence. (Exception: section dividers.)
- **Minto / top-down.** State the conclusion first, then support it. The audience should get the
  point from the title alone; bullets justify it. Don't build suspense.
- **One exhibit per result slide.** One figure, annotated (arrow/label to the effect that matters).
  Two figures competing for attention halves the message.
- **Result captions: no full sentences.** A result figure's caption is a fragment, a number, or a
  short equation — "*r* = .42, *p* < .01" or "bias ∝ Δθ" — never a sentence. The takeaway lives in
  the action title, not the caption. (Per the user: keep detailed stats out of prose.)
- **Restrained tone, no AI-slop** (see `ga-style-contract` §2). No hype adjectives, no filler
  connectives, no abbreviations you invented. If you need a short form and none is standard or
  user-supplied, surface it to the operator via the Director's inline human gate (one focused,
  prediction-first question) or leave `[PLACEHOLDER: short form TBD]` — do not coin one, and do not
  open an async interview/DM campaign for an in-chat operator.
- **Citations:** `Author et al., YYYY` (see `ga-style-contract` §3), placed small near the claim
  they support, not in a wall.
- **Color discipline:** ≤5 structural colors per slide; the same condition→color map as the abstract
  and the plots (the deck must look like it belongs to the same project).
- **Close with Conclusions**, not thanks: restate claim → key evidence → what's next.

## Bullet hygiene
- ≤6 bullets/slide, ≤2 lines each; the first bullet does not restate the title.
- Parallel grammatical structure across bullets.
- Numbers and terms only from user-supplied material; otherwise `[PLACEHOLDER: …]`.
