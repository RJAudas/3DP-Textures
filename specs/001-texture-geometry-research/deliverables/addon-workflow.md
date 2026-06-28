# Proposed Add-on Workflow & UX

A proposal for a streamlined Blender add-on ("Wood Grain Geometry" / texture-to-geometry) that
makes the recommended approach (A1 procedural Displace; A2 image as fallback — see
`approaches.md`) a guided, print-aware experience. This is a **design proposal**, not built
code. All mechanism claims cite the local Blender source/manual.

## Proposed User Journey

The end-to-end example journey — add a cylinder, apply a wood texture, size it, and export a
printable STL — as ordered steps. Each step lists the user action, the add-on's response, and
the resulting state (`live-modifier` / `baked-geometry` / `exported`).

| # | User action | Add-on response | Result state |
|---|-------------|-----------------|--------------|
| 1 | Add a mesh (e.g. cylinder) and select it | Panel detects an active mesh object and enables its controls | live-modifier (none yet) |
| 2 | Open the **Texture → Geometry** panel (N-panel / Object menu) | Shows preset picker + controls with print-aware defaults | live-modifier |
| 3 | Pick a **texture preset** (e.g. *Wood*) | Creates a procedural `Texture` datablock (Wood) and a **Displace** modifier referencing it; adds a **Subdivision Surface** (Simple) modifier below it for density [M1] [M5] [S4] [T1] | live-modifier |
| 4 | Place / size the texture (Scale, Strength in mm) | Updates `mid_level`/`strength` and texture scale; displaces along **Normal** so grain wraps the cylinder without UVs [M1] [S3] | live-modifier (live preview) |
| 5 | Preview in the viewport | Modifier stack shows displaced geometry in real time; nothing destructive yet [M2] | live-modifier |
| 6a | **Defer** (recommended): leave modifiers live | Add-on keeps the stack non-destructive; geometry realized only at export [M2] | live-modifier |
| 6b | **Apply now** (optional): bake to mesh | Add-on applies the Subdivision + Displace modifiers, replacing base geometry [M2] | baked-geometry |
| 7 | Export STL | Calls `bpy.ops.wm.stl_export(..., apply_modifiers=True)`; exporter writes the **evaluated** mesh so live displacement becomes real triangles [M3] [S1] [S2] [T1] | exported |

The journey supports **both** branches: deferring to export (6a, the non-destructive default)
and applying now (6b). Both end in a printable STL because Apply Modifiers on export realizes
any still-live modifiers [M3] [S2].

## Controls

The panel exposes these controls. The six required controls are **Texture selection**,
**Strength**, **Scale**, **Coordinate mode**, **Direction**, and **Mid-level**; each maps to a
real Displace/texture property [M1] [S5] [T1].

| Control | Purpose | Type | Default | Mode | Maps to |
|---------|---------|------|---------|------|---------|
| **Texture selection** | Choose what drives the displacement (a curated preset, or an advanced raw texture/image datablock) | preset enum **and** datablock/image picker | *Wood* preset | **both** (preset *and* advanced) | `DisplaceModifier.texture` (procedural `Texture` or `TEX_IMAGE`) [S4] [S5] [S6] |
| **Strength** | Physical relief depth of the displacement | float (mm) | **0.4 mm** | both | `DisplaceModifier.strength`; offset = `displacement × Strength` [M1] [S3] |
| **Scale** | Size/frequency of the texture pattern on the surface | float | **1.0** | both | texture mapping size (texture `noise_scale`/size + modifier coords) [M4] [S6] |
| **Coordinate mode** | Texture coordinate space (how the pattern sits on the mesh) | enum: Local / Global / Object / UV | **Local** (Generated-like; no UV needed) | advanced (preset picks a sensible default) | `DisplaceModifier.texture_coords` [M1] [M4] [T1] |
| **Direction** | Axis the vertices move along | enum: Normal / X / Y / Z / RGB→XYZ | **Normal** (wraps curved shapes) | advanced | `DisplaceModifier.direction` [M1] [S3] [T1] |
| **Mid-level** | Texture value treated as "no displacement" (balances push-out vs. push-in) | float (0–1) | **0.5** | advanced | `DisplaceModifier.mid_level`; `displacement = value − Midlevel` [M1] [S3] |
| Subdivision level | Base-mesh density for fine relief | int | auto for ~0.2–0.5 mm edges | advanced | Subdivision Surface (Simple) **Levels** [M5] |
| Apply / Defer | Realize geometry now or only at export | enum: Defer (default) / Apply now | **Defer** | both | modifier apply vs. export Apply Modifiers [M2] [M3] [S2] |

**Texture selection is dual-mode** (clarification Q3): a **preset** form (one click → *Wood/
Brick/Rock*) for quick starts, **and** an **advanced** raw form that lets a power user pick any
procedural `Texture` datablock or supply an image/height-map directly [S4] [S6].

## Texture Presets

Presets are curated quick-starts that preconfigure a texture + control values and select which
approach they drive. At least **Wood** is fully specified; **Brick** and **Rock** are named.

### Wood (fully specified)

- **id**: `wood`
- **maps_to**: a procedural **Wood**-type `Texture` datablock (`TEX_WOOD`) [S4] [S6] driving
  the **Displace** modifier (Approach A1). Configured for ring/band grain (the Wave/Wood
  pattern reference informs ring spacing) [T1].
- **default_controls**:
  - Texture selection: *Wood* preset
  - Strength: **0.4 mm**
  - Scale: **1.0** (ring frequency tuned for ~0.5–1 mm grain)
  - Coordinate mode: **Local** (no UV unwrap; grain follows the object)
  - Direction: **Normal** (grain wraps cylinders/curves seamlessly) [M1]
  - Mid-level: **0.5**
  - Subdivision: auto to ~0.2–0.5 mm edge length [M5]
- **drives approach**: A1 (Displace + procedural Texture).

### Brick (named)

- **id**: `brick` — maps to a procedural pattern (or brick height-map image) driving Displace;
  larger Scale, harder edges; drives A1 (procedural) or A2 (image) [S4] [M1].

### Rock (named)

- **id**: `rock` — maps to a Noise/Voronoi procedural `Texture` (`TEX_NOISE` / `TEX_VORONOI`)
  [S4] for irregular rocky relief; drives A1.

Each preset states the Approach it configures, so the same panel can later add image-based or
Geometry-Nodes presets without changing the journey.

## Apply Now vs. Defer to Export

Blender modifiers are **always live**: there is no special "export-only modifier" mode. The
effect the user wants — "apply the texture only when I export" — is achieved by simply leaving
the Displace (and Subdivision) modifiers **un-applied** and exporting with **Apply Modifiers**
on, which writes the *evaluated* mesh [M3] [S2]. The add-on should make this the default.

- **Defer to export (default, non-destructive).** Keep the modifier stack live. The base mesh
  stays editable; Strength/Scale/Mid-level remain adjustable; the displaced geometry is
  generated only for the exported STL via `apply_modifiers=True` [M2] [M3] [S1] [S2]. This
  upholds the project's non-destructive principle and lets the user iterate freely.
- **Apply now (optional, destructive).** If the user wants the displaced mesh *in the scene*
  (e.g. to sculpt further or hand off), the add-on applies the modifiers, replacing the base
  geometry and removing the modifiers [M2]. After this, export no longer depends on Apply
  Modifiers because the geometry is already real.

Either way the exported STL contains the displaced geometry; defer is recommended because it
preserves the editable source. (Note: an un-applied modifier is **not** lost at export — Apply
Modifiers realizes it for the exported copy only [M3] [S2].)

## Generalization to Other Shapes

The workflow is not cylinder-specific. The same preset → Displace-along-Normal → subdivide →
export pipeline applies to any closed mesh (boxes, spheres, organic shapes), because Normal
displacement and procedural coordinates need no UV map [M1] [M4]. Caveats to surface to the
user:

- **Flat faces** displace cleanly with Local/Generated coordinates; **curved/closed** shapes
  benefit most from **Direction = Normal** to avoid one-axis stretching [M1] [S3].
- **Image/UV presets (A2)** on non-flat shapes inherit UV **seams and stretching**; warn the
  user and prefer procedural presets for cylinders/spheres [M4].
- **Sharp concave features** can self-intersect under high Strength on any shape — keep
  Strength modest relative to wall thickness and validate watertightness with the 3D-Print
  Toolbox before printing [W2].
- **Very thin or small features** below printer resolution won't print regardless of shape;
  scale density to real mm (see `approaches.md` print-scale guidance) [M5].
