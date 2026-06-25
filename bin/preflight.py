#!/usr/bin/env python3
"""Academic_Drawing preflight — one command that tells a new user EXACTLY what's ready and what to
install before running the harness. Run it first on any machine:

    python3 bin/preflight.py

Checks the Python libs, the render/QC binaries, Node + pptxgenjs, and the optional integrations
(Codex, Zotero MCP). Prints a status table + copy-paste install hints. Exit 0 if all REQUIRED
components are present, 1 otherwise. Nothing here mutates the system.
"""
import importlib, shutil, subprocess, sys, os, tempfile
from pathlib import Path

# matplotlib refuses to import cleanly if its config dir isn't writable (read-only HOME / CI);
# point it at a temp dir so the import check reflects "installed", not "HOME writable".
# Defensive: if even temp can't be created (locked-down sandbox), skip — never crash preflight.
try:
    os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mpl-"))
except Exception:
    pass

# (label, kind, check, install hint, required?)
GREEN, RED, YEL, DIM, RST = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

def have_pylib(name):
    try: importlib.import_module(name); return True
    except Exception: return False

def have_bin(name):
    return shutil.which(name) is not None

def have_path(p):
    return Path(p).exists()

def npm_global(pkg):
    try:
        out = subprocess.run(["npm", "ls", "-g", pkg], capture_output=True, text=True, timeout=20).stdout
        return pkg in out
    except Exception:
        return False

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

CHECKS = [
    # REQUIRED — core render + plot + QC
    ("python: matplotlib", lambda: have_pylib("matplotlib"), "pip install matplotlib", True),
    ("python: numpy",      lambda: have_pylib("numpy"),      "pip install numpy", True),
    ("python: lxml",       lambda: have_pylib("lxml"),       "pip install lxml", True),
    ("python: cairosvg",   lambda: have_pylib("cairosvg"),   "pip install cairosvg", True),
    ("svg->png: rsvg-convert", lambda: have_bin("rsvg-convert"), "brew install librsvg", True),
    ("svg->pdf/png: inkscape", lambda: have_bin("inkscape"),     "brew install --cask inkscape", True),
    ("html/svg render: Google Chrome", lambda: have_path(CHROME), "install Google Chrome (.app bundle)", True),
    # REQUIRED for slides
    ("node", lambda: have_bin("node"), "brew install node", True),
    ("npm", lambda: have_bin("npm"), "(ships with node)", True),
    ("node: pptxgenjs (global)", lambda: npm_global("pptxgenjs"), "npm i -g pptxgenjs", True),
    ("pptx lint: python-pptx", lambda: have_pylib("pptx"), "pip install python-pptx", True),
    ("pptx->pdf: LibreOffice soffice", lambda: have_path(SOFFICE), "brew install --cask libreoffice", True),
    ("pdf->jpg: pdftoppm", lambda: have_bin("pdftoppm"), "brew install poppler", True),
    # REQUIRED for equation QC
    ("python: sympy", lambda: have_pylib("sympy"), "pip install sympy", True),
    # RECOMMENDED
    ("python: seaborn", lambda: have_pylib("seaborn"), "pip install seaborn", False),
    ("python: Pillow (image reads)", lambda: have_pylib("PIL"), "pip install pillow", False),
    # OPTIONAL integrations
    ("Codex CLI (independent naive reviewer)", lambda: have_bin("codex"), "see openai-codex plugin", False),
    ("uv (run render.py via PEP723)", lambda: have_bin("uv"), "curl -LsSf https://astral.sh/uv/install.sh | sh", False),
    ("markitdown[pptx] (slide text QA)", lambda: have_pylib("markitdown"), "pip install 'markitdown[pptx]'", False),
]

def main():
    print(f"\n{DIM}Academic_Drawing preflight — {sys.platform}, python {sys.version.split()[0]}{RST}\n")
    req_missing, opt_missing = [], []
    rows = []
    for label, check, hint, required in CHECKS:
        ok = False
        try: ok = bool(check())
        except Exception: ok = False
        tag = "REQ" if required else "opt"
        if ok:
            mark = f"{GREEN}OK  {RST}"
        else:
            mark = f"{RED}MISS{RST}" if required else f"{YEL}miss{RST}"
            (req_missing if required else opt_missing).append((label, hint))
        rows.append(f"  {mark}  {DIM}[{tag}]{RST} {label}" + ("" if ok else f"   {DIM}-> {hint}{RST}"))
    print("\n".join(rows))

    print()
    if req_missing:
        print(f"{RED}REQUIRED missing ({len(req_missing)}):{RST}")
        for l, h in req_missing: print(f"  - {l}: {h}")
    else:
        print(f"{GREEN}All REQUIRED components present.{RST}")
    if opt_missing:
        print(f"{YEL}Optional missing ({len(opt_missing)}) — features degrade gracefully:{RST}")
        for l, h in opt_missing: print(f"  - {l}: {h}")
    print(f"\n{DIM}Note: the Zotero MCP (real citations) is a Claude Code connector, not a CLI — "
          f"enable it in your client; the harness falls back to [PLACEHOLDER] citations without it.{RST}\n")
    sys.exit(1 if req_missing else 0)

if __name__ == "__main__":
    main()
