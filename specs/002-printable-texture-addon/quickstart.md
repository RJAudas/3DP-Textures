# Quickstart & Validation: Printable Texture Add-on

A run/validation guide for the add-on. Implementation details live in `plan.md`, `data-model.md`,
and `contracts/`; this file shows how to install, exercise, and verify the feature end-to-end.

## Prerequisites

- **Blender 4.2 LTS or newer** (the declared baseline — see `spec.md` § Clarifications).
- The extension package `3dp_textures/` (built per `plan.md` § Project Structure).
- For headless validation: the `blender` executable on `PATH`.

## Install (manual / dev)

1. Blender ▸ **Edit ▸ Preferences ▸ Get Extensions / Add-ons ▸ Install from Disk…**
2. Select the built `3dp_textures` extension (or zip), then enable it.
3. Confirm a **"Texture → Geometry"** tab appears in the 3D Viewport N-panel (press `N`).

Reload check (Constitution Principle II): disable and re-enable the extension — the console must
show no errors and the panel must disappear/reappear cleanly.

## Primary scenario — texture → printable STL (User Story 1)

Maps to spec Success Criteria SC-001/SC-002/SC-003.

1. **Create a primitive**: Add ▸ Mesh ▸ **Cylinder**.
2. **Open** the N-panel ▸ **Texture → Geometry**.
3. **Pick the *Wood* preset** and click **Apply Texture**.
   - Expected: visible ring/grain relief appears on the cylinder (live preview).
4. **Export STL**: click **Export STL…**, choose a path, confirm.
5. **Verify in a slicer**: open the STL in PrusaSlicer/Cura.
   - Expected: the surface grain is present as real geometry and the model slices.

**Pass criteria**: a new user reaches a sliceable, textured STL without manually configuring
modifiers (SC-001, SC-004), in far fewer steps than the native workflow (SC-003).

## Iterative scenario — adjust & preview (User Story 2)

Maps to SC-005/SC-006.

1. With the Wood setup live, increase **Strength** (mm).
   - Expected: relief deepens in the viewport within ~1 s (SC-005).
2. Change **Scale**.
   - Expected: grain frequency changes live.
3. Press **Ctrl+Z** (or click **Clear**).
   - Expected: original base cylinder is fully recovered — non-destructive (SC-006).
4. Re-apply and **Export STL**.
   - Expected: exported relief matches the last preview (FR-009).

## Generalization scenario — shapes & custom texture (User Story 3)

1. Repeat the primary scenario on a **flat plane** and a **sphere**.
   - Expected: relief applies cleanly on flat faces and wraps curves (Direction = Normal).
2. Switch **Strategy → Image**, load a grayscale height-map, **Apply Texture**.
   - Expected: relief follows the supplied image; on curved shapes a UV-seam/stretch **warning** is
     shown (edge case).

## Headless validation (Constitution Principle V — required)

Run the automated mesh-level checks without opening the UI:

```powershell
blender --background --python tests\run_headless.py
```

Expected output: all tests pass. The suite asserts (see `contracts/operators.md` and
`contracts/stl-export.md`):

| Check | Proves |
|-------|--------|
| `test_register.py` | enable/disable/re-enable leaves no residue (Principle II). |
| `test_displace_procedural.py` | Wood `apply_texture` changes the **evaluated** mesh (bounds/positions > tol), no NaN, no zero-area faces. |
| `test_displace_image.py` | image strategy displaces; missing image → ERROR + CANCELLED. |
| `test_export_stl.py` | exported STL, when re-read, contains relief absent from the base mesh (SC-002). |

A change is **not done** until this suite passes (Constitution Development Workflow / Definition of
Done).

## Definition of Done checklist (from constitution)

- [ ] Produces exporting geometry (relief present in STL).
- [ ] `register()`/`unregister()` round-trip cleanly (install→enable→disable→re-enable, no errors).
- [ ] Headless validation passes.
- [ ] User-facing errors reported via `self.report`, not raised.

## References

- Approach & UX: `specs/001-texture-geometry-research/deliverables/{approaches,addon-workflow,summary}.md`
- API/source map: `D:\dev\blender\blender-plugin-reference-toc.md`
- Manual: `D:\dev\blender\blender-manual` (Displace modifier, STL export, extensions)
- Source: `D:\dev\blender\blender` (MOD_displace.cc, io_stl_ops.cc, rna_modifier.cc)
