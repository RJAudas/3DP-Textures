# Prior Art — Community Workflows & Existing Add-ons

How the Blender community already turns textures into printable geometry, and which add-ons
already automate part of it. This grounds the proposed add-on (`addon-workflow.md`) in what
exists and surfaces the gaps it would fill. Web sources are supplemental and always cited;
local Blender source/manual remain authoritative for *mechanism* claims.

## Community Workflows

### W·1 — Subdivide → Displace → Apply → Export STL (the canonical manual workflow)

- **kind**: workflow
- **what_it_does**: The widely-shared community recipe for making displacement printable:
  heavily subdivide the mesh, add a Displace modifier driven by a (often baked) texture, apply
  the modifiers to make the geometry real, then export STL. This is the same pipeline this
  research recommends and that the Blender manual's Apply-Modifiers export option supports
  [W3] [M3] [S2].
- **gaps**: entirely manual and easy to get wrong — users must know to subdivide *enough*,
  pick coordinates, set Strength in the right range, and remember to apply/Apply-Modifiers.
  No presets, no print-scale guidance, no one-click path.
- **source**: [W3]

### W·2 — Shader (material) displacement, then bake to mesh

- **kind**: workflow
- **what_it_does**: Authors build displacement in the material/shader node tree (great live
  preview), then must **bake** that shader displacement into an actual height-map and feed it
  to a Displace modifier to get real geometry — because the material Displacement socket only
  affects render-time appearance, not the exported mesh [W4].
- **gaps**: multi-step and error-prone; the shader→geometry bake is exactly the friction the
  DisplaceIt add-on (below) was written to remove [W1]. Confirms our **out-of-scope** ruling:
  shader-only displacement is not printable on its own.
- **source**: [W4]

## Existing Add-ons / Plugins

### A·1 — DisplaceIt

- **kind**: addon
- **what_it_does**: A Blender add-on that "convert[s] shader displacement to mesh
  displacement." It moves the material's displacement output to the surface output, **bakes**
  the height texture, then sets up a Displace modifier on the (multires-subdivided) object so
  the procedural displacement becomes real geometry — explicitly so it "can be exported … to
  be 3D printed" [W1].
- **gaps**: focused narrowly on baking *shader-node* displacement; assumes the user already
  built a displacement material and added multires geometry. No texture presets (wood/brick/
  rock), no print-scale/mm guidance, no integrated cylinder-wrap UX, and it leans on baking
  rather than a live procedural `Texture`-datablock Displace modifier (our primary A1).
- **source**: [W1]

### A·2 — 3D-Print Toolbox (official Blender add-on)

- **kind**: addon
- **what_it_does**: Blender's bundled add-on for 3D-print preparation: checks a mesh for
  manifold/watertight problems, non-manifold edges, intersections, thin walls, and other
  print-blocking issues, and reports/cleans them [W2].
- **gaps**: it **validates/repairs** geometry but does **not** create texture-driven relief —
  it is the natural *post-step* after displacement, not a texture-to-geometry tool. Our add-on
  would generate the displaced geometry and hand off to this toolbox for the watertight check.
- **source**: [W2]

## Gaps & Opportunities

Across the prior art, no single tool delivers a **guided, geometry-first, print-aware**
texture-to-mesh experience for shapes like cylinders:

- **Presets are missing.** Community workflows and DisplaceIt expose raw mechanics; none ship
  curated "Wood / Brick / Rock" starting points (our `addon-workflow.md` Texture Presets).
- **Live procedural path is underserved.** DisplaceIt centers on *baking shader* displacement;
  the simpler, fully-procedural `Texture`-datablock Displace path (A1) — no UV, displace along
  Normal — is left to manual setup [W1] [M1].
- **No print-scale guidance.** None tie Strength/subdivision to **millimeters** and printer
  resolution; users guess, and over-strong displacement on coarse meshes yields non-manifold
  prints (hence the need for the 3D-Print Toolbox afterward) [W2].
- **Cylinder/curved placement is unsolved.** Image/UV workflows fight seams and stretch on
  non-flat shapes [M4]; a procedural-Normal default sidesteps this but isn't packaged.
- **Apply-vs-defer is implicit.** Workflows say "apply the modifier," but Blender can keep it
  live and realize it only at export via Apply Modifiers — a non-destructive default no
  existing tool foregrounds [M2] [M3] [S2].

**Opportunity**: a single add-on that picks a preset, applies a procedural Displace over
auto-subdivided geometry along the Normal, previews live, advises print-scale in mm, and
defers realization to STL export — then optionally validates with the 3D-Print Toolbox.

## Broader Ecosystem (Intentionally Excluded)

For completeness and to show awareness of the wider Blender landscape, these workflows also
exist and *can* produce or clean printable geometry. They are **intentionally excluded from
the v1 add-on** (see `approaches.md` → *Explicit Non-Goals* and *Rejected Alternatives*); each
is recorded here with the reason and its roadmap status.

- **Geometry Nodes displacement workflows** — node graphs that compute per-point displacement
  as a custom modifier [M2] [M9] [W5]. Powerful (layering, masks, blending) but high authoring
  complexity. **Deferred to v2** as the displacement engine behind the same UI, not removed.
- **Sculpt / Multiresolution workflows** — hand-sculpting detail on Multires levels and
  applying [M7] [W6]. Maximum art-direction, but manual and non-reproducible — a poor fit for a
  one-click parametric add-on. **Excluded from automation**; a niche manual path.
- **Voxel remesh cleanup workflows** — running the Remesh (Voxel/OpenVDB) modifier to rebuild a
  watertight manifold mesh [M6]. Useful as an *optional, user-invoked* repair, but harmful as a
  default stage because it can erase fine displaced relief. **Optional cleanup only**, paired
  with the 3D-Print Toolbox [W2].
- **Material (shader) displacement baking workflows** — authoring displacement in the shader
  tree, then baking it to a height-map for a Displace modifier [W1] [W4]. This is exactly the
  A2 fallback's input path; the standalone *shader-only* form produces no exportable geometry
  and is **out of scope** as a geometry source.

These are not gaps in the recommendation — they are deliberate boundaries. The v1 add-on
targets the simplest stable path (procedural Displace) and leaves these for explicit,
later-versioned, or user-invoked use.
