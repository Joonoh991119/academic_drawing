#!/usr/bin/env python3
"""Render the project palette + current label map to palette_swatch.png for human sign-off.

Reads ../assets/palette.json (relative to this script) and draws:
  - the muted `structural` tokens (name, role, hex),
  - the Okabe-Ito `data_series` strip,
  - the current `label_map` (so the human can confirm condition->color before any deliverable).

Usage:  python3 swatch.py [palette.json] [out.png]
Deps:   matplotlib (confirmed installed).
"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
pal_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "assets" / "palette.json"
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "assets" / "palette_swatch.png"
P = json.loads(pal_path.read_text())

struct = {k: v for k, v in P["structural"].items() if not k.startswith("_")}
series = P["data_series"]["series"]
series_names = P["data_series"]["names"]
# current label map = whatever is in label_map minus the _ keys; fall back to _template
label_map = {k: v for k, v in P["label_map"].items() if not k.startswith("_")}
if not label_map:
    label_map = P["label_map"].get("_template", {})

fig = plt.figure(figsize=(9, 7.5), dpi=150)
fig.patch.set_facecolor("white")
fig.suptitle("Academic_Drawing — project palette  (sign-off)", x=0.06, ha="left",
             fontsize=15, fontweight="bold", color="#1A1A1A")

# --- structural tokens ---
ax = fig.add_axes([0.06, 0.50, 0.88, 0.40]); ax.axis("off")
ax.text(0, 1.02, "structural  (diagrams / layout · ≤5 hues per slide)",
        fontsize=11, fontweight="bold", transform=ax.transAxes)
n = len(struct)
for i, (name, meta) in enumerate(struct.items()):
    y = 1.0 - (i + 1) / (n + 0.5)
    hexv = meta["hex"]
    ax.add_patch(Rectangle((0.0, y), 0.10, 0.9 / (n + 0.5), color=hexv,
                           ec="#cccccc", lw=0.5, transform=ax.transAxes))
    ax.text(0.125, y + 0.45 / (n + 0.5), f"{name}", va="center", fontsize=10,
            fontweight="bold", family="monospace", transform=ax.transAxes)
    ax.text(0.30, y + 0.45 / (n + 0.5), hexv, va="center", fontsize=9,
            family="monospace", color="#555", transform=ax.transAxes)
    ax.text(0.44, y + 0.45 / (n + 0.5), meta["role"], va="center", fontsize=8.5,
            color="#333", transform=ax.transAxes)

# --- data series strip ---
ax2 = fig.add_axes([0.06, 0.30, 0.88, 0.13]); ax2.axis("off")
ax2.text(0, 1.05, "data_series  (plotted data >2 conditions · Okabe-Ito CVD-safe · fixed order)",
         fontsize=11, fontweight="bold", transform=ax2.transAxes)
for i, (hexv, nm) in enumerate(zip(series, series_names)):
    x = i / len(series)
    ax2.add_patch(Rectangle((x, 0.15), 0.95 / len(series), 0.55, color=hexv,
                            ec="#cccccc", lw=0.5, transform=ax2.transAxes))
    ax2.text(x + 0.47 / len(series), -0.05, f"{i}\n{nm}", ha="center", va="top",
             fontsize=8, family="monospace", transform=ax2.transAxes)

# --- label map ---
ax3 = fig.add_axes([0.06, 0.04, 0.88, 0.18]); ax3.axis("off")
title = "label_map  (current)" if any(not k.startswith("_") for k in P["label_map"]) \
        else "label_map  (TEMPLATE — Director must replace with real conditions)"
ax3.text(0, 1.05, title, fontsize=11, fontweight="bold",
         color=("#1A1A1A" if "current" in title else "#B23A48"), transform=ax3.transAxes)
all_hex = {**{k: v["hex"] for k, v in struct.items()}}
for i, (lab, tok) in enumerate(label_map.items()):
    y = 0.78 - i * 0.26
    hexv = all_hex.get(tok, "#000000")
    ax3.add_patch(Rectangle((0.0, y), 0.05, 0.20, color=hexv, ec="#cccccc",
                            lw=0.5, transform=ax3.transAxes))
    ax3.text(0.07, y + 0.10, f"{lab}", va="center", fontsize=10, transform=ax3.transAxes)
    ax3.text(0.45, y + 0.10, f"-> {tok}  ({hexv})", va="center", fontsize=9,
             family="monospace", color="#555", transform=ax3.transAxes)

fig.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
print(f"[swatch] wrote {out_path}")
