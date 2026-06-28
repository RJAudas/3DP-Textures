# Contract: Operators & UI (Command Surface)

For a Blender add-on, the "API" is its **operators**, **panel**, and **registered properties** —
the contract between the user (or a test/script) and the add-on. All operators use
`bl_options = {'REGISTER', 'UNDO'}` (Constitution Principle III), guard with `poll()`, and report
user-facing errors via `self.report` (Principle II). Operator `bl_idname`s live in the `tdp`
namespace.

---

## Operator: `tdp.apply_texture`

Create or update the non-destructive relief setup on the active mesh object.

- **poll**: `context.active_object is not None and context.active_object.type == 'MESH'`.
- **Inputs** (read from `active_object.tdp_surface` / operator redo props): `preset`, `strategy`,
  `strength_mm`, `scale`, `coord_mode`, `direction`, `mid_level`, `subdiv_auto`, `subdiv_level`,
  optional `image` (required if `strategy == 'IMAGE'`).
- **Behavior**: ensure a `3DP Subdivision` (Simple) modifier and a `3DP Displace` modifier exist
  (create if absent, **update if present** — idempotent, no duplicate stacking); create/configure
  the owned `Texture` datablock per preset/strategy; set Displace properties from settings; compute
  subdivision level when `subdiv_auto`. Object state → `live`.
- **Outputs / return**: `{'FINISHED'}` on success; `{'CANCELLED'}` with `report({'ERROR'}, …)` when
  no eligible object or `strategy=='IMAGE'` with no image.
- **Warnings** (`report({'WARNING'}, …)`, non-blocking): strength large vs. smallest dimension;
  `coord_mode=='UV'` with no UV layer; detail finer than typical nozzle.
- **Acceptance link**: US1 #1, US3 #1–4, FR-002/003/004/005/010/012.

## Operator: `tdp.bake` ("Apply now")

Realize the live relief into permanent mesh geometry.

- **poll**: active mesh object has a `3DP Displace` modifier (state `live`).
- **Behavior**: apply `3DP Subdivision` then `3DP Displace` (order preserved) to the mesh; remove
  the add-on modifiers; leave the texture datablock unless orphaned. Object state → `baked`.
  Explicit, destructive, Undo-able.
- **Outputs**: `{'FINISHED'}`; `report({'INFO'}, …)` summarizing new vertex/face counts.
- **Acceptance link**: US2 #3 (revert via Undo), FR-014.

## Operator: `tdp.clear`

Remove the add-on's relief setup, restoring the base mesh.

- **poll**: active object has `3DP `-prefixed modifiers or a `tdp_surface` setup.
- **Behavior**: remove `3DP ` modifiers and owned texture; reset state → `none`. Non-destructive to
  the user's original base mesh.
- **Outputs**: `{'FINISHED'}`.
- **Acceptance link**: US2 #3 (non-destructive recovery), FR-007.

## Operator: `tdp.export_stl`

Export the active object as an STL containing the relief.

- **poll**: active mesh object exists.
- **Inputs**: `filepath` (via `invoke` file selector or passed directly in tests).
- **Behavior**: call
  `bpy.ops.wm.stl_export(filepath=…, export_selected_objects=True, apply_modifiers=True,
  use_scene_unit=True)` with only the target selected. When state is `live`, Apply Modifiers
  realizes the relief for the file; when `baked`, geometry is already real. Object state →
  `exported` (transient; object itself unchanged).
- **Outputs**: `{'FINISHED'}` and a written STL whose evaluated geometry matches the preview
  (FR-008/FR-009, SC-002); `report({'ERROR'}, …)` on export failure.
- **Acceptance link**: US1 #2–3, FR-008/009.

---

## Panel: `VIEW3D_PT_texture_to_geometry`

- **Location**: 3D Viewport ▸ N-panel ▸ tab **"Texture → Geometry"** (also an Object-menu entry).
- **Enablement**: controls disabled with a hint label when no active mesh object (edge case "no
  eligible object selected").
- **Layout** (top→bottom): Preset selector → Strength (mm) → Scale → [Advanced ▸ Coordinate mode,
  Direction, Mid-level, Strategy, Subdivision] → buttons **Apply Texture**, **Apply now**,
  **Clear**, **Export STL…**. Every property and operator has a tooltip (Platform Standards).
- **Live preview**: editing Strength/Scale/etc. re-runs `tdp.apply_texture` (or directly updates
  the live modifier) so the viewport updates within ~1 s (SC-005).

## Registered property

- `bpy.types.Object.tdp_surface : PointerProperty(type=SurfaceSettings)` — added in `register()`,
  deleted in `unregister()` (symmetric, idempotent — verified by `test_register.py`).

## Contract tests (headless)

| Test | Asserts |
|------|---------|
| `test_register.py` | enable→disable→re-enable leaves no `tdp_surface`, classes, or menu residue. |
| `test_displace_procedural.py` | after `tdp.apply_texture` (WOOD), evaluated mesh bounds/positions changed > tol; no NaN; no zero-area faces. |
| `test_displace_image.py` | `strategy='IMAGE'` with a height-map displaces; missing image → `{'CANCELLED'}`+ERROR. |
| `test_export_stl.py` | `tdp.export_stl` writes a file whose re-read geometry differs from the undisplaced base (relief present). |
