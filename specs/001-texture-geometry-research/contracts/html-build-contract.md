# Contract: HTML Build (`tools/build_docs.py`)

**Feature**: Texture-to-Geometry Approaches Research

Defines the behavior of the authoring-only build step that renders the user-facing review
page. This is **not** add-on code and never ships with the future Blender extension.

## Inputs

- `specs/001-texture-geometry-research/deliverables/summary.md` (required source).

## Output

- `docs/index.html` — a single, self-contained, styled HTML page.

## Behavior

- Convert `summary.md` to HTML using `python-markdown` with extensions: `toc`, `tables`,
  `fenced_code`, `sane_lists`, `admonition`.
- Wrap the body in an HTML template with **embedded** CSS only (no external stylesheets,
  fonts, JS, or network requests) so the page renders offline by double-click.
- Include a generated title (`3DP-Textures — Approaches Review`), a table of contents (from
  `toc`), and a visible "Generated from summary.md on <date>" footer.
- Be idempotent and re-runnable: overwrites `docs/index.html` cleanly each run.
- Exit non-zero with a clear message if the source file is missing or `markdown` is not
  installed (with the `pip install markdown` hint).

## CLI

```text
python tools/build_docs.py            # builds docs/index.html from summary.md
python tools/build_docs.py --check    # exits 0/1 without writing (used by validation C7)
```

## Constraints

- Pure Python + `markdown` only; no other third-party packages.
- No content authored inside the script — it only transforms `summary.md`. All wording lives
  in Markdown (single source of truth).
- Completes in < 5 seconds.
