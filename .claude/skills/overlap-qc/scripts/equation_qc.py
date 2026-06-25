#!/usr/bin/env python3
"""Deterministic EQUATION gate for LaTeX equations in figures/slides/manuscripts.

The vision pass can read an equation but cannot *prove* it is well-formed or that every symbol
in it is actually defined in the surrounding text — the two most common equation failures in a
paper. This script fills that gap deterministically, the same way overlap_check.py fills the
geometry gap: it MEASURES the equation instead of eyeballing it.

For each equation it runs three checks:
  (1) RENDERABILITY  — matplotlib MathTextParser().parse() fails fast on broken markup
                       (unbalanced braces, unknown commands, bad sub/superscripts).
                       A figure whose mathtext cannot parse will render as a red error box.
  (2) SYMBOL CLOSURE — sympy parse_latex(latex).free_symbols, then assert every free symbol
                       NAME appears in declared_symbols. This is the "every symbol must be
                       defined" rule: an equation that introduces an undefined symbol is a FAIL.
  (3) IDENTITY       — if reference_latex is given, sympy .equals()/simplify proves the two
                       expressions are mathematically identical (catches transcription errors
                       where the rendered equation drifted from the canonical one).

Verdict / severity policy (deterministic hard gate vs advisory), mirroring overlap_check.py:
  FAIL  mathtext cannot parse                 (equation renders as an error box)
  FAIL  free symbol not in declared_symbols   (undefined symbol — the closure rule)
  FAIL  reference_latex identity does not hold (transcription drift)
  WARN  symbol closure ran in REGEX fallback   (sympy/antlr unavailable -> reduced confidence)
  WARN  reference identity inconclusive        (sympy could not decide; needs human/CAS check)
  OK    renders, closed, identity holds

CRITICAL normalization gotcha (handled in normalize_symbol):
  sympy's parse_latex emits braced subscript names, e.g. \\sigma_p -> Symbol('sigma_{p}'), and
  decomposes accent macros, e.g. \\hat{x} -> hat*x (the symbols 'hat' and 'x'). If we compared
  raw names against declared_symbols we'd get false mismatches every time. So BOTH the parsed
  free-symbol names AND the declared_symbols are pushed through one normalizer that strips braces,
  strips accent/format macros (\\hat \\bar \\tilde \\vec \\dot ...), drops the bare accent tokens
  those macros leave behind, and lowercases greek spelled-out names — then we set-diff by NAME.

Graceful degradation (never silently pass), mirroring overlap_check.py:
  - sympy.parsing.latex (or its antlr/lark backend) unavailable  -> fall back to a regex symbol
    extractor; closure still runs but the report is marked reduced_confidence and closure
    findings are WARN, not FAIL.
  - even matplotlib mathtext unavailable                          -> exit 3 (could not run).
  - bad/missing input file                                        -> exit 3.

Usage:   python3 equation_qc.py eqs.json [--json out.json] [--strict]
  eqs.json = [{id, latex, declared_symbols:[...], reference_latex?, invariants?}, ...]
Exit:    0 = clean (no FAIL),  2 = FAIL present,  3 = could not run,  4 = WARN under --strict
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency probing (graceful-degrade like overlap_check's Chrome check)
# ---------------------------------------------------------------------------

# matplotlib mathtext is the MINIMUM dependency. If it is missing we cannot run at all -> exit 3.
try:
    from matplotlib.mathtext import MathTextParser

    _MATHTEXT = MathTextParser("agg")
    HAVE_MATHTEXT = True
    MATHTEXT_ERR = None
except Exception as e:  # pragma: no cover - environment dependent
    _MATHTEXT = None
    HAVE_MATHTEXT = False
    MATHTEXT_ERR = repr(e)

# sympy LaTeX parsing is the PREFERRED symbol-closure / identity engine. If it (or its
# antlr/lark backend) is missing we degrade to a regex extractor and reduced confidence.
try:
    from sympy.parsing.latex import parse_latex
    from sympy.parsing.latex.errors import LaTeXParsingError
    from sympy import simplify

    HAVE_SYMPY = True
    SYMPY_ERR = None
except Exception as e:  # pragma: no cover - environment dependent
    parse_latex = None
    LaTeXParsingError = Exception
    simplify = None
    HAVE_SYMPY = False
    SYMPY_ERR = repr(e)


# ---------------------------------------------------------------------------
# Symbol-name normalization  (THE critical gotcha)
# ---------------------------------------------------------------------------

# Accent / formatting macros that wrap a base symbol. parse_latex turns "\hat{x}" into the
# product hat*x, leaving a bare accent token "hat"; we both strip the macro from declared names
# and drop these bare tokens from parsed free symbols so the two sides line up on the base name.
ACCENT_MACROS = {
    "hat", "bar", "tilde", "vec", "dot", "ddot", "overline", "underline",
    "widehat", "widetilde", "mathbf", "mathrm", "mathcal", "mathbb", "boldsymbol",
    "text", "operatorname", "prime",
}

# Tokens parse_latex can leave behind as standalone free symbols that are NOT real variables
# (the accent macro names above, once \hat{x} -> hat*x). Compared after normalization.
_ACCENT_TOKEN_SET = {m.lower() for m in ACCENT_MACROS}


def normalize_symbol(name):
    """Normalize a symbol NAME (from either declared_symbols or parse_latex.free_symbols)
    to a canonical comparable string.

    Handles:
      - braced subscripts:           sigma_{p}  -> sigma_p ,   \\sigma_p -> sigma_p
      - leading backslash macros:    \\mu       -> mu
      - accent wrappers:             \\hat{x}   -> x   (accent macro stripped, base kept)
      - stray braces / whitespace:   {x}        -> x
      - case:                        Sigma      -> sigma   (greek spelled-out, case-insensitive)

    Returns "" for tokens that are purely an accent macro (e.g. the bare 'hat' that parse_latex
    leaves after decomposing \\hat{x}); callers drop empty results.
    """
    if name is None:
        return ""
    s = str(name).strip()

    # Strip TeX accent/format macros that wrap a base symbol: \hat{x} -> x, \bar{\mu} -> \mu.
    # Repeat to peel nested wrappers like \hat{\tilde{x}}.
    changed = True
    while changed:
        changed = False
        m = re.match(r"^\\?(" + "|".join(sorted(ACCENT_MACROS, key=len, reverse=True)) + r")\s*\{(.*)\}$", s)
        if m:
            s = m.group(2).strip()
            changed = True

    # Drop remaining backslashes (\sigma -> sigma) and all braces (sigma_{p} -> sigma_p).
    s = s.replace("\\", "").replace("{", "").replace("}", "")

    # Collapse any internal whitespace and a trailing/leading underscore noise.
    s = re.sub(r"\s+", "", s).strip("_")

    # A token that was ONLY an accent macro normalizes to that macro word -> treat as empty.
    if s.lower() in _ACCENT_TOKEN_SET:
        return ""

    return s.lower()


def normalize_set(names):
    """Normalize an iterable of names into a set, dropping empties (accent tokens)."""
    out = set()
    for n in names:
        z = normalize_symbol(n)
        if z:
            out.add(z)
    return out


# ---------------------------------------------------------------------------
# Symbol extraction
# ---------------------------------------------------------------------------

# Greek-letter and common macro names we want to KEEP as symbols when regex-extracting.
_GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta",
    "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "pi", "varpi", "rho", "varrho",
    "sigma", "varsigma", "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega",
}

# LaTeX macros that are STRUCTURE/operators, not variables — never count as free symbols.
_NON_SYMBOL_MACROS = {
    "frac", "sqrt", "sum", "prod", "int", "left", "right", "cdot", "times", "div",
    "log", "ln", "exp", "sin", "cos", "tan", "min", "max", "arg", "mathbb", "mathrm",
    "mathbf", "mathcal", "text", "operatorname", "partial", "nabla", "infty", "to",
    "begin", "end", "quad", "qquad", "cdots", "ldots", "approx", "propto", "leq", "geq",
    "neq", "equiv", "sim", "pm", "mp", "in", "forall", "exists", "Pr", "mathbb",
} | ACCENT_MACROS


def free_symbols_sympy(latex):
    """Return the set of NORMALIZED free-symbol names via sympy parse_latex.
    Raises on parse failure so the caller can decide FAIL vs fallback."""
    expr = parse_latex(latex)
    raw = {str(s) for s in expr.free_symbols}
    return normalize_set(raw), expr


def free_symbols_regex(latex):
    """Fallback symbol extractor when sympy is unavailable: pull \\greek / \\macro names and
    single ASCII letters, attaching simple subscripts (\\sigma_p, x_i) so they normalize the same
    way declared symbols do. Coarser than sympy (cannot understand grouping, superscripts on a
    base it treats as separate) but never silently passes — findings become WARN.

    Subscript handling: a base immediately followed by _x or _{xyz} keeps the subscript, e.g.
    \\sigma_p -> sigma_p, x_{ij} -> x_ij. Superscripts (^2) are exponents, never symbols, and are
    stripped first along with structural braces so they don't pollute the letter scan.
    """
    names = set()
    work = latex

    # Drop superscripts (exponents) entirely: a^2, a^{kn} -> a . They are never free symbols.
    work = re.sub(r"\^\s*\{[^{}]*\}", "", work)
    work = re.sub(r"\^\s*[A-Za-z0-9]", "", work)

    # 1) backslash macros, optionally subscripted: \sigma_p, \mu, \hat, \frac ...
    #    capture (macro)(optional _sub) so \sigma_p stays one token.
    for mac, sub in re.findall(r"\\([A-Za-z]+)((?:_\{[^{}]*\}|_[A-Za-z0-9])?)", work):
        if mac in _NON_SYMBOL_MACROS:
            continue
        if mac in _GREEK or len(mac) > 1:
            names.add(mac + sub if sub else mac)

    # 2) bare ASCII letters (optionally subscripted) that are variables: x, y_i, n_{kn} ...
    #    Remove backslash-macro sequences first so macro letters aren't double-counted, but keep
    #    their trailing subscripts attached above.
    stripped = re.sub(r"\\[A-Za-z]+(?:_\{[^{}]*\}|_[A-Za-z0-9])?", " ", work)
    for base, sub in re.findall(r"([A-Za-z])((?:_\{[^{}]*\}|_[A-Za-z0-9])?)", stripped):
        names.add(base + sub if sub else base)

    return normalize_set(names)


# ---------------------------------------------------------------------------
# Per-equation checks
# ---------------------------------------------------------------------------

def check_mathtext(latex):
    """(1) Renderability. Returns (ok, error_message_or_None)."""
    if not HAVE_MATHTEXT:
        return None, "matplotlib mathtext unavailable"
    try:
        # mathtext expects a math string wrapped in $...$. Wrap if the author did not.
        s = latex if latex.strip().startswith("$") else f"${latex}$"
        _MATHTEXT.parse(s)
        return True, None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_identity(latex, reference_latex):
    """(3) Identity vs a canonical reference. Returns ('PASS'|'FAIL'|'INCONCLUSIVE', detail)."""
    if not HAVE_SYMPY:
        return "INCONCLUSIVE", "sympy unavailable; cannot verify identity"
    try:
        a = parse_latex(latex)
        b = parse_latex(reference_latex)
    except Exception as e:
        return "INCONCLUSIVE", f"could not parse for identity: {type(e).__name__}: {e}"

    # If either side is an Eq, compare lhs-rhs difference so "x = a/b" matches "a/b" too.
    def as_expr(z):
        return (z.lhs - z.rhs) if getattr(z, "is_Equality", False) else z

    ea, eb = as_expr(a), as_expr(b)
    try:
        eq = ea.equals(eb)  # robust numeric+symbolic equality; returns True/False/None
        if eq is True:
            return "PASS", "expression matches reference_latex"
        if eq is False:
            # double-check with simplify before declaring a hard mismatch
            if simplify(ea - eb) == 0:
                return "PASS", "expression matches reference_latex (via simplify)"
            return "FAIL", "expression differs from reference_latex"
        # eq is None -> .equals could not decide; try simplify, else inconclusive
        if simplify(ea - eb) == 0:
            return "PASS", "expression matches reference_latex (via simplify)"
        return "INCONCLUSIVE", ".equals() inconclusive; manual/CAS check recommended"
    except Exception as e:
        return "INCONCLUSIVE", f"identity check errored: {type(e).__name__}: {e}"


def check_equation(eq, idx):
    """Run all checks for one equation dict. Returns a list of findings."""
    findings = []
    eid = eq.get("id", f"eq[{idx}]")
    latex = eq.get("latex")
    declared = eq.get("declared_symbols", [])
    ref = eq.get("reference_latex")

    if not latex or not isinstance(latex, str):
        findings.append({"severity": "FAIL", "kind": "no-latex", "id": eid,
                         "detail": "equation has no 'latex' string"})
        return findings

    # (1) Renderability ------------------------------------------------------
    ok, err = check_mathtext(latex)
    if ok is False:
        findings.append({"severity": "FAIL", "kind": "mathtext-parse", "id": eid,
                         "detail": f"matplotlib mathtext cannot parse this markup -> {err}"})
    elif ok is None:
        findings.append({"severity": "WARN", "kind": "mathtext-skip", "id": eid,
                         "detail": err})

    # (2) Symbol closure -----------------------------------------------------
    declared_norm = normalize_set(declared)
    used = None
    closure_severity = "FAIL"          # hard gate when sympy parsed cleanly
    closure_mode = "sympy"
    if HAVE_SYMPY:
        try:
            used, _expr = free_symbols_sympy(latex)
        except Exception as e:
            # sympy installed but THIS equation didn't parse: degrade to regex for closure,
            # and downgrade severity to WARN (we can't be sure of the symbol set).
            used = free_symbols_regex(latex)
            closure_severity = "WARN"
            closure_mode = "regex-after-parse-error"
            findings.append({"severity": "WARN", "kind": "sympy-parse-error", "id": eid,
                             "detail": f"sympy parse_latex failed ({type(e).__name__}: {e}); "
                                       f"symbol closure used regex fallback (reduced confidence)"})
    else:
        used = free_symbols_regex(latex)
        closure_severity = "WARN"
        closure_mode = "regex-no-sympy"

    undefined = sorted(used - declared_norm)
    if undefined:
        findings.append({"severity": closure_severity, "kind": "undefined-symbol", "id": eid,
                         "detail": f"symbol(s) used but NOT in declared_symbols: {undefined} "
                                   f"(declared={sorted(declared_norm)}, used={sorted(used)}, "
                                   f"mode={closure_mode})",
                         "undefined": undefined})

    # (3) Identity -----------------------------------------------------------
    if ref:
        status, detail = check_identity(latex, ref)
        if status == "FAIL":
            findings.append({"severity": "FAIL", "kind": "identity-mismatch", "id": eid,
                             "detail": detail})
        elif status == "INCONCLUSIVE":
            findings.append({"severity": "WARN", "kind": "identity-inconclusive", "id": eid,
                             "detail": detail})

    return findings


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def analyze(eqs):
    findings = []
    for i, eq in enumerate(eqs):
        findings.extend(check_equation(eq, i))

    fails = [f for f in findings if f["severity"] == "FAIL"]
    warns = [f for f in findings if f["severity"] == "WARN"]
    reduced = (not HAVE_SYMPY) or any(
        f["kind"] in ("sympy-parse-error",) for f in findings)
    return {
        "n_eq": len(eqs),
        "fail": len(fails),
        "warn": len(warns),
        "verdict": "FAIL" if fails else ("WARN" if warns else "PASS"),
        "reduced_confidence": bool(reduced),
        "engine": {
            "mathtext": HAVE_MATHTEXT,
            "sympy_latex": HAVE_SYMPY,
            "sympy_error": SYMPY_ERR,
        },
        "findings": findings,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic equation gate: renderability + symbol closure + identity.")
    ap.add_argument("input", help="eqs.json: [{id, latex, declared_symbols:[...], "
                                   "reference_latex?, invariants?}, ...]")
    ap.add_argument("--json", default=None, help="report output path "
                                                 "(default: <input>.equation.json)")
    ap.add_argument("--strict", action="store_true", help="WARNs also fail the gate (exit 4)")
    args = ap.parse_args()

    # Hard prerequisite: matplotlib mathtext. Without it we cannot run -> exit 3 (like overlap).
    if not HAVE_MATHTEXT:
        print(f"[equation] matplotlib mathtext unavailable ({MATHTEXT_ERR}); cannot run. "
              "Fallback: render the figure and use the vision pass.", file=sys.stderr)
        sys.exit(3)

    path = Path(args.input)
    if not path.exists():
        print(f"[equation] input not found: {path}", file=sys.stderr)
        sys.exit(3)
    try:
        eqs = json.loads(path.read_text())
    except Exception as e:
        print(f"[equation] could not parse {path} as JSON: {e}", file=sys.stderr)
        sys.exit(3)
    if not isinstance(eqs, list):
        print(f"[equation] {path} must be a JSON array of equation objects", file=sys.stderr)
        sys.exit(3)
    if not eqs:
        print(f"[equation] {path} is an empty array (no equations to check)", file=sys.stderr)
        sys.exit(3)

    rep = analyze(eqs)
    rep["input"] = str(path.resolve())
    out = Path(args.json) if args.json else path.with_suffix(".equation.json")
    out.write_text(json.dumps(rep, indent=2))

    conf = " [REDUCED CONFIDENCE: sympy/antlr fallback]" if rep["reduced_confidence"] else ""
    print(f"[equation] {rep['verdict']}  eqs={rep['n_eq']} "
          f"FAIL={rep['fail']} WARN={rep['warn']}{conf}  -> {out}")
    for f in rep["findings"]:
        print(f"  [{f['severity']}] {f['kind']} ({f['id']}): {f['detail']}")

    if rep["fail"] > 0:
        sys.exit(2)
    if args.strict and rep["warn"] > 0:
        sys.exit(4)
    sys.exit(0)


if __name__ == "__main__":
    main()
