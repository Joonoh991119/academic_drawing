# Claude design integration — live preview & iteration via show_widget

How this skill plugs into **Claude's design/visualize tool** so a graphical abstract can be rendered and
iterated *inside the chat* before publication export. This is the "claude design 연동" path.

## The tools
- `mcp__visualize__read_me` — returns the design contract. **Call it once before your first render**, with
  `modules: ["art","diagram"]` (a graphical abstract is part illustration = art, part flow = diagram) and
  `platform: "desktop"`. It defines CSS variables, color classes, viewBox rules, and the SVG setup.
- `mcp__visualize__show_widget` — renders an SVG (or HTML) inline. Pass `widget_code` = the SVG string
  (must start with `<svg`), a snake_case `title` (e.g. `oresti_serial_dependence_abstract`), and
  `loading_messages`. The user sees it in the conversation and can react.

## Preview-SVG dialect (what show_widget wants)
The in-chat preview SVG differs from the publication SVG. Follow these (from the visualize contract):
- **viewBox width is 680, load-bearing.** Use `<svg width="100%" viewBox="0 0 680 H" role="img">` with
  `<title>` + `<desc>` as the first children. Set `H` to the content's bottom + ~20px. For a portrait
  graphical abstract, that means a tall H (e.g. `0 0 680 920`) — center content, keep width 680.
- **Dark-mode-safe color.** Use the pre-built classes for colored elements: `c-blue c-teal c-amber c-green
  c-red c-purple c-coral c-pink c-gray` on `<g>`/shapes (not paths). Text uses classes `t` (14px), `ts`
  (12px), `th` (14px medium). Never hardcode `#333`-style colors (invisible in dark mode) — EXCEPT a true
  "physical-color scene", which must be all-hardcoded with a `prefers-color-scheme` dark variant.
- **Flat only.** No gradients/shadows/blur/glow (they flash during streaming). Sentence case. No emoji; use
  Tabler outline icons (`<i class="ti ti-...">`) only in HTML widgets — in SVG, use this skill's glyphs.
- **Arrow marker** `<defs>` block (see contract) for flow arrows; `fill="none"` on every connector path.
- **One `<svg>` per call.** Replace entirely to revise — never append a second SVG.

## The iteration loop
```
1. read_me(["art","diagram"])            # once, to load the contract
2. build preview SVG from the kit         # 680 viewBox, c-* classes, captions
3. show_widget(svg, title, loading_msgs)  # user sees it inline
4. user feedback → edit the SVG           # move an act, recolor, re-caption
5. show_widget again                       # repeat 3–5 until approved
6. translate to publication dialect → scripts/render.py   # export
```

## Preview ↔ publication translation
Keep ONE conceptual layout; only the dialect changes:

| Aspect | Preview (show_widget) | Publication (render.py) |
|---|---|---|
| viewBox | `0 0 680 H` (width fixed 680) | exact aspect, e.g. `0 0 1100 1500` (Cell portrait) |
| color | CSS classes `c-blue` etc. (auto dark-mode) | concrete hex from `palettes.json` (journal palette) |
| text | classes `t/ts/th` | explicit `font-family`/`font-size` (Arial), embedded on export |
| background | transparent (host provides) | white (`#ffffff`) page |
| output | inline widget | vector PDF + 300-dpi PNG at exact px |

Practical approach: author the **publication SVG** in `assets/` as the source of truth (concrete palette +
Arial + exact viewBox). To preview, produce a quick preview-dialect copy (swap hex→`c-*` classes, viewBox→680,
add `role/title/desc`) and feed it to `show_widget`. `scripts/render.py` consumes the publication SVG directly.
For fast rounds, it's fine to iterate in the preview dialect first, then port the agreed layout to publication.

## When to use which
- **Use show_widget** for: layout brainstorming, getting the user's eye on the arc, quick recolors, "does this
  read in 10 s?" checks — anything conversational and fast.
- **Use render.py** for: the deliverable (exact size, vector, embedded fonts, 300 dpi, validated).
- Don't export until the user has approved a preview — it's cheaper to iterate in the widget.
