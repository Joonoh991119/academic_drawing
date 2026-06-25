#!/usr/bin/env python3
"""Spec-lint for the Academic_Drawing harness — catches the prompt-system bugs an adversarial review
flagged, so they can't regress:
  1. a referenced skill that doesn't exist (not a project skill, not a known external one),
  2. a referenced script/asset path that doesn't resolve,
  3. duplicate ordered-list numbers in a markdown file (sign of rushed editing / ambiguous steps).

    python3 bin/spec_lint.py        # exit 0 clean, 1 if issues

Read-only. Run it before shipping and in CI.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
AGENTS_DIR = ROOT / ".claude" / "agents"

# Skills that may be referenced but live OUTSIDE the repo (Claude Code global / built-in / optional).
EXTERNAL_OK = {
    "scientific-visualization", "pptx", "statistical-analysis", "csnl-ontology",
    "interview", "matplotlib", "seaborn", "plotly", "markitdown", "pdf",
}

def project_skills():
    return {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}

def md_files():
    return sorted(list(AGENTS_DIR.glob("*.md")) + list(SKILLS_DIR.glob("*/SKILL.md"))
                  + list(SKILLS_DIR.glob("*/references/*.md")) + [ROOT/"CLAUDE.md", ROOT/"ARCHITECTURE.md", ROOT/"README.md"])

def check_skill_refs(known):
    """Flag `Load `x`` / `the `x` skill` references to unknown skills."""
    issues = []
    pat = re.compile(r"(?:Load|load|loads)\s+`([a-z][a-z0-9-]{2,})`(?:\s+skill)?|`([a-z][a-z0-9-]{2,})`\s+skill\b")
    for f in md_files():
        if not f.exists(): continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            for m in pat.finditer(line):
                name = m.group(1) or m.group(2)
                if not name or "-" not in name and name not in known and name not in EXTERNAL_OK:
                    continue  # skip single-word non-skill backticks unless clearly a skill
                if name not in known and name not in EXTERNAL_OK:
                    issues.append((f, i, f"references unknown skill `{name}` (not a project skill, not in EXTERNAL_OK)"))
    return issues

def check_script_paths():
    """Flag referenced .py / asset paths under .claude/skills that don't resolve."""
    issues = []
    pat = re.compile(r"(\.claude/skills/[A-Za-z0-9_-]+/(?:scripts|assets)/[A-Za-z0-9_./-]+\.(?:py|svg|json|png))")
    for f in md_files():
        if not f.exists(): continue
        txt = f.read_text()
        for m in set(pat.findall(txt)):
            if not (ROOT / m).exists():
                issues.append((f, 0, f"referenced path does not resolve: {m}"))
    return issues

def check_dup_numbering():
    """Flag duplicate ordered-list numbers within one contiguous list at the same indent."""
    issues = []
    item = re.compile(r"^(\s*)(\d+)\.\s")
    for f in md_files():
        if not f.exists(): continue
        lines = f.read_text().splitlines()
        # group contiguous ordered-list items by indent
        run = {}  # indent -> {num: firstline}
        prev_ol = False
        for i, line in enumerate(lines, 1):
            m = item.match(line)
            if m:
                indent, num = len(m.group(1)), int(m.group(2))
                run.setdefault(indent, {})
                if num in run[indent]:
                    issues.append((f, i, f"duplicate list number '{num}.' (also at line {run[indent][num]}) — renumber"))
                else:
                    run[indent][num] = i
                prev_ol = True
            elif line.strip() == "" and prev_ol:
                pass  # blank line may continue a list
            elif not line.startswith((" ", "\t")) and line.strip():
                run = {}; prev_ol = False  # a non-indented non-list line ends the list
    return issues

def check_bare_script_cmds():
    """Flag bare `python3 scripts/x.py` commands — they only work if cwd==the skill dir. Commands in
    docs must be repo-root-relative (.claude/skills/<skill>/scripts/x.py) so they copy-paste correctly."""
    issues = []
    pat = re.compile(r"python3?\s+scripts/[A-Za-z0-9_./-]+\.py")
    for f in md_files():
        if not f.exists(): continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if pat.search(line):
                issues.append((f, i, "bare 'scripts/…py' command — use repo-root-relative .claude/skills/<skill>/scripts/…py"))
    return issues

def main():
    known = project_skills()
    all_issues = []
    for label, fn in [("skill-ref", check_skill_refs), ("path", check_script_paths),
                      ("bare-path", check_bare_script_cmds), ("numbering", check_dup_numbering)]:
        for f, ln, msg in (fn(known) if fn is check_skill_refs else fn()):
            all_issues.append((label, f, ln, msg))
    if not all_issues:
        print(f"[spec-lint] clean — {len(known)} project skills, all refs/paths/numbering OK")
        sys.exit(0)
    print(f"[spec-lint] {len(all_issues)} issue(s):")
    for label, f, ln, msg in all_issues:
        loc = f"{f.relative_to(ROOT)}:{ln}" if ln else f"{f.relative_to(ROOT)}"
        print(f"  [{label}] {loc}  {msg}")
    sys.exit(1)

if __name__ == "__main__":
    main()
