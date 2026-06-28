# Texture-to-Geometry Approaches — Overview

This file is the entry point for the research deliverable set. It frames the problem,
defines shared vocabulary, and maps the rest of the documents.

## Purpose & Scope

This document set decides **how Blender can turn a surface texture (wood grain, brick,
rock, …) into real, printable mesh geometry** for STL export, and proposes how a future
add-on could streamline that workflow. It is **research and documentation only — no add-on
code is written in this feature.**

The scope is deliberately **geometry-first**: every approach considered here must produce
*actual vertices/faces* that survive STL export, because an STL file contains only triangle
geometry — no materials, shaders, or render-time effects. A texture that only changes how a
surface *looks* in a render is therefore worthless for 3D printing; it must be converted into
displacement of the mesh itself. Blender's STL exporter exports the *evaluated* mesh (the mesh
after all modifiers are calculated) when **Apply Modifiers** is enabled, which is the
mechanism that lets a live displacement become real printable geometry [M3] [S2].

In scope:

- Geometry-producing methods (Displace modifier, image/height-map displacement, Geometry
  Nodes displacement) over a sufficiently dense base mesh.
- The role of subdivision in providing enough vertices for fine detail.
- STL export behavior and the non-destructive "defer to export" vs. "apply now" choice.
- A proposed streamlined add-on workflow, controls, and presets.
- Prior art: how the community already does this and which add-ons exist.

## Glossary

Displacement
   Moving a mesh's vertices outward/inward based on a texture value, producing real geometry.
   The Displace modifier offsets each vertex by `(texture_value − Midlevel) × Strength` along
   a chosen direction [M1] [S3].

Modifier
   A non-destructive operation applied on top of an object's base geometry; it changes the
   displayed/rendered result without editing the original mesh until *applied* [M2].

Modifier stack
   The ordered list of modifiers on an object, evaluated top to bottom [M2].

Apply (a modifier)
   Making a modifier "real": the object's geometry is replaced by the modifier's result and
   the modifier is removed [M2]. STL export with **Apply Modifiers** does this implicitly for
   the exported copy via the evaluated mesh [M3] [S2].

Evaluated mesh
   The final mesh after the whole modifier stack is calculated. The STL exporter writes the
   evaluated mesh when **Apply Modifiers** is on [S2].

Subdivision Surface modifier
   A *Generate* modifier that adds geometry; in **Simple** mode it increases base-mesh
   resolution specifically so displacement maps have enough vertices to deform [M5].

Procedural texture
   A texture computed by formula (e.g. Wood, Noise, Voronoi) rather than from an image; stored
   in a `Texture` datablock and sampled by the Displace modifier [S4] [S6].

Height-map / image texture
   A grayscale (or color) image whose pixel values drive displacement, typically placed via UV
   or generated coordinates [M1] [M4].

Coordinate space
   How a texture is mapped onto the mesh (Local, Global, Object, UV); determines where the
   pattern sits and how it stretches over curved surfaces [M1] [M4] [T1].

Manifold ("watertight")
   A mesh with no holes or non-physical self-intersections — a requirement for reliable 3D
   printing. High displacement strength on a coarse mesh risks self-intersection.

Midlevel
   The texture value treated as "no displacement"; values above push out, below push in [M1]
   [S3].

## How to Read This Set

| File | What it gives you |
|------|-------------------|
| `00-overview.md` (this file) | Scope, glossary, geometry-first framing. |
| `approaches.md` | The candidate geometry approaches, a comparison matrix, and the **recommendation** (primary + fallback). Read as an **ADR**: also contains *Explicit Non-Goals (v1)*, *Rejected Alternatives*, *Legacy vs. Modern Procedural APIs*, and the *Future Evolution (Roadmap)*. Start here for the decision. |
| `addon-workflow.md` | The proposed add-on: end-to-end user journey, the six controls, texture presets, and apply-now vs. defer-to-export. |
| `prior-art.md` | How the community already textures objects for 3D printing and which add-ons exist, with gaps. |
| `references.md` | Every citation tag (`[S]`/`[M]`/`[T]`/`[W]`) resolved to a real path or URL. |
| `summary.md` | A short, non-technical summary; it is the source rendered into `docs/index.html` for browser review. |

Citation tags resolve in `references.md`: `[S]` = Blender source, `[M]` = Blender manual,
`[T]` = reference TOC, `[W]` = web.

## Out of Scope

The following are explicitly **not deliverables** of this research because they do not produce
exportable geometry (FR-011):

- **Material/shader-only texturing** — assigning an image or procedural texture to a material
  for *render* appearance only. This includes the material-output **Displacement** socket used
  for render-time micro-displacement/bump: it changes the rendered look but does **not** alter
  the exported mesh, so it is useless for STL/3D-print geometry [W4]. (A community add-on exists
  precisely to *bake* such shader displacement into real geometry — see `prior-art.md` [W1].)
- **Bump/normal mapping** — fakes surface relief via shading; no geometry change.
- **Texture painting / UV unwrapping for color** — surface color, not shape.
- **Writing the actual add-on** — this feature only researches and recommends; building the
  Blender extension is a follow-on feature.

Material/shader concepts appear here only where they *feed* a geometry path (e.g. a procedural
`Texture` datablock that drives the Displace modifier, or shader displacement that an add-on
bakes into mesh).

This section excludes methods that are *not geometry at all*. For implementation approaches
that **do** produce geometry but are nonetheless **intentionally deferred or excluded for v1**
(Geometry Nodes as the primary engine, vector displacement maps, adaptive/render-only
tessellation, sculpt/multires, automatic voxel remesh), see `approaches.md` →
**Explicit Non-Goals (v1)** and **Rejected Alternatives**.
