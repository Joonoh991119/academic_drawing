#!/usr/bin/env python3
"""Deterministic WCAG + CVD + grayscale CONTRAST gate for the project palette.

swatch.py renders the palette for a human to *look at*, but a human eyeballing swatches will not
reliably catch (a) text that fails the WCAG 4.5:1 legibility floor, or (b) two condition colors that
collapse onto each other for a color-blind reader or in grayscale print. This script is the
deterministic gate that runs at palette-lock time, before any swatch sign-off, so a palette edit
that breaks legibility or condition-separability is blocked mechanically rather than slipping
through review.

It reads ../assets/palette.json (the single source of truth) and checks two things:

1) TEXT LEGIBILITY (hard gate).  For every text-on-background pair (the `text`/`ink` tokens over the
   `bg`/`paper` backgrounds) it computes the WCAG 2.x relative-luminance contrast ratio and FAILs if
   it is below the AA floor: 4.5:1 for normal text, 3:1 for large text. A failing pair means body
   copy is not legible and must block sign-off.

2) CONDITION SEPARABILITY (advisory gate).  For every condition-vs-condition structural pair that is
   actually used in `label_map` (i.e. the colors the project assigns to distinct experimental
   conditions / the key finding), it computes three separation metrics:
     - CIELAB deltaE (CIE76)            — perceived color difference for a normal-vision reader,
     - a deuteranopia + protanopia simulation, then deltaE in that CVD-simulated space,
     - a grayscale luminance gap         — survives B/W printing?
   If any of these falls below its threshold the pair is "too close to tell apart by color alone".
   Per the style contract that is allowed ONLY if the two conditions ALSO differ by shape / position
   / weight / label — which this script cannot see — so it is a WARN, not a FAIL: it tells the human
   (and the design reviewer) exactly which pairs must lean on a non-color channel.

The accent (#B23A48 crimson) vs cond_a (#3D6E9B blue) pair is the canonical one to watch: the
contract already flags it as deuteranope-confusable, which is *why* accent is always also bold and
labeled.

Deps:  numpy + matplotlib only (both confirmed installed; no extra installs).
Usage: python3 contrast_check.py [palette.json] [--json out.json] [--strict]
Exit:  0 = clean (no FAIL),  2 = FAIL present (blocks swatch sign-off),
       3 = could not run (palette missing / unreadable / malformed),
       4 = WARN present under --strict.
Matches overlap_check.py: graceful-degrade to exit 3 with a clear message; never silently pass.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib.colors as mcolors
except Exception as e:  # numpy / matplotlib genuinely absent -> degrade, don't pass
    print(f"[contrast] missing dependency ({e}); install numpy + matplotlib. "
          "Cannot run the contrast gate — NOT a pass.", file=sys.stderr)
    sys.exit(3)

HERE = Path(__file__).resolve().parent
DEFAULT_PALETTE = HERE.parent / "assets" / "palette.json"

# --- thresholds (WCAG 2.x AA + perceptual separation floors) ---------------------------------
WCAG_NORMAL = 4.5   # AA contrast floor for normal-size text
WCAG_LARGE = 3.0    # AA contrast floor for large text (>=18pt, or >=14pt bold)
DELTAE_MIN = 15.0   # CIE76 deltaE below this = two conditions hard to tell apart by hue/lightness
DELTAE_CVD_MIN = 12.0  # same, after deuteranopia/protanopia simulation (slightly looser: CVD space
                       # is compressed, so a smaller residual deltaE still reads as "separable")
GRAY_GAP_MIN = 0.18    # min difference in relative luminance (0..1) to survive grayscale print

# Which structural tokens are "text" (foreground copy) vs "background" surfaces.
TEXT_TOKENS = ("text", "ink")
BG_TOKENS = ("bg", "paper")


# --- color math -------------------------------------------------------------------------------
def hex_to_rgb(hexv):
    """'#RRGGBB' -> (r, g, b) floats in 0..1."""
    h = hexv.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected #RRGGBB, got {hexv!r}")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _linearize(c):
    """sRGB channel (0..1) -> linear-light (WCAG / CIE transfer function)."""
    c = np.asarray(c, dtype=float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    """WCAG relative luminance Y (0..1) from an sRGB triple (0..1)."""
    r, g, b = _linearize(rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1, rgb2):
    """WCAG contrast ratio (1..21) between two sRGB triples."""
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_lab(rgb):
    """sRGB (0..1) -> CIELAB (D65). Vectorized; rgb is shape (...,3)."""
    rgb = np.asarray(rgb, dtype=float)
    lin = _linearize(rgb)
    # linear sRGB -> XYZ (D65)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T
    # normalize by D65 white point
    white = np.array([0.95047, 1.00000, 1.08883])
    xyz = xyz / white
    # f(t)
    eps = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16.0) / 116.0)
    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return np.stack([L, a, b], axis=-1)


def delta_e76(lab1, lab2):
    """CIE76 deltaE (Euclidean distance in CIELAB)."""
    return float(np.sqrt(np.sum((np.asarray(lab1) - np.asarray(lab2)) ** 2)))


def simulate_cvd(rgb, kind):
    """Simulate dichromatic vision on an sRGB triple (0..1).

    Uses the Brettel/Viénot-style linear projection in LMS space (the standard fixed matrices used
    by Coblis / colorspacious for full dichromacy). `kind` is 'deuteranopia' or 'protanopia'.
    Returns an sRGB triple (0..1), clipped to gamut.
    """
    rgb = np.asarray(rgb, dtype=float)
    lin = _linearize(rgb)
    # linear sRGB -> LMS (Hunt-Pointer-Estevez, normalized to D65), Viénot et al. 1999
    rgb2lms = np.array([[17.8824, 43.5161, 4.11935],
                        [3.45565, 27.1554, 3.86714],
                        [0.0299566, 0.184309, 1.46709]])
    lms = lin @ rgb2lms.T
    if kind == "protanopia":
        # L is reconstructed from M and S
        sim = np.array([[0.0, 2.02344, -2.52581],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0]])
    elif kind == "deuteranopia":
        # M is reconstructed from L and S
        sim = np.array([[1.0, 0.0, 0.0],
                        [0.494207, 0.0, 1.24827],
                        [0.0, 0.0, 1.0]])
    else:
        raise ValueError(f"unknown CVD kind {kind!r}")
    lms_sim = lms @ sim.T
    lms2rgb = np.linalg.inv(rgb2lms)
    lin_sim = lms_sim @ lms2rgb.T
    lin_sim = np.clip(lin_sim, 0.0, 1.0)
    # linear -> sRGB (delinearize) so downstream Lab/luminance stay in sRGB convention
    srgb = np.where(lin_sim <= 0.0031308,
                    lin_sim * 12.92,
                    1.055 * (lin_sim ** (1 / 2.4)) - 0.055)
    return np.clip(srgb, 0.0, 1.0)


# --- palette loading --------------------------------------------------------------------------
def load_palette(path):
    """Read palette.json -> dict, or raise with a clear message (caller maps to exit 3)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"palette not found at {p}")
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        raise ValueError(f"palette.json is not valid JSON: {e}")
    if "structural" not in data:
        raise ValueError("palette.json has no `structural` block")
    return data


def structural_hex(data):
    """{token: '#hex'} for every real structural token (skips _doc/_desc keys)."""
    out = {}
    for k, v in data["structural"].items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and "hex" in v:
            out[k] = v["hex"]
    return out


def active_label_map(data):
    """The condition->token map actually in force (real keys; fall back to _template)."""
    lm = data.get("label_map", {})
    real = {k: v for k, v in lm.items() if not k.startswith("_")}
    if real:
        return real
    return lm.get("_template", {})


# --- checks -----------------------------------------------------------------------------------
def check_text_contrast(struct_hex, findings):
    """WCAG ratio for every text-token over every background-token. FAIL below AA normal floor."""
    n_checked = 0
    for tk in TEXT_TOKENS:
        if tk not in struct_hex:
            continue
        for bk in BG_TOKENS:
            if bk not in struct_hex:
                continue
            n_checked += 1
            ratio = contrast_ratio(hex_to_rgb(struct_hex[tk]), hex_to_rgb(struct_hex[bk]))
            passes_normal = ratio >= WCAG_NORMAL
            passes_large = ratio >= WCAG_LARGE
            if not passes_normal:
                sev = "FAIL"
                if passes_large:
                    detail = (f"WCAG contrast {ratio:.2f}:1 — passes LARGE text ({WCAG_LARGE}:1) "
                              f"but FAILS normal text ({WCAG_NORMAL}:1). Use only at >=18pt / 14pt-bold.")
                else:
                    detail = (f"WCAG contrast {ratio:.2f}:1 — FAILS both normal ({WCAG_NORMAL}:1) "
                              f"and large ({WCAG_LARGE}:1) text. Not legible.")
            else:
                sev = "OK"
                detail = f"WCAG contrast {ratio:.2f}:1 — passes AA normal text ({WCAG_NORMAL}:1)."
            findings.append({
                "severity": sev, "kind": "text-contrast",
                "pair": f"{tk} on {bk}",
                "detail": detail,
                "ratio": round(ratio, 3),
            })
    return n_checked


def check_condition_separation(struct_hex, label_map, findings):
    """For each pair of DISTINCT condition colors used in label_map, measure normal/CVD/grayscale
    separation. WARN if a pair is too close on every channel a colorblind/grayscale reader has."""
    # Resolve label_map to the unique set of {token: hex} that conditions actually map to.
    cond_tokens = []
    for _label, tok in label_map.items():
        if tok in struct_hex and tok not in cond_tokens:
            cond_tokens.append(tok)

    n_checked = 0
    for i in range(len(cond_tokens)):
        for j in range(i + 1, len(cond_tokens)):
            t1, t2 = cond_tokens[i], cond_tokens[j]
            rgb1, rgb2 = hex_to_rgb(struct_hex[t1]), hex_to_rgb(struct_hex[t2])
            n_checked += 1

            # 1) normal-vision perceptual difference
            de = delta_e76(rgb_to_lab(rgb1), rgb_to_lab(rgb2))

            # 2) CVD-simulated difference (take the WORSE of deuteranopia/protanopia)
            de_cvd = {}
            for kind in ("deuteranopia", "protanopia"):
                lab1 = rgb_to_lab(simulate_cvd(rgb1, kind))
                lab2 = rgb_to_lab(simulate_cvd(rgb2, kind))
                de_cvd[kind] = delta_e76(lab1, lab2)
            worst_cvd_kind = min(de_cvd, key=de_cvd.get)
            worst_cvd = de_cvd[worst_cvd_kind]

            # 3) grayscale luminance gap
            gray_gap = abs(relative_luminance(rgb1) - relative_luminance(rgb2))

            # A pair is "weak" if it is too close on the CVD or grayscale channel — those are the
            # channels a color-blind / B&W reader is left with. Normal deltaE is reported for context.
            weak_cvd = worst_cvd < DELTAE_CVD_MIN
            weak_gray = gray_gap < GRAY_GAP_MIN
            weak_normal = de < DELTAE_MIN

            metrics = {
                "deltaE76": round(de, 2),
                "deltaE_cvd_worst": round(worst_cvd, 2),
                "cvd_worst_type": worst_cvd_kind,
                "deltaE_deuteranopia": round(de_cvd["deuteranopia"], 2),
                "deltaE_protanopia": round(de_cvd["protanopia"], 2),
                "grayscale_gap": round(gray_gap, 3),
            }

            if weak_cvd or weak_gray or weak_normal:
                reasons = []
                if weak_normal:
                    reasons.append(f"normal deltaE {de:.1f} < {DELTAE_MIN}")
                if weak_cvd:
                    reasons.append(f"{worst_cvd_kind} deltaE {worst_cvd:.1f} < {DELTAE_CVD_MIN}")
                if weak_gray:
                    reasons.append(f"grayscale gap {gray_gap:.2f} < {GRAY_GAP_MIN}")
                findings.append({
                    "severity": "WARN", "kind": "condition-separation",
                    "pair": f"{t1} vs {t2}",
                    "detail": ("conditions are hard to separate by color alone (" + "; ".join(reasons)
                               + "). Per the contract they MUST also differ by shape / position / "
                                 "weight / label."),
                    "metrics": metrics,
                })
            else:
                findings.append({
                    "severity": "OK", "kind": "condition-separation",
                    "pair": f"{t1} vs {t2}",
                    "detail": (f"separable: deltaE {de:.1f}, worst-CVD ({worst_cvd_kind}) "
                               f"{worst_cvd:.1f}, grayscale gap {gray_gap:.2f}."),
                    "metrics": metrics,
                })
    return n_checked


# --- driver -----------------------------------------------------------------------------------
def analyze(data):
    """Run both gates over a loaded palette dict and assemble the report."""
    struct_hex = structural_hex(data)
    label_map = active_label_map(data)
    findings = []

    n_text = check_text_contrast(struct_hex, findings)
    n_cond = check_condition_separation(struct_hex, label_map, findings)

    fails = [f for f in findings if f["severity"] == "FAIL"]
    warns = [f for f in findings if f["severity"] == "WARN"]
    return {
        "n_text_pairs": n_text,
        "n_condition_pairs": n_cond,
        "fail": len(fails),
        "warn": len(warns),
        "verdict": "FAIL" if fails else ("WARN" if warns else "PASS"),
        "findings": findings,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic WCAG + CVD + grayscale contrast gate over palette.json.")
    ap.add_argument("palette", nargs="?", default=str(DEFAULT_PALETTE),
                    help="path to palette.json (default: ../assets/palette.json next to this script)")
    ap.add_argument("--json", default=None, help="where to write the JSON report")
    ap.add_argument("--strict", action="store_true", help="WARNs also fail the gate (exit 4)")
    args = ap.parse_args()

    try:
        data = load_palette(args.palette)
    except (FileNotFoundError, ValueError) as e:
        print(f"[contrast] could not run: {e}. NOT a pass.", file=sys.stderr)
        sys.exit(3)

    try:
        rep = analyze(data)
    except Exception as e:  # malformed hex, bad structure -> degrade, never silently pass
        print(f"[contrast] could not run: palette contained unreadable color data ({e}). "
              "NOT a pass.", file=sys.stderr)
        sys.exit(3)

    rep["palette"] = str(Path(args.palette).resolve())
    out = Path(args.json) if args.json else Path(args.palette).with_suffix(".contrast.json")
    out.write_text(json.dumps(rep, indent=2))

    print(f"[contrast] {rep['verdict']}  text_pairs={rep['n_text_pairs']} "
          f"condition_pairs={rep['n_condition_pairs']} FAIL={rep['fail']} WARN={rep['warn']}  -> {out}")
    for f in rep["findings"]:
        if f["severity"] == "OK":
            continue  # one-line summary lists only what needs attention
        print(f"  [{f['severity']}] {f['kind']}: {f['pair']}  — {f['detail']}")

    if rep["fail"] > 0:
        sys.exit(2)
    if args.strict and rep["warn"] > 0:
        sys.exit(4)
    sys.exit(0)


if __name__ == "__main__":
    main()
