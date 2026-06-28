---

description: "Task list for Printable Texture Add-on (Texture-to-Geometry)"
---

# Tasks: Printable Texture Add-on (Texture-to-Geometry)

**Input**: Design documents from `specs/002-printable-texture-addon/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/operators.md,
contracts/stl-export.md, quickstart.md

**Tests**: Included as REQUIRED tasks. The feature spec does not request TDD, but the project
**Constitution (Principle V — NON-NEGOTIABLE)** mandates headless, automated mesh-level validation
for every geometry-producing feature and for register/unregister. Test tasks are therefore part of
the Definition of Done, not optional.

**Organization**: Tasks are grouped by user story (US1=P1, US2=P2, US3=P3) for independent
implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 / US2 / US3 (Setup, Foundational, Polish have no story label)
- All paths are repository-root-relative (extension package `3dp_textures/`, headless `tests/`)

## Path Conventions

Per plan.md § Project Structure: extension package at `3dp_textures/` with `engine/` subpackage;
headless test suite at `tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extension skeleton and test harness so everything else can be built and validated.

- [ ] T001 Create the package/dir layout from plan.md § Project Structure: `3dp_textures/`,
  `3dp_textures/engine/`, and `tests/` (empty `__init__.py` in `3dp_textures/` and
  `3dp_textures/engine/` as needed).
- [ ] T002 [P] Create `3dp_textures/blender_manifest.toml` (`schema_version="1.0.0"`,
  `id="3dp_textures"`, `type="add-on"`, `blender_version_min="4.2.0"`, `[permissions].files` for
  STL/image I/O, `[build].paths_exclude_pattern` excluding `tests/`, `__pycache__/`, `.*`).
- [ ] T003 Create `3dp_textures/__init__.py` with skeleton `register()`/`unregister()` that import
  and (un)register submodules in order, with reverse-order teardown (symmetric, idempotent).
- [ ] T004 [P] Create the headless test harness `tests/run_headless.py` (discovers/runs test
  modules, exits non-zero on failure) and `tests/helpers.py` (`build_test_mesh()` cylinder/plane,
  evaluated-mesh assertions, NaN/zero-area-face checks, temp STL path helpers).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared data model, presets, strategy interface, and panel skeleton that ALL user
stories build on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 [P] Implement `SurfaceSettings` `PropertyGroup` in `3dp_textures/properties.py` with all
  fields/defaults/validation from data-model.md (preset, strategy, texture, image, strength_mm,
  scale, coord_mode, direction, mid_level, subdiv_auto, subdiv_level, apply_mode) and the
  `Object.tdp_surface` `PointerProperty` registration helper.
- [ ] T006 [P] Implement the `Preset` registry in `3dp_textures/presets.py`: `wood` fully
  configured (`TEX_WOOD`, strength 0.4 mm, scale 1.0, LOCAL, NORMAL, mid 0.5) plus `brick`/`rock`
  named stub entries.
- [ ] T007 [P] Implement auto subdivision-level calculation in `3dp_textures/subdivision.py`
  (world-space bbox → Simple-subsurf `levels` targeting ~0.2–0.5 mm edge length).
- [ ] T008 Implement the strategy interface + registry in `3dp_textures/engine/__init__.py`
  (`build(obj, settings)`, `update(obj, settings)`, `teardown(obj)` contract; registry keyed by
  `strategy`).
- [ ] T009 Implement the panel skeleton `VIEW3D_PT_texture_to_geometry` in `3dp_textures/ui.py`
  (N-panel tab "Texture → Geometry", disabled-with-hint when no active mesh object).
- [ ] T010 Wire `register()`/`unregister()` in `3dp_textures/__init__.py` to (un)register
  `properties`, `presets`, `engine`, and `ui` (and the `Object.tdp_surface` pointer) symmetrically.
- [ ] T011 [P] Implement `tests/test_register.py`: enable → disable → re-enable leaves no
  `tdp_surface`, registered classes, or menu/panel residue (Constitution Principle II).

**Checkpoint**: Extension installs/enables cleanly with an empty panel; data model + strategy
interface available.

---

## Phase 3: User Story 1 - Turn a texture into a printable STL (Priority: P1) 🎯 MVP

**Goal**: A user selects a mesh, picks the **Wood** preset, sees relief, and exports an STL whose
geometry carries the relief.

**Independent Test**: On a cylinder, apply the Wood preset and export an STL; the re-read STL
contains relief absent from the flat base mesh, and it slices.

### Tests for User Story 1 (REQUIRED — write first, must FAIL before implementation) ⚠️

- [ ] T012 [P] [US1] `tests/test_displace_procedural.py`: after `tdp.apply_texture` (WOOD) on a
  cylinder, the **evaluated** mesh bounds/positions changed beyond tolerance; no NaN coords; no
  zero-area faces.
- [ ] T013 [P] [US1] `tests/test_export_stl.py`: `tdp.export_stl` writes a file whose re-read
  triangle geometry differs from the undisplaced base mesh (relief present → SC-002).

### Implementation for User Story 1

- [ ] T014 [US1] Implement the primary A1 strategy in `3dp_textures/engine/displace_procedural.py`:
  create/update a `3DP Subdivision` (SUBSURF, SIMPLE) + `3DP Displace` (DISPLACE) stack and an
  owned procedural `Texture` datablock; identify own modifiers by `3DP ` name prefix (idempotent,
  no duplicate stacking).
- [ ] T015 [US1] Implement the `tdp.apply_texture` operator in `3dp_textures/operators.py`
  (procedural path): `poll()` on active mesh, read `tdp_surface`, call the A1 strategy via the
  engine registry, compute subdivision when `subdiv_auto`, `bl_options={'REGISTER','UNDO'}`, report
  errors via `self.report`.
- [ ] T016 [US1] Implement the `tdp.export_stl` operator in `3dp_textures/operators.py`: select
  only the target, call `bpy.ops.wm.stl_export(export_selected_objects=True, apply_modifiers=True,
  use_scene_unit=True)`, restore selection, report success/error (contracts/stl-export.md).
- [ ] T017 [US1] Wire the MVP UI in `3dp_textures/ui.py`: Preset selector, Strength (mm), Scale,
  and **Apply Texture** + **Export STL…** buttons with tooltips.
- [ ] T018 [US1] Register the US1 operators in `3dp_textures/__init__.py` register/unregister lists.

**Checkpoint**: MVP complete — Wood preset → relief → STL works end-to-end; T011–T013 pass.

---

## Phase 4: User Story 2 - Adjust and preview before exporting (Priority: P2)

**Goal**: Interactive, non-destructive refinement — change relief depth/pattern with live preview,
revert cleanly, choose Defer vs Apply-now.

**Independent Test**: Apply a texture, change Strength/Scale and see the viewport update, then
Clear/Undo to fully recover the base mesh; exported relief matches the last preview.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T019 [P] [US2] `tests/test_nondestructive.py`: after `tdp.apply_texture` then `tdp.clear`
  (and via Undo), the base mesh vertex count/positions equal the original (SC-006); `tdp.bake`
  realizes geometry and removes `3DP ` modifiers.

### Implementation for User Story 2

- [ ] T020 [US2] Add live-update behavior to `SurfaceSettings` in `3dp_textures/properties.py`:
  `update=` callbacks that re-run the strategy `update()` so Strength/Scale/Mid-level edits refresh
  the live modifier within ~1 s (SC-005).
- [ ] T021 [US2] Implement the `tdp.bake` ("Apply now") operator in `3dp_textures/operators.py`:
  apply `3DP Subdivision` then `3DP Displace`, remove the add-on modifiers, report new vert/face
  counts (state → baked).
- [ ] T022 [US2] Implement the `tdp.clear` operator in `3dp_textures/operators.py`: remove `3DP `
  modifiers + owned texture, restoring the base mesh (state → none).
- [ ] T023 [P] [US2] Implement printability warnings in `3dp_textures/validation.py` (strength vs.
  smallest world-space dimension; detail finer than typical nozzle) surfaced via
  `self.report({'WARNING'})` (FR-013).
- [ ] T024 [US2] Extend `3dp_textures/ui.py`: an Advanced sub-section (Coordinate mode, Direction,
  Mid-level, Strategy, Subdivision), the Defer/Apply-now choice, and **Apply now** + **Clear**
  buttons; call the validation warnings on apply.
- [ ] T025 [US2] Register the US2 operators in `3dp_textures/__init__.py`.

**Checkpoint**: US1 + US2 both work; editing is live and non-destructive by default.

---

## Phase 5: User Story 3 - Work across shapes and choose textures flexibly (Priority: P3)

**Goal**: Same workflow on flat and curved shapes, with quick presets plus a user-supplied
image/height-map source.

**Independent Test**: Run apply→preview→export on a flat plane and a sphere; select both a built-in
preset and a custom image source; each yields a printable STL with the expected relief.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T026 [P] [US3] `tests/test_displace_image.py`: `strategy='IMAGE'` with a generated grayscale
  height-map displaces the evaluated mesh; missing image → `{'CANCELLED'}` + ERROR report.
- [ ] T027 [P] [US3] `tests/test_shapes.py`: the procedural Wood workflow produces relief on both a
  flat plane and a sphere (Direction=Normal wraps the curved surface) — FR-010.

### Implementation for User Story 3

- [ ] T028 [US3] Implement the A2 fallback strategy in `3dp_textures/engine/displace_image.py`:
  wrap a user `Image` in a `TEX_IMAGE` texture, drive Displace via UV/Generated coords, auto-handle
  missing UV (warn/fallback), register in the engine registry.
- [ ] T029 [US3] Extend `3dp_textures/ui.py`: Strategy switch (Procedural/Image), image/height-map
  picker (shown for Image), and the UV-seam/stretch warning on curved shapes.
- [ ] T030 [P] [US3] Complete the `brick` and `rock` preset configurations in
  `3dp_textures/presets.py` (rock → `TEX_NOISE`/`TEX_VORONOI`; brick → procedural or image source).
- [ ] T031 [US3] Ensure the engine registry in `3dp_textures/engine/__init__.py` resolves the
  `IMAGE` strategy and `tdp.apply_texture` dispatches by `settings.strategy`.

**Checkpoint**: All three stories independently functional across shapes and texture sources.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize quality gates, packaging, and docs across all stories.

- [ ] T032 [P] Tooltip + units pass across `3dp_textures/ui.py` and `3dp_textures/properties.py`
  (every property/operator has a tooltip; length fields use scene units — Platform Standards).
- [ ] T033 [P] Write `README.md` (install from disk, the three quickstart scenarios, 4.2 LTS
  requirement, link to research deliverables).
- [ ] T034 Verify reload discipline (install → enable → disable → re-enable, no console errors) and
  run the full headless suite `blender --background --python tests/run_headless.py` — all pass
  (Definition of Done).
- [ ] T035 Build/validate the extension package and confirm `blender_manifest.toml`
  `[build].paths_exclude_pattern` excludes `tests/` and caches from the shipped artifact.
- [ ] T036 Execute the `specs/002-printable-texture-addon/quickstart.md` validation scenarios
  (US1/US2/US3 + slice an exported STL).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — **BLOCKS all user stories**.
- **User Stories (Phase 3–5)**: each depends only on Foundational; can then proceed in parallel or
  in priority order (P1 → P2 → P3).
- **Polish (Phase 6)**: depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: after Foundational. No dependency on other stories (MVP).
- **US2 (P2)**: after Foundational. Builds on the US1 apply/modifier setup but is independently
  testable (its own non-destructive/clear test).
- **US3 (P3)**: after Foundational. Adds the image strategy + presets; reuses the US1 operator
  dispatch but is independently testable on its own shapes/source.

### Within Each User Story

- Tests (T012/T013, T019, T026/T027) are written first and must FAIL before implementation.
- Engine strategy (separate file) before the operator that calls it.
- Operators before UI wiring; UI before operator registration in `__init__.py`.

### Critical Path

T001→T003→T005→T008→T010 (foundation) → T014→T015→T016→T017→T018 (MVP) → US2 → US3 → Polish.

---

## Parallel Opportunities

- **Setup**: T002 and T004 run in parallel (distinct files); T001/T003 are sequential scaffolding.
- **Foundational**: T005, T006, T007 run in parallel (properties/presets/subdivision — distinct
  files); T011 (test_register) parallel with them. T008/T009/T010 follow.
- **Within a story**: the two test tasks run in parallel (e.g. T012 ‖ T013; T026 ‖ T027). T030
  (presets) is [P] vs other US3 code. Operator tasks sharing `operators.py` (T015/T016, T021/T022)
  are sequential.
- **Across stories**: with multiple developers, US1/US2/US3 can proceed in parallel after Phase 2,
  coordinating on shared files (`operators.py`, `ui.py`, `__init__.py`).

### Parallel Example: User Story 1

```text
# Write both US1 tests together (must fail first):
Task: "tests/test_displace_procedural.py — evaluated-mesh delta + integrity"
Task: "tests/test_export_stl.py — STL round-trip relief present"

# Foundational distinct-file tasks together:
Task: "3dp_textures/properties.py SurfaceSettings"
Task: "3dp_textures/presets.py registry"
Task: "3dp_textures/subdivision.py auto level"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 Setup → 2. Phase 2 Foundational (CRITICAL) → 3. Phase 3 US1 →
4. **STOP & VALIDATE**: run `tests/run_headless.py`; manually verify the quickstart primary
   scenario (Wood → STL → slice) → 5. Demo MVP.

### Incremental Delivery

- Setup + Foundational → foundation ready (empty panel installs/reloads cleanly).
- US1 → headless tests pass → MVP demo.
- US2 → live, non-destructive editing → demo.
- US3 → shapes + custom image + brick/rock → demo.
- Each story adds value without breaking earlier stories.

---

## Notes

- [P] = different files, no incomplete dependencies; tasks sharing `operators.py`, `ui.py`, or
  `__init__.py` are sequential.
- Every operator: `poll()` guard, `bl_options={'REGISTER','UNDO'}`, errors via `self.report`
  (Constitution Principle II/III).
- A change is **not done** until its headless validation passes (Principle V).
- Commit after each task or logical group; verify tests fail before implementing.

**Totals**: 36 tasks — Setup 4 (T001–T004), Foundational 7 (T005–T011), US1 7 (T012–T018),
US2 7 (T019–T025), US3 6 (T026–T031), Polish 5 (T032–T036).
