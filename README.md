# 3DP-Textures

A Blender add-on that turns surface textures into **real, printable mesh geometry**.

Visual/material textures — wood grain, brick, rock, and the like — render beautifully
but don't exist in the mesh, so when you export to STL for 3D printing you get a bare
cube or cylinder. 3DP-Textures bridges that gap: it converts texture concepts into
actual vertices and faces that survive STL export and show up in the printed object.

> Status: early scaffold. This repository currently contains the project constitution
> and Spec Kit workflow configuration; add-on source is being specified and built
> feature-by-feature.

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

## Planned workflow (in Blender)

1. Select a mesh object (cylinder, cube, custom model).
2. Open the 3DP-Textures panel in the 3D Viewport N-panel.
3. Choose a texture-to-geometry strategy and dial in strength, scale, and coordinate
   mode — preview live and non-destructively.
4. Apply/bake the displacement into real geometry when you're happy.
5. Export STL with modifiers applied, so the texture prints.
