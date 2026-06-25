#!/usr/bin/env python3
"""Deterministic text/shape OVERLAP detection for SVG graphical abstracts.

render.py (graphical-abstract) checks font minima + oversize, but NOT whether text collides with
shapes or other text — the user's #1 layout failure. This script fills that gap by measuring the
TRUE rendered geometry: it loads the SVG in headless Google Chrome (the same layout/font engine the
SVG will be viewed in), reads every element's getBoundingClientRect(), and does rectangle-intersection
math. No browser-automation library needed — it uses Chrome's `--dump-dom`, which executes the page's
JS and prints the resulting DOM, from which we recover the measured boxes.

Collision policy (deterministic hard gate vs advisory):
  FAIL  text<->text intersection            (overlapping labels — never intended)
  FAIL  text spills OUT of its container box (text partially crosses a filled shape's edge)
  FAIL  text extends beyond the SVG viewport (clipped)
  WARN  text near a stroked line/arrow/path  (bbox of diagonal strokes is coarse; vision confirms)
  OK    text fully contained in one filled shape (intended label-on-card)

Usage:   python3 overlap_check.py INPUT.svg [--json out.json] [--strict]
Exit:    0 = clean (no FAIL),  2 = FAIL present,  3 = could not measure (Chrome failed)
With --strict, WARNs also cause a nonzero (4) exit.
"""
import argparse, json, re, subprocess, sys, tempfile, os
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MEASURE_JS = r"""
<script>
function run(){
  var svg = document.querySelector('svg');
  if(!svg){ document.title='ERR:no-svg'; return; }
  var root = svg.getBoundingClientRect();
  var out = {root:{x:root.x,y:root.y,w:root.width,h:root.height}, items:[]};
  var els = svg.querySelectorAll('text, rect, circle, ellipse, line, polyline, polygon, path, image, use, tspan');
  for(var i=0;i<els.length;i++){
    var e = els[i];
    var r;
    try { r = e.getBoundingClientRect(); } catch(err){ continue; }
    if(!r || (r.width===0 && r.height===0)) continue;
    var tag = e.tagName.toLowerCase();
    var fill = (e.getAttribute('fill') || getComputedStyle(e).fill || '').trim();
    var stroke = (e.getAttribute('stroke') || getComputedStyle(e).stroke || '').trim();
    var hasFill = fill && fill!=='none' && fill!=='transparent';
    var isText = (tag==='text' || tag==='tspan');
    out.items.push({
      tag: tag, id: e.getAttribute('id')||'', isText: isText, hasFill: hasFill,
      text: isText ? (e.textContent||'').trim().slice(0,60) : '',
      x: r.x-root.x, y: r.y-root.y, w: r.width, h: r.height
    });
  }
  var pre = document.createElement('pre'); pre.id='__bbox__';
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
}
if(document.readyState!=='loading') run(); else document.addEventListener('DOMContentLoaded', run);
</script>
"""

def measure(svg_path):
    svg = Path(svg_path).read_text()
    # wrap the SVG in an HTML page so we can run measuring JS and dump the DOM
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>*{{margin:0}}</style></head><body>{svg}{MEASURE_JS}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html); htmlpath = f.name
    try:
        proc = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             "--virtual-time-budget=4000", "--run-all-compositor-stages-before-draw",
             "--dump-dom", f"file://{htmlpath}"],
            capture_output=True, text=True, timeout=60)
        dom = proc.stdout
    finally:
        os.unlink(htmlpath)
    m = re.search(r'<pre id="__bbox__">(.*?)</pre>', dom, re.S)
    if not m:
        return None
    raw = m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")
    try:
        return json.loads(raw)
    except Exception:
        return None

def inter(a, b):
    """area of intersection of two {x,y,w,h} rects"""
    ix = max(a["x"], b["x"]); iy = max(a["y"], b["y"])
    ax = min(a["x"]+a["w"], b["x"]+b["w"]); ay = min(a["y"]+a["h"], b["y"]+b["h"])
    if ax <= ix or ay <= iy: return 0.0
    return (ax-ix)*(ay-iy)

def contains(outer, inner, pad=0.5):
    return (inner["x"] >= outer["x"]-pad and inner["y"] >= outer["y"]-pad and
            inner["x"]+inner["w"] <= outer["x"]+outer["w"]+pad and
            inner["y"]+inner["h"] <= outer["y"]+outer["h"]+pad)

def area(r): return max(r["w"]*r["h"], 1e-6)

def analyze(data):
    items = data["items"]
    root = data["root"]; root_rect = {"x":0,"y":0,"w":root["w"],"h":root["h"]}
    texts  = [it for it in items if it["isText"] and it["tag"]=="text" and it["text"]]
    shapes = [it for it in items if not it["isText"]]
    findings = []

    # 1) text out of viewport (clipped)
    for t in texts:
        if not contains(root_rect, t, pad=1.0):
            findings.append({"severity":"FAIL","kind":"text-clipped","text":t["text"],
                             "detail":f"text box extends beyond SVG viewport ({root['w']:.0f}x{root['h']:.0f})",
                             "rect":{k:round(t[k],1) for k in ('x','y','w','h')}})

    # 2) text <-> text
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            a, b = texts[i], texts[j]
            ov = inter(a, b)
            if ov > 0.06*min(area(a), area(b)):
                findings.append({"severity":"FAIL","kind":"text-text",
                                 "text":f"{a['text']!r} ⟷ {b['text']!r}",
                                 "detail":f"overlapping labels ({ov/min(area(a),area(b))*100:.0f}% of smaller)",
                                 "rect":{k:round(a[k],1) for k in ('x','y','w','h')}})

    # 3) text <-> shape.  Only TIGHT-bbox shapes hard-fail; COARSE/complex bboxes are advisory
    # because <use> symbols, <image>, <path>, and diagonal <line>s have bounding boxes that
    # overestimate the actual inked area (a caption sitting just under an icon registers as
    # "overlap" with the icon's padded bbox even though nothing visually collides).
    TIGHT  = {"rect", "circle", "ellipse", "polygon"}
    COARSE = {"use", "image", "path", "line", "polyline"}
    for t in texts:
        for s in shapes:
            ov = inter(t, s)
            if ov <= 0: continue
            frac = ov/area(t)
            if contains(s, t, pad=1.5):
                continue  # text fully inside a shape's box = intended label-on-card / on-background
            if s["tag"] in TIGHT and s["hasFill"] and frac > 0.10:
                findings.append({"severity":"FAIL","kind":"text-spill",
                                 "text":t["text"],
                                 "detail":f"text crosses the edge of a filled {s['tag']} ({frac*100:.0f}% of the text box is over/outside it)",
                                 "rect":{k:round(t[k],1) for k in ('x','y','w','h')}})
            elif s["tag"] in COARSE and frac > 0.25:
                findings.append({"severity":"WARN","kind":"text-near-glyph",
                                 "text":t["text"],
                                 "detail":f"text box overlaps a {s['tag']} bbox ({frac*100:.0f}%); bbox is coarse for icons/paths — confirm visually that no inked element collides",
                                 "rect":{k:round(t[k],1) for k in ('x','y','w','h')}})

    fails = [f for f in findings if f["severity"]=="FAIL"]
    warns = [f for f in findings if f["severity"]=="WARN"]
    return {"n_text":len(texts), "n_shape":len(shapes),
            "fail":len(fails), "warn":len(warns),
            "verdict":"FAIL" if fails else ("WARN" if warns else "PASS"),
            "findings":findings}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--json", default=None)
    ap.add_argument("--strict", action="store_true", help="WARNs also fail the gate")
    args = ap.parse_args()

    if not Path(CHROME).exists():
        print(f"[overlap] Chrome not found at {CHROME}", file=sys.stderr); sys.exit(3)
    data = measure(args.input)
    if data is None:
        print("[overlap] could not measure geometry (Chrome dump-dom returned no boxes). "
              "Fallback: render to PNG and use the vision pass.", file=sys.stderr); sys.exit(3)
    rep = analyze(data)
    rep["input"] = str(Path(args.input).resolve())
    out = Path(args.json) if args.json else Path(args.input).with_suffix(".overlap.json")
    out.write_text(json.dumps(rep, indent=2))

    print(f"[overlap] {rep['verdict']}  texts={rep['n_text']} shapes={rep['n_shape']} "
          f"FAIL={rep['fail']} WARN={rep['warn']}  -> {out}")
    for f in rep["findings"]:
        print(f"  [{f['severity']}] {f['kind']}: {f['text']}  — {f['detail']}")
    if rep["fail"] > 0: sys.exit(2)
    if args.strict and rep["warn"] > 0: sys.exit(4)
    sys.exit(0)

if __name__ == "__main__":
    main()
