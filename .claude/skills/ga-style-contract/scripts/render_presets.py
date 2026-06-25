#!/usr/bin/env python3
"""Render a comparison of the journal palette presets in palette.json -> presets_compare.png,
so the operator can pick a Nature/Cell-style palette instead of generic blue/orange.

For each preset: the name, a color strip, and a mini regression-style sample (2 conditions +
identity) using that preset's first two colors — to show how it actually reads in a figure.
"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
PAL = json.loads((HERE.parent / "assets" / "palette.json").read_text())
PRE = PAL["journal_presets"]
ink = PAL["structural"]["ink"]["hex"]
neutral = PAL["structural"]["neutral"]["hex"]
names = [k for k in PRE if not k.startswith("_") and k != "active_preset"]

# deterministic sample data (same for every preset)
rng = np.random.default_rng(7)
x = np.linspace(0.4, 1.0, 40); mu = 0.7
y_a = mu + 0.85*(x-mu) + rng.normal(0, .03, x.size)   # shallow regression
y_b = mu + 0.60*(x-mu) + rng.normal(0, .03, x.size)   # stronger regression

plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Arial","Helvetica","DejaVu Sans"],
                     "axes.edgecolor":ink,"text.color":ink,"axes.labelcolor":ink,
                     "xtick.color":ink,"ytick.color":ink})
n = len(names)
fig, axes = plt.subplots(n, 2, figsize=(8.5, 1.5*n), dpi=150,
                         gridspec_kw={"width_ratios":[1.6,1.0], "wspace":0.05, "hspace":0.55})
fig.patch.set_facecolor("white")
fig.suptitle("Journal palette presets — pick one (active = "+PRE.get("active_preset","?")+")",
             x=0.5, y=0.995, fontsize=13, fontweight="bold", color=ink)

for i, key in enumerate(names):
    cols = PRE[key]["colors"]; label = PRE[key].get("_name", key)
    axL, axR = axes[i] if n > 1 else axes
    # color strip
    axL.axis("off")
    axL.text(0, 1.18, f"{key}", fontsize=11, fontweight="bold", family="monospace",
             transform=axL.transAxes, color=ink)
    axL.text(0.16, 1.18, f"— {label}", fontsize=9.5, transform=axL.transAxes, color="#555")
    for j, c in enumerate(cols):
        axL.add_patch(Rectangle((j/len(cols), 0.15), 0.97/len(cols), 0.7, color=c,
                                ec="#ccc", lw=0.4, transform=axL.transAxes))
    # mini sample plot using first two colors + neutral identity
    axR.plot([0.4,1.0],[0.4,1.0], ls="--", lw=1, color=neutral, zorder=1)
    axR.scatter(x, y_a, s=8, color=cols[0], marker="o", alpha=.7, zorder=2)
    axR.scatter(x, y_b, s=8, color=cols[1], marker="^", alpha=.7, zorder=2)
    axR.plot(x, mu+0.85*(x-mu), lw=2.2, color=cols[0])
    axR.plot(x, mu+0.60*(x-mu), lw=2.2, color=cols[1])
    axR.set_xticks([]); axR.set_yticks([])
    for s in ("top","right"): axR.spines[s].set_visible(False)
    axR.set_xlim(0.38,1.02); axR.set_ylim(0.38,1.02)

out = HERE.parent / "assets" / "presets_compare.png"
fig.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
print(f"[presets] wrote {out}")
