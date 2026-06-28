# Texture-to-Geometry — Summary

A short, non-technical review of the research. This is the page rendered to
`docs/index.html`. Full detail and citations live in the other deliverables
(`approaches.md`, `addon-workflow.md`, `prior-art.md`, `references.md`).

## Recommendation at a Glance

**Use the Displace modifier with a procedural texture over a subdivided mesh, and export STL
with "Apply Modifiers" on.**

Top reason: it is the smallest, best-documented, fully native Blender path that produces
**real, printable, watertight geometry** — no UV unwrap required — and displacing along the
surface **Normal** wraps grain cleanly around cylinders and other curved shapes. The displaced
surface becomes real triangles automatically at export, so nothing has to be baked or applied
by hand.

**Fallback:** the same Displace modifier driven by a user **image / height-map** (via UV
coordinates) when a *specific* real-world texture is needed — at the cost of a UV unwrap and
possible seams on curved shapes.

## Approaches (Short)

| Approach | What it is | Best for | Trade-off |
|----------|------------|----------|-----------|
| **A1 · Procedural Displace** *(recommended)* | Wood/Noise/Voronoi math texture drives a Displace modifier over a subdivided mesh | Cylinders & curved shapes; quick procedural grain | Detail capped by mesh density; not a photo match |
| **A2 · Image Displace** *(fallback)* | A grayscale height-map drives the same modifier via UV | Reproducing a specific real texture | Needs UV unwrap; seams/stretch on curves |
| **A3 · Geometry Nodes** *(deferred to v2)* | A node graph computes displacement as a custom modifier | Combined/masked effects, power users | Intentionally deferred — higher complexity than v1 needs |
| A4 · Sculpt/multires *(excluded)* | Hand-sculpted/baked detail on a dense mesh | Art-directed one-offs | Intentionally excluded from automation |

All approaches end the same way: the live modifiers are realized into real geometry when the
STL is exported with **Apply Modifiers**.

The v1 choice — procedural `Texture` datablock + Displace modifier — is a **deliberate
engineering tradeoff**: the simplest, most stable API that fully meets the goal. Blender's
modern procedural stack (Geometry Nodes, shader nodes) is more flexible but is intentionally
deferred to v2 because v1 values simplicity and reliable, print-ready output over maximum
flexibility. See `approaches.md` for the full ADR, including *Explicit Non-Goals*, *Rejected
Alternatives*, and the roadmap below.

## Proposed Workflow (Short)

The proposed add-on turns this into a guided, print-aware experience:

1. Select a mesh (e.g. a cylinder) and open the **Texture → Geometry** panel.
2. Pick a **preset** — *Wood* (fully designed), with *Brick* and *Rock* planned.
3. Adjust a few controls and preview live in the viewport.
4. **Defer to export** (recommended, non-destructive) or **Apply now**.
5. Export STL — the displaced surface becomes real printable geometry.

**The six controls:** *Texture selection* (preset **and** advanced picker), *Strength* (relief
depth in mm, default 0.4 mm), *Scale* (pattern size), *Coordinate mode* (default Local — no UV
needed), *Direction* (default Normal — wraps curves), and *Mid-level* (default 0.5). Print-scale
guidance ties subdivision density and Strength to real millimeters and printer resolution.

## Roadmap at a Glance

The v1 architecture is intentionally conservative; later versions add capability behind the
same controls without discarding the v1 foundation:

- **v1 (now):** procedural Texture datablock → Displace modifier → auto Subdivision → STL with
  Apply Modifiers.
- **v2:** Geometry Nodes engine behind the same UI — layered textures, masks, blending.
- **v3+:** AI-generated height maps, material libraries, advanced manufacturing textures,
  selective displacement, parametric surface generators.

## Open Questions & Next Step

Open questions / risks:

- **Cylinder/curved placement** with image textures still fights UV seams and stretching;
  procedural-along-Normal is the recommended way around it but should be validated on real
  prints.
- **Geometry Nodes** is intentionally deferred to v2 (a deliberate scope choice, not a gap);
  when it graduates it will lean more on community sources for the displacement pattern.
- **Watertightness** under high Strength on coarse meshes needs the 3D-Print Toolbox as a
  validation post-step.

**Single recommended next step:** scope a follow-on feature to **build the add-on around
Approach A1** — a panel that creates a procedural Wood Displace over auto-subdivided geometry
(displace along Normal), previews live, advises print-scale in mm, and exports STL with
`apply_modifiers=True` — with the image/height-map source (A2) as the first fallback option.
