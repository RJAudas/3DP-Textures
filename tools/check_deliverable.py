#!/usr/bin/env python3
"""Validate the research deliverable set against the validation contract.

Authoring-only tooling for the Texture-to-Geometry Approaches Research feature.
Implements checks C1-C6 from contracts/validation-contract.md (C7 lives in
build_docs.py; C8 is a manual human sign-off). Exits 0 when every check passes,
1 otherwise. Warnings (e.g. defined-but-unused citations) do not fail the run.

Usage::

    python tools/check_deliverable.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FEATURE = REPO_ROOT / "specs" / "001-texture-geometry-research"
DELIV = FEATURE / "deliverables"
HTML = REPO_ROOT / "docs" / "index.html"

CITATION_RE = re.compile(r"\[([SMTW]\d+)\]")

# C2 - required H2 sections per file (from contracts/document-outline.md).
REQUIRED_SECTIONS: "dict[str, list[str]]" = {
    "00-overview.md": ["Purpose & Scope", "Glossary", "Out of Scope"],
    "approaches.md": [
        "Approaches Overview",
        "Comparison Matrix",
        "Recommendation",
        "Subdivision & Print-Scale Guidance",
    ],
    "prior-art.md": ["Community Workflows", "Existing Add-ons / Plugins"],
    "addon-workflow.md": [
        "Proposed User Journey",
        "Controls",
        "Texture Presets",
        "Apply Now vs. Defer to Export",
        "Generalization to Other Shapes",
    ],
    "references.md": ["References"],
    "summary.md": [
        "Recommendation at a Glance",
        "Approaches (Short)",
        "Proposed Workflow (Short)",
        "Open Questions & Next Step",
    ],
}

# C1 - files that must exist and be non-empty.
REQUIRED_FILES = [DELIV / name for name in REQUIRED_SECTIONS] + [HTML]

# C5 - the six required controls (case-insensitive substring match).
REQUIRED_CONTROLS = [
    "texture selection",
    "strength",
    "scale",
    "coordinate",
    "direction",
    "mid-level",
]


class Report:
    def __init__(self) -> None:
        self.failures: "list[str]" = []
        self.warnings: "list[str]" = []

    def fail(self, check: str, msg: str) -> None:
        self.failures.append(f"[{check}] {msg}")

    def warn(self, check: str, msg: str) -> None:
        self.warnings.append(f"[{check}] {msg}")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _h2_sections(text: str) -> "set[str]":
    out = set()
    for line in text.splitlines():
        if line.startswith("## "):
            out.add(line[3:].strip())
    return out


def check_c1(rep: Report) -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            rep.fail("C1", f"missing file: {path.relative_to(REPO_ROOT)}")
        elif not path.read_text(encoding="utf-8").strip():
            rep.fail("C1", f"empty file: {path.relative_to(REPO_ROOT)}")


def check_c2(rep: Report) -> None:
    for name, required in REQUIRED_SECTIONS.items():
        sections = _h2_sections(_read(DELIV / name))
        for heading in required:
            if heading not in sections:
                rep.fail("C2", f"{name} missing required H2 section: '## {heading}'")


def check_c3(rep: Report) -> None:
    text = _read(DELIV / "approaches.md")
    approach_headings = [
        ln for ln in text.splitlines() if ln.startswith("## Approach:")
    ]
    if len(approach_headings) < 2:
        rep.fail(
            "C3",
            f"approaches.md has {len(approach_headings)} '## Approach:' sections (need >= 2)",
        )

    # Each ## Approach: ... block must carry >= 1 citation tag.
    blocks = re.split(r"(?m)^## ", text)
    for block in blocks:
        if block.startswith("Approach:"):
            title = block.splitlines()[0].strip()
            if not CITATION_RE.search(block):
                rep.fail("C3", f"'## {title}' has no citation tag")

    # Recommendation section: exactly one primary, >= 1 fallback.
    rec = _section_body(text, "Recommendation")
    if rec is not None:
        primaries = len(re.findall(r"(?i)\bprimary\b", rec))
        fallbacks = len(re.findall(r"(?i)\bfallback\b", rec))
        if primaries < 1:
            rep.fail("C3", "Recommendation section names no 'primary' approach")
        if fallbacks < 1:
            rep.fail("C3", "Recommendation section names no 'fallback' approach")


def check_c4(rep: Report) -> None:
    references_text = _read(DELIV / "references.md")
    defined = set(CITATION_RE.findall(references_text))
    if not defined:
        rep.fail("C4", "references.md defines no citation tags")

    has_local = any(
        re.search(rf"\[{re.escape(tag)}\][^\n]*\b(source|manual|toc)\b", references_text, re.I)
        for tag in defined
        if tag[0] in ("S", "M", "T")
    )
    if not (any(t[0] in ("S", "M", "T") for t in defined) and has_local):
        rep.fail(
            "C4",
            "references.md must define >= 1 local-authoritative tag (source/manual/toc)",
        )

    used: "set[str]" = set()
    for md_file in sorted(DELIV.glob("*.md")):
        used |= set(CITATION_RE.findall(_read(md_file)))

    undefined = sorted(used - defined)
    if undefined:
        rep.fail("C4", f"citation tags used but not defined in references.md: {undefined}")

    unused = sorted(defined - used)
    if unused:
        rep.warn("C4", f"citation tags defined but unused (warning): {unused}")


def check_c5(rep: Report) -> None:
    body = _section_body(_read(DELIV / "addon-workflow.md"), "Controls") or ""
    low = body.lower()
    for control in REQUIRED_CONTROLS:
        if control not in low:
            rep.fail("C5", f"Controls section missing required control: '{control}'")


def check_c6(rep: Report) -> None:
    text = _read(DELIV / "prior-art.md")
    entries = 0
    for heading in ("Community Workflows", "Existing Add-ons / Plugins"):
        body = _section_body(text, heading) or ""
        # Count entries as ### sub-headings or top-level bullet list items.
        entries += len(re.findall(r"(?m)^### ", body))
        entries += len(re.findall(r"(?m)^[-*] ", body))
    web_cites = len(re.findall(r"\[W\d+\]", text))
    if entries < 2:
        rep.fail("C6", f"prior-art.md has {entries} entries (need >= 2)")
    if web_cites < 2:
        rep.fail("C6", f"prior-art.md has {web_cites} [W] web citations (need >= 2)")


def _section_body(text: str, heading: str) -> "str | None":
    """Return the text of '## heading' up to the next '## ' (or end)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def main() -> int:
    rep = Report()
    check_c1(rep)
    check_c2(rep)
    check_c3(rep)
    check_c4(rep)
    check_c5(rep)
    check_c6(rep)

    for w in rep.warnings:
        print(f"WARN {w}")
    if rep.failures:
        for f in rep.failures:
            print(f"FAIL {f}")
        print(f"\n{len(rep.failures)} check(s) failed.")
        return 1
    print("OK: deliverable validation C1-C6 passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
