# Phase 0 Research: Printable Texture Add-on

This document consolidates the technical decisions for the implementation. The texture-to-geometry
strategy questions were already researched in depth in
`specs/001-texture-geometry-research/deliverables/` (an ADR with citations to the local Blender
source and manual); this file records the decisions adopted for this feature, plus the
packaging/testing decisions specific to building the add-on. Source/manual paths are indexed in
`D:\dev\blender\blender-plugin-reference-toc.md`.

There are **no open `NEEDS CLARIFICATION` items** — the single open question (minimum Blender
version) was resolved to **4.2 LTS** in `spec.md` § Clarifications.

---

## Decision 1 — Primary geometry strategy: Displace + procedural Texture (A1)

- **Decision**: Drive a `DISPLACE` modifier from a procedural `Texture` datablock over a mesh
  densified by a `SUBSURF` (Simple) modifier. Displace along **Normal** by default.
- **Rationale**: Smallest, best-documented, fully native path that yields real, manifold,
  printable geometry **without a UV unwrap**; Normal displacement wraps grain cleanly around
  cylinders/curves. Displacement math is ground-truth in the modifier source
  (`source/blender/modifiers/intern/MOD_displace.cc`: `delta = texres.tin − midlevel; delta *=
  strength`).
- **Alternatives considered**:
  - **A2 image/height-map** — kept as the *fallback* strategy (see Decision 2), not primary,
    because it needs a UV unwrap and produces seams/stretching on curved shapes.
  - **A3 Geometry Nodes** — deferred to v2 by design; higher authoring complexity than the MVP
    needs.
  - **A4 Sculpt/multires** — out of scope; manual and non-automatable.
- **Source**: `deliverables/approaches.md` (Recommendation); `deliverables/summary.md`.

## Decision 2 — Fallback strategy: Displace + image/height-map (A2)

- **Decision**: Implement an image/height-map (`TEX_IMAGE`) strategy behind the same interface,
  selectable via the advanced texture picker, using UV (or Generated/Object) coordinates.
- **Rationale**: Satisfies the "supply a custom texture source" requirement (FR-003) and
  Constitution Principle IV (more than one strategy). Reproduces a *specific* real-world surface.
- **Alternatives considered**: Shipping only A1 — rejected because the constitution requires
  >1 strategy and FR-003 requires a custom-source option.
- **Caveat surfaced to user**: warn about UV seams/stretching on curved shapes; prefer procedural
  for cylinders/spheres (edge case in spec).
- **Source**: `deliverables/approaches.md` (A2); `deliverables/addon-workflow.md` (Generalization).

## Decision 3 — Non-destructive default via "defer to export"

- **Decision**: Leave the Subsurf + Displace modifiers **live** by default; realize geometry only
  at export through `apply_modifiers=True`. Provide an explicit, opt-in **"Apply now"** bake.
- **Rationale**: Blender modifiers are always live; there is no "export-only modifier" mode. The
  desired "apply texture only on export" behavior is simply un-applied modifiers + Apply Modifiers
  on export, which writes the *evaluated* mesh. Upholds Constitution Principle III and FR-007/
  FR-014.
- **Alternatives considered**: Bake-on-apply as default — rejected; destructive and costs the user
  their editable source.
- **Source**: `deliverables/addon-workflow.md` (Apply Now vs. Defer);
  `source/blender/io/stl/exporter/stl_export.cc` (uses evaluated mesh when `apply_modifiers`).

## Decision 4 — STL export operator: `bpy.ops.wm.stl_export`

- **Decision**: Export through the native `wm.stl_export` operator with
  `export_selected_objects=True, apply_modifiers=True, use_scene_unit=True`. Add-on provides an
  "Export STL…" button that invokes it on the target object.
- **Rationale**: `wm.stl_export` is the modern C++ STL exporter present from Blender 4.x and stable
  in 4.2 LTS; it exposes `apply_modifiers` and writes the evaluated mesh. Using the native operator
  keeps us API-disciplined (Principle II) and avoids re-implementing STL writing.
- **Alternatives considered**: legacy `export_mesh.stl` add-on operator — rejected; replaced in
  4.x and our baseline is 4.2 LTS. Hand-rolled STL writer — rejected; unnecessary and risky.
- **Source**: `source/blender/editors/io/io_stl_ops.cc`; `blender-manual/.../import_export/stl.rst`;
  reference TOC snippet.

## Decision 5 — Packaging: Blender extension (`blender_manifest.toml`)

- **Decision**: Package as a modern Blender **extension**: a `3dp_textures/` package with
  `blender_manifest.toml` (`schema_version="1.0.0"`, `type="add-on"`,
  `blender_version_min="4.2.0"`, `[permissions].files` for STL/image I/O) and an `__init__.py`
  exposing `register()`/`unregister()`. No legacy `bl_info`.
- **Rationale**: Constitution Platform Standards mandate the extension format on the 4.2 baseline;
  extensions are the supported install path from 4.2 onward.
- **Alternatives considered**: legacy `bl_info` add-on — rejected by constitution; would not list
  on the Extensions platform.
- **Source**: `scripts/addons_core/bl_pkg/example_extension/blender_manifest.toml`;
  `blender-manual/.../extensions/getting_started.rst`, `.../extensions/addons.rst`.

## Decision 6 — Settings storage & registration discipline

- **Decision**: Store user controls in a `SurfaceSettings` `PropertyGroup` attached to
  `bpy.types.Object` (`bpy.props.PointerProperty`). All UI-exposed values use `bpy.props.*`.
  `register()`/`unregister()` register/remove every class, the pointer property, and UI/menu hooks
  symmetrically and idempotently.
- **Rationale**: Per-object storage lets multiple objects keep independent setups and survives
  save/reload. Symmetric registration is a hard constitution gate (Principle II) verified by a
  headless reload test.
- **Alternatives considered**: Scene-level or WindowManager storage — rejected; per-object is the
  natural scope and matches "target object" entity. Module globals — rejected; not persisted, not
  reload-safe.
- **Source**: `scripts/addons_core/io_mesh_uv_layout/__init__.py` (register pattern);
  `scripts/templates_py/addon_add_object.py`.

## Decision 7 — Auto subdivision sizing in real-world mm

- **Decision**: Compute the Subsurf (Simple) level automatically so post-subdivision edge length
  targets ~0.2–0.5 mm, derived from the object's world-space bounding box and base edge count.
  Expose an advanced override.
- **Rationale**: Relief detail is capped by mesh density; tying density to real mm keeps results
  printable and predictable (Constitution Principle I; spec edge cases "coarse base geometry" and
  "detail below printer resolution"). Simple subdivision is documented for exactly this purpose.
- **Alternatives considered**: Fixed subdivision level — rejected; not scale-aware, blocky on large
  objects, wasteful on small ones.
- **Source**: `blender-manual/.../modifiers/deform/displace.rst`; deliverables print-scale guidance
  in `approaches.md`.

## Decision 8 — Printability warnings (guidance, not auto-repair)

- **Decision**: Surface warnings via `self.report({'WARNING'}, ...)` when Strength is large
  relative to the object's smallest dimension/wall, or when pattern detail is finer than a typical
  printer nozzle. Do **not** auto-repair; link users to the 3D-Print Toolbox for watertightness
  validation.
- **Rationale**: FR-013 + spec Assumptions (validation may rely on existing tooling). Keeps MVP
  scope tight while honoring Principle I's "warn when it cannot guarantee a printable result."
- **Alternatives considered**: Bundling/automating mesh repair — rejected for v1 scope; the
  3D-Print Toolbox already does this and is the documented path.
- **Source**: `deliverables/addon-workflow.md` (Generalization caveats); `deliverables/prior-art.md`.

## Decision 9 — Headless test strategy

- **Decision**: A `tests/run_headless.py` entry run via `blender --background --python` builds a
  known mesh (e.g. a cylinder), runs each operator, and asserts on the **evaluated** mesh
  (`evaluated_get`/`to_mesh`): displacement changed bounds/vertex positions beyond a tolerance, no
  NaN coordinates, no zero-area faces. An export test writes an STL and re-reads it to confirm the
  relief is present; a reload test enables/disables/re-enables the extension with no residue.
- **Rationale**: Constitution Principle V (NON-NEGOTIABLE) — geometry correctness is invisible to a
  glance; mesh assertions are the only reliable guard. Done == validation passes.
- **Alternatives considered**: UI/manual testing only — rejected by constitution. `pytest` inside
  Blender — viable later, but a plain headless runner has zero extra dependencies for v1.
- **Source**: Constitution Principle V & Development Workflow; reference TOC evaluated-mesh snippet.

---

## Resolved unknowns summary

| Unknown | Resolution |
|---------|------------|
| Min Blender version | 4.2 LTS (spec Clarifications) |
| Primary vs fallback strategy | A1 procedural primary; A2 image fallback |
| Destructive vs non-destructive | Defer-to-export default; explicit Apply now |
| Export mechanism | Native `wm.stl_export(apply_modifiers=True)` |
| Packaging | Extension (`blender_manifest.toml`), no `bl_info` |
| Settings storage | `PropertyGroup` on `Object` via `PointerProperty` |
| Subdivision sizing | Auto from world-space bbox → ~0.2–0.5 mm edges |
| Printability handling | Warn via `self.report`; link 3D-Print Toolbox |
| Validation | Headless `blender --background --python` mesh assertions |

All Technical Context items are resolved; ready for Phase 1 design.
