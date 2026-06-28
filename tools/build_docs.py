#!/usr/bin/env python3
"""Render the curated summary deliverable into a self-contained HTML review page.

Authoring-only tooling for the Texture-to-Geometry Approaches Research feature.
This is NOT add-on code and never ships with the future Blender extension.

Per contracts/html-build-contract.md it transforms ONLY ``summary.md`` into
``docs/index.html`` using python-markdown with an embedded (offline) CSS template.
No content is authored inside this script; all wording lives in the Markdown.

Usage::

    python tools/build_docs.py            # build docs/index.html from summary.md
    python tools/build_docs.py --check    # validate inputs/build without writing (C7)
"""
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = (
    REPO_ROOT
    / "specs"
    / "001-texture-geometry-research"
    / "deliverables"
    / "summary.md"
)
OUTPUT = REPO_ROOT / "docs" / "index.html"
TITLE = "3DP-Textures \u2014 Approaches Review"

MD_EXTENSIONS = ["toc", "tables", "fenced_code", "sane_lists", "admonition"]

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.6; max-width: 880px; margin: 0 auto; padding: 2rem 1.25rem;
  color: #1b1b1b; background: #fdfdfc;
}
h1, h2, h3 { line-height: 1.25; }
h1 { border-bottom: 3px solid #c47f3d; padding-bottom: .3rem; }
h2 { border-bottom: 1px solid #e3ddd3; padding-bottom: .2rem; margin-top: 2rem; }
a { color: #b3631f; }
code, pre { font-family: SFMono-Regular, Consolas, Menlo, monospace; }
pre { background: #f4f0ea; padding: .8rem 1rem; overflow-x: auto; border-radius: 6px; }
code { background: #f4f0ea; padding: .1rem .35rem; border-radius: 4px; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #ddd6cb; padding: .5rem .7rem; text-align: left; vertical-align: top; }
th { background: #f4ede1; }
blockquote { border-left: 4px solid #c47f3d; margin: 1rem 0; padding: .3rem 1rem; background: #faf6ef; }
.toc { background: #faf6ef; border: 1px solid #e3ddd3; border-radius: 6px; padding: .5rem 1rem; }
.toc ul { margin: .3rem 0; }
.admonition { border-left: 4px solid #6a8caf; background: #f1f5f9; padding: .5rem 1rem; margin: 1rem 0; }
.admonition-title { font-weight: 600; margin: 0; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e3ddd3; color: #777; font-size: .9rem; }
@media (prefers-color-scheme: dark) {
  body { color: #e6e1d8; background: #1b1a18; }
  pre, code { background: #2a2824; }
  th { background: #2a2824; }
  blockquote, .toc { background: #232220; border-color: #38352f; }
}
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<main>
<nav class="toc" aria-label="Table of contents">
<strong>Contents</strong>
{toc}
</nav>
{body}
</main>
<footer>Generated from <code>summary.md</code> on {date}.</footer>
</body>
</html>
"""


def _fail(message: str) -> "int":
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def render() -> "str | None":
    """Return the rendered HTML page, or None on a (reported) failure."""
    try:
        import markdown  # noqa: PLC0415  (deferred so --help/errors stay friendly)
    except ImportError:
        _fail(
            "the 'markdown' package is not installed. "
            "Install the authoring dependency with: pip install markdown"
        )
        return None

    if not SUMMARY.is_file():
        _fail(f"source summary not found: {SUMMARY}")
        return None

    text = SUMMARY.read_text(encoding="utf-8")
    if not text.strip():
        _fail(f"source summary is empty: {SUMMARY}")
        return None

    md = markdown.Markdown(extensions=MD_EXTENSIONS, output_format="html5")
    body = md.convert(text)
    toc = getattr(md, "toc", "") or ""
    return PAGE_TEMPLATE.format(
        title=TITLE,
        css=CSS,
        body=body,
        toc=toc,
        date=_dt.date.today().isoformat(),
    )


def main(argv: "list[str]") -> int:
    check_only = "--check" in argv[1:]
    page = render()
    if page is None:
        return 1

    if check_only:
        print("OK: summary.md renders and contains a non-empty body (C7 dry-run).")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"OK: wrote {OUTPUT} ({len(page)} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
