<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.0.1
Rationale: PATCH — added a "Reference Materials" section recording the authoritative
local Blender source tree, manual, and add-on reference TOC paths for this project.
No principles changed.

Prior entry:
Version change: TEMPLATE (unversioned) → 1.0.0
Rationale: Initial ratification — all placeholder tokens replaced with concrete,
project-specific principles for a 3D-print texture-to-geometry Blender add-on.

Principles defined:
  - I. Geometry-First, Print-Ready Output
  - II. Native Blender Integration & API Discipline
  - III. Non-Destructive by Default
  - IV. Multiple Strategies Behind One Interface
  - V. Headless, Automated Validation (NON-NEGOTIABLE)

Added sections:
  - Blender Platform & Packaging Standards (replaces [SECTION_2_NAME])
  - Development Workflow & Quality Gates (replaces [SECTION_3_NAME])

Removed sections: none (template placeholders fully populated)

Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no change needed (Constitution Check
    gate references constitution dynamically; gates derived at plan time)
  - .specify/templates/spec-template.md ✅ no principle-specific content to sync
  - .specify/templates/tasks-template.md ✅ no principle-specific content to sync
  - .specify/templates/commands/*.md ⚠ directory not present (skipped)
  - README.md ⚠ not present (skipped)

Follow-up TODOs: none — ratification date set to first authoring date.
-->

# 3DP-Textures Constitution

3DP-Textures is a Blender add-on that converts surface texture concepts (wood grain,
brick, rock, and similar) into real, printable mesh geometry so that exported STL
models carry the texture in the model itself rather than as a render-only material.

## Core Principles

### I. Geometry-First, Print-Ready Output

The add-on MUST modify actual mesh geometry, not just shading or materials. Every
texturing feature MUST produce vertices/faces that survive STL export with
`apply_modifiers=True` (or an explicit bake) and appear in the printed object.

- Material-only / shader-only "textures" are out of scope as deliverables; they MAY
  exist only as previews that are explicitly labeled non-exporting.
- Generated geometry MUST be export-validated: the result SHOULD be manifold
  (watertight) and free of degenerate or zero-area faces wherever the source mesh
  allowed it. The add-on MUST warn the user when it cannot guarantee a printable result.
- Displacement strength, mid-level, and scale defaults MUST be chosen for real-world
  print scale (millimeters), not arbitrary unit values.

Rationale: The entire reason this project exists is that visual textures do not export;
geometry that prints is the single non-negotiable outcome.

### II. Native Blender Integration & API Discipline

The add-on MUST use documented `bpy` APIs and follow Blender add-on/extension
conventions; it MUST NOT monkey-patch Blender internals or depend on private symbols.

- Packaging MUST follow the modern extension format (`blender_manifest.toml` +
  `__init__.py`) targeting the supported Blender baseline (see Platform Standards).
- `register()`/`unregister()` MUST be symmetric and idempotent: every class, property,
  keymap, and UI hook registered MUST be cleanly removed, leaving no residue after
  disable/reload.
- Operators MUST implement a `poll()` guard so they are only available in valid context
  (e.g., an active, selected mesh object), and MUST report user-facing errors via
  `self.report({'ERROR'|'WARNING'|'INFO'}, ...)` rather than raising raw exceptions.
- Geometry generation SHOULD prefer non-destructive primitives Blender already provides
  (the `DISPLACE` modifier, Geometry Nodes) over hand-rolled vertex math, using the
  evaluated depsgraph (`evaluated_get` / `to_mesh`) when real geometry must be read.

Rationale: Following the platform's grain keeps the add-on stable across Blender
releases, installable as a standard extension, and free of "ghost" state on reload.

### III. Non-Destructive by Default

User data MUST be protected. Operations that change geometry MUST be reversible or
preview-based by default, and destructive bakes MUST be explicit and clearly labeled.

- Texturing setups SHOULD default to live modifiers the user can tweak; "Apply"/bake to
  permanent geometry MUST be a separate, deliberate action.
- Every operator that mutates the scene MUST support Blender Undo (`bl_options` includes
  `{'REGISTER', 'UNDO'}`) and MUST NOT delete or overwrite the user's original mesh
  without an explicit opt-in.
- Long or high-poly operations SHOULD provide progress feedback and MUST NOT silently
  freeze the UI without indication.

Rationale: Modelers iterate; the tool must never cost them work, and previews let users
dial in print scale before committing geometry.

### IV. Multiple Strategies Behind One Interface

Texture-to-geometry conversion has several valid approaches (e.g., `DISPLACE` modifier
with procedural textures, Geometry Nodes, image/height-map displacement). The add-on
MUST support more than one strategy and expose them through a consistent UI and naming.

- Each strategy MUST be implemented as a self-contained, independently testable unit
  with a clear, documented purpose — no organizational-only stubs.
- Adding a new strategy MUST NOT require changing existing strategies; shared controls
  (strength, scale, coordinate space, axis/direction) MUST use common property
  definitions so the UX stays uniform.
- Strategy-specific limitations (e.g., "requires UV map", "best on subdivided mesh")
  MUST be surfaced to the user in the UI or via `report`.

Rationale: There is no single best method across object shapes and textures; a pluggable
design lets the project grow coverage without regressions.

### V. Headless, Automated Validation (NON-NEGOTIABLE)

Behavior MUST be verifiable without manual clicking. Tests MUST be runnable headlessly
via `blender --background --python`, and geometry-producing features MUST assert on the
resulting mesh, not merely that an operator ran.

- For each strategy, an automated test MUST: build a known input mesh, run the operator,
  and assert the output changed geometry (e.g., vertex-count or bounds/displacement
  delta) and passes basic print-integrity checks (no NaN coords, no zero-area faces).
- STL export paths MUST be covered by a test that exports and re-reads the file, or
  inspects the evaluated mesh, to confirm the texture is present in exported geometry.
- A change is not "done" until its validation passes; failing or absent validation for
  new geometry behavior blocks merge.

Rationale: Geometry correctness is invisible to a quick glance and easy to break;
automated mesh assertions are the only reliable guard for print-ready output.

## Blender Platform & Packaging Standards

- **Baseline**: Target Blender 4.2 LTS or newer using the extension system. The minimum
  supported version MUST be declared in `blender_manifest.toml` and honored in code
  (no use of APIs newer than the declared minimum without a guarded fallback).
- **Language/Style**: Python only, following PEP 8 and Blender's add-on conventions
  (proper `bl_idname`/`bl_label`, relative imports within the package, `bpy.props` for
  all UI-exposed settings). No third-party runtime dependencies unless bundled per
  Blender extension wheel rules and justified in the plan.
- **UI placement**: Controls live in conventional locations (3D Viewport N-panel and/or
  Properties editor) with tooltips on every operator and property and sensible defaults.
- **Units & scale**: All length-based settings MUST be expressed in scene units suitable
  for 3D printing; the add-on SHOULD respect `use_scene_unit` on export.
- **Performance**: Operations on dense meshes SHOULD remain responsive; expensive work
  SHOULD avoid blocking patterns where Blender offers modal/progress alternatives.

## Development Workflow & Quality Gates

- **Spec Kit flow**: Features follow `speckit.specify` → `speckit.plan` → `speckit.tasks`
  → `speckit.implement`. The `plan.md` Constitution Check gate MUST pass before Phase 0
  research and be re-verified after Phase 1 design.
- **Definition of Done**: A feature is complete only when (1) it produces exporting
  geometry, (2) register/unregister round-trips cleanly, (3) headless validation passes,
  and (4) user-facing errors are reported, not thrown.
- **Reload discipline**: Before marking work done, the add-on MUST install, enable,
  disable, and re-enable in Blender without errors in the console.
- **Complexity**: Any deviation from these principles (extra dependency, destructive-by-
  default behavior, skipped validation) MUST be recorded in the plan's Complexity
  Tracking table with justification and the rejected simpler alternative.

## Reference Materials

The following local resources are authoritative references for research, planning, and
implementation. Plans and specs SHOULD cite them when justifying a technical approach:

- **Blender source tree**: `D:\dev\blender\blender` — C/C++ internals and bundled Python
  (`scripts/templates_py/`, `scripts/addons_core/`, `scripts/startup/bl_ui/`,
  `source/blender/modifiers/`, `source/blender/io/stl/`) for ground-truth API/behavior.
- **Blender manual**: `D:\dev\blender\blender-manual` — user-facing documentation for
  add-ons/extensions, modifiers (Displace), textures, coordinates, and STL export.
- **Add-on reference TOC**: `D:\dev\blender\blender-plugin-reference-toc.md` — a curated
  map of the most relevant source files and manual pages for this project, with the
  rationale for each, plus starter Python snippets (Displace modifier, STL export,
  evaluated-mesh access).

## Governance

This constitution supersedes other practices for the 3DP-Textures add-on. All plans,
tasks, and code reviews MUST verify compliance with the principles above; reviewers MUST
reject changes that violate a MUST without a documented, approved exception.

- **Amendments**: Proposed via a change to this file describing the motivation and
  impact. Amendments MUST update the version, the Last Amended date, and the Sync Impact
  Report, and MUST propagate any required changes to dependent `.specify` templates.
- **Versioning policy** (semantic): MAJOR for backward-incompatible principle removals or
  redefinitions; MINOR for a new principle/section or materially expanded guidance; PATCH
  for clarifications and non-semantic refinements.
- **Compliance review**: At each plan and implement step, confirm the Definition of Done
  and Quality Gates are met. Unjustified complexity or skipped validation is a compliance
  failure that blocks merge. Use the active feature `plan.md` for runtime development
  guidance.

**Version**: 1.0.1 | **Ratified**: 2026-06-28 | **Last Amended**: 2026-06-28
