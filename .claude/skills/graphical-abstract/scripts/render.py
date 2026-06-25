# /// script
# requires-python = ">=3.10"
# dependencies = ["cairosvg>=2.7", "lxml>=5"]
# ///
"""Render a graphical-abstract SVG to publication-grade PDF + PNG at exact journal size.

Vector source -> vector PDF (fonts crisp) + 300-dpi PNG. Picks the best available renderer:
inkscape -> rsvg-convert -> cairosvg (Python fallback). Runs a best-effort validation pass
(font minima at final size, aspect vs target, oversize warnings) before/after export.

Usage:
    uv run render.py INPUT.svg                         # default: Cell graphical abstract
    uv run render.py INPUT.svg --target nature2 --out figs/
    uv run render.py INPUT.svg --target square --width-px 1200
    uv run render.py INPUT.svg --target custom --width-px 1500 --dpi 600

Targets:
    cell           Cell Press graphical abstract (OFFICIAL): 5.5 in SQUARE @ 300 dpi = 1650 px, Arial 12-16 pt, one panel
    cell_portrait  taller GA (<=1323 x <=1863 px) — only where a venue/use allows portrait; NOT the Cell default
    nature1        Nature single column: 89 mm @ dpi
    nature2        Nature double column: 183 mm @ dpi
    pnas1/15/2     PNAS 1 / 1.5 / 2 column: 87 / 114 / 178 mm @ dpi
    square         1200 x 1200 px universal
    custom         use --width-px / --dpi
"""
import argparse, shutil, subprocess, sys, re
from pathlib import Path

MM = 25.4
TARGETS = {
    # Cell Press graphical abstract — OFFICIAL spec (cell.com GA_guide.pdf): 5.5 in SQUARE @ 300 dpi
    # (= 1650 px), Arial 12-16 pt, ONE single panel.
    "cell":          {"width_mm": 139.7, "max_w_px": 1650, "max_h_px": 1650, "min_font_pt": 9.0, "rec_font_pt": 12.0},
    # Taller portrait GA — only where a venue/use explicitly allows it; NOT the Cell default.
    "cell_portrait": {"width_px": 1200, "max_w_px": 1323, "max_h_px": 1863, "min_font_pt": 9.0, "rec_font_pt": 12.0},
    "nature1": {"width_mm": 89.0,  "min_font_pt": 5.0, "rec_font_pt": 7.0},
    "nature2": {"width_mm": 183.0, "min_font_pt": 5.0, "rec_font_pt": 7.0},
    # PNAS figure column widths (verified): 1-col 8.7cm, 1.5-col 11.4cm, 2-col 17.8cm; max height 22.5cm; text 6-8pt.
    "pnas1":   {"width_mm": 87.0,  "min_font_pt": 6.0, "rec_font_pt": 8.0},
    "pnas15":  {"width_mm": 114.0, "min_font_pt": 6.0, "rec_font_pt": 8.0},
    "pnas2":   {"width_mm": 178.0, "min_font_pt": 6.0, "rec_font_pt": 8.0},
    "square":  {"width_px": 1200, "min_font_pt": 8.0, "rec_font_pt": 12.0},
    "custom":  {"min_font_pt": 5.0, "rec_font_pt": 8.0},
}

def get_viewbox(svg_path):
    txt = Path(svg_path).read_text()
    m = re.search(r'viewBox\s*=\s*"([\d.\s\-]+)"', txt)
    if m:
        p = [float(x) for x in m.group(1).split()]
        if len(p) == 4:
            return p[2], p[3], txt
    wm = re.search(r'width\s*=\s*"(\d+)', txt); hm = re.search(r'height\s*=\s*"(\d+)', txt)
    return (float(wm.group(1)) if wm else 1000.0), (float(hm.group(1)) if hm else 1000.0), txt

def collect_font_sizes(svg_text):
    return [float(x) for x in re.findall(r'font-size\s*=\s*"(\d+(?:\.\d+)?)', svg_text)] + \
           [float(x) for x in re.findall(r'font-size:\s*(\d+(?:\.\d+)?)', svg_text)]

def validate(svg_path, width_px, dpi, t):
    vb_w, vb_h, txt = get_viewbox(svg_path)
    out_h = width_px * vb_h / vb_w
    scale = width_px / vb_w                       # user-units -> output px
    issues = []
    sizes = collect_font_sizes(txt)
    if sizes:
        rendered_px = min(sizes) * scale          # smallest text, in final raster px
        if "width_mm" in t:
            # physical target (Nature): convert to true pt and check the pt floor
            min_pt = rendered_px * 72.0 / dpi
            if min_pt < t["min_font_pt"]:
                issues.append(f"FAIL font: smallest text ~{min_pt:.1f} pt < hard min {t['min_font_pt']} pt at final size")
            elif min_pt < t.get("rec_font_pt", 0):
                issues.append(f"warn font: smallest text ~{min_pt:.1f} pt < recommended {t['rec_font_pt']} pt")
        else:
            # pixel target (Cell/square): no fixed physical size -> check legibility as a fraction of width
            floor = width_px * 0.020; rec = width_px * 0.028
            if rendered_px < floor:
                issues.append(f"FAIL font: smallest text ~{rendered_px:.0f}px ({rendered_px/width_px*100:.1f}% of width) < {floor:.0f}px floor — enlarge it")
            elif rendered_px < rec:
                issues.append(f"warn font: smallest text ~{rendered_px:.0f}px ({rendered_px/width_px*100:.1f}% of width) < {rec:.0f}px recommended")
    # oversize (Cell)
    if t.get("max_w_px") and width_px > t["max_w_px"]:
        issues.append(f"FAIL size: width {width_px}px > journal max {t['max_w_px']}px")
    if t.get("max_h_px") and out_h > t["max_h_px"]:
        issues.append(f"FAIL size: height {out_h:.0f}px > journal max {t['max_h_px']}px (shorten the abstract)")
    return vb_w, vb_h, out_h, issues

def render_inkscape(inp, pdf, png, w):
    subprocess.run(["inkscape", str(inp), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
    subprocess.run(["inkscape", str(inp), "--export-type=png", f"--export-width={int(w)}", f"--export-filename={png}"], check=True, capture_output=True)

def render_rsvg(inp, pdf, png, w):
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(pdf), str(inp)], check=True, capture_output=True)
    subprocess.run(["rsvg-convert", "-w", str(int(w)), "-f", "png", "-o", str(png), str(inp)], check=True, capture_output=True)

def render_cairosvg(inp, pdf, png, w):
    import cairosvg
    cairosvg.svg2pdf(url=str(inp), write_to=str(pdf))
    cairosvg.svg2png(url=str(inp), write_to=str(png), output_width=int(w))

def main():
    ap = argparse.ArgumentParser(description="Render a graphical-abstract SVG to PDF+PNG at exact journal size.")
    ap.add_argument("input", help="input SVG")
    ap.add_argument("--target", choices=list(TARGETS), default="cell")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--width-px", type=int, default=None, help="override raster width (px)")
    ap.add_argument("--renderer", choices=["auto","inkscape","rsvg","cairosvg"], default="auto")
    ap.add_argument("--force", action="store_true", help="render even if hard validation FAILs are present")
    args = ap.parse_args()

    inp = Path(args.input).resolve()
    if not inp.exists(): sys.exit(f"no such file: {inp}")
    t = TARGETS[args.target]
    if args.width_px: width_px = args.width_px
    elif "width_px" in t: width_px = t["width_px"]
    elif "width_mm" in t: width_px = round(t["width_mm"] / MM * args.dpi)
    else: sys.exit("custom target needs --width-px")

    vb_w, vb_h, out_h, issues = validate(inp, width_px, args.dpi, t)
    print(f"[plan] target={args.target} viewBox={vb_w:.0f}x{vb_h:.0f} -> raster {width_px}x{out_h:.0f}px @ {args.dpi}dpi")
    for i in issues: print(f"[validate] {i}")
    if any(i.startswith("FAIL") for i in issues):
        if not args.force:
            sys.exit("[validate] hard failures above — fix the SVG/target, or pass --force to render anyway.")
        print("[validate] hard failures above — rendering anyway (--force).")

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    stem = inp.stem
    pdf = outdir / f"{stem}.pdf"; png = outdir / f"{stem}.png"

    order = {"auto": ["inkscape","rsvg","cairosvg"], "inkscape": ["inkscape"], "rsvg": ["rsvg"], "cairosvg": ["cairosvg"]}[args.renderer]
    avail = {"inkscape": shutil.which("inkscape"), "rsvg": shutil.which("rsvg-convert"), "cairosvg": True}
    last = None
    for r in order:
        if not avail.get(r): continue
        try:
            print(f"[render] using {r}")
            {"inkscape": render_inkscape, "rsvg": render_rsvg, "cairosvg": render_cairosvg}[r](inp, pdf, png, width_px)
            print(f"[done] {pdf}\n[done] {png}")
            return
        except Exception as e:
            last = e; print(f"[render] {r} failed: {e}")
    sys.exit(f"all renderers failed (last: {last})")

if __name__ == "__main__":
    main()
