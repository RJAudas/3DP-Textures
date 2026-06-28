# Phase 0 Research: How We Will Produce the Options Document

**Feature**: Texture-to-Geometry Approaches Research | **Date**: 2026-06-28

This file resolves the *planning* unknowns for **how** the research is conducted and how the
two deliverable surfaces (agent Markdown + user HTML) are produced. It is **not** the
deliverable document — that is authored under `deliverables/` during `/speckit.implement`.

There were no `NEEDS CLARIFICATION` markers in Technical Context; the spec's three
clarifications (texture source, local-vs-web weighting, preset-vs-advanced UX) are already
resolved. The decisions below cover method and tooling.

---

## Decision 1 — Deliverable shape: authored Markdown + generated HTML

- **Decision**: Author all content as focused Markdown files under `deliverables/` (single
  source of truth) and generate the user-facing HTML review page from a curated
  `summary.md`. Markdown is what agents read; HTML is what the owner reviews.
- **Rationale**: The user asked for both surfaces. One authored source + one generated
  surface prevents the two from drifting and keeps editing in plain Markdown.
- **Alternatives considered**:
  - *Author HTML by hand* — rejected: duplicate maintenance and guaranteed drift.
  - *Single combined HTML of everything* — rejected: the user wants HTML to be **high
    level** for review, while agents want the full detail; separating concerns serves both.

## Decision 2 — HTML generation toolchain: `python-markdown`

- **Decision**: Use Python 3.12 with the `python-markdown` package (extensions: `toc`,
  `tables`, `fenced_code`, `sane_lists`, `admonition`) in `tools/build_docs.py`, wrapping
  output in a minimal embedded CSS template (no external assets, fully offline).
- **Rationale**: Python 3.12 is already installed; `python-markdown` is a single, well-known
  pip dependency, pure-Python, and produces a self-contained styled page. Authoring-only
  tooling — it never ships in the future add-on.
- **Alternatives considered**:
  - *pandoc* — rejected: not installed on this machine; heavier external dependency.
  - *VS Code "Markdown to HTML" / manual export* — rejected: not reproducible/scriptable.
  - *MkDocs/Sphinx static site* — rejected: overkill for a single high-level review page.
- **Verification**: `python --version` → 3.12.10 confirmed present; `pandoc` confirmed
  absent. `python-markdown` will be installed at implement time (`pip install markdown`).

## Decision 3 — Research method & source precedence

- **Decision**: Treat local references as authoritative ground truth and consult them first,
  in this precedence: (1) reference TOC `D:\dev\blender\blender-plugin-reference-toc.md` as
  the map, (2) Blender manual `D:\dev\blender\blender-manual` for concepts/behavior, (3)
  Blender source `D:\dev\blender\blender` for ground-truth API/behavior. Use the web only to
  *supplement* — specifically to discover how others texture for 3D printing and what add-ons
  exist — and cite every web claim with a re-findable URL.
- **Rationale**: Matches the spec clarification (local primary, web supplemental, web focused
  on approaches/workflows + prior art, not code). The TOC already maps the highest-value
  files, minimizing search effort.
- **Alternatives considered**:
  - *Web-first* — rejected by clarification (accuracy risk, code-level noise).
  - *Local-only* — rejected: would miss community workflows and existing-add-on prior art the
    user specifically wants.

## Decision 4 — Which geometry approaches to investigate (research backlog)

Authoritative anchors come from the reference TOC. The document must cover ≥2 (target 3+):

| Candidate approach | Texture source(s) | Primary local anchors to mine |
|--------------------|-------------------|-------------------------------|
| Displace modifier + procedural Texture datablock over subdivided mesh | Procedural (Wood/Noise/Voronoi); image height-map | `manual/modeling/modifiers/deform/displace.rst`; `source/.../modifiers/intern/MOD_displace.cc`; `rna_modifier.cc`; `DNA_texture_types.h`; `rna_texture.cc` |
| Image/height-map displacement (UV-driven) | User image / height-map | Displace docs (`texture_coords='UV'`); `texture_coordinate.rst`; STL export docs |
| Geometry Nodes / node-based displacement | Procedural fields; image input | `manual/modeling/modifiers/introduction.rst` (GN as custom modifier); web for GN displacement patterns |
| (Stretch) Sculpt + texture/bake or remesh | Procedural/image | Manual sculpt + web; flagged as heavier/secondary |

- **Decision**: Investigate the first three as serious contenders (Displace-procedural is the
  expected primary per constitution + TOC); document Geometry Nodes as the flexible
  alternative; note sculpt/remesh briefly as a stretch option if web prior art warrants it.
- **Rationale**: Covers the spec's required Displace-over-subdivision and Geometry Nodes
  approaches plus the image-source path the clarification put in scope.

## Decision 5 — Export & non-destructive behavior framing

- **Decision**: Document STL export via `bpy.ops.wm.stl_export` with `apply_modifiers=True`
  as the path that turns a live Displace/GN modifier into real exported geometry, and frame
  "defer-to-export" (keep live modifier) vs. "apply/bake now" accordingly. Anchor claims to
  `io_stl_ops.cc`, `stl_export.cc` (evaluated mesh on apply), and `manual/.../stl.rst`.
- **Rationale**: Directly supports spec FR-007 and the user's "modifier that only applies on
  export" idea; the exporter using the *evaluated* mesh is the mechanism that makes deferral
  work. Upholds Constitution Principle III (non-destructive default).
- **Note for the deliverable**: Blender modifiers are always "live"; there is no special
  "export-only" modifier mode — the effect is simply that an un-applied modifier becomes real
  geometry at export when `apply_modifiers=True`. The document must state this clearly.

## Decision 6 — Citation format (shared by all deliverables)

- **Decision**: Use inline reference tags resolved in `references.md`, each tagged by type:
  `[S]` source path, `[M]` manual path, `[T]` reference TOC entry, `[W]` web URL. Every
  approach's "how it works", every control claim, and every export claim carries ≥1 tag.
- **Rationale**: Satisfies spec FR-010 and SC-003 (100% of major claims cited) and lets a
  later implementer jump straight to the API.

## Decision 7 — Validation approach for a document deliverable

- **Decision**: Validate with (a) a Python completeness checker that asserts each required
  deliverable file and required H2 sections exist and that `approaches.md` entries each
  contain a citation tag; (b) an HTML build smoke check (file exists, non-empty, build exits
  0); (c) a manual review against `quickstart.md` mapped to spec Success Criteria.
- **Rationale**: Gives objective, re-runnable gates appropriate to docs without pretending to
  run Blender (no code exists yet — Constitution Principle V defers to the add-on phase).

---

## Open questions / risks (carried into tasks & the deliverable)

- **R1 (web availability)**: Prior-art/web research depends on network access at implement
  time; if unavailable, the prior-art section ships with a clearly marked "local-only" gap
  and a TODO to revisit. Mitigation: capture findings as they are gathered.
- **R2 (Geometry Nodes depth)**: GN displacement is less documented locally; expect heavier
  reliance on web sources for that approach. Mitigation: cite reputable GN sources; mark
  confidence.
- **R3 (image-source placement)**: UV/coordinate placement on non-flat shapes (cylinder wrap)
  is a known pain point; the document must surface seams/stretching honestly rather than
  imply it is solved.

**Output**: All planning unknowns resolved. Proceed to Phase 1 (data-model, contracts,
quickstart).
