# References

Consolidated citations for the deliverable set. Every major claim across the documents
(approach mechanism, control behavior, STL export behavior, prior art) carries ≥1 tag that
resolves here to a real local path or URL.

**Citation tag convention** (shared by all deliverables):

- `[S#]` — **source**: Blender C/C++/Python source (ground-truth behavior).
- `[M#]` — **manual**: Blender manual `.rst` (documented concepts/behavior).
- `[T#]` — **toc**: the project reference TOC that maps the high-value files.
- `[W#]` — **web**: community workflow, add-on, or documentation page (supplemental).

Local source/manual/TOC are authoritative; web sources are supplemental and re-findable.

## References

### Source `[S]`

- **[S1]** · `source` · `D:\dev\blender\blender\source\blender\editors\io\io_stl_ops.cc`
  (lines 72, 123, 207). Supports: the STL exporter exposes an **Apply Modifiers** option that
  **defaults to `true`** (`RNA_def_boolean(... "apply_modifiers", true, ...)`, line 207), read
  into `export_params.apply_modifiers` (line 72).
- **[S2]** · `source` · `D:\dev\blender\blender\source\blender\io\stl\exporter\stl_export.cc`
  (lines 121–122). Supports: when `apply_modifiers` is true the exporter writes the
  **evaluated** mesh — `BKE_object_get_evaluated_mesh(obj_eval)` — i.e. live modifiers become
  real exported geometry; otherwise the original mesh is used.
- **[S3]** · `source` · `D:\dev\blender\blender\source\blender\modifiers\intern\MOD_displace.cc`
  (lines 165–233). Supports: displacement math and direction handling —
  `delta = texres.tin − dmd->midlevel; delta *= strength;`, and the `MOD_DISP_DIR_*` direction
  cases (X/Y/Z, NOR = Normal, CLNOR = Custom Normal, RGB_XYZ).
- **[S4]** · `source` · `D:\dev\blender\blender\source\blender\makesdna\DNA_texture_types.h`
  (lines 64–101, 397). Supports: procedural/image texture type enums — `TEX_CLOUDS`,
  `TEX_WOOD=2`, `TEX_MARBLE`, `TEX_STUCCI`, `TEX_NOISE=7`, `TEX_IMAGE=8`, `TEX_MUSGRAVE`,
  `TEX_VORONOI=12`.
- **[S5]** · `source` ·
  `D:\dev\blender\blender\source\blender\makesrna\intern\rna_modifier.cc`
  (Displace modifier RNA, approx. lines 2853–2909 / 4130–4220 per the TOC). Supports: the
  Python-visible Displace properties `texture`, `texture_coords`, `uv_layer`, `strength`,
  `mid_level`, `direction`, `space`, `vertex_group`.
- **[S6]** · `source` · `D:\dev\blender\blender\source\blender\makesrna\intern\rna_texture.cc`.
  Supports: procedural `Texture` datablock types (Wood, Noise, Voronoi, …) exposed to Python;
  these are the datablocks the Displace modifier samples.

### Manual `[M]`

- **[M1]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\modifiers\deform\displace.rst`. Supports: the
  Displace modifier displaces vertices by a texture (procedural or image); Texture,
  Coordinates, Direction (X/Y/Z, Normal, Custom Normal, RGB→XYZ), Space, Strength
  (`vertex_offset = displacement × Strength`), and Midlevel
  (`displacement = texture_value − Midlevel`).
- **[M2]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\modifiers\introduction.rst`. Supports:
  modifiers are non-destructive; the stack is evaluated top-to-bottom; *Apply* makes a modifier
  real and removes it; Geometry Nodes groups with the **Modifier** property enabled act as
  custom modifiers.
- **[M3]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\files\import_export\stl.rst`. Supports: STL is the
  common 3D-printing format; the **Apply Modifiers** export option exports the **evaluated
  mesh** — "the resulting mesh after all Modifiers have been calculated."
- **[M4]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\render\shader_nodes\input\texture_coordinate.rst`.
  Supports: coordinate spaces (Generated, Normal, UV, Object, …) used to place textures;
  relevant to UV vs. procedural placement and cylinder-wrap seams/stretch.
- **[M5]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\modifiers\generate\subdivision_surface.rst`
  (lines 50–71). Supports: **Simple** subdivision "can be used … to increase the base mesh
  resolution when using displacement maps"; separate **Levels Viewport / Render** for
  preview-vs-final density.
- **[M6]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\modifiers\generate\remesh.rst` (lines 8–9,
  34–36). Supports: the **Remesh** modifier regenerates topology; **Voxel** mode uses OpenVDB
  to "generate a new manifold mesh from the current geometry while trying to preserve the
  mesh's original volume" — i.e. a watertight-cleanup tool, not a texture-to-geometry tool.
- **[M7]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\modifiers\generate\multiresolution.rst`
  (lines 8–12, 41–43). Supports: the **Multiresolution** modifier subdivides a mesh and lets
  you edit/sculpt the subdivision levels in Sculpt Mode — the basis of the sculpt/multires
  workflow.
- **[M8]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\render\cycles\render_settings\subdivision.rst`
  (lines 10, 15–16). Supports: Cycles **Adaptive Subdivision** is a *render* setting (dicing
  rate controls micropolygon size for the final/viewport **render**); it tessellates at render
  time and does not change the exported mesh.
- **[M9]** · `manual` ·
  `D:\dev\blender\blender-manual\manual\modeling\geometry_nodes\index.rst`. Supports: Geometry
  Nodes is Blender's modern node-based procedural geometry system; relevant as the deferred
  v2 implementation path and a broader-ecosystem workflow.

### Reference TOC `[T]`

- **[T1]** · `toc` · `D:\dev\blender\blender-plugin-reference-toc.md`. Supports: the curated
  map of the highest-value Blender files for this add-on, the scripted Displace setup
  (`modifier = obj.modifiers.new(type="DISPLACE")`, `texture_coords`, `strength`, `mid_level`,
  `direction`, `space`), the `bpy.ops.wm.stl_export(..., apply_modifiers=True)` example, and
  the project goal statement ("Wood Grain Geometry" add-on).

### Web `[W]`

- **[W1]** · `web` · <https://github.com/gentlegiantJGC/DisplaceIt>. Supports: an existing
  add-on that converts shader (material) displacement into mesh displacement by baking the
  height texture and setting up a Displace modifier, explicitly for 3D-print export.
- **[W2]** · `web` · <https://extensions.blender.org/add-ons/print3d-toolbox/>. Supports:
  Blender's official 3D-Print Toolbox add-on that checks/repairs meshes for printability
  (manifold/watertight, non-manifold edges, intersections, thin walls) — the validation
  post-step after displacement.
- **[W3]** · `web` ·
  <https://blender.stackexchange.com/questions/262677/how-to-turn-a-displacement-model-in-to-something-3d-printable>.
  Supports: the canonical community workflow — subdivide, Displace, apply modifiers, export
  STL — for making displacement printable.
- **[W4]** · `web` ·
  <https://docs.blender.org/manual/en/latest/render/materials/components/displacement.html>.
  Supports: material/shader **Displacement** affects render-time geometry only (not the
  exported mesh on its own), motivating the geometry-first scope and the bake-to-mesh step.
- **[W5]** · `web` ·
  <https://blender.stackexchange.com/questions/126441/how-to-displace-a-mesh-with-geometry-nodes>.
  Supports: community example of node-based (Geometry Nodes) displacement — evidence the
  modern GN workflow exists and is viable, but with higher authoring complexity than a Displace
  modifier.
- **[W6]** · `web` · <https://www.blender.org/features/sculpting/>. Supports: Blender's
  official sculpting feature overview — the sculpt/multires workflow as a recognized part of
  the broader ecosystem (intentionally excluded for v1).
