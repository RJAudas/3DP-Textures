# Contract: STL Export Behavior

Defines the guaranteed behavior of the export path so it is independently testable. Grounded in
the native exporter: `source/blender/editors/io/io_stl_ops.cc` (operator options) and
`source/blender/io/stl/exporter/stl_export.cc` (uses the **evaluated** mesh when
`apply_modifiers` is true). Manual: `blender-manual/.../files/import_export/stl.rst`.

## Invocation

```python
bpy.ops.wm.stl_export(
    filepath=<output.stl>,
    export_selected_objects=True,   # only the target object
    apply_modifiers=True,           # realize live Subsurf + Displace into the file
    global_scale=1.0,
    use_scene_unit=True,            # respect scene units for print scale
)
```

The add-on selects only the target object before calling, then restores prior selection.

## Guarantees

1. **Relief is present in the file.** When the object is in `live` state, the exported triangles
   reflect the displaced (evaluated) surface — not the flat base mesh — because `apply_modifiers`
   writes the evaluated mesh (FR-008, SC-002).
2. **Preview parity.** The exported geometry matches the relief visible in the viewport at export
   time (FR-009): same Strength/Scale/Mid-level/Direction, because both read the same live
   modifier stack.
3. **Non-destructive.** Exporting from `live` state does **not** modify the source object; the
   modifiers remain live and editable afterward (Constitution Principle III).
4. **Baked parity.** When the object is in `baked` state, the file contains the same geometry as
   the in-scene mesh (modifiers already applied).
5. **Determinism.** Identical object + settings + scale produce byte-stable relief geometry across
   runs (SC-007); procedural textures are seedless/deterministic for a given configuration.
6. **Scale fidelity.** With `use_scene_unit=True` and `strength_mm` interpreted as length, a 0.4 mm
   relief depth in the UI yields ~0.4 mm of displacement in the exported model at scene scale
   (Constitution Principle I — real-world mm).

## Failure modes

| Condition | Behavior |
|-----------|----------|
| No active mesh object | Operator `poll()` false; export button disabled. |
| Invalid/unwritable `filepath` | `wm.stl_export` fails → operator reports `{'ERROR'}`, returns `{'CANCELLED'}`. |
| Non-manifold relief (high Strength on coarse mesh) | Export still succeeds (STL is just triangles); a pre-export `{'WARNING'}` advises validating with the 3D-Print Toolbox (FR-013). |

## Round-trip validation (test_export_stl.py)

1. Build a cylinder; run `tdp.apply_texture` (WOOD).
2. Export to a temp STL with the contract invocation.
3. Re-read the STL (parse triangle vertices).
4. Assert the exported vertex bounds / surface differ from the undisplaced base beyond tolerance →
   proves relief is real geometry, not shading (SC-002).
