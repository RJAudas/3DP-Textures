# Contract: Deliverable Validation

**Feature**: Texture-to-Geometry Approaches Research

Defines the objective, re-runnable checks that gate "done" for this documentation feature.
These replace software tests (no product code exists yet). Implemented as a small Python
checker invoked from `tools/` during `/speckit.implement`.

## C1 — File presence

All of the following MUST exist and be non-empty:

- `deliverables/00-overview.md`
- `deliverables/approaches.md`
- `deliverables/prior-art.md`
- `deliverables/addon-workflow.md`
- `deliverables/references.md`
- `deliverables/summary.md`
- `docs/index.html` (generated)

## C2 — Required sections

Each file MUST contain the H2 sections marked *(Required)* in
`contracts/document-outline.md`. The checker greps for the exact section headings.

## C3 — Approach completeness

- `approaches.md` MUST contain ≥2 `## Approach:` sections.
- Exactly one approach MUST be labelled the primary recommendation and ≥1 labelled fallback
  (string check in the `## Recommendation` section).
- Each `## Approach:` section MUST contain ≥1 citation tag matching `\[[SMTW]\d+\]`.

## C4 — Citation integrity

- Every citation tag used anywhere in `deliverables/*.md` MUST be defined in `references.md`.
- `references.md` MUST define ≥1 tag of type `source` or `manual` or `toc` (local
  authoritative) — i.e., the document is not web-only.
- No citation tag is defined-but-unused (warning, not failure).

## C5 — Controls coverage

`addon-workflow.md` Controls section MUST mention all six required controls (case-insensitive
substring): texture selection, strength, scale, coordinate, direction, mid-level.

## C6 — Prior-art coverage

`prior-art.md` MUST contain ≥2 prior-art entries combined across "Community Workflows" and
"Existing Add-ons / Plugins" (counted by list items or sub-headings), each with a `[W…]` web
citation.

## C7 — HTML build smoke check

- `tools/build_docs.py` exits 0.
- `docs/index.html` is produced, is non-empty, contains `<html` and the text of the
  `## Recommendation at a Glance` heading.

## C8 — Human review (manual)

A reviewer confirms the spec Success Criteria SC-001…SC-007 using `quickstart.md`. This is a
sign-off step, not automated.

**Pass condition**: C1–C7 pass automatically and C8 is signed off. Any C1–C7 failure blocks
completion.
