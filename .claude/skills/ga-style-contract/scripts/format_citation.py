#!/usr/bin/env python3
"""Deterministic Zotero-JSON -> short "Author et al., YYYY" citation formatter.

The Style Contract (SKILL.md §3) requires one at-a-glance attribution form, identical across the
graphical abstract, the slides, and the manuscript. Authoring that string by hand (or letting an LLM
"format" it) is a hallucination risk — wrong year, invented co-author, "et al." where there are two
authors. This script removes the judgement call: it reads a Zotero `get_item_details`-style JSON
record, applies the rules straight from the single source of truth (`assets/palette.json` ->
`citation.rules`), and emits exactly one string. It NEVER hand-fabricates: a record missing a usable
year or any author yields a "[PLACEHOLDER: citation unresolved]" string and a nonzero exit, so a
human (or the `interview` skill) supplies the missing fact instead of the model guessing.

What it does:
  - Counts only creators with creatorType == "author" (editors/translators/contributors ignored).
  - Uses each author's `lastName` as the contract's {First}/{Second} token (matching palette
    examples: "Kim", "Kim & Lee", "Kim et al.").
  - Extracts the year by regex — the FIRST 4-digit run (19xx/20xx) anywhere in the free-form `date`
    field, so "May 5, 2023", "2023-05", and "2023" all resolve to 2023.
  - Picks the rule by author count: 1 -> one_author, 2 -> two_authors, 3+ -> three_plus.

Matches the overlap_check.py gate style: argparse CLI, a JSON report
{verdict, fail, warn, findings:[...]}, a one-line summary, and the same exit-code contract.

Usage:   python3 format_citation.py item.json [--json out.json] [--strict]
         python3 format_citation.py --stdin   < item.json
Exit:    0 = resolved cleanly,  2 = FAIL (citation unresolved -> placeholder emitted),
         3 = could not run (palette/input missing or unreadable),
         4 = WARN under --strict.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PALETTE = HERE.parent / "assets" / "palette.json"
PLACEHOLDER = "[PLACEHOLDER: citation unresolved]"

# A 4-digit year in the plausible publication range, as a whole token (so we don't grab the "20" of
# a day or a 5-digit page id). Anchored on non-digit boundaries rather than \b so "2023-05" works.
YEAR_RE = re.compile(r"(?<!\d)(1[5-9]\d{2}|20\d{2}|21\d{2})(?!\d)")


def load_palette(path):
    """Load palette.json and return its `citation.rules` dict, or raise with a clear message."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"palette not found at {p}")
    data = json.loads(p.read_text())
    cit = data.get("citation")
    if not cit or "rules" not in cit:
        raise KeyError("palette.json has no `citation.rules` block")
    rules = cit["rules"]
    for key in ("one_author", "two_authors", "three_plus"):
        if key not in rules:
            raise KeyError(f"palette.json citation.rules is missing `{key}`")
    return rules


def load_item(args):
    """Read the Zotero item JSON from --stdin or the positional path. Raises on read/parse error."""
    if args.stdin:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("no JSON received on stdin")
        return json.loads(raw)
    if not args.input:
        raise ValueError("no input file given (pass item.json or --stdin)")
    p = Path(args.input)
    if not p.exists():
        raise FileNotFoundError(f"item JSON not found at {p}")
    return json.loads(p.read_text())


def extract_year(date_field):
    """First plausible 4-digit year anywhere in a free-form date string. None if absent."""
    if not date_field:
        return None
    m = YEAR_RE.search(str(date_field))
    return m.group(1) if m else None


def author_lastnames(creators):
    """Surnames of creators whose creatorType == 'author', in order. Editors etc. are excluded.

    Falls back to a lone `name` field (Zotero stores some institutional/single-field authors that
    way) when `lastName` is absent. Blank entries are dropped so they can't masquerade as authors.
    """
    names = []
    for c in (creators or []):
        if (c.get("creatorType") or "").strip().lower() != "author":
            continue
        last = (c.get("lastName") or c.get("name") or "").strip()
        if last:
            names.append(last)
    return names


def format_citation(item, rules):
    """Apply the contract rules. Returns (citation_string, findings, resolved: bool).

    findings is a list of overlap_check-style dicts. resolved is False (-> FAIL) when the record
    lacks a year or any author, in which case the string is the placeholder.
    """
    findings = []
    creators = item.get("creators")
    lastnames = author_lastnames(creators)
    year = extract_year(item.get("date"))

    if not lastnames:
        findings.append({
            "severity": "FAIL", "kind": "no-author",
            "detail": "no creator with creatorType=='author' (editors/translators don't count); "
                      "cannot build a citation — supply the author via the user or Zotero.",
        })
    if not year:
        findings.append({
            "severity": "FAIL", "kind": "no-year",
            "detail": f"no 4-digit year found in date field {item.get('date')!r}; "
                      "will not fabricate a year.",
        })

    if findings:  # missing year or authors -> placeholder, never a guessed string
        return PLACEHOLDER, findings, False

    if len(lastnames) == 1:
        template = rules["one_author"]
        text = template.replace("{First}", lastnames[0]).replace("{YYYY}", year)
    elif len(lastnames) == 2:
        template = rules["two_authors"]
        text = (template.replace("{First}", lastnames[0])
                        .replace("{Second}", lastnames[1])
                        .replace("{YYYY}", year))
    else:
        template = rules["three_plus"]
        text = template.replace("{First}", lastnames[0]).replace("{YYYY}", year)

    return text, findings, True


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic Zotero-JSON -> 'Author et al., YYYY' short citation formatter.")
    ap.add_argument("input", nargs="?", default=None,
                    help="path to a Zotero get_item_details-style JSON file")
    ap.add_argument("--stdin", action="store_true", help="read the item JSON from stdin instead")
    ap.add_argument("--palette", default=str(DEFAULT_PALETTE),
                    help="path to palette.json (default: ../assets/palette.json)")
    ap.add_argument("--json", default=None, help="write the JSON report here")
    ap.add_argument("--strict", action="store_true", help="WARNs also fail the gate (exit 4)")
    args = ap.parse_args()

    # Graceful-degrade like overlap_check: any setup/read failure is exit 3 with a clear message,
    # never a silent pass.
    try:
        rules = load_palette(args.palette)
    except Exception as e:
        print(f"[citation] could not load palette: {e}", file=sys.stderr)
        sys.exit(3)
    try:
        item = load_item(args)
    except Exception as e:
        print(f"[citation] could not read input: {e}", file=sys.stderr)
        sys.exit(3)

    citation, findings, resolved = format_citation(item, rules)

    fails = [f for f in findings if f["severity"] == "FAIL"]
    warns = [f for f in findings if f["severity"] == "WARN"]
    rep = {
        "verdict": "PASS" if resolved else "FAIL",
        "fail": len(fails),
        "warn": len(warns),
        "citation": citation,
        "resolved": resolved,
        "findings": findings,
    }
    if not args.stdin and args.input:
        rep["input"] = str(Path(args.input).resolve())

    if args.json:
        Path(args.json).write_text(json.dumps(rep, indent=2))

    print(f"[citation] {rep['verdict']}  -> {citation!r}  "
          f"FAIL={rep['fail']} WARN={rep['warn']}")
    for f in findings:
        print(f"  [{f['severity']}] {f['kind']}: {f['detail']}")

    if rep["fail"] > 0:
        sys.exit(2)
    if args.strict and rep["warn"] > 0:
        sys.exit(4)
    sys.exit(0)


if __name__ == "__main__":
    main()
