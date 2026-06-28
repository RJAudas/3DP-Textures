# Texture-to-Geometry Approaches

This document catalogs the Blender-native ways to turn a surface texture into **real,
exportable mesh geometry** for STL/3D printing, compares them, and ends with one justified
recommendation plus a fallback. Geometry-first framing and the glossary are in
`00-overview.md`.

> **Read this as an Architecture Decision Record (ADR).** The recommendation below is a
> deliberate v1 engineering decision, not a survey of equally-weighted options. Sections
> **Explicit Non-Goals (v1)**, **Rejected Alternatives**, **Legacy vs. Modern Procedural
> APIs**, and **Future Evolution (Roadmap)** record *what is intentionally excluded and why*,
> so the decision is unambiguous to future contributors and AI coding agents. Where an approach
> is called "secondary" or "deferred," that is an intentional scoping choice with a defined
> future path — not an oversight or a limitation.

## Approaches Overview

For 3D printing, a texture must become actual displaced vertices, because STL stores only
triangle geometry. All viable approaches therefore share the same skeleton: **(1)** give the
surface enough vertices (subdivision), **(2)** drive a per-vertex offset from a texture
(displacement), and **(3)** realize the result as real geometry at export via **Apply
Modifiers**, which exports the *evaluated* mesh [M3] [S2]. The approaches differ in *what
supplies the texture* and *how the displacement is computed*.

Three serious contenders are evaluated below, plus one stretch option:

1. **Displace modifier + procedural Texture** (Wood/Noise/Voronoi) over a subdivided mesh.
2. **Image / height-map displacement** (UV- or coordinate-driven) over a subdivided mesh.
3. **Geometry Nodes displacement** (node-based, procedural or image input).
4. *(Stretch)* **Sculpt / multiresolution bake** — heavier, noted for completeness.

The comparison matrix summarizes them; full records follow.

## Comparison Matrix

| Field | A1 · Displace + procedural | A2 · Displace + image/height-map | A3 · Geometry Nodes displacement | A4 · Sculpt/multires *(stretch)* |
|-------|----------------------------|----------------------------------|----------------------------------|----------------------------------|
| Texture source | Procedural `Texture` datablock (Wood, Noise, Voronoi) [S4] [S6] | User image / grayscale height-map [M1] | Procedural fields **or** image input [M2] | Brush/image baked to multires |
| Mechanism | Per-vertex offset `(tex − Midlevel) × Strength` along direction [M1] [S3] | Same offset math; texture sampled in UV/coord space [M1] [M4] | Node graph computes per-point offset; runs as a custom modifier [M2] | Sculpted detail baked into dense mesh |
| Required inputs | Subdivided mesh + Texture datablock + Displace modifier [M5] [T1] | Subdivided mesh + image + UV map + Displace modifier [M4] | Subdivided/instanced geometry + node group [M2] | High-res multires mesh |
| Key controls | Strength, Midlevel, Direction, Coordinates, Texture [M1] [S5] | Strength, Midlevel, Direction, UV/Coordinates, Image [M1] [M4] | Arbitrary (node inputs); can expose Strength/Scale | Brush settings, bake resolution |
| Print-readiness risk | **Low** | **Low–Medium** (seams/stretch on curves) | **Medium** (complexity, less local docs) | **High** (manual, heavy) |
| Export behavior | Realized by Apply Modifiers → evaluated mesh [M3] [S2] | Same [M3] [S2] | Same — GN is a modifier; evaluated at export [M2] [S2] | Apply multires then export |
| Recommended role | **primary** | **fallback** | secondary | stretch |

## Approach: Displace modifier + procedural Texture (A1)

- **id**: `displace-procedural`
- **mechanism**: The Displace modifier samples a texture value per vertex and offsets the
  vertex by `(texture_value − Midlevel) × Strength`. In source this is literally
  `delta = texres.tin − dmd->midlevel; delta *= strength;` then applied along the chosen
  direction [S3], matching the manual's `vertex_offset = displacement × Strength` and
  `displacement = texture_value − Midlevel` [M1].
- **texture_sources**: `procedural` — a `Texture` datablock of type Wood, Noise, Voronoi,
  Marble, Clouds, etc. (`TEX_WOOD`, `TEX_NOISE`, `TEX_VORONOI` … in DNA) [S4], exposed through
  the legacy texture RNA API [S6].
- **required_inputs**: a mesh with enough vertices — use a **Subdivision Surface** modifier
  (Simple mode is intended for exactly this: "increase the base mesh resolution when using
  displacement maps") [M5]; a procedural `Texture` datablock; a **Displace** modifier
  referencing it. A scripted setup is sketched in the reference TOC [T1].
- **controls**: Texture (pick), Strength, Midlevel, Direction (Normal / X/Y/Z / RGB→XYZ),
  Coordinates (Local/Global/Object/UV), Space — all Python-visible (`texture`,
  `texture_coords`, `strength`, `mid_level`, `direction`, `space`) [M1] [S5] [T1].
- **strengths**:
  - Fully procedural — no image, no UV unwrap required for Local/Generated coordinates.
  - Non-destructive and live-previewable; tune Strength/Midlevel before committing [M2].
  - Direction = **Normal** displaces outward along the surface, ideal for wrapping grain
    around a cylinder without an explicit UV map [M1].
  - Smallest, best-documented native path; the reference TOC names it as the primary build
    target [T1].
- **limitations**:
  - Detail is capped by base-mesh density: too few vertices → blocky/aliased grain. Needs
    generous subdivision, which costs memory/time [M5].
  - Procedural patterns are math-driven; matching a *specific* real-wood photo is harder than
    with an image.
- **print_readiness_risk**: **low** — outward (Normal) displacement of a closed, subdivided
  mesh stays manifold for moderate Strength; risk rises only with very high Strength on a
  coarse mesh (self-intersection).
- **export_behavior**: With the Displace (and Subdivision) modifiers left live, STL export
  with **Apply Modifiers** (default on) writes the evaluated mesh, turning the displacement
  into real triangles [M3] [S1] [S2].
- **recommended_role**: `primary`.
- **references**: [M1] [M2] [M5] [S3] [S4] [S5] [S6] [T1] [S1] [S2] [M3].

## Approach: Displace modifier + image / height-map (A2)

- **id**: `displace-image`
- **mechanism**: Identical displacement math to A1, but the texture is an **image**
  (grayscale height-map). The pixel value at each vertex's texture coordinate sets the offset
  `(value − Midlevel) × Strength` [M1] [S3].
- **texture_sources**: `image-heightmap` — a `TEX_IMAGE` texture datablock [S4] wrapping a
  user-supplied height-map.
- **required_inputs**: subdivided mesh; an image; a **coordinate mapping** — usually **UV**
  (`texture_coords='UV'`) so the map sits predictably, which requires a UV unwrap; or
  Generated/Object coordinates for simpler cases [M1] [M4] [T1].
- **controls**: Strength, Midlevel, Direction, **Coordinates = UV** (+ UV layer), Image
  [M1] [M4].
- **strengths**:
  - Reproduces a *specific* real texture (scanned wood, brick photo) faithfully.
  - UV coordinates give precise, repeatable placement and tiling [M4].
- **limitations**:
  - Requires a UV unwrap; on curved/closed shapes (cylinder wrap) UVs introduce **seams and
    stretching** that show up as visible artifacts in the printed relief [M4]. This is a known
    pain point, not a solved problem.
  - Quality is bounded by both image resolution and mesh density.
- **print_readiness_risk**: **low–medium** — clean where UVs are clean; seams/stretch on
  non-flat shapes can create uneven relief.
- **export_behavior**: same as A1 — realized by **Apply Modifiers** at STL export [M3] [S2].
- **recommended_role**: `fallback`.
- **references**: [M1] [M4] [S3] [S4] [T1] [M3] [S2].

## Approach: Geometry Nodes displacement (A3)

- **id**: `geometry-nodes`
- **mechanism**: A Geometry Nodes group used as a **custom modifier** computes a per-point
  offset (from a procedural noise field or a sampled image) and writes it to point positions.
  Blender explicitly allows users to "make their own modifiers through Geometry Nodes"; a node
  group with its **Modifier** property enabled appears in the Add Modifier menu [M2].
- **texture_sources**: `procedural`, `image-heightmap` — node graphs can use Noise/Voronoi
  texture nodes or an Image Texture node as the field [M2].
- **required_inputs**: a base mesh (subdivided or subdivided *inside* the graph) and a GN
  node group configured as a modifier [M2].
- **controls**: arbitrary — the node group can expose named inputs (Strength, Scale, Seed,
  etc.) on the modifier panel, mirroring A1's controls plus anything custom.
- **strengths**:
  - Most flexible: combine multiple textures, masks, falloffs, and procedural subdivision in
    one non-destructive graph [M2].
  - Reusable as an asset/category in the Add Modifier menu [M2].
- **limitations**:
  - Highest authoring complexity; least covered by the local manual for the specific
    displacement pattern (heavier reliance on community sources) — see `prior-art.md`.
  - Easier to produce non-manifold results if the graph self-intersects geometry.
- **print_readiness_risk**: **medium** — power comes with more ways to break manifoldness;
  needs validation (3D Print Toolbox) before export [W2].
- **export_behavior**: a GN modifier is part of the modifier stack, so it is realized by the
  evaluated mesh on **Apply Modifiers** at export, exactly like A1/A2 [M2] [S2].
- **recommended_role**: `secondary` — **intentionally deferred to a future version (v2)**.
  Geometry Nodes is not rejected on technical merit; it is deferred because it substantially
  increases implementation complexity (a node-graph builder, exposed inputs, asset management)
  while providing flexibility beyond the goals of the initial release. See **Future Evolution
  (Roadmap)** and **Rejected Alternatives**.
- **references**: [M2] [S2] [W2] [W5].

## Approach: Sculpt / multiresolution bake — stretch (A4)

- **id**: `sculpt-multires`
- **mechanism**: Add a Multiresolution modifier, sculpt or bake texture detail into the
  subdivided levels, then apply — producing dense real geometry.
- **texture_sources**: `procedural`, `image-heightmap` (as sculpt stencil/bake source).
- **required_inputs**: high-resolution multires mesh; manual sculpting or a bake step.
- **strengths**: art-directable, can localize detail.
- **limitations**: labor-intensive, heavy meshes, least automatable of the four — poor fit for
  a one-click add-on. Listed only for completeness.
- **print_readiness_risk**: **high** (heavy meshes, manual cleanup).
- **export_behavior**: apply multires, then export [M3] [S2].
- **recommended_role**: `stretch` — **intentionally out of scope for the automated pipeline.**
  Its manual, art-directed nature is a poor fit for a one-click, reproducible add-on; it is
  recorded for completeness, not as a contender.
- **references**: [M3] [M7] [S2].

## Recommendation

**Primary: A1 — Displace modifier + procedural `Texture` over a subdivided mesh.**

Top reason: it is the **smallest, best-documented, fully native** path that produces real,
manifold, printable geometry with no UV unwrap, and it maps directly onto the project's stated
goal (a "Wood Grain Geometry" add-on driving a `DISPLACE` modifier with a procedural texture
and STL export via `apply_modifiers=True`) [T1]. The displacement math is ground-truth in the
modifier source [S3], the procedural texture types exist in DNA/RNA [S4] [S6], Simple
subdivision is documented for exactly this purpose [M5], and STL export realizes the live
modifier through the evaluated mesh [M3] [S2]. Displacing along **Normal** wraps grain around
cylinders without seams [M1] — a decisive advantage over image/UV mapping for the target
shapes.

**Fallback: A2 — Displace modifier + image / height-map.** When a user needs a *specific*
real-world texture rather than a procedural look, switch the same Displace modifier to a
`TEX_IMAGE` source with UV coordinates [M1] [M4] [S4]. It reuses the entire A1 pipeline and
controls, so the add-on can offer it as an alternate texture source with minimal extra code —
at the cost of requiring a UV unwrap and accepting possible seams/stretch on curved shapes
[M4].

**Secondary: A3 — Geometry Nodes displacement** is the flexible "power-user" path. It is
**intentionally deferred to v2**, not dismissed: GN substantially increases implementation
complexity (graph construction, exposed modifier inputs, asset/category management) while
delivering capabilities — layering, masking, blending — beyond the goals of the initial
release [M2] [M9] [W5]. **A4 (sculpt/multires)** is **intentionally excluded** from the
automated pipeline because its manual nature defeats one-click reproducibility [M7].

These exclusions are recorded deliberately in **Explicit Non-Goals (v1)** and **Rejected
Alternatives** below so the decision is not silently reopened. A single proposed UI can present
A1 and A2 (and, in v2, A3) as interchangeable "texture source" strategies behind one panel —
see `addon-workflow.md`.

## Subdivision & Print-Scale Guidance

Displacement detail is bounded by vertex density: each "bump" needs several vertices across it
to render as real relief instead of an aliased step. Use a **Subdivision Surface** modifier in
**Simple** mode below the Displace modifier — its documented role is to "increase the base mesh
resolution when using displacement maps" [M5] — and keep it **live** so density and strength
can be re-tuned before export.

Print-scale rules of thumb (all length values are real-world mm, since STL is unit-bearing and
3D-print slicers read millimeters):

- **Match vertex spacing to detail size.** For grain/relief features of size *d* mm, aim for
  edge length ≲ *d*/3 in the displaced region. Example: ~0.6 mm wood-grain ridges → target
  ~0.2 mm edges in the displaced band.
- **Default starting density.** For a small printed part (tens of mm), start with enough
  Simple-subdivision levels to reach roughly **0.2–0.5 mm** average edge length on the
  textured surface, then increase only if the relief looks stepped [M5].
- **Strength in mm, not "units".** Set Displace **Strength** to the desired physical relief
  depth (e.g. 0.3–0.8 mm for tactile wood grain). Because the offset is `displacement ×
  Strength` [M1] [S3], keep Strength small relative to wall thickness to avoid
  self-intersection / non-manifold geometry.
- **Respect printer resolution.** There is no value in sub-resolution detail: features below
  the printer's minimum feature size (~0.2–0.4 mm for FDM; finer for resin) won't print, so
  don't pay the vertex-count cost for them.
- **Performance trade-off.** Subdivision cost grows ~4× per level. Tune in the viewport at a
  low level, then raise levels only for the final export; the Subdivision modifier supports
  separate **Viewport** and **Render** levels for exactly this kind of preview-vs-final
  trade-off [M5].

Citations for this section: [M1] [M5] [S3].

## Explicit Non-Goals (v1)

The following implementation approaches are **intentionally excluded from v1**. Each is a
deliberate scoping decision to keep the initial release simple, stable, and reliably
print-ready. The tone is **"not now," not "never"** — future possibilities are noted.

| Non-goal | What it is | Why excluded from v1 | Future possibility? |
|----------|-----------|----------------------|---------------------|
| **Geometry Nodes as the primary implementation** | Building the displacement in a GN node graph used as a custom modifier [M2] [M9] | Substantially higher implementation complexity (graph construction, exposed inputs, asset/category management) for capabilities beyond v1's goals; a Displace modifier reaches the goal with far less surface area | **Yes — planned v2.** It is the natural home for layering/masking/blending |
| **Shader-only displacement workflows** | Using the material output **Displacement** socket for render-time relief [W4] | Produces **no exportable geometry** — STL ignores materials, so it cannot be printed on its own | Only as an *input to bake into mesh* (see DisplaceIt prior art [W1]); never as the geometry source |
| **Vector displacement maps** | RGB-encoded maps that push vertices in arbitrary XYZ directions (vs. scalar height along a direction) | Authoring/baking vector maps is a specialist, image-pipeline task; scalar height displacement covers wood/brick/rock relief with a simpler control set. The Displace modifier's `RGB→XYZ` direction exists [M1] [S3] but is not a v1 preset | **Yes — later**, if real-world demand for overhangs/undercuts appears |
| **Adaptive subdivision / render-only tessellation** | Cycles Adaptive Subdivision dices geometry into micropolygons **at render time** [M8] | It is a *render* feature: the diced geometry is **not** in the exported mesh, so it cannot drive an STL. v1 needs real, persistent vertices via the Subdivision Surface modifier [M5] | No clear path; render-time tessellation is structurally mismatched with mesh export |
| **Sculpt / Multiresolution workflows** | Hand-sculpting detail on Multires levels, then applying [M7] | Manual and art-directed; defeats one-click, reproducible, parametric generation | **Niche future** for art-directed one-offs, not the automated pipeline |
| **Automatic voxel remeshing in the standard pipeline** | Running the Remesh (Voxel/OpenVDB) modifier to rebuild manifold topology [M6] | Regenerates topology and can erase fine displaced relief and inflate vertex counts; making it automatic would fight the displacement it follows | **Yes — as an *optional, user-invoked* repair step**, not a default stage; pair with the 3D-Print Toolbox [W2] |

## Rejected Alternatives

Major implementation *strategies* that were evaluated for v1 and deliberately not selected.
This section exists to **prevent already-made decisions from being silently reopened.** Each
records advantages, disadvantages, the reason for rejection, and roadmap status.

### Geometry Nodes as the v1 engine (rejected for v1; on the v2 roadmap)

- **Advantages**: maximum flexibility — procedural subdivision, multi-texture layering, masks,
  and falloffs in one non-destructive, reusable graph [M2] [M9] [W5].
- **Disadvantages**: large implementation surface (programmatically building/wiring a node
  graph, exposing typed inputs on the modifier, managing the group as an asset); steeper user
  mental model; lighter local documentation for the specific displacement pattern.
- **Why not selected**: it trades v1's core virtues — simplicity and stability — for
  flexibility the initial goals (wood/brick/rock relief on simple shapes) do not require.
- **Roadmap**: **v2 primary engine.** The architecture deliberately keeps the controls
  (Strength/Scale/Direction/Mid-level) approach-agnostic so a GN backend can slot behind the
  same panel later.

### Shader/material displacement as the geometry source (rejected outright)

- **Advantages**: excellent live preview; trivial to author in the shader editor.
- **Disadvantages**: render-time only — contributes **zero** geometry to an STL [W4].
- **Why not selected**: it cannot satisfy the geometry-first, printable mandate. It is viable
  only when *baked* into a height-map and fed to a Displace modifier — which is exactly the A2
  fallback / DisplaceIt prior-art path [W1].
- **Roadmap**: not a geometry source; possibly a *preview aid* or bake input later.

### Vector displacement maps (deferred)

- **Advantages**: can model overhangs/undercuts a single-direction scalar height cannot.
- **Disadvantages**: requires specialist vector-map authoring/baking; harder to validate for
  manifoldness; overkill for ridged/grained surfaces.
- **Why not selected**: scalar height displacement along the Normal covers the target textures
  with a simpler, safer control set.
- **Roadmap**: **possible later** if undercut-style textures are requested.

### Voxel remesh as a standard pipeline stage (rejected as a default)

- **Advantages**: guarantees a watertight, uniformly-quad manifold mesh [M6].
- **Disadvantages**: rebuilds topology and can smooth away the very displacement detail it
  follows; raises vertex counts; another heavy step in the default path.
- **Why not selected**: it conflicts with preserving fine relief and with v1 simplicity.
- **Roadmap**: **optional user-invoked cleanup**, paired with the 3D-Print Toolbox [W2] — not
  automatic.

### Sculpt/Multiresolution bake (rejected for automation)

- **Advantages**: ultimate art-direction and localized detail [M7].
- **Disadvantages**: manual, slow, heavy meshes; not reproducible/parametric.
- **Why not selected**: incompatible with a one-click, deterministic add-on.
- **Roadmap**: niche/manual workflow only.

## Legacy vs. Modern Procedural APIs

The v1 recommendation relies on **procedural `Texture` datablocks** (Wood/Noise/Voronoi)
[S4] [S6] driving the Displace modifier. This is a **deliberate engineering tradeoff**, not an
accidental use of outdated APIs:

- **The ecosystem has shifted.** Blender's *modern* procedural authoring centers on
  **Geometry Nodes** and **shader nodes** [M9]; new procedural development largely happens
  there.
- **Texture datablocks remain fully supported.** They are a current, documented part of
  Blender, exposed through stable RNA (`texture`, `texture_coords`, `strength`, `mid_level`,
  `direction`, `space`) [S5] and consumed directly by the Displace modifier [M1] [S3].
- **They are the simplest API for this project's goals.** A `Texture` datablock + a Displace
  modifier is a two-object setup with a small, stable, well-understood property surface — far
  less code and fewer moving parts than constructing and wiring a node graph.
- **Simplicity and stability outweigh maximum flexibility for v1.** The initial release values
  a small, predictable, easily-tested implementation over the open-ended power of nodes. The
  flexibility GN offers is real but unneeded for wood/brick/rock relief, and it is explicitly
  scheduled for v2 (see roadmap).

In short: the project chooses the **simplest stable API that fully meets the goal**, with a
clear, intentional upgrade path to the modern node-based stack when the added flexibility is
warranted.

## Future Evolution (Roadmap)

The v1 architecture is **intentionally conservative**: the smallest stable surface that
produces printable geometry. The roadmap below shows how it can grow without throwing away the
v1 foundation. Crucially, the proposed controls and presets are kept approach-agnostic
(`addon-workflow.md`), so later versions can swap the *engine* behind the same UI.

**Version 1 (this recommendation)**

- Procedural `Texture` datablocks (Wood/Noise/Voronoi) [S4] [S6]
- Displace modifier [M1] [S3]
- Automatic Subdivision Surface (Simple) for density [M5]
- Non-destructive modifier stack; STL export with **Apply Modifiers** [M2] [M3] [S2]

**Version 2 (Geometry Nodes engine behind the same UI)**

- Geometry Nodes implementation as the displacement backend [M2] [M9]
- Layered procedural textures, masks, and multi-texture blending
- More advanced procedural effects (falloffs, per-region control)

**Version 3+ (richer content & manufacturing features)**

- AI-generated height maps as a texture source
- Curated material/texture libraries
- Advanced manufacturing textures (knurling, lattices, functional grips)
- Selective / masked displacement
- Parametric surface generators

Each step is **additive**: v1's Displace path remains valid, and later engines are introduced
behind the established controls rather than as a rewrite.

