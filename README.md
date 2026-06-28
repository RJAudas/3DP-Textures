# 3DP-Textures

A Blender add-on that turns surface textures into **real, printable mesh geometry**.

Visual/material textures — wood grain, brick, rock, and the like — render beautifully
but don't exist in the mesh, so when you export to STL for 3D printing you get a bare
cube or cylinder. 3DP-Textures bridges that gap: it converts texture concepts into
actual vertices and faces that survive STL export and show up in the printed object.

> Status: User Story 1–3 implemented. The add-on package lives in
> [`tdp_textures/`](tdp_textures/) with a headless test suite in [`tests/`](tests/).
> (The extension id is `tdp_textures` — Blender extension ids must be valid Python
> identifiers and cannot start with a digit, so the package is not named `3dp_textures`.)

## Why this exists

In Blender, a shader/material texture only affects how an object is _rendered_. It is
not part of the geometry, so STL export (which only carries mesh data) drops it
entirely. To 3D print a textured surface you have to bake that texture into the mesh
itself — for example via the **Displace** modifier, **Geometry Nodes**, or height-map
displacement. 3DP-Textures wraps these techniques in a single, consistent Blender UI.

## Goals

- **Geometry-first, print-ready output.** Every feature produces mesh geometry that
  survives STL export (`apply_modifiers=True` or an explicit bake) and appears in the
  print. Material-only effects are treated as previews only.
- **Native Blender integration.** Packaged as a modern Blender extension
  (`blender_manifest.toml` + `__init__.py`), using documented `bpy` APIs, clean
  symmetric `register()`/`unregister()`, and `poll()`-guarded operators.
- **Non-destructive by default.** Live, tweakable modifiers by default; full Undo
  support; baking to permanent geometry is a deliberate, clearly labeled action that
  never overwrites your original mesh without opt-in.
- **Multiple strategies, one interface.** More than one texture-to-geometry approach
  (Displace modifier with procedural textures, Geometry Nodes, image/height-map
  displacement) behind a uniform set of controls — strength, scale, coordinate space,
  axis/direction.
- **Print-correct results.** Sensible millimeter-scale defaults, respect for scene
  units on export, and warnings when a printable (manifold) result can't be guaranteed.

These goals are the binding principles of the project — see
[`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Requirements

- **Blender 4.2 LTS or newer** (declared baseline; developed/tested against 5.1).

## Install (from disk)

1. Build the extension zip (optional — you can also point Blender at the source folder):
   ```powershell
   blender --command extension build --source-dir .\tdp_textures --output-dir .\dist
   ```
2. In Blender: **Edit ▸ Preferences ▸ Get Extensions ▸ Install from Disk…** and select
   `dist\tdp_textures-1.0.0.zip` (or the `tdp_textures` folder), then enable it.
3. Press `N` in the 3D Viewport and confirm the **"Texture → Geometry"** tab appears.

Reload check: disable and re-enable the extension — the console must show no errors and
the panel must disappear/reappear cleanly (symmetric `register()`/`unregister()`).

## Usage

### 1. Texture → printable STL (Wood preset)

1. Add a mesh (e.g. **Add ▸ Mesh ▸ Cylinder**).
2. Open the **Texture → Geometry** N-panel, pick the **Wood** preset, click **Apply Texture**.
   Ring/grain relief appears live as a non-destructive Subsurf + Displace modifier stack.
3. Click **Export STL…**, choose a path. The exported triangles carry the relief
   (`apply_modifiers=True`), so it slices and prints.

### 2. Adjust & preview, non-destructively

- Change **Strength (mm)** / **Scale** — the viewport updates live.
- **Clear** (or `Ctrl+Z`) fully restores the base mesh. Use **Apply now** to bake the
  relief into permanent geometry only when you choose to.

### 3. Other shapes & a custom image source

- The same workflow runs on planes and spheres (Direction = Normal wraps curved surfaces).
- Open **Advanced ▸ Strategy ▸ Image** and load a grayscale height-map to drive relief
  from your own image (UVs recommended; a warning is shown on curved shapes without UVs).

## Headless validation (required)

Geometry correctness is validated automatically at the mesh level (Constitution
Principle V):

```powershell
blender --background --factory-startup --python tests\run_headless.py
```

All checks must pass: register/unregister leaves no residue; procedural and image
strategies displace the **evaluated** mesh (no NaN, no zero-area faces); apply/clear is
non-destructive; and a round-tripped exported STL contains relief absent from the base.

## Background & research

The texture-to-geometry strategy decisions (Displace + procedural texture as primary,
image/height-map as fallback) are documented in
[`specs/001-texture-geometry-research/deliverables/`](specs/001-texture-geometry-research/deliverables/)
and the feature design lives in
[`specs/002-printable-texture-addon/`](specs/002-printable-texture-addon/).

## Workflow (in Blender)

1. Select a mesh object (cylinder, cube, custom model).
2. Open the 3DP-Textures panel in the 3D Viewport N-panel.
3. Choose a texture-to-geometry strategy and dial in strength, scale, and coordinate
   mode — preview live and non-destructively.
4. Apply/bake the displacement into real geometry when you're happy.
5. Export STL with modifiers applied, so the texture prints.
