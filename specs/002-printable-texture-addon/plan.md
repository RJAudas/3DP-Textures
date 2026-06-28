# Implementation Plan: Printable Texture Add-on (Texture-to-Geometry)

**Branch**: `002-printable-texture-addon` | **Date**: 2026-06-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-printable-texture-addon/spec.md`

## Summary

Build a Blender 4.2 LTS extension that turns a surface texture into **real, printable mesh
geometry**. The add-on adds a 3D-Viewport N-panel that, for the active mesh object, builds a
non-destructive modifier setup — a **Subdivision Surface (Simple)** modifier for density plus a
**Displace** modifier driven by a procedural `Texture` datablock — and exposes six print-aware
controls (Texture selection, Strength in mm, Scale, Coordinate mode, Direction, Mid-level). The
user previews relief live, optionally bakes ("Apply now") or defers (default), and exports an STL
via `bpy.ops.wm.stl_export(apply_modifiers=True)` so the evaluated displaced mesh becomes real
triangles. The MVP ships the **Wood** preset; **Brick**/**Rock** are named extension points.

Technical approach is taken directly from the research deliverables — **Approach A1 (Displace +
procedural Texture)** as primary, **A2 (image/height-map)** as the fallback texture source — see
`specs/001-texture-geometry-research/deliverables/approaches.md` and `addon-workflow.md`. API/
packaging ground-truth comes from the local Blender source/manual indexed in
`D:\dev\blender\blender-plugin-reference-toc.md`.

## Technical Context

**Language/Version**: Python 3.11 (Blender 4.2 LTS bundled interpreter)

**Primary Dependencies**: `bpy` (Blender 4.2 LTS API) only — no third-party runtime dependencies
(per Constitution Platform Standards). Uses native `DISPLACE` + `SUBSURF` modifiers, legacy
`Texture` datablocks (`TEX_WOOD`/`TEX_NOISE`/`TEX_VORONOI`/`TEX_IMAGE`), and the `wm.stl_export`
operator.

**Storage**: N/A. State lives in the Blender scene: a `PropertyGroup` of settings stored on the
object (`bpy.types.Object`) plus the modifier stack and a procedural `Texture` datablock. No files
or DB beyond the user-chosen STL output.

**Testing**: Headless `blender --background --python tests/run_headless.py` (Constitution
Principle V). Tests build a known mesh, run operators, and assert on the **evaluated** mesh
(vertex/bounds/displacement delta, no NaN/zero-area faces) and on a round-tripped exported STL.

**Target Platform**: Blender 4.2 LTS or newer (desktop: Windows/macOS/Linux). Packaged as a
Blender **extension** (`blender_manifest.toml` + `__init__.py`).

**Project Type**: Single Blender extension package (one add-on), with a sibling headless `tests/`
suite. Not a web/mobile project.

**Performance Goals**: Live preview update feels interactive — viewport reflects a control change
within ~1 s on a typical primitive (SC-005). Achieved by relying on Blender's native live modifier
evaluation (no custom per-vertex Python loops on the hot path).

**Constraints**: Non-destructive by default (defer-to-export); length controls expressed in
real-world mm; output should remain manifold for moderate Strength and warn otherwise;
register/unregister must be symmetric and idempotent; no APIs newer than 4.2 without guarded
fallback.

**Scale/Scope**: One panel, ~7 controls, two pluggable strategies (A1 primary, A2 fallback), three
presets (Wood designed; Brick/Rock named), 3 prioritized user stories. Small codebase (~6–9 Python
modules) plus headless tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution v1.0.1. Each principle evaluated against this plan:

| Principle | Gate | Status |
|-----------|------|--------|
| **I. Geometry-First, Print-Ready Output** | Feature MUST produce vertices/faces that survive STL export; mm-scale defaults; warn when not printable | **PASS** — Displace+Subsurf realized via `apply_modifiers=True`; Strength default 0.4 mm; FR-013 + edge cases drive non-printable warnings. Material/shader-only paths excluded. |
| **II. Native Blender Integration & API Discipline** | Documented `bpy` only; extension packaging (`blender_manifest.toml`); symmetric idempotent register; `poll()` guards; `self.report` for errors; prefer native modifiers + evaluated depsgraph | **PASS** — uses `DISPLACE`/`SUBSURF`, `wm.stl_export`, `evaluated_get`/`to_mesh`; operators gated on active mesh; design mandates symmetric register/unregister. |
| **III. Non-Destructive by Default** | Reversible/preview by default; explicit bake; Undo support (`{'REGISTER','UNDO'}`); never overwrite original without opt-in | **PASS** — Defer-to-export is the default (US2/FR-007/FR-014); "Apply now" is explicit; operators register Undo. |
| **IV. Multiple Strategies Behind One Interface** | More than one strategy; self-contained, independently testable; shared property defs; surface strategy limits | **PASS** — A1 (procedural) + A2 (image) implemented behind a common strategy interface and shared `PropertyGroup`; A2 UV-seam limits surfaced (FR-010, edge cases). A3 Geometry Nodes deferred to v2 by design. |
| **V. Headless, Automated Validation (NON-NEGOTIABLE)** | Headless tests; assert on resulting mesh; STL export covered; done == validation passes | **PASS** — `tests/run_headless.py` builds mesh, runs operators, asserts evaluated-mesh delta + integrity, and round-trips an STL. |

Platform & Packaging Standards: PASS (4.2 LTS baseline declared in manifest; Python/PEP 8; N-panel
UI with tooltips; mm units; native modifier performance).

**Result**: All gates PASS. No violations → Complexity Tracking left empty.

## Project Structure

### Documentation (this feature)

```text
specs/002-printable-texture-addon/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature spec (/speckit.specify)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── operators.md     # Operator + property (UI/command) contracts
│   └── stl-export.md    # STL export behavior contract
├── checklists/
│   └── requirements.md  # Spec quality checklist (/speckit.specify)
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
3dp_textures/                     # Blender extension package (extension id: 3dp_textures)
├── blender_manifest.toml         # type="add-on", blender_version_min="4.2.0", permissions.files
├── __init__.py                   # register()/unregister(); wires all submodules
├── properties.py                 # SurfaceSettings PropertyGroup (shared controls) on Object
├── presets.py                    # Preset registry: wood (designed), brick/rock (named stubs)
├── engine/
│   ├── __init__.py               # Strategy interface + registry (build/update/teardown)
│   ├── displace_procedural.py    # Strategy A1 (primary): procedural Texture + Displace + Subsurf
│   └── displace_image.py         # Strategy A2 (fallback): image/height-map via UV/coords
├── operators.py                  # OT_apply_texture, OT_bake (apply now), OT_clear, OT_export_stl
├── ui.py                         # VIEW3D N-panel "Texture → Geometry" + Object-menu entry
└── subdivision.py                # auto subdivision-level calc for target ~0.2–0.5 mm edge length

tests/
├── run_headless.py               # `blender --background --python` entry; discovers + runs tests
├── helpers.py                    # build_test_mesh(), evaluated-mesh assertions, temp STL paths
├── test_register.py              # enable/disable/re-enable leaves no residue (Principle II)
├── test_displace_procedural.py   # A1 changes evaluated geometry; integrity checks (Principle V)
├── test_displace_image.py        # A2 height-map path
└── test_export_stl.py            # export + re-read STL; relief present in exported geometry
```

**Structure Decision**: Single Blender extension package `3dp_textures/` at the repo root (the
project currently has no product source tree — see repository guidance). The `engine/` subpackage
realizes Constitution Principle IV (pluggable strategies behind one UI): `displace_procedural.py`
is the primary A1 strategy and `displace_image.py` the A2 fallback, both implementing the same
interface and sharing `properties.py`. A separate headless `tests/` tree satisfies Principle V and
is excluded from the packaged extension via `blender_manifest.toml` `[build].paths_exclude_pattern`.

## Complexity Tracking

> No Constitution Check violations — table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _(none)_  | _(none)_   | _(none)_                            |
