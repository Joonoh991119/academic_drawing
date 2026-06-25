#!/usr/bin/env python3
"""Shared matplotlib setup for every Academic_Drawing plot — the one place that enforces the
Nature/Cell toned-down look so figures match the diagram and the slides:

  * Arial/Helvetica typography (no silent DejaVu fallback — warns if the real font is missing),
  * the MUTED `data_series` prop-cycle (NOT bright Okabe-Ito),
  * ink-colored axes, top/right spines off, minimal chartjunk,
  * selectable vector text on SVG/PDF export.

Every plot the plot-engineer writes must `apply_style()` first, and map NAMED conditions through
`condition_color()` so the same condition is the same muted hue in the plot, the abstract, and the deck.

Usage:
    import sys; sys.path.insert(0, "<repo>/.claude/skills/ga-style-contract/scripts")
    from academic_mpl import apply_style, condition_color, series_colors
    P = apply_style()                              # sets rcParams, returns the palette dict
    ax.plot(x, y, color=condition_color("low_var_context"), marker="o", label="Low-var")
    ax.plot(x, y, color=condition_color("high_var_context"), marker="^", label="High-var")
"""
import json, sys
from pathlib import Path
import matplotlib
import matplotlib.font_manager as fm

PALETTE = Path(__file__).resolve().parent.parent / "assets" / "palette.json"


def load(palette=PALETTE):
    return json.loads(Path(palette).read_text())


def _real_sans():
    """Return the first of Arial/Helvetica that is actually installed (not a matplotlib fallback)."""
    for fam in ("Arial", "Helvetica", "Helvetica Neue"):
        try:
            p = fm.findfont(fm.FontProperties(family=fam), fallback_to_default=False)
            if p and Path(p).exists():
                return fam
        except Exception:
            pass
    return None


def apply_style(palette=PALETTE):
    """Set the project rcParams (Arial + muted prop-cycle + ink axes). Returns the palette dict."""
    P = load(palette)
    S = P["structural"]
    ink, bg = S["ink"]["hex"], S["bg"]["hex"]
    fam = _real_sans()
    sans = ([fam] if fam else []) + ["Arial", "Helvetica", "DejaVu Sans"]
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": sans,
        "svg.fonttype": "none",        # keep text selectable in exported SVG
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.edgecolor": ink, "axes.labelcolor": ink, "text.color": ink,
        "xtick.color": ink, "ytick.color": ink,
        "axes.facecolor": bg, "figure.facecolor": bg, "savefig.facecolor": bg,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.prop_cycle": matplotlib.cycler(color=P["data_series"]["series"]),
        "legend.frameon": False,
    })
    if fam is None:
        sys.stderr.write("[academic_mpl] WARN: Arial/Helvetica not installed; figure font may look "
                         "generic (DejaVu). Install Arial/Helvetica for the Nature/Cell look.\n")
    return P


def series_colors(palette=PALETTE):
    """The muted categorical series (use in order for unnamed levels)."""
    return load(palette)["data_series"]["series"]


def condition_color(label, palette=PALETTE):
    """Muted hex for a NAMED condition via label_map (so plot color == diagram color).
    Unknown label -> ink (caller should instead take the next series_colors() entry)."""
    P = load(palette)
    lm = {k: v for k, v in P["label_map"].items() if not k.startswith("_")}
    tok = lm.get(label)
    if tok and tok in P["structural"]:
        return P["structural"][tok]["hex"]
    return P["structural"]["ink"]["hex"]


if __name__ == "__main__":
    P = apply_style()
    print("[academic_mpl] font.sans-serif:", matplotlib.rcParams["font.sans-serif"][0])
    print("[academic_mpl] muted series:", P["data_series"]["series"])
    for lab in ("low_var_context", "high_var_context", "adaptive_prior", "veridical"):
        print(f"  condition_color({lab!r}) -> {condition_color(lab)}")
